"""Gera atlas de textura (pintura procedural realista), geometria Bedrock e renderizações de conferência."""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from bt import rot_bb, vec_bb

R = 4            # texels por unidade
PAD = 2
rng = np.random.default_rng(7)

FACES = ("north", "south", "east", "west", "up", "down")


def face_dims(s, f):
    sx, sy, sz = s
    return {"north": (sx, sy), "south": (sx, sy), "east": (sz, sy), "west": (sz, sy),
            "up": (sx, sz), "down": (sx, sz)}[f]


# ------------------------------------------------------------ materiais
def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


# ------------------------------------------------------------ pintura 3D
# Cada texel sabe seu ponto 3D na arma (espaço bb do modelo). Assim:
#  - ruído, veio e manchas são CONTÍNUOS entre faces e entre cubos vizinhos (antes: cada face era um retalho);
#  - oclusão ambiente (sujeira/sombra de contato) sai da geometria real, por SDF dos cubos;
#  - o desgaste fica nas quinas EXPOSTAS e em manchas irregulares (antes: contorno claro em todo cubo).
class Ruido3D:
    """Ruído de valor 3D (rede periódica, interpolação suave) + fbm."""

    def __init__(self, seed, n=48):
        self.n = n
        self.g = np.random.default_rng(seed).random((n, n, n)) * 2 - 1

    def __call__(self, p):
        p = np.asarray(p, float)
        i0 = np.floor(p).astype(int)
        f = p - i0
        f = f * f * (3 - 2 * f)
        n, g = self.n, self.g
        out = 0.0
        for dx in (0, 1):
            wx = f[..., 0] if dx else 1 - f[..., 0]
            for dy in (0, 1):
                wy = f[..., 1] if dy else 1 - f[..., 1]
                for dz in (0, 1):
                    wz = f[..., 2] if dz else 1 - f[..., 2]
                    out = out + wx * wy * wz * g[(i0[..., 0] + dx) % n, (i0[..., 1] + dy) % n, (i0[..., 2] + dz) % n]
        return out

    def fbm(self, p, oitavas=4):
        s, a, tot = 0.0, 1.0, 0.0
        for k in range(oitavas):
            s = s + a * self(np.asarray(p) * (2 ** k) + k * 17.31)
            tot += a
            a *= 0.5
        return s / tot


RUIDO = Ruido3D(11)


def _esticado(P, eixo, ao_longo, atraves):
    """Coordenadas para ruído esticado ao longo de 'eixo' (escovado, fibra da madeira, riscos)."""
    t = P @ eixo
    return P * atraves + np.multiply.outer(t, eixo) * (ao_longo - atraves)


def _caixa(c):
    """Dados do cubo para SDF no espaço bb (com rotação)."""
    o = np.array(c["o"], float); s = np.array(c["s"], float)
    lo, hi = vec_bb(o), vec_bb(o + s)
    lo, hi = np.minimum(lo, hi), np.maximum(lo, hi)
    R = rot_bb(c["r"]) if "r" in c else None
    pv = vec_bb(c["p"]) if "r" in c else None
    return ((lo + hi) / 2, (hi - lo) / 2, R, pv)


def sdf_cubos(P, caixas):
    """Distância com sinal de P (..., 3) ao conjunto de cubos (negativa dentro)."""
    d = np.full(P.shape[:-1], 1e9)
    for centro, meia, R, pv in caixas:
        Q = P if R is None else (P - pv) @ R + pv          # para o referencial do cubo (R ortonormal)
        q = np.abs(Q - centro) - meia
        fora = np.linalg.norm(np.maximum(q, 0), axis=-1)
        dentro = np.minimum(q.max(-1), 0)
        d = np.minimum(d, fora + dentro)
    return d


