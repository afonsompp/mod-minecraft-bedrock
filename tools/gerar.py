"""Gera modelos, texturas, attachables e animações das armas + renders de conferência.

Uso: python3 tools/gerar.py <pasta_RP> <pasta_previews>
Também pode ser importado (ajuste.py usa first_person/PLACE).
"""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from bt import rot_bb, vec_bb, euler_from_bb, Ry
import modelos
from geometria import build_geometry, render

AQUI = Path(__file__).resolve().parent

ESCALA = 0.25
PIV = np.array([0, 24, 0], float)          # pivô do osso raiz (bedrock == bb pois x=0)

# ---------------- referência de primeira pessoa (Blockbench, attachable_first com binding)
TB = np.array([-20.0, 21.0, 0.0])
R_BASE = rot_bb([95, -45, 115])
CAM_BB = np.array([0.0, 19.0, -40.0])
_f = np.array([0.0, 16.0, 0.0]) - CAM_BB
_f /= np.linalg.norm(_f)
_r = np.cross(_f, [0, 1, 0]); _r /= np.linalg.norm(_r)
_u = np.cross(_r, _f)
BC_BB = np.stack([_r, _u, _f], axis=1)      # colunas: direita, cima, frente (em bb)

# Câmera REAL do jogo: a do Blockbench não bate com o Bedrock (no celular a arma aparecia ~2x maior
# e mais para baixo/direita, e a Glock saía da tela). Calibrada ajustando a silhueta da M4A4 renderizada
# a um print do jogo (celular, 1600x738): [desloc. x, y, z da câmera, rotação bb rx, ry, rz, FOV vertical].
# O 6º número (roll da câmera) é ZERO de propósito: o ajuste por silhueta da v1.1.1 tinha achado 1,963°,
# mas a silhueta de um fuzil quase não restringe o roll, e era ruído do otimizador. Com ele, a arma saía
# girada ~2° na tela do jogo — invisível nas miras de ferro, mas o retículo da luneta, que atravessa a
# tela, ficava visivelmente torto (vídeo da v1.6.2). A prévia nunca mostrava, porque usa a mesma câmera.
CALIB = [1.686, -0.153, 5.428, -1.187, 1.132, 0.0, 67.5]
CAM = CAM_BB + np.array(CALIB[:3])
BC = rot_bb(CALIB[3:6]) @ BC_BB
VFOV = CALIB[6]
# Agachado, a câmera do jogo se desloca em relação ao braço (espaço da câmera: direita, cima, frente).
# Medido na v1.6.2 com o painel da luneta da AWP (`tools/calibrar_mira.py`), que fica a ~1,7 un do olho e
# amplia o erro umas 4x em relação à AK: 6 quadros do vídeo com o jogador parado deram o mesmo valor.
# Antes era (1,346, -1,009, 1,757), ajustado por silhueta na v1.2.1; o resíduo era pequeno demais para
# aparecer nas outras armas, mas na luneta tirava o retículo 8° do centro — e o tiro sai do centro da tela.
AGACHADO = np.array([1.187, -1.283, 1.521])

# ---------------- terceira pessoa
ARM_PIV = np.array([5.0, 22.0, 0.0])
ITEM_REL = np.array([1.0, -7.0, 1.0])

