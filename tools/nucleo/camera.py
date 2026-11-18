"""Câmera orbital para as prévias 3D.

Estava copiada à mão em cada gerador que precisava mostrar alguma coisa (as armas, o dardo, os
blocos), e cada cópia nova repetia o mesmo erro: o referencial de câmera do renderizador é
**espelhado** (a direita da tela é −X do espaço bb). Escrita com a convenção destra de sempre, a
câmera passa no teste de visibilidade ao contrário e mostra o objeto por dentro — faces de cima
escuras e interiores à mostra.
"""
import numpy as np


def orbital(giro, incl, dist, alvo=(0.0, 0.0, 0.0), fov=26.0, tela=(900, 640)):
    """Devolve `(vista, projetar, tamanho)` para passar ao `render`.

    `giro` roda em torno de Y e `incl` sobe a câmera, as duas em graus. Com a elevação, o alto do
    objeto fica **mais perto** da câmera — é isso que distingue olhar de cima de olhar de baixo.
    """
    W, H = tela
    cg, sg = np.cos(np.radians(giro)), np.sin(np.radians(giro))
    ci, si = np.cos(np.radians(incl)), np.sin(np.radians(incl))
    alvo = np.asarray(alvo, float)

    def vista(q_bb):
        q = np.asarray(q_bb, float) - alvo
        direita = -(q[:, 0] * cg - q[:, 2] * sg)
        fundo = q[:, 0] * sg + q[:, 2] * cg
        cima = q[:, 1] * ci + fundo * si
        prof = fundo * ci - q[:, 1] * si
        return np.stack([direita, cima, prof + dist], axis=1)

    f = W / 2 / np.tan(np.radians(fov / 2))

    def projetar(p):
        return (W / 2 + p[0] / p[2] * f, H / 2 - p[1] / p[2] * f)

    return vista, projetar, (W, H)