def contexto_face(c, f, w, h, caixas):
    """Ponto 3D, normal, distância à borda e oclusão ambiente de cada texel da face (h, w)."""
    q = cube_face_quads(c)[f]
    a = (np.arange(w) + 0.5) / w
    b = (np.arange(h) + 0.5) / h
    A, B = np.meshgrid(a, b)
    A3, B3 = A[..., None], B[..., None]
    P = (q[0] * (1 - A3) + q[1] * A3) * (1 - B3) + (q[3] * (1 - A3) + q[2] * A3) * B3
    n = np.cross(q[1] - q[0], q[3] - q[0])
    centro = np.mean(np.concatenate(list(cube_face_quads(c).values())), axis=0)
    if np.dot(n, q.mean(0) - centro) < 0:
        n = -n
    n = n / (np.linalg.norm(n) or 1.0)
    fw, fh = face_dims(c["s"], f)
    E = np.minimum(np.minimum(A * fw, (1 - A) * fw), np.minimum(B * fh, (1 - B) * fh))
    # eixo longo do cubo (veio/escovado seguem a peça)
    k = int(np.argmax(c["s"]))
    eixo = vec_bb(np.eye(3)[k])
    if "r" in c:
        eixo = rot_bb(c["r"]) @ eixo
    eixo = eixo / np.linalg.norm(eixo)
    # oclusão ambiente por SDF: amostras acima da superfície; se algo está mais perto que a altura, escurece
    ocl = np.zeros((h, w))
    for alt, peso in ((0.35, 0.5), (0.9, 0.3), (2.0, 0.2)):
        d = sdf_cubos(P + n * alt, caixas)
        ocl += peso * np.clip((alt - d) / alt, 0, 1)
    ao = 1 - np.clip(ocl, 0, 1)
    # altura do texel dentro do cubo (para a luz pintada: degradê, faixa de reflexo, quina de cima/baixo)
    todos = np.concatenate(list(cube_face_quads(c).values()))
    ymin, ymax = todos[:, 1].min(), todos[:, 1].max()
    alt_rel = np.clip((P[..., 1] - ymin) / max(ymax - ymin, 1e-6), 0, 1)
    return dict(P=P, n=n, E=E, ao=ao, eixo=eixo, fw=fw, fh=fh, alt=alt_rel,
                d_topo=ymax - P[..., 1], d_base=P[..., 1] - ymin)


# Paleta em cinzas MÉDIOS (v1.4): arma preta de verdade, sob a luz chapada do Minecraft, precisa de base
# ~#40-#60 para as faces mostrarem volume; com ~#20 (até a v1.3) tudo virava silhueta.
METAIS = {"aco": "#56595e", "aco_claro": "#74787e", "aco_escuro": "#404246", "ferrolho": "#505357",
          "quebra_chama": "#3d3f42", "ferrolho_serrilha": "#505357", "carregador": "#424448",
          "carregador_m4": "#63666a", "anodizado": "#4c4f53", "guarda_mao": "#484b4f", "trilho": "#45484c"}
POLIMEROS = {"polimero": "#3a3c3f", "polimero_grip": "#36383b", "borracha": "#2b2b2c"}