# posição desejada na tela (direita, cima, profundidade) do punho e "toe-in" (graus).
# olho = distância (unidades de câmera, 1/16 de bloco) do olho ao ponto de trás da linha de visada na pose
# de mira. Fuzil com luneta: o ponto de trás é a ocular e "olho" é o alívio de olho.
PLACE = {
    "ak47": dict(grip=(8.19, -6.12, 7.30), yaw=5.7, pitch=1.0, roll=-4, intervalo=3, olho=7.5, atirando=0.45),
    "m4a4": dict(grip=(7.77, -6.09, 6.82), yaw=5.7, pitch=1.0, roll=-4, intervalo=3, olho=3.5, atirando=0.45),
    "glock": dict(grip=(4.70, -3.93, 5.42), yaw=5.8, pitch=1.0, roll=-3, intervalo=5, olho=2.5, atirando=0.3),
    "awp": dict(grip=(8.19, -6.12, 7.30), yaw=5.7, pitch=1.0, roll=-4, intervalo=25, olho=2.0, atirando=0.3),
}
# Mira (ADS): agachado = mira completa. Atirando em pé, a arma é puxada parte do caminho para o centro
# (PLACE[...]["atirando"]: fração do caminho quadril -> mira; menor na Glock, que perto do olho ocupa a tela).
# Ela continua puxada por SOLTA_COMBATE segundos depois de soltar, para não ir e voltar a cada toque.
# (Na v1.2.2 isso saiu porque a arma "subia" ao atirar; a causa era a respiração vanilla, hoje compensada.)
SOLTA_COMBATE = 0.5
# Osso "alca" (alça com orifício, ex.: M4): encolhe para dentro da base entre v.ads 0,55 e 0,75. Atirando em pé
# (v.ads 0,45) ela continua visível; na mira completa some e mira-se pela massa.
ALCA_NA_MIRA = "math.clamp(1.0 - (v.ads - 0.55) * 5.0, 0.0, 1.0)"
# Luneta (estilo CS): na mira completa a ARMA SOME e um painel preto com furo circular toma a tela.
# É assim que os FPS fazem a mira de sniper; e resolve o tubo da luneta tapar a visão.
# O painel é dimensionado pelo FOV NORMAL (o da arma em 1ª pessoa, VFOV), não pelo FOV do zoom:
# - o /camera fov_set precisa de cheats e só aceita de 30 a 110 (a v1.6.0 pedia 18 e era recusada);
# - a arma em 1ª pessoa parece ter FOV próprio (a calibração deu 67,5, diferente do FOV do mundo),
#   então o zoom amplia o mundo e não deve mexer no tamanho do painel.
# Assim o painel cobre a tela com ou sem zoom. Se um print mostrar a vinheta sumindo quando agacha,
# é porque o zoom TAMBÉM amplia a arma: aí é só dimensionar por FOV_ZOOM.
FOV_ZOOM = 30.0             # igual ao ARMAS[...].mira.fov do main.js (mínimo que o jogo aceita)
# só na mira completa: durante a aproximação a arma ainda está a caminho e o painel sairia torto
NA_LUNETA = "(v.ads > 0.995 ? 1.0 : 0.0)"
MIRA_CIRCULO = 0.86         # diâmetro do furo em fração da altura da tela


def painel_luneta(cfg, info):
    """Tamanho e posição do painel da luneta, no espaço do modelo. Ele fica logo atrás da ocular e é
    dimensionado para cobrir a tela COM O FOV DA MIRA (se o zoom não funcionar no aparelho, aparece
    pequeno no centro: é o sinal de que o /camera fov_set falhou)."""
    y = info["visada"][0][1] - info["grip"][1]
    z = info["visada_rel"][0][2] - 1.25                  # 1,25 un atrás da ocular
    d = cfg["olho"] - 1.25 * ESCALA                      # distância do olho, em unidades de câmera
    meia = d * np.tan(np.radians(VFOV / 2)) / ESCALA      # meia-altura da tela, em unidades de modelo
    # o painel tem 1,5x a meia-altura da tela (folga para telas largas e FOV maior)
    return dict(y=y, z=z, hw=round(meia * 2.4 * 1.5, 3), hh=round(meia * 1.5, 3),
                raio=round(meia * MIRA_CIRCULO, 3))
MIRA_VELOCIDADE = 12.0      # 1/s: ~0,25 s para chegar à mira
# Balanços que o jogo aplica no braço/item em 1ª pessoa (player_firstperson.animation.json vanilla):
#  - respiração (osso rightitem): y = v.bob_animation * sin(q.life_time * 45) * 0.5  -> ciclo de 8 s;
#  - caminhada (osso rightarm, no espaço do corpo): x = sin(-dist*180)*hand_bob*9.75, y = -|cos(-dist*180)|*hand_bob*15.
# Na mira, 0,5 un. a ~4 un. do olho = vários graus: a arma "subia" sozinha por ~2 s. A animação desconta a
# respiração sempre e a caminhada proporcionalmente a v.ads (no quadril o balanço de andar é bem-vindo).
# Supõe "balanço da visão" ligado (padrão do jogo): v.bob_animation não é legível pelo attachable.
COMPENSA_RESPIRACAO = True
COMPENSA_CAMINHADA = True
RECUO_MIRA = 0.4            # recuo na mira, relativo ao recuo do quadril
QUADROS_MIRA = 8            # segmentos do caminho quadril -> mira (quadros-chave dirigidos por v.ads)
NOMES = {"ak47": "AK-47", "m4a4": "M4A4", "glock": "Glock", "awp": "AWP"}


