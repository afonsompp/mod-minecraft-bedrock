"""O Velociraptor: o primeiro esqueleto articulado do projeto.

**Unidades e eixos.** 1 unidade = 1/16 de bloco (entidade, não arma). O chão é `y = 0`. A frente de
qualquer entidade no Bedrock é **−Z**, então a cabeça fica em Z negativo e a cauda em Z positivo —
o contrário das armas, onde +Z é o cano.

**A régua é o raptor do cinema**, não o animal do registro fóssil (que tinha o tamanho de um peru):
cerca de 1,8 m até o alto da cabeça e 3,5 m do focinho à ponta da cauda. Em unidades, ~29 de altura
por ~56 de comprimento.

**A pose desenhada é a pose parada**, e é a única que existe nos cubos: as rotações de repouso são
assadas por `esqueleto.achatar`, e cada quadro-chave de animação é o delta puro em relação a isto.
Se o Molang falhar no jogo, o bicho fica exatamente nesta pose — de pé, correto —, em vez de
desmontado.
"""
from nucleo.esqueleto import Osso, espelhar_x
from nucleo.formas import box, sym

D, F, V, X, G, T, O = ("pele_dorso", "pele_flanco", "pele_ventre", "pele_faixa",
                       "garra", "dente", "olho")


def _dedo(x0, z0, comp, larg, alt, y=0.0):
    """Um dedo com garra na ponta, apoiado no chão."""
    return [
        box(x0, x0 + larg, y, y + alt, z0 - comp, z0, V),
        box(x0 + larg * 0.15, x0 + larg * 0.85, y, y + alt * 0.8, z0 - comp - 1.6, z0 - comp, G),
    ]