def base_3d(mat, cx):
    """Cor base (h, w, 3) contínua no espaço, por material."""
    P, eixo = cx["P"], cx["eixo"]
    h, w = P.shape[:2]
    if mat in METAIS:
        col = hexrgb(METAIS[mat])
        img = np.ones((h, w, 3)) * col
        # Estilo LIMPO (v1.4.1): nada de ruído fino. O jogo desenha textura sem suavização e, com a arma
        # perto do olho, cada texel de granulado vira um "quadradinho" (aspecto pixelado e sujo).
        escovado = mat not in ("anodizado", "guarda_mao", "trilho")
        img += (3.0 * RUIDO.fbm(P / 10.0))[..., None]                      # manchas muito suaves
        if escovado:
            img += (1.5 * RUIDO(_esticado(P, eixo, 0.05, 0.8) + 90))[..., None]
        # aço tratado puxa levemente para o azul (não é cinza puro)
        img += np.multiply.outer(RUIDO.fbm(P / 12.0 + 7), np.array([-1.5, 0.0, 2.5]))
        return img
    if mat in POLIMEROS:
        img = np.ones((h, w, 3)) * hexrgb(POLIMEROS[mat])
        img += (2.0 * RUIDO.fbm(P / 8.0 + 3))[..., None]                   # polímero liso (fosco de verdade)
        return img
    if mat == "madeira":
        # nogueira/bétula laminada da AK: anéis de crescimento cortados quase em paralelo ao comprimento
        t = P @ eixo
        perp = P - np.multiply.outer(t, eixo)
        ref = np.cross(eixo, [0.0, 1.0, 0.0])
        if np.linalg.norm(ref) < 1e-3:
            ref = np.array([1.0, 0, 0])
        ref = ref / np.linalg.norm(ref)
        r = np.linalg.norm(perp - ref * 60.0, axis=-1)                     # "centro da árvore" longe da peça
        r = r + 2.4 * RUIDO.fbm(_esticado(P, eixo, 0.06, 0.5) + 500) + 0.02 * t
        aneis = 0.5 + 0.5 * np.sin(r * 2 * np.pi / 2.6)
        aneis = aneis ** 2.2                                               # lenho tardio mais estreito e escuro
        fibra = RUIDO(_esticado(P, eixo, 0.05, 4.5) + 700)
        base, escuro, claro = hexrgb("#7d3b1c"), hexrgb("#4a1d0c"), hexrgb("#9e5428")
        img = base + np.multiply.outer(aneis, escuro - base) * 0.75
        img += np.multiply.outer(np.clip(-aneis + 0.6, 0, 1), claro - base) * 0.5
        img += np.multiply.outer(fibra, np.array([5.0, 3.5, 2.5]))
        img += (5.0 * RUIDO.fbm(P / 6.0 + 900))[..., None]                 # verniz irregular
        return img
    if mat == "luva":
        img = np.ones((h, w, 3)) * hexrgb("#2d2c29")
        img += (3.0 * RUIDO.fbm(P / 4.0 + 60))[..., None]
        return img
    if mat == "manga":
        img = np.ones((h, w, 3)) * hexrgb("#4d5233")
        img += np.multiply.outer(RUIDO.fbm(P / 4.0 + 80), np.array([7.0, 7.0, 4.0]))   # manchas do tecido
        return img
    if mat == "boca":
        return np.ones((h, w, 3)) * 9 + (1.5 * RUIDO(P * 3 + 5))[..., None]
    raise ValueError(mat)