def rot_axis(axis, ang):
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    a = np.radians(ang)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K


def r3(v):
    return [round(float(x), 3) for x in v]


def first_person(cfg):
    yaw, pitch, roll = cfg["yaw"], cfg["pitch"], cfg["roll"]
    d_cam = np.array([-np.tan(np.radians(yaw)), np.tan(np.radians(pitch)), 1.0])
    d_cam /= np.linalg.norm(d_cam)
    fg = BC @ d_cam
    ug = BC @ np.array([0, 1, 0.0])
    ug = ug - fg * (ug @ fg); ug /= np.linalg.norm(ug)
    ug = rot_axis(fg, roll) @ ug
    xg = np.cross(ug, fg)
    R_des = np.stack([xg, ug, fg], axis=1)
    R_g = R_BASE.T @ R_des
    rot = euler_from_bb(R_g)
    assert np.allclose(rot_bb(rot), R_g, atol=1e-6)
    WG = CAM + BC @ np.array(cfg["grip"], float)
    T_bb = R_BASE.T @ (WG - TB) - PIV
    kick_bb = R_BASE.T @ (BC @ np.array([0, 0, -1.0]))   # recuo: só para trás, no eixo da câmera (não tira a mira)
    to_bed = lambda v: np.array([-v[0], v[1], v[2]])
    return dict(rot=rot, pos=to_bed(T_bb), kick=to_bed(kick_bb), R_g=R_g, T_bb=T_bb)


def cam_de(fp, p_rel):
    """Ponto do modelo (bedrock, relativo ao punho) -> espaço de câmera (direita, cima, frente)."""
    q = vec_bb(np.array(p_rel, float) + PIV)
    A = PIV + fp["T_bb"] + fp["R_g"] @ (ESCALA * (q - PIV))
    return (TB + R_BASE @ A - CAM) @ BC


def pose_mira(cfg, info):
    """Pose de mira: linha de visada sobre o eixo da câmera (centro da tela), arma sem inclinação,
    ponto de trás da visada a cfg["olho"] do olho."""
    tras, frente = (np.array(v, float) for v in info["visada_rel"])
    d = frente - tras
    pitch = -np.degrees(np.arctan2(d[1], d[2]))       # visada inclinada em relação ao cano
    base = first_person(dict(grip=(0, 0, 0), yaw=0, pitch=pitch, roll=0))
    grip = np.array([0, 0, cfg["olho"]]) - cam_de(base, tras)   # translação do punho é 1:1 na câmera
    cfg_mira = dict(grip=tuple(grip), yaw=0, pitch=pitch, roll=0)
    fp = first_person(cfg_mira)
    t, f = cam_de(fp, tras), cam_de(fp, frente)
    assert np.allclose(t, [0, 0, cfg["olho"]], atol=1e-6) and np.allclose(f[:2], 0, atol=1e-6), (t, f)
    return cfg_mira


def caminho_mira(cfg, cfg_mira, n=QUADROS_MIRA):
    """Quadros-chave quadril -> mira. O caminho é interpolado no espaço da CÂMERA (punho, yaw, pitch, roll)
    e cada quadro é resolvido exatamente; interpolar direto os ângulos de Euler do osso não anda reto na tela."""
    out = []
    for i in range(n + 1):
        a = i / n
        s = suave(a)
        c = {k: (1 - s) * np.array(cfg[k], float) + s * np.array(cfg_mira[k], float)
             for k in ("grip", "yaw", "pitch", "roll")}
        # o "grip" é relativo à câmera de cada estado: agachado ela se desloca (AGACHADO)
        c["grip"] = c["grip"] + peso_agachado(a, cfg["atirando"]) * AGACHADO
        out.append((a, first_person(c)))
    # Euler contínuo entre quadros (evita salto de 360° na interpolação do jogo)
    for i in range(1, len(out)):
        prev = np.array(out[i - 1][1]["rot"])
        out[i][1]["rot"] = prev + delta_rot(prev, out[i][1]["rot"])
    return out


def suave(a):
    a = min(max(a, 0.0), 1.0)
    return a * a * (3 - 2 * a)


