"""Definição dos modelos 3D (cubos) das armas e das mãos.

Coordenadas em unidades de 1/64 de bloco (o osso usa escala 0.25).
Eixos (Bedrock): +Z = frente (cano), +Y = cima, +X = lado direito da arma.
Cada cubo: dict(o=(x0,y0,z0), s=(sx,sy,sz), m=material, r=(rx,ry,rz) opcional, p=pivô opcional)
"""
import numpy as np
from nucleo.bt import rot_bb, euler_from_bb


def box(x0, x1, y0, y1, z0, z1, m, r=None, p=None):
    c = dict(o=(x0, y0, z0), s=(x1 - x0, y1 - y0, z1 - z0), m=m)
    if r is not None:
        c["r"] = tuple(r)
        c["p"] = tuple(p)
    return c


def sym(hw, y0, y1, z0, z1, m, **kw):
    return box(-hw, hw, y0, y1, z0, z1, m, **kw)


def chain(top, length, width_x, depth_z, angles, m, seg_names=None):
    """Carregador curvo: segmentos que descem a partir de 'top' girando para a frente."""
    cubes = []
    p = np.array(top, float)
    for a in angles:
        # direção para baixo girada 'a' graus em direção a +Z
        d = np.array([0, -np.cos(np.radians(a)), np.sin(np.radians(a))])
        center = p + d * length / 2
        o = (center[0] - width_x / 2, center[1] - length / 2, center[2] - depth_z / 2)
        # no Bedrock, rx positivo leva a parte de baixo para +Z (ver bt.rot_bb)
        cubes.append(dict(o=o, s=(width_x, length, depth_z), m=m, r=(a, 0, 0), p=tuple(center)))
        p = p + d * length * 0.97
    return cubes


