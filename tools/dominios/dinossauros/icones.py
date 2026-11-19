"""Ícones de item do laboratório: fóssil, ovo sintético, tubo de DNA e ovo de cada espécie.

Desenho 2D em 512 px reduzido para 64 (ver `nucleo/icones.py`). Os dois ícones por espécie saem da
cor dela, então uma espécie nova não pede desenho novo — é o mesmo princípio do registro.
"""
import numpy as np
from PIL import Image

from nucleo.icones import (S, contorno, cyl_shade, esfera, faixa, mascara_elipse, mascara_ovo,
                           mascara_pedra, salvar)


def _por(arr, mask, campo):
    arr[..., :3][mask] = campo[mask]
    arr[..., 3][mask] = 255


def _imagem(arr):
    return contorno(Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA"))


def _coluna(campo, x0):
    """Espalha uma coluna de cores (w, 3) por toda a altura, a partir da coluna x0."""
    out = np.zeros((S, S, 3))
    out[:, x0:x0 + campo.shape[0]] = campo[None, :, :]
    return out


def fossil():
    """Um fêmur preso na rocha: a peça que sai do chão e vira DNA.

    O osso é desenhado inteiro — haste e as duas cabeças — porque uma listra diagonal na pedra lê
    como risco, não como osso."""
    arr = np.zeros((S, S, 4), float)
    pedra = mascara_pedra(256, 272, 196, rugas=7, forca=0.17, semente=5)
    _por(arr, pedra, esfera(236, 250, 232, 232, (106, 102, 97), (196, 193, 188), claro=0.18))
    # veios da rocha: ondulação larga, nunca ruído fino (some na redução e vira sujeira)
    yy, xx = np.mgrid[0:S, 0:S]
    veio = np.sin((xx * 0.7 + yy) / 29.0) * 6.0
    arr[..., :3][pedra] += veio[pedra][:, None]

    osso_cor = esfera(214, 236, 150, 150, (216, 208, 182), (255, 253, 243), claro=0.26)
    ax, ay, bx, by = 142, 352, 372, 206            # as duas pontas do fêmur
    # haste: faixa entre as pontas, afinando no meio como um osso de verdade
    dx, dy = bx - ax, by - ay
    comp = np.hypot(dx, dy)
    t = ((xx - ax) * dx + (yy - ay) * dy) / comp ** 2
    perp = np.abs((xx - ax) * dy - (yy - ay) * dx) / comp
    meia = 30 - 10 * np.sin(np.clip(t, 0, 1) * np.pi)
    haste = (perp <= meia) & (t >= 0) & (t <= 1) & pedra
    # epífises: duas cabeças por ponta, que é o que dá a silhueta de osso
    cabecas = np.zeros_like(haste)
    for cx, cy, s in ((ax, ay, 1), (bx, by, -1)):
        cabecas |= mascara_elipse(S, S, cx - 16 * s, cy + 20 * s, 46, 40)
        cabecas |= mascara_elipse(S, S, cx + 20 * s, cy - 6 * s, 40, 36)
    osso = (haste | (cabecas & pedra))
    # sombra de contato: o osso está DENTRO da pedra, não colado por cima
    borda = np.zeros_like(osso)
    for d in (4, -4):
        borda |= np.roll(osso, d, 0) | np.roll(osso, d, 1)
    arr[..., :3][borda & ~osso & pedra] *= 0.58
    _por(arr, osso, osso_cor)
    # rachadura na cabeça de baixo: é um fóssil, não um osso novo
    trinca = (np.abs((yy - 352) * 0.9 + (xx - 142) * 0.4) < 3) & mascara_elipse(S, S, 128, 368, 44, 38)
    arr[..., :3][trinca] *= 0.70
    return _imagem(arr)


def ovo_sintetico():
    """Casca vazia de laboratório: branca, lisa, com o anel de vedação por onde o DNA entra."""
    arr = np.zeros((S, S, 4), float)
    cx, cy, rx, ry = 256, 272, 128, 182
    m = mascara_ovo(cx, cy, rx, ry)
    _por(arr, m, esfera(cx, cy, rx, ry, (224, 222, 214), (255, 255, 255), claro=0.42))
    yy, _ = np.mgrid[0:S, 0:S]
    arr[..., :3][m & (np.abs(yy - (cy + 10)) < 7)] *= 0.74          # anel de vedação
    arr[..., :3][m & (np.abs(yy - (cy + 10)) < 3)] *= 0.92
    return _imagem(arr)


def ovo(cor):
    """Ovo de dinossauro: a casca puxa para a cor da espécie e ganha manchas dela, mais escuras.

    **O contraste aqui não é enfeite.** No hotbar o ícone tem 16 px, e até a v1.9.1 este ovo e o
    sintético eram os dois um oval quase branco — ao ponto de nem dar para dizer qual era qual num
    vídeo do jogo. Casca tingida de verdade e manchas escuras são o que distingue um do outro de
    relance e, com mais espécies, o que distingue uma espécie da outra: a cor é o único sinal que o
    ícone tem.
    """
    base = np.array(cor, float)
    arr = np.zeros((S, S, 4), float)
    cx, cy, rx, ry = 256, 272, 128, 182
    m = mascara_ovo(cx, cy, rx, ry)
    _por(arr, m, esfera(cx, cy, rx, ry, tuple(np.clip(base * 0.45 + 126, 0, 255)),
                        tuple(np.clip(base * 0.22 + 206, 0, 255)), claro=0.34))

    rng = np.random.default_rng(11)
    yy, xx = np.mgrid[0:S, 0:S]
    # Menos manchas e maiores: a 16 px, muita mancha pequena vira uma textura cinza uniforme. E
    # nenhuma encosta no contorno (`dentro`): mancha escura na borda apaga um pedaço da silhueta, e
    # a 16 px a silhueta de ovo é metade do que faz o ícone ser reconhecido.
    dentro = mascara_ovo(cx, cy, rx - 16, ry - 20)
    for _ in range(11):
        mx = rng.integers(cx - 92, cx + 92)
        my = rng.integers(cy - 136, cy + 136)
        mancha = mascara_elipse(S, S, mx, my, rng.integers(26, 54), rng.integers(22, 46)) & dentro
        arr[..., :3][mancha] = arr[..., :3][mancha] * 0.34 + base * 0.58
    # casca: ondulação larga. Ruído fino vira sujeira ao reduzir para 64 px.
    arr[..., :3][m] += (np.sin(xx / 23.0) * np.cos(yy / 19.0) * 5.0)[m][:, None]
    return _imagem(arr)


def dna(cor):
    """Tubo de ensaio com rolha, o líquido na cor da espécie e a hélice dentro dele."""
    arr = np.zeros((S, S, 4), float)
    base = np.array(cor, float)
    w, topo, fundo = 150, 104, 374
    x0 = 256 - w // 2
    yy, xx = np.mgrid[0:S, 0:S]

    tubo = (((np.abs(xx - 256) <= w / 2) & (yy >= topo) & (yy <= fundo))
            | mascara_elipse(S, S, 256, fundo, w / 2, 54))
    _por(arr, tubo, _coluna(cyl_shade(w, (204, 216, 226), (255, 255, 255)), x0))

    lw = w - 26
    liq = tubo & (yy >= 198) & (np.abs(xx - 256) <= lw / 2)
    _por(arr, liq, _coluna(cyl_shade(lw, tuple(np.clip(base * 0.75 + 26, 0, 255)),
                                     tuple(np.clip(base * 0.45 + 186, 0, 255))), 256 - lw // 2))

    # hélice: duas fitas em senoide com os degraus entre elas — é o que diz "DNA" de longe
    clara = np.clip(base * 0.30 + 210, 0, 255)
    for passo in range(214, 376, 6):
        a = np.sin((passo - 214) / 162.0 * np.pi * 3.2) * 40
        if abs(a) > 11:
            degrau = (np.abs(yy - passo) <= 2) & (np.abs(xx - 256) <= abs(a)) & liq
            arr[..., :3][degrau] = clara * 0.78
        for sinal in (1, -1):
            fita = (np.abs(xx - (256 + sinal * a)) <= 7) & (np.abs(yy - passo) <= 3) & liq
            arr[..., :3][fita] = clara

    rw = w + 22
    rolha = (np.abs(xx - 256) <= rw / 2) & (yy >= 62) & (yy < 118)
    _por(arr, rolha, _coluna(cyl_shade(rw, (96, 76, 58), (196, 170, 142)), 256 - rw // 2))

    # reflexo do vidro por cima de tudo, à esquerda
    brilho = tubo & (np.abs(xx - (x0 + 24)) <= 9) & (yy > 130) & (yy < 350)
    arr[..., :3][brilho] = np.clip(arr[..., :3][brilho] * 0.40 + 200, 0, 255)
    return _imagem(arr)


def gerar(destino, previews, especies):
    """Escreve os ícones e a prévia em faixa. Devolve os nomes de textura para o atlas de itens."""
    nomes = {}
    f, ov = fossil(), ovo_sintetico()
    salvar(f, f"{destino}/fossil.png")
    salvar(ov, f"{destino}/ovo_sintetico.png")
    nomes["joao_fossil"] = "textures/items/fossil"
    nomes["joao_ovo_sintetico"] = "textures/items/ovo_sintetico"

    amostras = [f, ov]
    for e in especies:
        d, o = dna(e.cor), ovo(e.cor)
        salvar(d, f"{destino}/dna_{e.id}.png")
        salvar(o, f"{destino}/ovo_{e.id}.png")
        nomes[f"joao_dna_{e.id}"] = f"textures/items/dna_{e.id}"
        nomes[f"joao_ovo_{e.id}"] = f"textures/items/ovo_{e.id}"
        amostras += [d, o]

    if previews:
        faixa(amostras, f"{previews}/dino_itens.png")
    return nomes