def peso_agachado(a, atirando):
    """Quanto da câmera agachada vale no tempo a da mira. Até a fração 'atirando' o jogador está em pé
    (câmera normal); dali até 1 está agachando (câmera desloca para AGACHADO)."""
    return suave((a - atirando) / (1 - atirando))


def disparo_molang(tipo, intervalo):
    """Molang do recuo/clarão. Automática: cicla enquanto o gatilho está apertado (como a rajada do script).
    Semiautomática (pistola) e ferrolho (sniper): UM ciclo por aperto, mesmo segurando, igual ao script
    (itemUse = 1 tiro). Antes a Glock ciclava enquanto o dedo ficava na tela, sem som nem tiro."""
    I = f"{intervalo}.0"
    if tipo not in ("pistola", "sniper"):
        return [
            "v.atirando = q.main_hand_item_use_duration > 0.0;",
            f"v.ciclo = math.mod(q.life_time * 20.0, {I}) / {I};",
            "v.kick = v.atirando ? (1.0 - v.ciclo) : 0.0;",
            "v.mostra_clarao = v.atirando && v.ciclo < 0.34;",
        ]
    return [
        "v.usando = q.main_hand_item_use_duration > 0.0;",
        # tempo desde o último aperto (borda de subida do "usando"); começa "longe" para não disparar ao equipar
        "v.t_tiro = (v.usando && !(v.usou ?? 0.0)) ? 0.0 : (v.t_tiro ?? 99.0) + q.delta_time;",
        "v.usou = v.usando;",
        f"v.ciclo = math.min(v.t_tiro * 20.0 / {I}, 1.0);",
        "v.atirando = v.ciclo < 1.0;",
        "v.kick = v.atirando ? (1.0 - v.ciclo) : 0.0;",
        "v.mostra_clarao = v.atirando && v.ciclo < 0.34;",
    ]


def compensacao_bob():
    """Expressões Molang (x, y, z do osso, Bedrock) que descontam os balanços vanilla de 1ª pessoa.
    O osso da arma está preso ao rightitem, cujo referencial tem a orientação do rightarm (R_BASE):
    - respiração: é posição do próprio rightitem -> desconto direto em y;
    - caminhada: é posição do rightarm no espaço do corpo -> levar para o referencial do braço (R_BASE^T)."""
    termos = [[], [], []]
    if COMPENSA_RESPIRACAO:
        termos[1].append("- v.respira")
    if COMPENSA_CAMINHADA:
        F = np.diag([-1.0, 1.0, 1.0])               # Bedrock <-> bb
        M = F @ R_BASE.T @ F                        # deslocamento no corpo (Bedrock) -> no braço (Bedrock)
        for i in range(3):
            cx, cy = M[i, 0], M[i, 1]
            if abs(cx) > 1e-4 or abs(cy) > 1e-4:
                termos[i].append(f"- v.ads * ({cx:.4f} * v.passo_x {'-' if cy < 0 else '+'} {abs(cy):.4f} * v.passo_y)")
    return ["".join(f" {t}" for t in ts) for ts in termos]


def mistura(caminho, a):
    """Simula o jogo: interpolação linear entre os quadros-chave vizinhos (rotação Euler e posição)."""
    ts = [t for t, _ in caminho]
    j = min(int(np.searchsorted(ts, a, side="right")) - 1, len(ts) - 2)
    (t0, p0), (t1, p1) = caminho[j], caminho[j + 1]
    u = (a - t0) / (t1 - t0)
    rot = np.array(p0["rot"]) + u * (np.array(p1["rot"]) - np.array(p0["rot"]))
    pos = p0["pos"] + u * (p1["pos"] - p0["pos"])
    return dict(R_g=rot_bb(rot), T_bb=np.array([-pos[0], pos[1], pos[2]]))


def delta_rot(a, b):
    return (np.array(b) - np.array(a) + 180.0) % 360.0 - 180.0


def third_person(arm_rot, grip_off=(0, -1.0, 0)):
    R_arm = rot_bb(arm_rot)
    R_des = Ry(180)
    R_g = R_arm.T @ R_des
    rot = euler_from_bb(R_g)
    T_bb = np.array(grip_off, float)        # punho um pouco na direção dos dedos
    return dict(rot=rot, pos=np.array([-T_bb[0], T_bb[1], T_bb[2]]), R_g=R_g, T_bb=T_bb, R_arm=R_arm)


