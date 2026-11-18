"""Ícones de item: desenho 2D procedural em 512 px, reduzido para 64.

Os ícones do modpack não são pixel art. São desenhados grandes, com o volume **pintado**, e só então
reduzidos com LANCZOS — o mesmo princípio das texturas 3D das armas, e pelo mesmo motivo: o Minecraft
não dá brilho nem sombra a um ícone de inventário, então o que não estiver pintado não existe.
"""
import numpy as np
from PIL import Image

S = 512   # lado da tela de desenho


def tela(lado=S):
    return Image.new("RGBA", (lado, lado), (0, 0, 0, 0))


def cyl_shade(w, base, hi):
    """Uma coluna de cores que faz uma faixa de `w` pixels parecer um cilindro iluminado da esquerda.

    `base` é a cor do material e `hi` o brilho especular. É o que dá volume a tudo que é tubo: cano,
    cartucho, agulha, tubo de ensaio."""
    x = np.linspace(-1, 1, w)
    l = np.clip(0.55 + 0.45 * np.cos((x + 0.35) * 1.4), 0, 1) ** 1.2
    spec = np.exp(-((x + 0.45) / 0.12) ** 2) * 0.6
    base = np.array(base, float)
    hi = np.array(hi, float)
    return np.clip(base * (0.35 + 0.65 * l)[:, None] + hi * spec[:, None], 0, 255)


def esfera(cx, cy, rx, ry, base, hi, claro=0.38, lado=S):
    """Campo de cor (lado, lado, 3) de um corpo arredondado centrado em (cx, cy).

    Os raios têm de ser os do objeto, não os da imagem: é a curvatura que dá o volume, e uma esfera
    do tamanho da tela inteira deixa o desenho chapado. Fora da elipse o valor não importa — quem
    recorta é a máscara de quem chama."""
    yy, xx = np.mgrid[0:lado, 0:lado]
    nx = (xx - cx) / rx
    ny = (yy - cy) / ry
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    luz = (-0.45, -0.55, 0.70)
    l = np.clip(nx * luz[0] + ny * luz[1] + nz * luz[2], 0, 1)
    spec = np.exp(-(((nx + 0.42) ** 2 + (ny + 0.48) ** 2) / 0.045)) * claro
    base = np.array(base, float)
    hi = np.array(hi, float)
    return np.clip(base * (0.32 + 0.78 * l)[..., None] + hi * spec[..., None], 0, 255)


def mascara_elipse(lado, _alt, cx, cy, rx, ry):
    """Máscara elíptica. A assinatura carrega `lado` duas vezes por compatibilidade com o uso
    antigo (largura, altura) — as telas aqui são sempre quadradas."""
    yy, xx = np.mgrid[0:lado, 0:lado]
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1


def mascara_ovo(cx, cy, rx, ry, bojo=0.20, lado=S):
    """Máscara de ovo de verdade: as duas pontas fecham e o bojo fica **abaixo** do meio.

    Uma elipse simples vira bola e um perfil de raio constante vira copo — os dois erros aparecem na
    hora, porque todo mundo sabe de cor o formato de um ovo."""
    yy, xx = np.mgrid[0:lado, 0:lado]
    v = (yy - cy) / ry                                  # -1 no topo, +1 na base
    raio = rx * np.sqrt(np.clip(1 - v ** 2, 0, 1)) * (1 + bojo * v)
    return (np.abs(xx - cx) <= raio) & (np.abs(v) <= 1)


def mascara_pedra(cx, cy, raio, rugas=7, forca=0.16, semente=3, lado=S):
    """Máscara de uma pedra: círculo com o raio ondulado, para não parecer um seixo de desenho."""
    rng = np.random.default_rng(semente)
    fases = rng.uniform(0, 2 * np.pi, rugas)
    pesos = rng.uniform(0.4, 1.0, rugas)
    yy, xx = np.mgrid[0:lado, 0:lado]
    ang = np.arctan2(yy - cy, xx - cx)
    d = np.hypot(xx - cx, yy - cy)
    onda = sum(p * np.cos((k + 2) * ang + f) for k, (f, p) in enumerate(zip(fases, pesos)))
    return d <= raio * (1 + forca * onda / rugas * 2)


def contorno(img, cor=(40, 28, 10, 255)):
    """Linha escura de 1 px em volta do desenho. Sem ela, um ícone claro some no fundo do inventário."""
    a = np.array(img)
    alpha = a[..., 3] > 0
    edge = np.zeros_like(alpha)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        edge |= np.roll(np.roll(alpha, dx, 1), dy, 0)
    out = a.copy()
    out[edge & ~alpha] = cor
    return Image.fromarray(out, "RGBA")


def salvar(img, caminho, lado=64):
    img.resize((lado, lado), Image.LANCZOS).save(caminho)


def faixa(imagens, destino, lado=128, fundo=(139, 139, 139, 255)):
    """Prévia com os ícones lado a lado, no cinza do inventário, para julgar os quatro de uma vez."""
    prev = Image.new("RGBA", (len(imagens) * (lado + 2), lado + 2), fundo)
    for i, im in enumerate(imagens):
        prev.alpha_composite(im.resize((lado, lado), Image.LANCZOS), (i * (lado + 2), 1))
    prev.save(destino)
    return prev
