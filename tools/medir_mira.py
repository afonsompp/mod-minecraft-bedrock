"""Mede o desalinhamento da mira em prints do jogo e devolve os ângulos da câmera (CALIB) corrigidos.

Uso:
  python tools/medir_mira.py awp=quadro1.png awp=quadro2.png glock=quadro3.png ak47=quadro4.png

Cada argumento é `arma=print`, de um print MIRANDO AGACHADO, do pack da versão ATUAL (a medição compara
o print com a pose que o gerador produz hoje). Vale a pena dar mais de uma arma: é o que separa um erro
de ÂNGULO da câmera de um erro de POSIÇÃO dela (o AGACHADO).

Como ele mede:
  - arma com luneta (AWP): o cruzamento do retículo contra o retículo do jogo. As linhas têm 1 px e alto
    contraste, então dá ~0,07° — é o instrumento bom, e também mede o giro (roll);
  - arma de mira de ferro: encaixa a silhueta escura do print na silhueta que o modelo prevê. Dá ~0,2°,
    e só o eixo horizontal é confiável (a arma é comprida, e deslizar ao longo dela quase não muda a
    silhueta). Serve de confirmação.

Por que não existe mais o `calibrar_mira.py`: ele media o mesmo desvio e jogava TUDO no AGACHADO, como se
a câmera só pudesse estar deslocada. Um erro de ângulo da câmera dá o MESMO desvio em todas as armas; um
erro de posição dá um desvio proporcional a 1/distância do olho, então a AWP (olho 2,0) erraria quase 4x
mais que a AK (olho 7,5). Na v1.6.2 isso foi confundido e o AGACHADO absorveu um erro que era de ângulo.
Com duas armas ou mais, os dois efeitos se separam, e é por isso que esta ferramenta pede várias.

A PRÉVIA NUNCA MOSTRA ESSE ERRO: `previews/fp_mira_*.png` desenha com a mesma câmera que posiciona a
arma, então câmera errada dá prévia certa e jogo errado. Só print ou vídeo do jogo serve.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar as G
import modelos
from bt import rot_bb
from geometria import cube_face_quads


def pose_de_mira(arma):
    """A pose que o jogo está usando hoje na mira completa (agachado), e o info do modelo."""
    corpo, maos, info, _ = modelos.build(arma)
    cfg = G.PLACE[arma]
    cm = G.pose_mira(cfg, info)
    c = dict(cm)
    c["grip"] = np.array(cm["grip"], float) + G.AGACHADO
    return G.first_person(c), info, corpo, maos


def para_camera(fp, pontos_bb, calib):
    """Pontos do modelo (bb) -> espaço de câmera, usando uma câmera candidata."""
    cam = G.CAM_BB + np.array(calib[:3])
    bc = rot_bb(calib[3:6]) @ G.BC_BB
    A = G.PIV + fp["T_bb"] + (fp["R_g"] @ (G.ESCALA * (np.atleast_2d(pontos_bb) - G.PIV).T)).T
    return ((G.TB + (G.R_BASE @ A.T).T - cam) @ bc) - G.AGACHADO


def desvio_previsto(arma, calib):
    """Onde o ponto de mira cairia na tela, em graus, se a câmera do jogo fosse `calib`."""
    fp, info, _, _ = pose_de_mira(arma)
    q = G.vec_bb(np.array(info["visada_rel"][0], float) + G.PIV)
    t = para_camera(fp, q, calib)[0]
    return np.degrees(np.arctan2(t[0], t[2])), np.degrees(np.arctan2(t[1], t[2]))


# ---------------- leitura dos prints

def centro_da_tela(a):
    """Centro da projeção: o meio exato da imagem. É de lá que o tiro sai e é onde o jogo põe o retículo.

    Não vale medir o retículo e usar isso como centro: ele é um sprite que inverte as cores do fundo, e
    achar o meio dele erra uns 3 px conforme o cenário — 0,2°, que é mais do que a precisão que a luneta
    dá. O retículo entra só como conferência, para pegar print cortado ou redimensionado.
    """
    h, w = a.shape[:2]
    return w / 2, h / 2


def conferir_reticulo(a):
    """Caixa do retículo do jogo, só para avisar se o print não estiver inteiro."""
    h, w = a.shape[:2]
    r = 40
    jan = a[h // 2 - r:h // 2 + r, w // 2 - r:w // 2 + r]
    dif = np.abs(jan - np.median(jan.reshape(-1, 3), 0)).sum(2)
    ys, xs = np.nonzero(dif > 90)
    if len(xs) < 10:
        return None
    return (xs.min() + xs.max()) / 2 + w // 2 - r, (ys.min() + ys.max()) / 2 + h // 2 - r


def medir_luneta(a, cx, cy):
    """Cruzamento e giro do retículo da luneta (linhas pretas de 1 px sobre o mundo)."""
    g = a.mean(2)
    h, w = g.shape

    def faixa(fixos, lo, hi, vertical):
        pts = []
        for v in fixos:
            seg = g[v, lo:hi] if vertical else g[lo:hi, v]
            esc = np.nonzero(seg < 15)[0]
            if 2 <= len(esc) <= 14 and esc.max() - esc.min() <= 13:
                pts.append((v, (esc.min() + esc.max()) / 2 + lo))
        return np.array(pts)

    V = faixa(range(int(h * 0.13), int(h * 0.74)), int(cx - 40), int(cx + 40), True)
    Hz = faixa(range(int(w * 0.33), int(w * 0.67)), int(cy - 40), int(cy + 40), False)
    if len(V) < 60 or len(Hz) < 60:
        raise SystemExit("não achei o retículo da luneta: o print é de alguém agachado mirando?")
    m, b = np.polyfit(V[:, 0], V[:, 1], 1)        # x = m*y + b
    m2, b2 = np.polyfit(Hz[:, 0], Hz[:, 1], 1)    # y = m2*x + b2
    yc = (m2 * b + b2) / (1 - m2 * m)
    return m * yc + b, yc, np.degrees(np.arctan(m)), np.degrees(np.arctan(m2))


def medir_silhueta(a, arma, cx, cy):
    """Encaixa a silhueta escura do print na que o modelo prevê. Devolve (dx, dy) em px."""
    h, w = a.shape[:2]
    sc = 3
    pq = np.asarray(Image.fromarray(a.astype(np.uint8)).resize((w // sc, h // sc), Image.BOX)).astype(int)
    hh, ww = pq.shape[:2]
    alvo = (pq.max(2) < 95) & (np.ptp(pq, 2) < 26)
    yy, xx = np.mgrid[0:hh, 0:ww]
    alvo &= (xx > 0.30 * ww) & (xx < 0.72 * ww) & (yy > 0.42 * hh) & (yy < 0.88 * hh)

    fp, info, corpo, maos = pose_de_mira(arma)
    sem_alca = bool(info.get("alca_pivo"))        # na mira a alça da M4 se recolhe
    cubos = [c for c in G.offset(corpo, G.PIV) if not (sem_alca and c.get("bone") == "alca")]
    cubos += [c for c in G.offset(maos, G.PIV) if c["m"] == "luva"]
    fy = (hh / 2) / np.tan(np.radians(G.VFOV / 2))

    def mascara(dx, dy):
        im = Image.new("L", (ww, hh), 0)
        d = ImageDraw.Draw(im)
        for cb in cubos:
            for q in cube_face_quads(cb).values():
                p = para_camera(fp, np.asarray(q, float), G.CALIB)
                if np.any(p[:, 2] < 0.5):
                    continue
                d.polygon([(cx / sc + v[0] / v[2] * fy + dx, cy / sc - v[1] / v[2] * fy + dy) for v in p],
                          fill=255)
        return np.asarray(im) > 127

    def iou(dx, dy):
        m = mascara(dx, dy)
        return (m & alvo).sum() / max((m | alvo).sum(), 1)

    melhor = max(((iou(dx, dy), dx, dy) for dx in range(-24, 25, 2) for dy in range(-24, 25, 2)))
    v, dx, dy = melhor
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            s = iou(dx + ddx, dy + ddy)
            if s > v:
                v, dx, dy = s, dx + ddx, dy + ddy
    return dx * sc, dy * sc, v


# ---------------- programa

def main(args):
    fy_ref = None
    medidas = []                                   # (arma, desvio_x°, desvio_y° ou None, peso)
    for arg in args:
        arma, _, caminho = arg.partition("=")
        if arma not in G.PLACE:
            raise SystemExit(f"arma desconhecida: {arma} (use {', '.join(G.PLACE)})")
        a = np.asarray(Image.open(caminho).convert("RGB")).astype(float)
        h, w = a.shape[:2]
        fy = (h / 2) / np.tan(np.radians(G.VFOV / 2))
        fy_ref = fy
        cx, cy = centro_da_tela(a)
        _, _, info, _ = modelos.build(arma)
        print(f"\n{arma} — {Path(caminho).name} ({w}x{h}); centro da tela em ({cx:.0f},{cy:.0f})")
        conf = conferir_reticulo(a)
        if conf and max(abs(conf[0] - cx), abs(conf[1] - cy)) > 12:
            print(f"   AVISO: o retículo do jogo aparece em ({conf[0]:.0f},{conf[1]:.0f}), longe do centro."
                  " O print foi cortado ou redimensionado?")
        if info.get("luneta"):
            xc, yc, giro_v, giro_h = medir_luneta(a, cx, cy)
            dx, dy = xc - cx, yc - cy
            print(f"   retículo da luneta em ({xc:.1f},{yc:.1f}) -> ({dx:+.1f},{dy:+.1f}) px")
            print(f"   giro: {giro_v:+.2f}° na linha vertical, {giro_h:+.2f}° na horizontal "
                  f"(se não for ~0, o roll do CALIB está errado)")
            peso = 8.0
        else:
            dx, dy, iou = medir_silhueta(a, arma, cx, cy)
            print(f"   silhueta encaixa deslocando ({dx:+d},{dy:+d}) px (IoU {iou:.2f})")
            print("   só o eixo horizontal entra na conta (a silhueta não fixa bem o vertical)")
            dy, peso = None, 1.0
        gx = np.degrees(np.arctan(dx / fy))
        gy = None if dy is None else np.degrees(np.arctan(-dy / fy))
        print(f"   => {gx:+.2f}° à direita" + ("" if gy is None else f", {gy:+.2f}° acima"))
        medidas.append((arma, gx, gy, peso))

    def custo(p):
        cal = [*G.CALIB[:3], p[0], p[1], G.CALIB[5], G.CALIB[6]]
        s = 0.0
        for arma, mx, my, peso in medidas:
            px, py = desvio_previsto(arma, cal)
            s += peso * (px - mx) ** 2
            if my is not None:
                s += peso * (py - my) ** 2
        return s

    r = minimize(custo, [G.CALIB[3], G.CALIB[4]], method="Nelder-Mead",
                 options=dict(xatol=1e-5, fatol=1e-9, maxiter=4000))
    rx, ry = r.x
    novo = [*G.CALIB[:3], round(float(rx), 3), round(float(ry), 3), G.CALIB[5], G.CALIB[6]]
    print("\n" + "-" * 70)
    print(f"ângulos de hoje:    rx={G.CALIB[3]:+.3f}  ry={G.CALIB[4]:+.3f}")
    print(f"ângulos que batem:  rx={rx:+.3f}  ry={ry:+.3f}")
    print("\nresíduo (o que sobraria de desvio no jogo depois de regerar):")
    for arma, mx, my, _ in medidas:
        px, py = desvio_previsto(arma, novo)
        linha = f"   {arma:6s} {px - mx:+.2f}° na horizontal"
        if my is not None:
            linha += f", {py - my:+.2f}° na vertical"
        print(linha)
    if len(medidas) < 2:
        print("\nATENÇÃO: com uma arma só não dá para separar ângulo de posição da câmera (AGACHADO).")
    print(f"\nCole em tools/gerar.py:\nCALIB = {novo}")
    if fy_ref:
        print(f"(1° ≈ {np.tan(np.radians(1)) * fy_ref:.0f} px nesta tela)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
