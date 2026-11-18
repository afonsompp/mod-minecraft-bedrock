"""Os dois jeitos de declarar um cubo. Valem para arma, bloco, criatura — qualquer coisa.

Um cubo é `dict(o=origem, s=tamanho, m=material, r=rotação opcional, p=pivô da rotação)`. As
unidades dependem de quem desenha: arma usa 1/64 de bloco, entidade e bloco usam 1/16.
"""


def box(x0, x1, y0, y1, z0, z1, m, r=None, p=None):
    """Cubo pelos extremos, que é como se pensa uma peça — não por origem e tamanho."""
    c = dict(o=(x0, y0, z0), s=(x1 - x0, y1 - y0, z1 - z0), m=m)
    if r is not None:
        c["r"] = tuple(r)
        c["p"] = tuple(p)
    return c


def sym(hw, y0, y1, z0, z1, m, **kw):
    """Cubo centrado em X, de meia-largura `hw`. Quase toda peça de arma e de bicho é simétrica."""
    return box(-hw, hw, y0, y1, z0, z1, m, **kw)