def offset(cubes, d):
    out = []
    for c in cubes:
        c = dict(c)
        c["o"] = tuple(np.array(c["o"]) + d)
        if "p" in c:
            c["p"] = tuple(np.array(c["p"]) + d)
        out.append(c)
    return out



def main(RP, PREV):
    RP = Path(RP)
    PREV = Path(PREV)
    PREV.mkdir(parents=True, exist_ok=True)
    animations = {}
    anim_json_path = RP / "animations" / "joao_armas.animation.json"
    for d in ("models/entity/joao", "textures/entity/joao", "attachables", "animations", "render_controllers"):
        (RP / d).mkdir(parents=True, exist_ok=True)

    TP_MIRA = third_person([-90, -5.73, 0])
    TP_BAIXO = third_person([-18, 0, 0])

    bg = None
    try:
        bg = Image.open(AQUI / "assets" / "fundo_previa.jpg").convert("RGBA")
    except FileNotFoundError:
        pass

    previews = []
    for nome in ("glock", "ak47", "m4a4", "awp"):
        corpo, maos, info, tipo = modelos.build(nome)
        cfg = cfg0 = PLACE[nome]
        corpo = offset(corpo, PIV)
        maos = offset(maos, PIV)
        muzzle = np.array(info["muzzle_rel"]) + PIV
        geo_id = f"geometry.joao.{nome}"
        alca = [c for c in corpo if c.get("osso") == "alca"]
        corpo = [c for c in corpo if c.get("osso") != "alca"]
        ossos = [("arma", None, PIV, []), ("corpo", "arma", PIV, corpo)]
        if alca:
            ossos.append(("alca", "arma", PIV + np.array(info["alca_pivo_rel"]), alca))
        ossos.append(("maos", "arma", PIV, maos))
        luneta = painel_luneta(cfg0, info) if info.get("luneta") else None
        if luneta:
            luneta = dict(luneta, y=luneta["y"] + PIV[1], z=luneta["z"] + PIV[2])
        geo, atlas, faces = build_geometry(geo_id, ossos, flash_at=(muzzle[0], muzzle[1], muzzle[2] + 0.5),
                                           scope=luneta)
        (RP / f"models/entity/joao/{nome}.geo.json").write_text(json.dumps(geo, indent=1))
        atlas.save(RP / f"textures/entity/joao/{nome}.png")

        fp = first_person(cfg)
        caminho = caminho_mira(cfg, pose_mira(cfg, info))
        ads = caminho[-1][1]
        k = fp["kick"] * {"pistola": 0.5, "sniper": 0.9}.get(tipo, 0.35)   # sniper: coice bem maior
        dk = k * (RECUO_MIRA - 1.0)
        # recuo (aditivo) menor na mira
        recuo = [f" + v.kick * ({k[i]:.3f} + v.ads * {dk[i]:.3f})" for i in range(3)]
        bob = compensacao_bob()
        rot_kf, pos_kf = {}, {}
        for t, q in caminho:
            rot_kf[f"{t:.4f}"] = r3(q["rot"])
            pos_kf[f"{t:.4f}"] = [f"{q['pos'][i]:.3f}{recuo[i]}{bob[i]}" for i in range(3)]
        # o tempo da animação É o v.ads (0 = quadril, 1 = mira); comprimento > 1 para nunca "terminar"
        animations[f"animation.joao.{nome}.primeira_pessoa"] = {
            "loop": True,
            "animation_length": 1.05,
            "anim_time_update": "v.ads",
            "bones": {"arma": {"rotation": rot_kf, "position": pos_kf, "scale": ESCALA},
                      **({"alca": {"scale": ALCA_NA_MIRA}} if alca else {}),
                      # na luneta a arma some e só fica o painel (como no CS)
                      **({"corpo": {"scale": f"1.0 - {NA_LUNETA}"},
                          "maos": {"scale": f"1.0 - {NA_LUNETA}"},
                          "luneta": {"scale": NA_LUNETA}} if luneta else {})},
        }
        for tag, tp in (("mira", TP_MIRA), ("baixo", TP_BAIXO)):
            animations[f"animation.joao.{nome}.terceira_{tag}"] = {
                "loop": True,
                "bones": {"arma": {"rotation": r3(tp["rot"]), "position": r3(tp["pos"]), "scale": ESCALA}},
            }

        I = cfg["intervalo"]
        att = {
            "format_version": "1.10.0",
            "minecraft:attachable": {
                "description": {
                    "identifier": f"joao:{nome}",
                    "materials": {"default": "entity_alphatest", "enchanted": "entity_alphatest_glint",
                                  "flash": "entity_beam_additive"},
                    "textures": {"default": f"textures/entity/joao/{nome}",
                                 "enchanted": "textures/misc/enchanted_item_glint"},
                    "geometry": {"default": geo_id},
                    "animations": {
                        "primeira": f"animation.joao.{nome}.primeira_pessoa",
                        "terceira_mira": f"animation.joao.{nome}.terceira_mira",
                        "terceira_baixo": f"animation.joao.{nome}.terceira_baixo",
                        "sem_maos": "animation.joao.sem_maos",
                        "clarao": "animation.joao.clarao",
                    },
                    "scripts": {
                        "pre_animation": disparo_molang(tipo, I) + [
                            "v.mira = c.owning_entity->v.joao_mira > 0.0;",
                            f"v.tem_luneta = {1.0 if info.get('luneta') else 0.0};",
                            # mira (ADS): agachado = 1, em pé = 0; suavizado por tempo real
                            "v.ads = v.ads ?? 0.0;",
                            "v.uso = q.main_hand_item_use_duration > 0.0;",
                            "v.t_solto = v.uso ? 0.0 : (v.t_solto ?? 99.0) + q.delta_time;",
                            f"v.alvo_ads = q.is_sneaking ? 1.0 : (v.t_solto < {SOLTA_COMBATE} ? {cfg['atirando']} : 0.0);",
                            f"v.ads = v.ads + (v.alvo_ads - v.ads) * math.min(1.0, q.delta_time * {MIRA_VELOCIDADE});",
                            # balanços vanilla recalculados aqui (as queries do attachable são as do jogador)
                            "v.respira = math.sin(q.life_time * 45.0) * 0.5;",
                            "v.mao_bob = v.mao_bob ?? 0.0;",
                            "v.mao_bob = v.mao_bob + ((q.is_on_ground && q.is_alive ? math.clamp(math.sqrt(math.pow(q.position_delta(0), 2.0) + math.pow(q.position_delta(2), 2.0)), 0.0, 0.1) : 0.0) - v.mao_bob) * 0.02;",
                            "v.passo_x = math.sin(-q.walk_distance * 180.0) * v.mao_bob * 9.75;",
                            "v.passo_y = -math.abs(math.cos(-q.walk_distance * 180.0)) * v.mao_bob * 15.0;",
                        ],
                        "animate": [
                            {"primeira": "c.is_first_person"},
                            {"terceira_mira": "!c.is_first_person && v.mira"},
                            {"terceira_baixo": "!c.is_first_person && !v.mira"},
                            {"sem_maos": "!c.is_first_person"},
                            "clarao",
                        ],
                    },
                    "render_controllers": ["controller.render.joao_arma"],
                }
            },
        }
        (RP / f"attachables/{nome}.json").write_text(json.dumps(att, indent=1))

        # ---------------- render de conferência em primeira pessoa (quadril, mira e transição)
        W, H = 1300, 600
        if bg is not None:
            bgi = bg.resize((W, H))
        else:
            bgi = Image.new("RGBA", (W, H), (120, 160, 200, 255))
        fy = (H / 2) / np.tan(np.radians(VFOV / 2))

        def proj(p, fy=fy):
            return (W / 2 + p[0] / p[2] * fy, H / 2 - p[1] / p[2] * fy)



        def render_fp(pose, rotulo=None, agachado=0.0, com_alca=True, na_luneta=False, zoom=False):
            def fp_world(q_bb):
                # q_bb: pontos do modelo (bb). A(p) = P + T + R_g s (p - P); mundo = TB + R_BASE A
                A = PIV + pose["T_bb"] + (pose["R_g"] @ (ESCALA * (q_bb - PIV).T)).T
                Wd = TB + (R_BASE @ A.T).T
                return ((Wd - CAM) @ BC) - agachado * AGACHADO   # coords de câmera (direita, cima, frente)
            if na_luneta:                 # mira com luneta: a arma some, fica só o painel
                ossos_v = {"luneta": fp_world}
            else:
                ossos_v = {"corpo": fp_world, "maos": fp_world, **({"alca": fp_world} if com_alca else {})}
            im = render(faces, ossos_v, proj, (W, H), bg=zoom_bg if zoom else bgi)
            from PIL import ImageDraw
            dr = ImageDraw.Draw(im)
            dr.line([(W / 2 - 8, H / 2), (W / 2 + 8, H / 2)], fill=(255, 255, 255, 255), width=2)
            dr.line([(W / 2, H / 2 - 8), (W / 2, H / 2 + 8)], fill=(255, 255, 255, 255), width=2)
            if rotulo:
                dr.text((12, 10), rotulo, fill=(255, 255, 255, 255))
            return im

        im_quadril = render_fp(fp)
        im_quadril.save(PREV / f"fp_{nome}.png")
        # fundo "com zoom": o cenário da prévia ampliado, para simular o /camera fov_set
        zoom_bg = bgi.resize((int(W * VFOV / FOV_ZOOM), int(H * VFOV / FOV_ZOOM)), Image.LANCZOS)
        zx, zy = zoom_bg.width, zoom_bg.height
        zoom_bg = zoom_bg.crop(((zx - W) // 2, (zy - H) // 2, (zx - W) // 2 + W, (zy - H) // 2 + H))
        im_mira = render_fp(mistura(caminho, 1.0), agachado=1.0, com_alca=False,
                            na_luneta=bool(luneta), zoom=bool(luneta))      # pela mesma interpolação do jogo
        im_mira.save(PREV / f"fp_mira_{nome}.png")
        quadros = [im_quadril, render_fp(mistura(caminho, cfg["atirando"])), im_mira]
        tira = Image.new("RGBA", (W // 2 * 3, H // 2))
        for i, (q, rot_) in enumerate(zip(quadros, ("quadril (0)", f"atirando em pé ({cfg['atirando']})", "mira (1)"))):
            q = q.resize((W // 2, H // 2), Image.LANCZOS)
            from PIL import ImageDraw
            ImageDraw.Draw(q).text((8, 6), rot_, fill=(255, 255, 0, 255))
            tira.paste(q, (i * W // 2, 0))
        tira.save(PREV / f"fp_transicao_{nome}.png")

        # ---------------- vista lateral (também vira o ícone)
        def side(q_bb):
            # olhando o lado direito da arma (+X bedrock = -X bb): câmera em x_bb muito negativo
            q = q_bb - PIV
            return np.stack([q[:, 2], q[:, 1], q[:, 0] + 1000], axis=1)   # direita=z(frente), cima=y, prof

        pts = np.array([np.array(c["o"]) for c in corpo] + [np.array(c["o"]) + np.array(c["s"]) for c in corpo]) - PIV
        zmin, zmax = pts[:, 2].min(), pts[:, 2].max()
        ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
        S = 512
        span = max(zmax - zmin, ymax - ymin) * 1.6
        cz, cy = (zmin + zmax) / 2, (ymin + ymax) / 2
        sc = S / span

        def oproj(p):
            return ((p[0] - cz) * sc + S / 2, S / 2 - (p[1] - cy) * sc)

        side_img = render(faces, {"corpo": side, "alca": side}, oproj, (S, S))
        bb = side_img.getbbox()
        crop = side_img.crop(bb)
        side_n = max(crop.width, crop.height) + 12
        sq = Image.new("RGBA", (side_n, side_n), (0, 0, 0, 0))
        sq.alpha_composite(crop, ((side_n - crop.width) // 2, (side_n - crop.height) // 2))
        side_img = sq.resize((S, S), Image.LANCZOS)
        side_img.save(PREV / f"lado_t_{nome}.png")
        icon = side_img.resize((64, 64), Image.LANCZOS)
        (RP / "textures/items").mkdir(parents=True, exist_ok=True)
        icon.save(RP / f"textures/items/{nome}.png")
        big = Image.new("RGBA", (S, S), (190, 190, 190, 255)); big.alpha_composite(side_img)
        big.save(PREV / f"lado_{nome}.png")

        # ---------------- detalhe em 3/4 (perspectiva, grande): para julgar peças pequenas e a paleta
        dist_det = 2.6 * max(zmax - zmin, 2.0 * (ymax - ymin))   # enquadra armas compridas e altas

        def tres_quartos(q_bb, giro=np.radians(28.0), incl=np.radians(16.0), dist=dist_det):
            q = q_bb - PIV - np.array([0.0, cy, cz])
            cg, sg, ci, si = np.cos(giro), np.sin(giro), np.cos(incl), np.sin(incl)
            Ryy = np.array([[cg, 0, sg], [0, 1, 0], [-sg, 0, cg]])
            # câmera elevada: gira em torno do eixo "direita" da câmera (que é z no referencial da vista lateral)
            Rel = np.array([[ci, -si, 0], [si, ci, 0], [0, 0, 1]])
            q = q @ Ryy.T @ Rel.T
            return np.stack([q[:, 2], q[:, 1], q[:, 0] + dist], axis=1)   # mesmo referencial da vista lateral

        DW, DH = 1600, 800
        fd = DW / 2 / np.tan(np.radians(13))

        def pproj(p):
            return (DW / 2 + p[0] / p[2] * fd, DH / 2 - p[1] / p[2] * fd)

        det = render(faces, {"corpo": tres_quartos, "alca": tres_quartos}, pproj, (DW, DH),
                     bg=Image.new("RGBA", (DW, DH), (200, 203, 207, 255)))
        det.save(PREV / f"detalhe_{nome}.png")

        # ---------------- terceira pessoa (de lado, com braço) para conferir orientação
        def tp_world(q_bb, tp=TP_MIRA):
            A = PIV + tp["T_bb"] + (tp["R_g"] @ (ESCALA * (q_bb - PIV).T)).T
            Wd = ARM_PIV + (tp["R_arm"] @ (ITEM_REL + A - PIV).T).T
            return Wd

        print(nome, "FP rot", r3(fp["rot"]), "pos", r3(fp["pos"]), "| mira rot", r3(ads["rot"]), "pos", r3(ads["pos"]), "| TP mira", r3(TP_MIRA["rot"]), "| TP baixo", r3(TP_BAIXO["rot"]))
        previews.append((nome, tp_world, faces))

    anim = {"format_version": "1.10.0", "animations": animations}
    anim["animations"]["animation.joao.sem_maos"] = {"loop": True,
        "bones": {"maos": {"scale": 0}, "luneta": {"scale": 0}}}
    # o clarão some junto com a arma quando a luneta cobre a tela (senão aparece solto embaixo)
    anim["animations"]["animation.joao.clarao"] = {"loop": True, "bones": {"flash": {
        "scale": f"(v.mostra_clarao && !(v.tem_luneta > 0.5 && {NA_LUNETA} > 0.5)) ? 1.0 : 0.0"}}}
    anim_json_path.write_text(json.dumps(anim, indent=1))

    rc = {"format_version": "1.10.0", "render_controllers": {"controller.render.joao_arma": {
        "geometry": "Geometry.default",
        "materials": [{"*": "Material.default"}, {"flash": "Material.flash"}],
        "textures": ["Texture.default"]}}}
    (RP / "render_controllers/joao_armas.render_controllers.json").write_text(json.dumps(rc, indent=1))

    # terceira pessoa: render simples de lado (jogador olhando para -Z, vemos pelo lado direito dele)
    for nome, tpw, faces in previews:
        def side_tp(q_bb, tpw=tpw):
            Wd = tpw(q_bb)
            # câmera à direita do jogador (x_bb grande), olhando para -X; direita da tela = -Z (frente do jogador)
            return np.stack([-Wd[:, 2], Wd[:, 1], 200 - Wd[:, 0]], axis=1)
        S = 400
        im = Image.new("RGBA", (S, S), (200, 220, 235, 255))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(im)
        sc = 8
        o = lambda p: (S / 2 + p[0] * sc, S - 20 - p[1] * sc + 0)
        # corpo do jogador (caixas simples, vista lateral)
        for (z0, z1, y0, y1) in [(-2, 2, 12, 24), (-4, 4, 24, 32), (-2, 2, 0, 12)]:
            dr.rectangle([o((-z1, y1)), o((-z0, y0))], fill=(80, 110, 160, 255))
        # braço direito estendido para frente (rot -90)
        dr.rectangle([o((0, 24)), o((12, 20))], fill=(200, 160, 120, 255))
        im2 = render(faces, {"corpo": side_tp, "alca": side_tp}, lambda p: o((p[0], p[1])), (S, S), bg=im)
        im2.save(PREV / f"tp_{nome}.png")
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