def detalhes_2d(mat, img):
    """Padrões usinados/moldados da face (fendas, serrilha, nervuras, trama), no referencial da face."""
    h, w = img.shape[:2]
    long_u = w >= h
    L = w if long_u else h
    S = h if long_u else w

    def faixa(s_sl, l_sl):
        return (s_sl, l_sl) if long_u else (l_sl, s_sl)

    if mat == "quebra_chama":
        for k in range(4, L - 3, 6):
            img[faixa(slice(S // 3, 2 * S // 3), slice(k, k + 3))] = 10
    elif mat == "ferrolho_serrilha":
        for k in range(2, L - 1, 4):
            img[faixa(slice(None), slice(k, k + 2))] -= 16
    elif mat == "carregador" and S > 6:
        mid = S // 2
        img[faixa(slice(mid - 1, mid + 1), slice(2, -2))] += 14
    elif mat == "guarda_mao" and S > 8:
        for k in range(6, L - 6, 10):
            j = S // 2
            img[faixa(slice(j - 2, j + 2), slice(k - 3, k + 3))] = 9
    elif mat == "trilho":
        for k in range(0, L, 8):
            img[faixa(slice(None), slice(k, k + 4))] -= 13
    elif mat == "polimero_grip":
        # textura de empunhadura: losangos finos em relevo (não ruído aleatório, que parecia chuvisco)
        yy, xx = np.mgrid[0:h, 0:w]
        img[((xx + yy) % 4 == 0) | ((xx - yy) % 4 == 0)] -= 5
    elif mat == "luva":
        img[::2, ::2] -= 4
        img[1::2, 1::2] += 3
    elif mat == "manga":
        if long_u:
            img[h // 2, :] -= 14
        else:
            img[:, w // 2] -= 14
    return img


def acabamento(mat, img, cx):
    """Luz PINTADA (o Minecraft não tem brilho especular em entidade), desgaste e sombra de contato.
    - laterais: degradê vertical (baixo mais escuro), faixa de reflexo do céu perto do topo (metais),
      quina de cima clara e nítida, quina de baixo escura;
    - faces de cima um pouco mais claras, de baixo mais escuras;
    - desgaste só em quina exposta, em manchas; sombra de contato leve (muita sombra deixava tudo opaco)."""
    P, n, E, ao = cx["P"], cx["n"], cx["E"], cx["ao"]
    metal, poli = mat in METAIS, mat in POLIMEROS
    exposto = ao ** 2
    if abs(n[1]) < 0.5:                                                     # face lateral
        t = cx["alt"]
        img = img * (0.84 + 0.24 * t)[..., None]
        if metal:
            img = img + (16.0 * np.exp(-((t - 0.8) / 0.09) ** 2))[..., None]
        elif poli or mat == "madeira":
            img = img + (5.0 * np.exp(-((t - 0.8) / 0.12) ** 2))[..., None]
        topo = (np.clip(1 - cx["d_topo"] / 0.3, 0, 1) * exposto)[..., None]
        base = (np.clip(1 - cx["d_base"] / 0.3, 0, 1))[..., None]
        img = img + topo * (30 if metal else 16 if poli else 10) - base * 10
    elif n[1] > 0:                                                          # face de cima
        img = img * 1.07
        img = img + (np.clip(1 - E / 0.3, 0, 1) * exposto)[..., None] * (22 if metal else 12)
    else:                                                                   # face de baixo
        img = img * 0.86
    # desgaste: só perto da borda exposta, em manchas
    borda = np.clip(1 - E / 0.6, 0, 1) ** 1.6
    mancha = np.clip((RUIDO(P * 1.2 + 200) + 0.1) * 2.0, 0, 1)
    gasto = (borda * mancha * exposto)[..., None]
    if metal:
        img = img + (hexrgb("#8a8f96") - img) * gasto * 0.3                 # aço nu aparecendo
    elif mat == "madeira":
        img = img + (hexrgb("#b07a4f") - img) * gasto * 0.3
    elif poli or mat in ("luva", "manga"):
        img = img + 8 * gasto
    # sombra de contato leve
    sujo = (1 - ao)[..., None]
    if metal or poli:
        img = img + (hexrgb("#2a2620") - img) * sujo * 0.12
    img = img * (0.78 + 0.22 * ao)[..., None]
    return img


def paint(mat, w, h, cx=None):
    """RGBA (h, w, 4) do material. Com contexto 3D (cx), pinta contínuo no espaço; sem, usa uma face plana."""
    if cx is None:
        cx = dict(P=np.dstack(np.meshgrid(np.arange(w) / R, np.arange(h) / R) + [np.zeros((h, w))]),
                  n=np.array([0.0, 0.0, 1.0]), E=np.full((h, w), 9.0), ao=np.ones((h, w)),
                  eixo=np.array([1.0, 0, 0]) if w >= h else np.array([0, 1.0, 0]),
                  alt=np.repeat(1 - (np.arange(h) + 0.5)[:, None] / h, w, axis=1),
                  d_topo=np.full((h, w), 9.0), d_base=np.full((h, w), 9.0))
    img = base_3d(mat, cx)
    img = detalhes_2d(mat, img)
    img = acabamento(mat, img, cx)
    rgba = np.concatenate([img.clip(0, 255), np.full((h, w, 1), 255.0)], axis=2)
    return rgba.astype(np.uint8)


def flash_texture(size):
    """Clarão do tiro para material aditivo (preto = invisível)."""
    y, x = np.mgrid[0:size, 0:size]
    c = (size - 1) / 2
    r = np.hypot(x - c, y - c) / c
    ang = np.arctan2(y - c, x - c)
    star = (1 - r).clip(0, 1) ** 1.5 * (0.6 + 0.4 * np.cos(ang * 5) ** 2)
    core = (1 - r * 2.2).clip(0, 1)
    v = (star + core).clip(0, 1)
    img = np.stack([v * 255, v * 215 + core * 40, v * 110 + core * 140], axis=2).clip(0, 255)
    return np.concatenate([img, np.full((size, size, 1), 255)], axis=2).astype(np.uint8)


# ------------------------------------------------------------ atlas
class Atlas:
    def __init__(self, width_px=1024):
        self.W = width_px
        self.x = self.y = self.row_h = 0
        self.items = []  # (px, py, img)

    def add(self, img):
        h, w = img.shape[:2]
        pw, ph = w + 2 * PAD, h + 2 * PAD
        if self.x + pw > self.W:
            self.x = 0
            self.y += self.row_h
            self.row_h = 0
        px, py = self.x + PAD, self.y + PAD
        self.items.append((px, py, img))
        self.x += pw
        self.row_h = max(self.row_h, ph)
        return px, py

    def image(self):
        H = self.y + self.row_h
        H = 1 << (H - 1).bit_length()
        out = np.zeros((H, self.W, 4), np.uint8)
        for px, py, img in self.items:
            h, w = img.shape[:2]
            padded = np.pad(img, ((PAD, PAD), (PAD, PAD), (0, 0)), mode="edge")
            out[py - PAD:py + h + PAD, px - PAD:px + w + PAD] = padded
        return Image.fromarray(out, "RGBA")


def build_geometry(identifier, bones_cubes, atlas_width=1024, flash_at=None):
    """bones_cubes: lista de (nome_osso, pai, pivô, cubos). Retorna (geo_json, atlas_img, faces_render)."""
    atlas = Atlas(atlas_width)
    render_faces = []   # para o renderizador: (bone, cube, face, img)
    bones = []
    # oclusão: as peças da arma (todos os ossos menos "maos") sombreiam umas às outras; as mãos só a si mesmas,
    # porque somem fora da 1ª pessoa
    caixas_arma = [_caixa(c) for name, _, _, cs in bones_cubes if name != "maos" for c in cs]
    for name, parent, pivot, cubes in bones_cubes:
        jcubes = []
        caixas = [_caixa(c) for c in cubes] if name == "maos" else caixas_arma
        for c in cubes:
            uv = {}
            for f in FACES:
                fw, fh = face_dims(c["s"], f)
                pw, ph = max(1, int(round(fw * R))), max(1, int(round(fh * R)))
                img = paint(c["m"], pw, ph, contexto_face(c, f, pw, ph, caixas))
                px, py = atlas.add(img)
                uv[f] = {"uv": [px / R, py / R], "uv_size": [fw, fh]}
                render_faces.append((name, c, f, img))
            jc = {"origin": [round(v, 4) for v in c["o"]], "size": [round(v, 4) for v in c["s"]], "uv": uv}
            if "r" in c:
                jc["rotation"] = [round(v, 4) for v in c["r"]]
                jc["pivot"] = [round(v, 4) for v in c["p"]]
            jcubes.append(jc)
        b = {"name": name, "pivot": [round(v, 4) for v in pivot], "cubes": jcubes}
        if parent is None:
            b["binding"] = "q.item_slot_to_bone_name(c.item_slot)"
        else:
            b["parent"] = parent
        bones.append(b)

    if flash_at is not None:
        fimg = flash_texture(64)
        px, py = atlas.add(fimg)
        fx, fy, fz = flash_at
        size = 12
        uvf = {"uv": [px / R, py / R], "uv_size": [16, 16]}
        # dois planos cruzados + um de frente
        cubes = [
            {"origin": [fx - size / 2, fy - size / 2, fz], "size": [size, size, 0], "uv": {"north": uvf, "south": uvf}},
            {"origin": [fx, fy - size / 2, fz - 1], "size": [0, size, size * 1.4], "uv": {"east": uvf, "west": uvf}},
            {"origin": [fx - size / 2, fy, fz - 1], "size": [size, 0, size * 1.4], "uv": {"up": uvf, "down": uvf}},
        ]
        bones.append({"name": "flash", "parent": bones[0]["name"], "pivot": [fx, fy, fz], "cubes": cubes})

    img = atlas.image()
    geo = {
        "format_version": "1.16.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": identifier,
                "texture_width": img.width / R,
                "texture_height": img.height / R,
                "visible_bounds_width": 4,
                "visible_bounds_height": 4,
                "visible_bounds_offset": [0, 1.5, 0],
            },
            "bones": bones,
        }],
    }
    return geo, img, render_faces


# ------------------------------------------------------------ renderizador (conferência)
def cube_face_quads(c):
    """Cantos (espaço bb, antes de rotação de osso) de cada face do cubo, já com rotação do cubo."""
    o = np.array(c["o"], float)
    s = np.array(c["s"], float)
    x0, y0, z0 = o
    x1, y1, z1 = o + s
    # cantos em coordenadas Bedrock
    P = {
        "north": [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        "south": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        "east": [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
        "west": [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
        "up": [(x1, y1, z1), (x0, y1, z1), (x0, y1, z0), (x1, y1, z0)],
        "down": [(x1, y0, z0), (x0, y0, z0), (x0, y0, z1), (x1, y0, z1)],
    }
    out = {}
    for f, pts in P.items():
        q = np.array([vec_bb(p) for p in pts])
        if "r" in c:
            Rm = rot_bb(c["r"])
            pv = vec_bb(c["p"])
            q = (Rm @ (q - pv).T).T + pv
        out[f] = q
    return out


SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.62, "west": 0.62}


def render(render_faces, bone_world, project, size, bg=None, lightdir=None, perto=0.05):
    """bone_world: nome_osso -> função(pts_bb Nx3) -> pts no espaço de câmera (x direita, y cima, z frente).
    project: função(pts_cam) -> (u, v) pixels.
    Pintor por PEDAÇO de face (cada face é subdividida e todos os pedaços são ordenados juntos): com a câmera
    colada na arma (mira), ordenar faces inteiras pelo centro trocava a ordem de faces grandes. Pedaços atrás
    do plano 'perto' são descartados um a um (antes a face inteira sumia se um canto passasse do plano)."""
    W, H = size
    img = bg.copy() if bg is not None else Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pedacos = []
    for bone, c, f, tex in render_faces:
        if bone not in bone_world:
            continue
        q = cube_face_quads(c)[f]
        qc = bone_world[bone](q)
        n = np.cross(qc[1] - qc[0], qc[3] - qc[0])
        center = qc.mean(0)
        # face voltada para a câmera (câmera na origem). O referencial da câmera (direita, cima, frente) é um
        # espelho do bb, então a ordem dos cantos de cube_face_quads dá a normal para DENTRO: visível com n·c > 0.
        # (Até a v1.2.2 o teste estava invertido e as prévias mostravam o verso das faces.)
        if np.dot(n, center) <= 0:
            continue
        sh = SHADE[f]
        th, tw = tex.shape[:2]
        sub_u, sub_v = min(tw, 40), min(th, 40)
        a = np.linspace(0, 1, sub_u + 1)[None, :, None]
        b = np.linspace(0, 1, sub_v + 1)[:, None, None]
        G = (qc[0] * (1 - a) + qc[1] * a) * (1 - b) + (qc[3] * (1 - a) + qc[2] * a) * b   # (sub_v+1, sub_u+1, 3)
        for i in range(sub_v):
            for j in range(sub_u):
                cantos = np.array([G[i, j], G[i, j + 1], G[i + 1, j + 1], G[i + 1, j]])
                if np.any(cantos[:, 2] <= perto):
                    continue
                ty = min(th - 1, int((i + 0.5) / sub_v * th))
                tx = min(tw - 1, int((j + 0.5) / sub_u * tw))
                col = tuple(int(v) for v in tex[ty, tx, :3].astype(float) * sh) + (255,)
                pedacos.append((float(np.linalg.norm(cantos.mean(0))), cantos, col))
    pedacos.sort(key=lambda t: -t[0])
    for _, cantos, col in pedacos:
        draw.polygon([tuple(project(p)) for p in cantos], fill=col)
    return img