def braco(start, direction, length, t, m_glove, m_sleeve, glove_len):
    """Antebraço (manga) a partir do punho, com luva no começo."""
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    # rotação no espaço bb (x invertido) que leva +Z para d
    dbb = np.array([-d[0], d[1], d[2]])
    z = dbb
    up = np.array([0, 1, 0]) if abs(z[1]) < 0.9 else np.array([1, 0, 0])
    x = np.cross(up, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.stack([x, y, z], axis=1)
    rot = tuple(round(v, 3) for v in euler_from_bb(R))
    s = np.asarray(start, float)
    out = []
    for z0, z1, m in ((0, glove_len, m_glove), (glove_len, length, m_sleeve)):
        o = (s[0] - t / 2, s[1] - t / 2, s[2] + z0)
        out.append(dict(o=o, s=(t, t, z1 - z0), m=m, r=rot, p=tuple(s)))
    return out


# ---------------------------------------------------------------- AK-47
def nervuras_carregador(segs, m, folga=0.12, prof=1.2):
    """Nervura de reforço no meio de cada segmento de carregador curvo (mesma rotação do segmento)."""
    out = []
    for sg in segs:
        sx, sy, sz = sg["s"]
        pc = np.array(sg["p"], float)
        out.append(dict(o=(pc[0] - sx / 2 - folga, pc[1] - sy * 0.36, pc[2] - prof / 2),
                        s=(sx + 2 * folga, sy * 0.72, prof), m=m, r=sg["r"], p=sg["p"]))
    return out


def base_carregador(topo, comp, angulos, tam, m, recuo=0.97, folga=0.35):
    """Base (chapa) no fim de um carregador feito com chain()."""
    p = np.array(topo, float)
    for a in angulos:
        p = p + np.array([0, -np.cos(np.radians(a)), np.sin(np.radians(a))]) * comp * recuo
    a = angulos[-1] + 2
    d = np.array([0, -np.cos(np.radians(a)), np.sin(np.radians(a))])
    cb = p + d * folga
    sx, sy, sz = tam
    return dict(o=(cb[0] - sx / 2, cb[1] - sy / 2, cb[2] - sz / 2), s=tam, m=m, r=(a, 0, 0), p=tuple(cb))


def ak47():
    """AKM (caixa estampada, tampa nervurada, freio de boca inclinado). ~1,36 cm por unidade.
    Pontos calibrados (não mexer sem refazer a pose): punho, visada (alça/massa a y 10,25), boca e guarda-mão."""
    c = []
    S, W, D = "aco", "madeira", "aco_escuro"
    # ---------------- caixa da culatra e tampa
    c += [
        sym(2, 0, 6.5, -7, 13, S),                       # caixa (chapa estampada)
        sym(1.75, 6.5, 8, -6, 11, "aco_claro"),          # tampa
        sym(1.4, 8, 8.35, -5.5, 10.5, "aco_claro"),      # topo arredondado da tampa
        sym(0.5, 6.25, 7.25, -7.4, -6.6, "aco"),         # botão da trava da tampa (guia da mola)
        sym(1.5, 2, 6, -7.5, -7, S),                     # espiga traseira (encaixe da coronha)
    ]
    c += [sym(1.5, 8.35, 8.55, z, z + 0.4, "aco_claro") for z in np.arange(-4.5, 10, 2.0)]   # nervuras da tampa
    # alça tangente: bloco, folha com entalhe em U (topo a y 10,25), folha se estendendo para a frente e cursor
    c += [
        sym(1.5, 6.5, 9.25, 13, 16, S),                  # bloco da alça
        sym(1, 9.25, 9.5, 13.5, 16, D),                  # folha: base
        box(-1, -0.25, 9.5, 10.25, 13.5, 16, D),         # entalhe em U
        box(0.25, 1, 9.5, 10.25, 13.5, 16, D),
        sym(0.85, 9.25, 9.45, 16, 19.5, D),              # folha tangente (para a frente)
        sym(1.1, 9.0, 9.6, 17, 18, S),                   # cursor de distância
        box(1.1, 1.4, 9.05, 9.5, 17.2, 17.8, S),         # trava do cursor
    ]
    # lado direito: janela de ejeção, manivela, seletor grande; rebites e pinos dos dois lados
    c += [
        box(2, 2.12, 4, 6, 3, 10.5, "boca"),             # janela de ejeção (0,12 para não cintilar)
        box(2, 3.25, 5, 6, 10, 11, "aco_claro"),         # manivela de manejo
        box(3.25, 3.75, 5.1, 5.9, 10.1, 10.9, "aco_claro"),
        box(2, 2.25, 3.5, 4.75, 0, 9, "aco_claro"),      # seletor: chapa
        box(2, 2.5, 2.75, 3.75, 7.5, 9, "aco_claro"),    # seletor: aba para o dedo
        box(2, 2.4, 3.6, 4.6, -0.6, 0.4, "aco"),         # seletor: eixo
        box(1.95, 2.1, 1, 2.5, 7.5, 12, "aco_claro"),    # rebaixos estampados sobre o carregador
        box(-2.1, -1.95, 1, 2.5, 7.5, 12, "aco_claro"),
    ]
    for x0, x1 in ((2, 2.15), (-2.15, -2)):
        c += [box(x0, x1, y, y + 0.5, z, z + 0.5, "aco_claro")
              for y, z in ((1.5, -5.5), (4.5, -5.5), (2, 13.5), (2, 11.5), (4.5, 11.5), (2.5, 1.5), (2.5, 3.5))]
    # gatilho, guarda-mato e retém do carregador
    c += [
        sym(0.5, -2, -1.5, -0.5, 7, S),                  # guarda-mato
        sym(0.5, -2, 0, 6.5, 7, S),
        sym(0.5, -1.75, 0, -0.75, -0.25, S),
        sym(0.25, -1.5, 0, 2.5, 3.25, D),                # gatilho
        sym(0.25, -1.9, -1.3, 2.2, 2.7, D),
        sym(0.75, -1.25, 0, 7.75, 8.5, S),               # retém do carregador
        sym(0.75, -1.75, -1.25, 7.75, 9.25, S),          # aba do retém
    ]
    # empunhadura e coronha
    RG, PG = (-20, 0, 0), (0, 0, -1)
    c += [
        sym(1.5, -10, 0, -5, -1, W, r=RG, p=PG),         # empunhadura
        sym(1.3, -10.4, -10, -4.8, -1.2, D, r=RG, p=PG), # porca da base
    ]
    RS, PS = (7, 0, 0), (0, 5.75, -6.5)
    c += [
        sym(1.4, 0.75, 5.75, -10.5, -6.5, W, r=RS, p=PS),     # punho da coronha (mais fino)
        # coronha: linha de cima a 7°, linha de baixo a 12° (engrossa para trás). Dois cubos da mesma
        # largura, sobrepostos, girando no mesmo pivô: a emenda fica escondida dentro da madeira
        sym(1.75, 0.5, 5.75, -24, -10.5, W, r=RS, p=PS),
        sym(1.75, -1.5, 3, -24.1, -10.5, W, r=(12, 0, 0), p=PS),
        sym(0.6, 5.75, 6, -11, -6.5, S, r=RS, p=PS),          # espiga de aço por cima
        sym(1.85, -3.25, 6, -25.1, -24.1, D, r=(9.5, 0, 0), p=PS),   # chapa da soleira (cobre as duas)
        sym(1.2, 0.5, 4.5, -25.25, -25.1, S, r=(9.5, 0, 0), p=PS),   # tampa do compartimento
        sym(0.25, -2.25, -1.5, -21.5, -20.5, S, r=(12, 0, 0), p=PS), # argola da bandoleira
    ]
    # guarda-mãos de madeira com abraçadeiras de aço; tubo e bloco de gás
    c += [
        sym(2.35, 0.5, 5.75, 15.5, 16.25, S),            # abraçadeira de trás
        box(2.35, 2.65, 4.5, 5, 15.4, 16.6, S),          # alavanca da abraçadeira
        sym(2.25, 0.75, 5.5, 16.25, 26.75, W),           # guarda-mão inferior
        sym(2.45, 2, 4.25, 18.5, 25, W),                 # abaulamento para a mão
        sym(2.35, 0.5, 5.75, 26.75, 27.5, S),            # abraçadeira da frente
        sym(1.75, 6.25, 8.75, 16, 25, W),                # guarda-mão superior
        sym(1.4, 8.75, 9, 16.5, 24.5, W),                # topo arredondado
        sym(1, 6.5, 8.25, 25, 28.25, S),                 # tubo de gás
        sym(1.2, 3.25, 5.75, 28, 30.5, S),               # bloco de gás: anel no cano
        sym(1, 5.75, 8.25, 28.25, 30.25, S),             # bloco de gás: câmara
        sym(0.75, 3.75, 5.25, 13, 37, D),                # cano
        sym(0.25, 2.5, 3, 27, 35, D),                    # vareta de limpeza
        sym(0.35, 2.4, 3.1, 35, 35.5, S),                # cabeça da vareta
    ]
    # massa de mira (torre alta com orelhas), baioneta e freio de boca inclinado
    c += [
        sym(1, 3.25, 6.75, 33, 35.5, S),                 # base da massa
        sym(0.25, 6.75, 10.25, 34, 34.5, D),             # massa (torre alta)
        box(-1, -0.5, 6.75, 10, 33.5, 35, S),            # orelhas
        box(0.5, 1, 6.75, 10, 33.5, 35, S),
        sym(0.5, 2.25, 3.25, 31.5, 33.5, S),             # ressalto da baioneta
        sym(0.9, 3.6, 5.4, 37, 39.5, D),                 # freio de boca
        box(-1, 0, 3.5, 4.25, 38.5, 39.5, D),            # lábio inclinado do freio (lado esquerdo)
        box(-0.5, 0.5, 5.4, 5.5, 37.5, 38.5, "boca"),    # janela de cima do freio
    ]
    # carregador curvo de aço com nervuras, ressaltos e base
    seg = chain((0, 0.25, 10), 6, 3, 5, [8, 18, 28], "carregador")
    c += seg + nervuras_carregador(seg, "carregador")
    c += [sym(0.6, -0.5, 0.25, 12.4, 13.2, "carregador")]                   # ressalto da frente
    c.append(base_carregador((0, 0.25, 10), 6, [8, 18, 28], (3.3, 0.7, 5.4), D))
    return c, dict(grip=(0, -4, -3), muzzle=(0, 4.5, 39.5), handguard=(0, 0.75, 21.5),
                   visada=((0, 10.25, 14.75), (0, 10.25, 34.25)))


# ---------------------------------------------------------------- M4A4
def osso(nome, c):
    """Põe o cubo num osso próprio (filho de "arma"), para animar à parte. Ex.: "alca" some na mira."""
    c = dict(c)
    c["osso"] = nome
    return c


def dentes_z(z0, z1, cria, passo=1.0, larg=0.5):
    """Dentes de trilho Picatinny ao longo de Z: cria(z_ini, z_fim) devolve o cubo de um dente."""
    out, z = [], z0
    while z + larg <= z1 + 1e-9:
        out.append(cria(z, z + larg))
        z += passo
    return out


def m4a4():
    """M4A1 com trilho quádruplo (RIS). Escala ~1,3 cm por unidade (62 un. ~ 80 cm, coronha recolhida).
    Pontos calibrados (não mexer sem refazer a pose): punho, visada, boca do cano e guarda-mão."""
    c = []
    A, R, G = "anodizado", "trilho", "guarda_mao"
    # ---------------- receptor superior (flat-top)
    c += [
        sym(2, 2, 5.5, -6.5, 11.5, A),                   # corpo
        sym(1.6, 5.5, 6.5, -6.5, 11.5, A),               # ombros do topo (perfil afunilado)
        sym(1.1, 6.5, 6.9, -6, 11.25, R),                # base do trilho Picatinny
    ]
    c += dentes_z(-5.75, 11.25, lambda a, b: sym(1.25, 6.9, 7.5, a, b, R))
    c += [
        box(2, 2.2, 3, 4.75, 2, 7.5, A),                 # tampa da janela de ejeção (fechada)
        box(2, 2.3, 2.6, 2.95, 2, 7.5, "aco"),           # dobradiça da tampa
        box(2, 2.8, 4, 5.4, -0.75, 1.5, A),              # defletor de cartucho
        box(2, 3.1, 4.1, 5.6, -3, -0.75, A),             # forward assist (corpo)
        box(2.2, 2.95, 4.3, 5.4, -3.6, -3, "aco"),       # forward assist (botão)
        sym(1.75, 5.5, 6.25, -7.5, -6.5, A),             # alavanca de manejo
        box(-2.6, -1.6, 5.5, 6.25, -7.5, -6.6, A),       # trava da alavanca (esquerda)
    ]
    # alça de mira rebatível (BUIS) sobre o trilho: orifício + orelhas de proteção + botão de regulagem.
    # Toda ela fica no osso "alca", que encolhe até o trilho na mira (como se rebatesse): colada no olho, a
    # moldura do orifício e a base tapavam o centro da tela. Na mira completa, mira-se pela massa.
    c += [osso("alca", x) for x in (
        sym(1, 7.5, 9.75, -5, -3, A),                    # base
        box(1.45, 1.9, 8, 8.75, -4.5, -3.5, "aco"),      # botão de regulagem
        box(-1, -0.25, 9.75, 10.5, -4.5, -3.75, A),      # laterais do orifício (peep)
        box(0.25, 1, 9.75, 10.5, -4.5, -3.75, A),
        sym(1, 10.5, 11, -4.5, -3.75, A),                # topo do orifício
        box(1, 1.45, 7.5, 10.75, -4.75, -3.25, A),       # orelhas
        box(-1.45, -1, 7.5, 10.75, -4.75, -3.25, A),
    )]
    # ---------------- receptor inferior
    c += [
        sym(1.9, -1, 2, -6, 8.5, A),                     # corpo
        sym(1.75, -4, -1, 4.5, 9.5, A),                  # alojamento do carregador
        sym(1.95, -4.5, -3.75, 4.25, 9.75, A),           # boca do alojamento (alargada)
        sym(1.5, 0.5, 2, 8.5, 9.75, A),                  # nariz do inferior (frente)
        box(1.9, 2.3, -0.25, 0.75, 3.5, 4.25, "aco"),    # retém do carregador (direita)
        box(-2.3, -1.9, 0.25, 1.75, 3, 4, A),            # retém do ferrolho (esquerda)
        box(-2.4, -1.95, 0.6, 1.2, -3.75, -1.5, "aco"),  # seletor de tiro: alavanca (esquerda)
        box(-2.3, -1.9, 0.25, 1.6, -3.1, -2.2, A),       # seletor: eixo
        box(1.9, 2.15, 0.4, 1.1, -3.1, -2.3, "aco"),     # seletor: ponta do eixo (direita)
        box(1.9, 2.1, 1.3, 1.8, -5.25, -4.75, "aco"),    # pinos de desmontagem
        box(-2.1, -1.9, 1.3, 1.8, -5.25, -4.75, "aco"),
        box(1.9, 2.1, 1.3, 1.8, 9.1, 9.6, "aco"),
        box(-2.1, -1.9, 1.3, 1.8, 9.1, 9.6, "aco"),
        sym(0.5, -2.5, -2, -0.5, 5, A),                  # guarda-mato
        sym(0.5, -2.5, -1, 4.5, 5, A),
        sym(0.5, -2.25, -1, -0.75, -0.25, A),
        sym(0.25, -1.5, -0.5, 1.75, 2.25, "aco_escuro"), # gatilho (curvo: dois segmentos)
        sym(0.25, -2.1, -1.4, 1.4, 1.9, "aco_escuro"),
    ]
    # empunhadura A2 (inclinada) com ressalto para o dedo médio
    RG, PG = (-20, 0, 0), (0, -1, -2)
    c += [
        sym(1.5, -9, -1, -4.5, -1, "polimero_grip", r=RG, p=PG),
        sym(1.5, -5.5, -4.5, -1, -0.4, "polimero_grip", r=RG, p=PG),   # ressalto do dedo
        sym(1.3, -9, -1.5, -5.1, -4.5, "polimero_grip", r=RG, p=PG),   # dorso
        sym(1.6, -9.6, -9, -5, -0.6, "polimero", r=RG, p=PG),          # tampa da base
    ]
    # ---------------- tubo do amortecedor e coronha M4 (6 posições)
    c += [
        sym(1, 3, 5.5, -17, -7, "aco_escuro"),           # tubo (seção "redonda" = 2 cubos cruzados)
        sym(1.25, 3.25, 5.25, -17, -7, A),
        sym(1.5, 2.75, 5.75, -7.6, -6.6, "aco"),         # porca castelo / placa
        sym(1.5, 2.75, 6.5, -23.5, -15, "polimero"),     # corpo da coronha
        sym(1.1, 6.5, 7, -23, -15.5, "polimero"),        # crista do apoio de rosto
        sym(1.35, -0.5, 2.75, -24, -19.5, "polimero"),   # parte de baixo da coronha
        sym(1.1, 0.25, 2.75, -19.5, -17.5, "polimero"),  # rampa da parte de baixo
        sym(0.5, 2, 2.75, -17.25, -15, "aco_escuro"),    # alavanca de ajuste
        box(1.5, 1.7, 3.5, 5.5, -22.5, -17, "polimero"), # nervura lateral
        box(-1.7, -1.5, 3.5, 5.5, -22.5, -17, "polimero"),
        sym(1.75, -0.75, 7.25, -25, -24, "borracha"),    # soleira
    ]
    # ---------------- guarda-mão RIS (trilho nos 4 lados) com anéis
    c += [
        sym(2.5, 1.25, 7, 11.25, 11.75, "aco"),          # anel delta (junção com o receptor)
        sym(2, 1.75, 6.5, 11.75, 25.75, G),              # tubo do guarda-mão
        sym(2.35, 1.5, 6.75, 25.75, 26.25, "aco"),       # anel da frente
        sym(1.1, 6.5, 6.9, 12, 25.5, R),                 # trilho de cima: base
        box(2, 2.4, 3.5, 4.75, 12, 25.5, R),             # trilho direito: base
        box(-2.4, -2, 3.5, 4.75, 12, 25.5, R),           # trilho esquerdo: base
        sym(1.1, 1.35, 1.75, 12, 25.5, R),               # trilho de baixo: base
    ]
    c += dentes_z(12.25, 25.5, lambda a, b: sym(1.25, 6.9, 7.5, a, b, R))
    c += dentes_z(12.25, 25.5, lambda a, b: box(2.4, 2.95, 3.35, 4.9, a, b, R))
    c += dentes_z(12.25, 25.5, lambda a, b: box(-2.95, -2.4, 3.35, 4.9, a, b, R))
    c += dentes_z(12.25, 25.5, lambda a, b: sym(1.25, 0.75, 1.35, a, b, R))
    # ---------------- cano, base da massa (em A) e quebra-chama A2
    c += [
        sym(0.75, 3.5, 5, 26, 27, "aco_escuro"),         # cano (perfil grosso junto da base)
        sym(0.6, 3.6, 4.9, 29, 34, "aco_escuro"),        # cano (rebaixo do lança-granadas)
        sym(0.7, 3.55, 4.95, 29, 30, "aco_escuro"),
        sym(1, 3, 5.5, 27, 29, "aco"),                   # base da massa: abraçadeira no cano
        sym(0.75, 5.5, 7, 27.25, 28.75, "aco"),          # torre (base larga)
        sym(0.55, 7, 9, 27.5, 28.75, "aco"),             # torre (topo estreito: perfil em A)
        sym(0.25, 9, 10.5, 27.75, 28.5, "aco_escuro"),   # poste da massa
        box(-1, -0.5, 7, 10.25, 27.25, 29, "aco"),       # orelhas de proteção
        box(0.5, 1, 7, 10.25, 27.25, 29, "aco"),
        sym(0.4, 2.25, 3, 27.5, 29, "aco"),              # ressalto da baioneta
        sym(0.3, 2, 2.6, 28.75, 29.75, "aco"),           # fixação da bandoleira
        sym(0.85, 3.4, 5.1, 34, 34.5, "aco"),            # anel do quebra-chama
        sym(1, 3.25, 5.25, 34.5, 37, "quebra_chama"),    # quebra-chama A2 ("gaiola")
    ]
    # ---------------- carregador STANAG de 30 (levemente curvo) com base
    c += chain((0, -4, 7), 6, 2.5, 4.5, [4, 12], "carregador_m4")
    p = np.array([0, -4, 7], float)
    for a in (4, 12):
        p = p + np.array([0, -np.cos(np.radians(a)), np.sin(np.radians(a))]) * 6 * 0.97
    d = np.array([0, -np.cos(np.radians(14)), np.sin(np.radians(14))])
    cb = p + d * 0.35
    c.append(dict(o=(cb[0] - 1.45, cb[1] - 0.4, cb[2] - 2.5), s=(2.9, 0.8, 5.0), m="aco_escuro",
                  r=(14, 0, 0), p=tuple(cb)))             # base do carregador
    # visada: centro do orifício da alça -> ponta do poste da massa
    return c, dict(grip=(0, -5, -3.5), muzzle=(0, 4.25, 37), handguard=(0, 0.75, 20),
                   visada=((0, 10.125, -4.125), (0, 10.5, 28.125)), alca_pivo=(0, 7.5, -4))


# ---------------------------------------------------------------- GLOCK
def glock():
    """Glock 17 (Gen 5). ~1,13 cm por unidade. Pontos calibrados: punho, visada (topos a y 7,25), boca."""
    c = []
    P, F, D = "polimero", "ferrolho", "aco_escuro"
    # ---------------- ferrolho
    c += [
        sym(1.25, 3.5, 6.25, -3.25, 12.75, F),           # ferrolho
        sym(1.0, 6.25, 6.5, -3.25, 12.75, F),            # topo chanfrado (quina da Glock)
        sym(1.05, 3.6, 6.4, 12.75, 12.85, F),            # frente chanfrada
        sym(0.9, 3.75, 6.1, -3.5, -3.25, D),             # placa traseira
        box(-0.6, 0.9, 6.25, 6.55, 2.5, 7, "aco"),       # capuz do cano (aparece na janela)
        box(1.25, 1.37, 5.6, 6.25, 3, 6.5, "aco"),       # janela de ejeção: aparece o bloco do cano (aço)
        box(1.25, 1.33, 5.45, 5.6, 3, 6.5, "boca"),      # fresta escura embaixo da janela
        box(1.25, 1.4, 5.2, 5.6, 1.5, 3, "aco"),         # extrator
        sym(0.6, 4.4, 5.6, 12.75, 13, "aco"),            # cano saindo do ferrolho
        sym(0.4, 4.6, 5.4, 13, 13.25, "boca"),           # boca do cano
    ]
    for x0, x1 in ((1.25, 1.35), (-1.35, -1.25)):        # serrilhas: traseiras e dianteiras
        c += [box(x0, x1, 3.75, 6.0, z, z + 0.25, F) for z in np.arange(-3, -0.9, 0.5)]
        c += [box(x0, x1, 4.0, 6.0, z, z + 0.25, F) for z in np.arange(9.75, 11.6, 0.5)]
    # miras: alça em U (topo 7,25) e massa com folga dos dois lados no entalhe
    c += [
        sym(1, 6.5, 6.75, -2.5, -1.25, D),               # alça: base
        box(-1, -0.25, 6.75, 7.25, -2.5, -1.25, D),      # alça: entalhe em U
        box(0.25, 1, 6.75, 7.25, -2.5, -1.25, D),
        sym(0.2, 6.5, 7.25, 11.75, 12.75, D),            # massa
    ]
    # ---------------- armação (polímero)
    c += [
        sym(1.2, 2, 3.5, 1, 12.75, P),                   # capa de proteção / frente da armação
        sym(1.2, 2.75, 3.5, -3.5, 1, P),                 # faixa da armação sob o ferrolho
        sym(1.25, 2, 3, -5, -3, P),                      # beavertail
        sym(0.9, 1.6, 2, 6.75, 12.25, P),                # trilho de acessórios
        box(1.25, 1.4, 2.5, 3.2, 3.5, 4.5, D),           # alavanca de desmontagem
        box(-1.4, -1.25, 2.5, 3.2, 3.5, 4.5, D),
        box(-1.5, -1.25, 2.75, 3.25, 1, 3, D),           # retém do ferrolho
        box(-1.55, -1.25, 0.25, 1.25, -0.25, 0.5, P),    # retém do carregador
    ]
    c += [sym(1.05, 1.35, 1.6, z, z + 0.75, P) for z in (7.25, 9.25, 11.25)]   # ranhuras do trilho
    c += [
        sym(0.5, -1.75, -1.25, 0.5, 6, P),               # guarda-mato (quadrado)
        sym(0.5, -1.75, 2, 5.5, 6.25, P),
        sym(0.5, -1.5, -0.75, 6, 6.4, P),                # quina da frente do guarda-mato
        sym(0.3, -0.5, 2, 2.25, 2.85, P),                # gatilho
        sym(0.3, -1, -0.5, 2.05, 2.55, P),
        sym(0.1, -0.6, 1.75, 2.85, 3.0, "aco"),          # trava do gatilho (lâmina do meio)
    ]
    # empunhadura com ressaltos para os dedos, dorso e base do carregador
    RG, PG = (-18, 0, 0), (0, 3.5, -2)
    c += [
        sym(1.5, -5, 3.5, -4, 0.75, "polimero_grip", r=RG, p=PG),
        sym(1.35, -4.4, 2, -4.4, -4, P, r=RG, p=PG),               # dorso
    ]
    c += [sym(1.3, y, y + 0.6, 0.75, 1.05, P, r=RG, p=PG) for y in (-3.6, -2.0, -0.4)]   # ressaltos
    c += [
        sym(1.6, -5.4, -5, -4.25, 1, P, r=RG, p=PG),               # boca do alojamento
        sym(1.4, -6, -5.4, -4.0, 0.9, P, r=RG, p=PG),              # base do carregador
    ]
    # visada: topo da alça -> topo da massa (pistola: "topos nivelados")
    return c, dict(grip=(0, -1.5, -2.5), muzzle=(0, 5, 13.25),
                   visada=((0, 7.25, -1.875), (0, 7.25, 12.25)))


def anel(cx, cy, z0, z1, raio, esp, m):
    """Anel vazado (4 paredes finas) em torno do eixo Z: sino da luneta. Olha-se pelo centro aberto."""
    r, e = raio, esp
    return [
        box(cx - r, cx + r, cy + r - e, cy + r, z0, z1, m),          # topo
        box(cx - r, cx + r, cy - r, cy - r + e, z0, z1, m),          # base
        box(cx - r, cx - r + e, cy - r + e, cy + r - e, z0, z1, m),  # esquerda
        box(cx + r - e, cx + r, cy - r + e, cy + r - e, z0, z1, m),  # direita
    ]


def awp():
    """Sniper de ferrolho no padrão Accuracy International (chassi verde, cano flutuado, luneta grande).
    ~1,36 cm por unidade (~86 un = ~1,17 m). Pontos calibrados: punho, visada (eixo da luneta), boca."""
    c = []
    V, S, D, P = "chassi", "aco", "aco_escuro", "polimero"
    # ---------------- ação (caixa de aço) e ferrolho
    c += [
        sym(1.75, 1, 5.5, -9, 10, S),                    # corpo da ação
        sym(1.5, 5.5, 6.25, -9, 10, S),                  # topo da ação (base do trilho)
        sym(1.2, 6.25, 6.6, -8.5, 9.5, D),               # trilho
        sym(0.9, 2.5, 4.75, -11.5, -9, S),               # cauda da ação
        box(1.75, 2.5, 3.5, 5, -6, 3, S),                # corpo do ferrolho (direita)
        box(2.5, 3, 3.9, 4.6, -5.5, -4, S),              # maçaneta: haste
        box(2.9, 3.4, 3.6, 4.9, -5.6, -3.9, S),          # maçaneta: esfera
        box(-2.1, -1.75, 2.5, 4, -8, -6.5, S),           # trava do ferrolho (esquerda)
        box(1.75, 1.87, 3.6, 5, 2.5, 7.5, "boca"),       # janela de ejeção
    ]
    c += [sym(1.3, 6.6, 6.9, z, z + 0.4, D) for z in np.arange(-8, 9, 1.6)]   # dentes do trilho
    # ---------------- chassi verde: corpo central, coronha vazada e apoio de rosto
    c += [
        sym(1.9, -1.5, 1, -11, 12, V),                   # corpo do chassi sob a ação
        sym(2.1, -1.5, 2.5, 10, 12, V),                  # ombro de junção com o guarda-mão
        sym(1.6, -2, -1.5, -8, 10, V),                   # quilha inferior
        sym(2, 1, 4.5, -18, -11, V),                     # pescoço da coronha
        sym(1.9, -1, 1, -24, -18, V),                    # barra inferior da coronha (vazada)
        sym(1.9, 4.5, 7, -24, -17, V),                   # barra superior / apoio de rosto
        sym(2.1, 7, 7.6, -23, -18, P),                   # almofada do apoio de rosto
        sym(0.6, 1, 4.5, -23.5, -22, V),                 # montante traseiro (deixa o vão)
        sym(2.2, -1.5, 7.5, -25.5, -24, P),              # soleira (borracha)
        sym(1.1, -1.5, 1.5, -25.5, -24.5, S),            # espaçador da soleira
        sym(0.3, -1.5, -1, -21, -20, S),                 # argola da bandoleira (coronha)
    ]
    # ---------------- empunhadura de pistola e gatilho
    RG, PG = (-22, 0, 0), (0, -1, -5)
    c += [
        sym(1.5, -10, -1, -8, -3.5, V, r=RG, p=PG),      # empunhadura
        sym(1.3, -10.5, -1, -8.6, -8, V, r=RG, p=PG),    # dorso
        sym(1.6, -10.6, -10, -8.2, -3.7, P, r=RG, p=PG), # tampa da base
        sym(0.5, -2.5, -2, -2.5, 3, S),                  # guarda-mato
        sym(0.5, -2.5, -1.5, 2.5, 3, S),
        sym(0.5, -2.25, -1.5, -3, -2.5, S),
        sym(0.25, -2, -0.5, -0.75, 0, D),                # gatilho
        sym(0.25, -2.4, -1.8, -1.1, -0.5, D),
    ]
    # ---------------- carregador reto destacado
    c += [
        sym(1.5, -6.5, -1, 1, 7, D),                     # corpo do carregador
        sym(1.65, -7.2, -6.5, 0.8, 7.2, S),              # base
        sym(1.55, -2.5, -1.2, 6.8, 7.6, S),              # lábio da frente
        box(-1.8, -1.4, -1, 0.25, 7, 8.2, S),            # retém do carregador
    ]
    # ---------------- guarda-mão longo e cano flutuado (canelado) com freio de boca
    c += [
        sym(2.1, 0.5, 5, 12, 33, V),                     # guarda-mão (chassi)
        sym(2.3, 1.5, 4, 14, 31, V),                     # abaulamento lateral
        sym(1.9, 5, 5.6, 12, 33, V),                     # topo do guarda-mão
        sym(2.2, 1.25, 4.25, 32.5, 33.5, S),             # anel da ponta do guarda-mão
        sym(1.1, 1.6, 2, 25, 32, D),                     # trilho inferior (bipé)
        sym(0.4, 0.6, 1.6, 27.5, 31, S),                 # pé do bipé recolhido
        sym(0.3, 1.9, 2.4, 20, 21, S),                   # argola da bandoleira (frente)
        sym(1, 2.6, 4.6, 10, 52, D),                     # cano (seção quadrada)
        sym(0.8, 2.4, 4.8, 10, 52, D),                   # cano (seção cruzada: fica "redondo")
        sym(1.3, 2.3, 4.9, 52, 57, D),                   # freio de boca
        box(-1.35, 1.35, 4.9, 5.05, 53, 56.5, "boca"),   # rasgo de cima do freio
        box(1.3, 1.45, 2.6, 4.6, 53, 54.5, "boca"),      # rasgos laterais
        box(-1.45, -1.3, 2.6, 4.6, 53, 54.5, "boca"),
        box(1.3, 1.45, 2.6, 4.6, 55.2, 56.5, "boca"),
        box(-1.45, -1.3, 2.6, 4.6, 55.2, 56.5, "boca"),
        sym(1.35, 2.25, 4.95, 56.6, 57, S),              # aro da boca
        sym(0.45, 3.15, 4.05, 57, 57.2, "boca"),         # boca do cano
    ]
    # caneluras do cano (fluting): sulcos ao longo do cano exposto
    c += [box(x, x + 0.25, 3.1, 4.1, 34, 50, "aco_escuro") for x in (-1.1, -0.15, 0.85)]
    c += [sym(1.1, 2.5, 4.7, z, z + 0.6, S) for z in (34, 44, 50)]   # anéis do cano
    # ---------------- luneta (sólida: na mira a arma some e o painel da luneta assume a tela)
    EIXO_Y = 10.75                                       # altura do eixo óptico
    RT = 1.5                                             # raio do tubo
    c += [
        sym(RT, EIXO_Y - RT, EIXO_Y + RT, -7.5, 12, D),          # tubo (seção quadrada)
        sym(RT - 0.4, EIXO_Y - RT - 0.4, EIXO_Y + RT + 0.4, -7.5, 12, D),   # seção cruzada: fica "redondo"
        sym(2.0, EIXO_Y - 2.0, EIXO_Y + 2.0, -9.75, -7.5, D),    # sino da ocular
        sym(1.6, EIXO_Y - 2.4, EIXO_Y + 2.4, -9.75, -7.5, D),
        sym(2.1, EIXO_Y - 2.1, EIXO_Y + 2.1, -10.1, -9.75, S),   # aro da ocular
        sym(2.5, EIXO_Y - 2.5, EIXO_Y + 2.5, 12, 16.5, D),       # sino da objetiva
        sym(2.0, EIXO_Y - 2.9, EIXO_Y + 2.9, 12, 16.5, D),
        sym(2.6, EIXO_Y - 2.6, EIXO_Y + 2.6, 16.5, 16.9, S),     # aro da objetiva
        box(-2.0, 2.0, EIXO_Y - 2.0, EIXO_Y + 2.0, 16.9, 17.0, "boca"),     # lente (escura)
        sym(RT + 0.25, EIXO_Y - RT - 0.25, EIXO_Y + RT + 0.25, 7.5, 9.5, D),  # anel do aumento
        box(-1.75, 1.75, EIXO_Y + RT + 0.25, EIXO_Y + RT + 0.45, 7.8, 9.2, S),
        box(-0.7, 0.7, EIXO_Y + RT, EIXO_Y + RT + 1.3, -1.5, 1, D),          # torre de elevação
        box(-0.85, 0.85, EIXO_Y + RT + 1.3, EIXO_Y + RT + 1.6, -1.6, 1.1, S),
        box(RT, RT + 1.3, EIXO_Y - 0.7, EIXO_Y + 0.7, -1.5, 1, D),           # torre lateral
        box(RT + 1.3, RT + 1.6, EIXO_Y - 0.85, EIXO_Y + 0.85, -1.6, 1.1, S),
        # anéis de montagem: ligam o tubo ao trilho da ação
        sym(1.5, 6.9, EIXO_Y - RT, -6.8, -4.2, S),       # pé traseiro
        sym(1.5, 6.9, EIXO_Y - RT, 4.5, 7.1, S),         # pé dianteiro
        sym(1.85, EIXO_Y - RT - 0.35, EIXO_Y - RT + 0.35, -7, -4, S),   # abraçadeira traseira
        sym(1.85, EIXO_Y - RT - 0.35, EIXO_Y - RT + 0.35, 4.3, 7.3, S), # abraçadeira dianteira
        box(-1.9, 1.9, EIXO_Y + RT - 0.35, EIXO_Y + RT + 0.35, -7, -4, S),
        box(-1.9, 1.9, EIXO_Y + RT - 0.35, EIXO_Y + RT + 0.35, 4.3, 7.3, S),
    ]
    # visada: centro da ocular -> centro da objetiva (eixo óptico)
    return c, dict(grip=(0, -3.5, -1.5), muzzle=(0, 3.6, 57.2), handguard=(0, 1, 22),
                   visada=((0, EIXO_Y, -8.75), (0, EIXO_Y, 14.25)), luneta=True)


# ---------------------------------------------------------------- Besta de dardos tranquilizantes
CORDA_Y = 5.9                    # altura da corda: ela corre SOBRE a calha, não dentro do sulco
DARDO_Y = 5.25                   # o dardo assenta no sulco, com a metade de cima à mostra
CAM = (18.3, CORDA_Y, 14.4)      # roldana direita, no fim do terceiro trecho do arco (a esquerda é espelhada)
SERVING_Z = 0.5                  # corda armada: recuada até a ação
SERVING_SOLTA_Z = 13.6           # até onde ela corre: a linha das roldanas, onde a corda para
SERVING_HW = 0.9                 # meia-largura do serving (onde cada meia-corda termina)


def meia_corda(ponta_z):
    """(comprimento, ry) da meia-corda, da roldana direita até a borda do serving.

    O cubo é desenhado reto, ao longo de -Z a partir da roldana, e a rotação em Y o leva até o centro
    da calha; a animação interpola essa rotação e a escala em Z entre armada e solta (ver gerar.py).
    ry = -atan2(dx, -dz) sai de rot_bb (x_bb = -x): sinal de rotação no Bedrock não se chuta (bt.py)."""
    dx, dz = SERVING_HW - CAM[0], ponta_z - CAM[2]
    return float(np.hypot(dx, dz)), -float(np.degrees(np.arctan2(dx, -dz)))


def trecho_arco(lado, pivo, x0, x1, y0, y1, z0, z1, ry, m):
    """Um trecho do arco: cubo ao longo de X, girado em Y no pivô para abrir e avançar.

    ry POSITIVO leva a ponta do lado direito para TRÁS (-Z), que é para onde os arcos de uma besta
    abrem: o riser fica na ponta da frente e as roldanas ficam atrás dele, perto do atirador.
    Encadeando trechos com ângulos crescentes, o arco faz a curva da besta composta sem precisar de
    dezenas de degraus."""
    xa, xb = sorted((lado * x0, lado * x1))
    return box(xa, xb, y0, y1, z0, z1, m, r=(0, ry * lado, 0), p=pivo)


def tirante(a, b, esp, m):
    """Barra reta entre dois pontos no plano XZ (um cabo da besta, por exemplo).

    Mesma ideia da meia-corda: o cubo é desenhado ao longo de -Z a partir de `a` e a rotação em Y o
    leva até `b`. Cabo desenhado "paralelo ao arco" fica flutuando no ar; ligando os dois pontos de
    verdade, ele cai onde cai na besta real."""
    dx, dz = b[0] - a[0], b[2] - a[2]
    L = float(np.hypot(dx, dz))
    ry = -float(np.degrees(np.arctan2(dx, -dz)))
    return box(a[0] - esp, a[0] + esp, a[1] - esp, a[1] + esp, a[2] - L, a[2], m,
               r=(0, ry, 0), p=tuple(a))


def besta():
    """Besta composta de dardos tranquilizantes, no padrão das bestas táticas de hoje: coronha AR
    ajustável, calha vazada (esqueletada), arcos curvos com roldanas grandes, estribo em argola e
    luneta de média distância. ~1,36 cm por unidade (~55 un = ~75 cm; ~30 cm de ponta a ponta dos
    arcos). Pontos calibrados (não mexer sem refazer a pose): punho, visada, boca."""
    c = []
    T, TC, S, D, B = "tatico", "tatico_claro", "aco", "aco_escuro", "borracha"
    F, C, G = "fibra", "cabo", "polimero_grip"
    EIXO_Y = 10.5                                        # eixo óptico da luneta

    # ---------------- coronha AR ajustável: tubo de recuo + corpo vazado que corre sobre ele
    c += [
        sym(1.15, 2.45, 4.75, -25.5, -13.5, D),          # tubo de recuo (seção quadrada)
        sym(0.85, 2.15, 5.05, -25.5, -13.5, D),          # seção cruzada: fica redondo
        sym(1.4, 2.2, 5.0, -14.6, -13.6, S),             # flange do tubo no receiver
        sym(2.35, 4.75, 5.45, -25.2, -17.2, T),          # chapa de cima
        sym(2.35, 1.35, 2.15, -25.2, -17.2, T),          # chapa de baixo
        sym(2.35, 1.35, 5.45, -25.2, -24.2, T),          # montante traseiro
        sym(2.35, 1.35, 5.45, -21.6, -20.6, T),          # montante do meio (deixa as duas janelas)
        sym(2.35, 1.35, 5.45, -18.2, -17.2, T),          # montante dianteiro
        sym(2.05, 5.45, 6.15, -24.6, -18.0, TC),         # apoio de bochecha
        sym(2.15, 6.15, 6.4, -23.8, -18.8, B),           # borracha do apoio
        box(-0.8, 0.8, 1.05, 1.9, -22.4, -19.4, D),      # alavanca de ajuste do comprimento
        box(-0.5, 0.5, 0.7, 1.4, -21.8, -20.0, S),
        box(2.35, 2.6, 2.6, 4.2, -24.0, -22.4, D),       # gancho de bandoleira (direita)
        box(-2.6, -2.35, 2.6, 4.2, -24.0, -22.4, D),
    ]
    RB, PB = (9, 0, 0), (0, 3.4, -25.6)                  # placa de recuo levemente inclinada
    c += [
        sym(2.45, 0.9, 6.5, -26.6, -25.4, T, r=RB, p=PB),
        sym(2.55, 0.7, 6.7, -27.4, -26.6, B, r=RB, p=PB),
    ]
    # ---------------- receiver e trilho da luneta
    c += [
        sym(2.15, 1.0, 5.2, -13.6, 0.5, T),              # corpo
        sym(2.35, 1.6, 4.4, -12.6, -0.4, T),             # abaulamento lateral
        sym(2.4, 2.0, 3.6, -11.0, -7.5, TC),             # placa de identificação
        sym(1.95, 5.2, 5.75, -13.6, -1.0, S),            # base do trilho
        sym(1.5, 5.75, 6.05, -13.0, -1.2, D),            # trilho
        box(2.15, 2.5, 1.5, 3.4, -8.8, -6.8, D),         # trava de segurança (direita)
        box(-2.5, -2.15, 1.7, 2.9, -8.8, -7.2, S),       # retém da corda (esquerda)
        box(-2.5, -2.15, 3.1, 3.7, -7.8, -6.9, D),       # trava anti-disparo a seco
        sym(1.6, 0.55, 1.05, -12.5, -2.0, D),            # chapa inferior
        box(2.15, 2.45, 3.8, 4.6, -13.2, -12.0, D),      # pinos de desmontagem
        box(-2.45, -2.15, 3.8, 4.6, -13.2, -12.0, D),
        box(2.15, 2.45, 1.4, 2.2, -4.4, -3.2, D),
        box(-2.45, -2.15, 1.4, 2.2, -4.4, -3.2, D),
    ]
    c += dentes_z(-12.8, -1.3, lambda z0, z1: sym(1.6, 6.05, 6.4, z0, z1, D), passo=1.6, larg=0.5)
    # ---------------- empunhadura AR, gatilho e guarda-mato
    RG, PG = (-19, 0, 0), (0, -1, -7.8)
    c += [
        sym(1.5, -10.6, -1.0, -10.2, -5.4, T, r=RG, p=PG),         # empunhadura
        sym(1.3, -11.0, -1.0, -10.8, -10.2, T, r=RG, p=PG),        # dorso
        sym(1.55, -10.0, -1.8, -9.8, -8.8, G, r=RG, p=PG),         # pegada
        sym(1.6, -11.2, -10.6, -10.4, -5.6, T, r=RG, p=PG),        # tampa da base
        sym(1.7, -1.7, -0.7, -8.6, -6.4, T),                       # beavertail
        sym(0.55, -3.0, -2.45, -5.2, 0.6, S),                      # guarda-mato: barra de baixo
        sym(0.55, -3.0, -1.0, 0.1, 0.6, S),                        # haste da frente
        sym(0.55, -2.8, -1.0, -5.5, -5.0, S),                      # haste de trás
        sym(0.25, -2.4, -0.6, -3.2, -2.5, D),                      # gatilho
        sym(0.25, -2.8, -2.1, -3.6, -2.8, D),                      # ponta do gatilho
        sym(0.95, -1.5, -1.0, -3.8, -2.2, D),                      # alojamento do gatilho
    ]
    # ---------------- calha esqueletada: duas bandas e montantes, e o que sobra são as janelas
    Z0, Z1 = 0.5, 22.0
    c += [
        box(-0.95, 0.95, 4.95, 5.15, Z0, Z1, D),         # fundo do sulco (corda e dardo correm aqui)
        sym(2.05, 4.55, 4.95, Z0, Z1, T),                # alma, por baixo do sulco
        box(-2.15, -2.05, 5.15, 5.6, 3.0, 4.2, D),       # retentor do dardo (clipe)
        box(2.05, 2.15, 5.15, 5.6, 3.0, 4.2, D),
    ]
    for lado in (1, -1):
        x0, x1 = (0.95, 2.1) if lado > 0 else (-2.1, -0.95)
        c += [box(x0, x1, 5.15, 5.7, Z0, Z1, TC),        # banda de cima
              box(x0, x1, 3.55, 4.1, Z0, Z1, T)]         # banda de baixo
        z = Z0
        while z + 0.8 <= Z1 - 0.8:                       # montantes: as janelas ficam entre eles
            c.append(box(x0, x1, 4.1, 5.15, z, z + 0.8, T))
            z += 3.4
        c.append(box(x0, x1, 4.1, 5.15, Z1 - 0.8, Z1, T))
    # ---------------- guarda-mão com trilho e abas de proteção do dedo
    c += [
        sym(1.8, 0.9, 3.7, 8.5, 16.5, T),
        sym(1.95, 1.6, 3.1, 9.5, 15.5, G),               # pegada
        box(1.8, 2.45, 1.8, 4.4, 10.5, 14.0, T),         # aba direita (o dedo não sobe até a corda)
        box(-2.45, -1.8, 1.8, 4.4, 10.5, 14.0, T),
        sym(1.5, 0.5, 0.9, 9.0, 16.0, D),                # trilho inferior
        sym(0.4, 0.1, 0.6, 12.5, 13.5, S),               # argola da bandoleira
    ]
    c += dentes_z(9.3, 15.7, lambda z0, z1: sym(1.5, 0.2, 0.5, z0, z1, D), passo=1.6, larg=0.5)
    # ---------------- riser (bloco dos arcos)
    c += [
        sym(2.8, 2.1, 7.0, 18.6, 23.2, S),
        sym(3.0, 3.3, 6.1, 19.2, 22.6, D),               # faixa central
        sym(1.5, 7.0, 7.5, 19.2, 22.6, S),               # topo
        sym(2.6, 0.9, 2.1, 19.0, 23.4, S),               # base
        sym(0.7, 7.5, 8.0, 20.0, 21.8, D),               # olhal de montagem
        box(2.8, 3.2, 3.1, 4.0, 19.6, 22.2, D),          # parafusos laterais
        box(-3.2, -2.8, 3.1, 4.0, 19.6, 22.2, D),
    ]
    # ---------------- arcos: três trechos por lado, abrindo e avançando (a curva da composta)
    for lado in (1, -1):
        p1 = (lado * 2.8, 5.0, 21.0)
        p2 = (lado * 9.1, 5.2, 19.8)
        p3 = (lado * 14.9, 5.5, 17.2)
        c += [
            trecho_arco(lado, p1, 2.8, 9.2, 3.3, 6.7, 19.8, 22.2, 11.0, F),    # interno (grosso)
            trecho_arco(lado, p1, 2.6, 9.4, 4.2, 5.9, 19.5, 22.5, 11.0, F),    # nervura
            trecho_arco(lado, p1, 2.7, 4.5, 2.9, 7.1, 19.6, 22.4, 11.0, S),    # sapata no riser
            trecho_arco(lado, p1, 3.0, 4.2, 2.6, 3.0, 20.0, 22.0, 11.0, D),    # parafuso da sapata
            trecho_arco(lado, p2, 9.0, 15.6, 3.6, 6.5, 18.7, 20.9, 24.0, F),   # trecho do meio
            trecho_arco(lado, p2, 9.0, 15.8, 4.3, 5.9, 18.4, 21.2, 24.0, F),
            trecho_arco(lado, p2, 8.9, 10.4, 3.4, 6.7, 18.6, 21.0, 24.0, D),   # luva de emenda
            trecho_arco(lado, p3, 14.8, 19.2, 4.1, 6.3, 16.1, 18.3, 38.0, F),  # ponta
            trecho_arco(lado, p3, 14.8, 19.4, 4.7, 5.9, 15.9, 18.5, 38.0, F),
            # cabos: vão da roldana ao riser, por cima e por baixo da linha da corda
            tirante((lado * CAM[0], CORDA_Y + 2.3, CAM[2]), (lado * 2.2, CORDA_Y + 2.3, 20.6), 0.22, C),
            tirante((lado * CAM[0], CORDA_Y - 2.3, CAM[2]), (lado * 2.2, CORDA_Y - 2.3, 20.6), 0.22, C),
        ]
        # roldana (cam): disco grosso de dois quadrados cruzados, cubo central, eixo e pino
        cx = lado * CAM[0]
        c += [
            box(cx - 0.6, cx + 0.6, CORDA_Y - 3.0, CORDA_Y + 3.0, CAM[2] - 2.1, CAM[2] + 2.1, D),
            box(cx - 0.6, cx + 0.6, CORDA_Y - 2.1, CORDA_Y + 2.1, CAM[2] - 3.0, CAM[2] + 3.0, D),
            box(cx - 1.0, cx + 1.0, CORDA_Y - 2.3, CORDA_Y + 2.3, CAM[2] - 1.6, CAM[2] + 1.6, D),
            box(cx - 1.2, cx + 1.2, CORDA_Y - 0.55, CORDA_Y + 0.55, CAM[2] - 0.55, CAM[2] + 0.55, S),
            box(cx - 0.7, cx + 0.7, CORDA_Y + 0.9, CORDA_Y + 1.6, CAM[2] + 2.1, CAM[2] + 2.9, S),
        ]
    # ---------------- estribo em argola, saindo da frente (é onde entra o pé para armar)
    for lado in (1, -1):
        bx = lado * 2.0
        c += [
            box(bx - 0.75, bx + 0.75, -1.4, 1.5, 22.2, 23.7, D),     # sai da base do riser
            box(bx - 0.75, bx + 0.75, -4.1, -1.0, 23.1, 24.5, D),    # desce
            box(bx - 0.75, bx + 0.75, -5.5, -3.8, 23.6, 25.3, D, r=(45, 0, 0), p=(0, -4.4, 24.4)),
            box(bx - 0.75, bx + 0.75, -6.0, -4.6, 25.1, 27.0, D),    # fundo (a barra do pé)
            box(bx - 0.75, bx + 0.75, -5.6, -4.2, 26.6, 28.0, D, r=(-45, 0, 0), p=(0, -4.9, 27.3)),
        ]
    # a argola é um U aberto, como na besta de verdade: o pé entra por cima
    c += [
        box(-2.75, 2.75, -6.05, -4.65, 25.4, 26.8, B),               # borracha onde pisa o pé
        box(-2.75, 2.75, -4.9, -4.0, 27.4, 28.2, D),                 # travessa da frente
    ]
    # ---------------- luneta de média distância (sólida: na mira a arma some e o painel assume a tela)
    RT = 1.4                                             # raio do tubo
    c += [
        sym(RT, EIXO_Y - RT, EIXO_Y + RT, -11.5, 2.2, D),                    # tubo (seção quadrada)
        sym(RT - 0.35, EIXO_Y - RT - 0.35, EIXO_Y + RT + 0.35, -11.5, 2.2, D),  # seção cruzada
        sym(1.85, EIXO_Y - 1.85, EIXO_Y + 1.85, -13.7, -11.5, D),            # sino da ocular
        sym(1.5, EIXO_Y - 2.2, EIXO_Y + 2.2, -13.7, -11.5, D),
        sym(1.95, EIXO_Y - 1.95, EIXO_Y + 1.95, -14.1, -13.7, S),            # aro da ocular
        sym(2.0, EIXO_Y - 2.0, EIXO_Y + 2.0, -14.4, -14.1, B),               # borracha da ocular
        sym(2.3, EIXO_Y - 2.3, EIXO_Y + 2.3, 2.2, 6.4, D),                   # sino da objetiva
        sym(1.85, EIXO_Y - 2.7, EIXO_Y + 2.7, 2.2, 6.4, D),
        sym(2.4, EIXO_Y - 2.4, EIXO_Y + 2.4, 6.4, 6.8, S),                   # aro da objetiva
        box(-1.8, 1.8, EIXO_Y - 1.8, EIXO_Y + 1.8, 6.8, 6.9, "boca"),        # lente
        sym(RT + 0.25, EIXO_Y - RT - 0.25, EIXO_Y + RT + 0.25, -4.6, -2.6, D),  # anel do aumento
        box(-1.65, 1.65, EIXO_Y + RT + 0.25, EIXO_Y + RT + 0.42, -4.3, -2.9, S),
        box(-0.65, 0.65, EIXO_Y + RT, EIXO_Y + RT + 1.25, -7.0, -4.7, D),    # torre de elevação
        box(-0.8, 0.8, EIXO_Y + RT + 1.25, EIXO_Y + RT + 1.55, -7.1, -4.6, S),
        box(RT, RT + 1.25, EIXO_Y - 0.65, EIXO_Y + 0.65, -7.0, -4.7, D),     # torre lateral
        box(RT + 1.25, RT + 1.55, EIXO_Y - 0.8, EIXO_Y + 0.8, -7.1, -4.6, S),
        # anéis de montagem altos: ligam o tubo ao trilho do receiver
        sym(1.4, 6.3, EIXO_Y - RT, -10.6, -8.4, S),      # pé traseiro
        sym(1.4, 6.3, EIXO_Y - RT, -4.1, -1.9, S),       # pé dianteiro
        sym(1.8, EIXO_Y - RT - 0.33, EIXO_Y - RT + 0.33, -10.8, -8.2, S),
        sym(1.8, EIXO_Y - RT - 0.33, EIXO_Y - RT + 0.33, -4.3, -1.7, S),
        box(-1.85, 1.85, EIXO_Y + RT - 0.33, EIXO_Y + RT + 0.33, -10.8, -8.2, S),
        box(-1.85, 1.85, EIXO_Y + RT - 0.33, EIXO_Y + RT + 0.33, -4.3, -1.7, S),
        box(1.8, 2.05, EIXO_Y - RT - 0.5, EIXO_Y - RT + 0.5, -10.6, -8.4, D),   # parafusos dos anéis
        box(1.8, 2.05, EIXO_Y - RT - 0.5, EIXO_Y - RT + 0.5, -4.1, -1.9, D),
        box(-2.05, -1.8, EIXO_Y - RT - 0.5, EIXO_Y - RT + 0.5, -10.6, -8.4, D),
        box(-2.05, -1.8, EIXO_Y - RT - 0.5, EIXO_Y - RT + 0.5, -4.1, -1.9, D),
    ]
    # ---------------- corda: ossos próprios, animados pelo ciclo do disparo (ver gerar.py)
    L_arm, ry_arm = meia_corda(SERVING_Z)
    L_sol, ry_sol = meia_corda(SERVING_SOLTA_Z)
    c.append(osso("corda", box(-SERVING_HW - 0.15, SERVING_HW + 0.15, CORDA_Y - 0.3, CORDA_Y + 0.3,
                               SERVING_Z - 0.4, SERVING_Z + 0.4, C)))          # serving central
    for lado, nome in ((1, "corda_d"), (-1, "corda_e")):
        cx = lado * CAM[0]
        c.append(osso(nome, box(cx - 0.2, cx + 0.2, CORDA_Y - 0.2, CORDA_Y + 0.2,
                                CAM[2] - L_arm, CAM[2], C)))
    # ---------------- dardo na calha (some no tiro, volta quando a besta rearma)
    DZ0, AL = 1.4, "aluminio"
    c += [osso("dardo", x) for x in (
        box(-0.55, 0.55, DARDO_Y + 0.05, DARDO_Y + 1.15, DZ0, DZ0 + 1.0, "fluor"),       # penacho
        box(-0.35, 0.35, DARDO_Y - 0.1, DARDO_Y + 1.3, DZ0 + 0.3, DZ0 + 0.7, "fluor"),
        box(-0.5, 0.5, DARDO_Y + 0.1, DARDO_Y + 1.1, DZ0 + 1.0, DZ0 + 6.2, AL),          # corpo (3 cc)
        box(-0.35, 0.35, DARDO_Y - 0.05, DARDO_Y + 1.25, DZ0 + 1.0, DZ0 + 6.2, AL),      # seção cruzada
        box(-0.4, 0.4, DARDO_Y + 0.2, DARDO_Y + 1.0, DZ0 + 6.2, DZ0 + 6.8, D),           # colar
        box(-0.15, 0.15, DARDO_Y + 0.45, DARDO_Y + 0.75, DZ0 + 6.8, DZ0 + 9.4, S),       # cânula
    )]
    # visada: centro da ocular -> centro da objetiva (eixo óptico)
    return c, dict(
        grip=(0, -4, -7), muzzle=(0, CORDA_Y + 0.6, 26.0), handguard=(0, 1.6, 12.5),
        visada=((0, EIXO_Y, -12.6), (0, EIXO_Y, 4.3)), luneta=True, vista_icone="topo",
        # a luneta é de rifle de média distância, não a vinheta fechada da AWP: campo mais largo,
        # retículo duplex e marcas de queda (o dardo cai de verdade; o tiro sai do centro da tela)
        luneta_furo=0.93, luneta_duplex=True, luneta_marcas=2,
        ossos={
            # a corda dispara para a frente e volta sendo puxada, no ritmo do ciclo (v.ciclo: 0 no tiro,
            # 1 rearmada). Cada meia-corda gira no pivô da roldana e muda de comprimento (escala em Z),
            # que é o que a roldana faz na vida real ao liberar e recolher corda.
            "corda": dict(pivo=(0, CORDA_Y, SERVING_Z),
                          anim={"position": [0, 0, f"(1.0 - v.ciclo) * {SERVING_SOLTA_Z - SERVING_Z:.3f}"]}),
            # "repouso" é a pose parada (besta armada), que as prévias desenham e que o jogo mostra
            # se o Molang falhar: a corda tem de parecer certa mesmo sem animação nenhuma.
            "corda_d": dict(pivo=CAM, repouso=dict(rot=(0, ry_arm, 0)), anim={
                "rotation": [0, f"math.lerp({ry_sol:.3f}, {ry_arm:.3f}, v.ciclo)", 0],
                "scale": [1, 1, f"math.lerp({L_sol / L_arm:.4f}, 1.0, v.ciclo)"]}),
            "corda_e": dict(pivo=(-CAM[0], CAM[1], CAM[2]), repouso=dict(rot=(0, -ry_arm, 0)), anim={
                "rotation": [0, f"math.lerp({-ry_sol:.3f}, {-ry_arm:.3f}, v.ciclo)", 0],
                "scale": [1, 1, f"math.lerp({L_sol / L_arm:.4f}, 1.0, v.ciclo)"]}),
            # o dardo some no disparo e reaparece com a besta rearmada
            "dardo": dict(pivo=(0, DARDO_Y, DZ0), anim={"scale": "(v.ciclo > 0.98) ? 1.0 : 0.0"}),
        })

def maos(info, tipo):
    """Mãos com luva + manga, só aparecem em primeira pessoa (coordenadas já relativas ao punho)."""
    c = []
    if tipo in ("fuzil", "sniper", "besta"):
        # mão direita fechada na empunhadura
        c.append(sym(2.5, -7, -0.5, -6.5, 0.5, "luva", r=(-20, 0, 0), p=(0, -0.5, -3)))
        c.append(box(-2.5, -1.5, -1.5, 0.5, 0.5, 3, "luva"))     # dedo no guarda-mato
        c += braco((1, -6, -6), (0.55, -0.55, -0.63), 34, 6.5, "luva", "manga", 3)
        # mão esquerda segurando o guarda-mão por baixo
        hx, hy, hz = info["handguard_rel"]
        c.append(box(hx - 3, hx + 3, hy - 2.5, hy + 3, hz - 3, hz + 3, "luva"))
        c += braco((hx - 1, hy - 1.5, hz - 2), (-0.62, -0.42, -0.66), 46, 6.5, "luva", "manga", 3)
    else:
        c.append(sym(2.25, -5.5, 1.75, -6, 0.5, "luva", r=(-20, 0, 0), p=(0, 1.75, -3)))
        c.append(box(-2.25, -1.25, -1, 0.75, 0.75, 3, "luva"))   # indicador
        c.append(box(-3.25, -1.75, -5, 1, -4.5, 0.75, "luva", r=(-20, 0, 0), p=(0, 1.75, -3)))  # mão esquerda envolvendo
        c += braco((1, -6, -6), (0.5, -0.5, -0.7), 34, 6, "luva", "manga", 3)
        c += braco((-2.5, -6, -4), (-0.5, -0.5, -0.7), 34, 6, "luva", "manga", 3)
    return c