def ossos():
    """O esqueleto inteiro: 19 ossos, cinco níveis de profundidade."""
    # ---------------- tronco ----------------
    quadril = [
        sym(4.6, 16.0, 23.0, -1.0, 8.0, D),            # bacia
        sym(4.0, 15.4, 16.6, -1.0, 7.0, V),            # ventre, mais claro (countershading)
        sym(4.2, 22.4, 23.6, 0.0, 6.0, D),             # crista do quadril
    ]
    corpo = [
        sym(5.0, 15.4, 23.2, -11.0, -1.0, F),          # caixa torácica
        sym(4.4, 14.8, 16.2, -10.0, -1.0, V),
        sym(5.2, 22.6, 23.8, -9.5, -1.5, D),           # linha do dorso
        # faixa escura do flanco, a marca que o João vai reconhecer de longe
        box(-5.15, -4.6, 18.0, 20.6, -10.0, -1.0, X),
        box(4.6, 5.15, 18.0, 20.6, -10.0, -1.0, X),
    ]
    peito = [
        sym(4.6, 15.8, 22.6, -16.0, -11.0, F),
        sym(4.0, 15.2, 16.6, -15.0, -11.0, V),
        sym(4.8, 21.8, 23.0, -15.0, -11.0, D),
        sym(3.4, 16.6, 20.0, -17.2, -16.0, F),         # peitoral, à frente da caixa
    ]

    # ---------------- pescoço e cabeça ----------------
    pescoco = [
        sym(3.0, 20.0, 24.0, -21.0, -16.0, F),
        sym(2.6, 24.0, 25.0, -20.5, -16.5, D),
        sym(2.4, 19.2, 20.2, -20.0, -16.5, V),
    ]
    cabeca = [
        sym(3.0, 24.6, 28.4, -27.0, -21.0, F),         # crânio
        sym(3.1, 28.4, 29.2, -26.0, -21.5, D),         # topo do crânio
        sym(2.4, 25.4, 28.0, -31.5, -27.0, D),         # focinho
        sym(2.0, 24.8, 25.6, -31.0, -27.0, V),
        box(-2.1, 2.1, 28.0, 28.8, -31.0, -27.5, D),   # cana nasal
        # arco superciliar: a sobrancelha que dá cara de predador. Peça própria, como a regra manda
        # para detalhe que depende de posição.
        box(-3.2, -1.6, 28.0, 29.0, -26.6, -24.0, X),
        box(1.6, 3.2, 28.0, 29.0, -26.6, -24.0, X),
        # olhos, para os lados (campo de visão de caçador)
        box(-3.3, -2.9, 25.9, 28.1, -27.0, -24.8, O),
        box(2.9, 3.3, 25.9, 28.1, -27.0, -24.8, O),
        # dentes de cima
        *[box(x, x + 0.5, 24.2, 25.4, -30.6 + i * 1.5, -30.1 + i * 1.5, T)
          for i in range(3) for x in (-2.1, 1.6)],
    ]
    mandibula = [
        sym(2.2, 22.6, 24.6, -31.0, -22.0, F),
        sym(1.8, 22.2, 23.0, -30.0, -23.0, V),
        *[box(x, x + 0.5, 24.4, 25.4, -30.4 + i * 1.5, -29.9 + i * 1.5, T)
          for i in range(3) for x in (-1.9, 1.4)],
    ]

    # ---------------- cauda, em três segmentos ----------------
    cauda1 = [sym(3.8, 17.0, 22.4, 8.0, 17.0, F),
              sym(3.9, 21.8, 22.8, 8.0, 16.5, D),
              sym(3.2, 16.6, 17.6, 8.0, 16.0, V)]
    cauda2 = [sym(2.8, 17.6, 21.6, 17.0, 25.0, F),
              sym(2.9, 21.2, 22.0, 17.0, 24.5, D)]
    cauda3 = [sym(1.8, 18.4, 20.8, 25.0, 32.0, F),
              sym(1.0, 19.0, 20.2, 32.0, 36.0, F)]

    # ---------------- membros ----------------
    # a coxa de um raptor é um músculo pesado em cima que afina até o joelho — um bloco só vira placa
    coxa = [box(3.1, 6.7, 13.4, 19.2, -2.4, 5.2, F),
            box(3.2, 6.6, 10.6, 13.6, -1.8, 4.4, F),
            box(3.5, 6.3, 8.0, 10.8, -1.0, 3.4, F),
            box(3.3, 6.5, 12.6, 14.0, -2.0, 4.8, V)]
    canela = [box(3.9, 6.0, 2.2, 8.8, 0.0, 2.8, F),
              box(4.1, 5.8, 2.0, 4.4, -0.3, 2.4, V)]
    pe = [box(3.9, 5.9, 0.0, 1.9, -1.8, 1.8, F),
          # a garra em foice do segundo dedo, erguida e sem tocar o chão — a assinatura do bicho
          box(4.3, 5.5, 1.5, 3.4, -3.4, -1.9, G),
          *_dedo(3.7, -1.8, 1.9, 1.1, 1.0),
          *_dedo(5.0, -1.5, 1.7, 1.1, 0.9),
          *_dedo(4.4, 1.8, 1.2, 1.1, 0.9)]
    braco = [box(3.0, 5.0, 16.0, 19.4, -15.4, -12.6, F)]
    antebraco = [box(3.2, 4.8, 11.6, 16.4, -15.0, -13.0, F),
                 box(3.3, 4.7, 10.2, 11.8, -15.6, -12.6, V),
                 *[box(3.4 + i * 0.5, 3.8 + i * 0.5, 9.0, 10.4, -15.4 + i * 0.6, -14.0 + i * 0.6, G)
                   for i in range(3)]]

    def par(nome, pai, pivo, cubos, repouso=(0.0, 0.0, 0.0)):
        """O mesmo membro dos dois lados. Espelhar é operação de dados — nunca escala negativa."""
        rx, ry, rz = repouso
        return [Osso(f"{nome}_d", pai, pivo, cubos, repouso),
                Osso(f"{nome}_e", pai, (-pivo[0], pivo[1], pivo[2]), espelhar_x(cubos),
                     (rx, -ry, -rz))]

    return [
        Osso("raiz", None, (0.0, 0.0, 0.0), []),
        Osso("quadril", "raiz", (0.0, 19.0, 3.0), quadril),
        Osso("corpo", "quadril", (0.0, 19.5, -1.0), corpo, repouso=(-4.0, 0.0, 0.0)),
        Osso("peito", "corpo", (0.0, 19.6, -11.0), peito, repouso=(-3.0, 0.0, 0.0)),
        Osso("pescoco", "peito", (0.0, 20.4, -16.0), pescoco, repouso=(-30.0, 0.0, 0.0)),
        Osso("cabeca", "pescoco", (0.0, 26.0, -21.0), cabeca, repouso=(33.0, 0.0, 0.0)),
        Osso("mandibula", "cabeca", (0.0, 24.6, -22.0), mandibula),
        Osso("cauda1", "quadril", (0.0, 19.8, 8.0), cauda1, repouso=(3.0, 0.0, 0.0)),
        Osso("cauda2", "cauda1", (0.0, 19.6, 17.0), cauda2, repouso=(2.0, 0.0, 0.0)),
        Osso("cauda3", "cauda2", (0.0, 19.6, 25.0), cauda3, repouso=(2.0, 0.0, 0.0)),
        # rx NEGATIVO leva a parte de baixo para −Z, que é a frente. Daí a corrente da perna:
        # coxa para a frente (joelho), canela de volta (tornozelo), pé horizontal no chão.
        *par("coxa", "quadril", (4.9, 18.6, 1.8), coxa, repouso=(-18.0, 0.0, 0.0)),
        *par("canela", "coxa_d", (4.9, 8.4, 1.6), canela, repouso=(43.0, 0.0, 0.0)),
        *par("pe", "canela_d", (4.9, 2.4, 1.2), pe, repouso=(-25.0, 0.0, 0.0)),
        *par("braco", "peito", (4.0, 19.4, -14.0), braco, repouso=(30.0, 0.0, 0.0)),
        *par("antebraco", "braco_d", (4.0, 16.2, -14.0), antebraco, repouso=(-70.0, 0.0, 0.0)),
    ]


def arrumar_pares(lista):
    """Liga `canela_e` a `coxa_e` (e assim por diante): o helper `par` monta os dois lados com o pai
    do lado direito, e aqui o esquerdo é redirecionado para o seu."""
    saida = []
    nomes = {o.nome for o in lista}
    for o in lista:
        if o.nome.endswith("_e") and o.pai and o.pai.endswith("_d"):
            candidato = o.pai[:-2] + "_e"
            if candidato in nomes:
                o = o._replace(pai=candidato)
        saida.append(o)
    return saida


def modelo():
    return arrumar_pares(ossos())
