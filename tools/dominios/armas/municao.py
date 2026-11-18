import sys
import numpy as np
from PIL import Image

from nucleo.icones import S, contorno, cyl_shade, faixa, salvar

OUT = sys.argv[1]
PREV = sys.argv[2] if len(sys.argv) > 2 else None

def cartucho(img, cx, top, w, case_h, bullet_h, neck=0.0):
    arr = np.array(img).astype(float)
    brass = cyl_shade(w, (196, 150, 62), (255, 240, 190))
    copper = cyl_shade(w, (176, 98, 56), (255, 210, 170))
    x0 = cx - w // 2
    # ogiva
    for yy in range(bullet_h):
        t = yy / bullet_h
        half = int(w / 2 * (np.sin(t * np.pi / 2) ** 0.7)) if t < 1 else w // 2
        half = max(1, half)
        y = top + yy
        cols = copper[w // 2 - half: w // 2 + half]
        arr[y, cx - half: cx + half, :3] = cols
        arr[y, cx - half: cx + half, 3] = 255
    # pescoço (fuzil)
    y = top + bullet_h
    if neck:
        nh = int(case_h * 0.12)
        for yy in range(nh):
            half = int(w / 2 * (0.78 + 0.22 * yy / nh))
            arr[y + yy, cx - half: cx + half, :3] = brass[w // 2 - half: w // 2 + half]
            arr[y + yy, cx - half: cx + half, 3] = 255
        y += nh
        case_h -= nh
    arr[y:y + case_h, x0:x0 + w, :3] = brass[None, :, :]
    arr[y:y + case_h, x0:x0 + w, 3] = 255
    # sulco do extrator e base
    g = int(case_h * 0.9)
    arr[y + g: y + g + max(2, w // 12), x0:x0 + w, :3] *= 0.55
    arr[y + case_h - max(3, w // 10): y + case_h, x0 - 2:x0 + w + 2, :3] = brass[None, np.linspace(0, w - 1, w + 4).astype(int), :] * 0.85
    arr[y + case_h - max(3, w // 10): y + case_h, x0 - 2:x0 + w + 2, 3] = 255
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")

def dardo(img, cx, top, w, corpo_h, penacho_h, agulha_h):
    """Dardo tranquilizante: penacho laranja, corpo de alumínio com o líquido à mostra e agulha fina.
    Não sai do cartucho(): não tem ogiva de latão nem sulco de extrator — é uma seringa com cauda."""
    arr = np.array(img).astype(float)
    aluminio = cyl_shade(w, (150, 156, 164), (235, 240, 248))
    laranja = cyl_shade(w, (196, 86, 30), (255, 190, 140))
    remedio = cyl_shade(max(2, w - 10), (120, 196, 150), (220, 255, 230))
    x0, y = cx - w // 2, top
    # penacho (estabilizador): mais largo que o corpo
    pw = int(w * 1.35)
    px = cx - pw // 2
    arr[y:y + penacho_h, px:px + pw, :3] = cyl_shade(pw, (196, 86, 30), (255, 190, 140))[None, :, :]
    arr[y:y + penacho_h, px:px + pw, 3] = 255
    # corpo de alumínio
    y += penacho_h
    arr[y:y + corpo_h, x0:x0 + w, :3] = aluminio[None, :, :]
    arr[y:y + corpo_h, x0:x0 + w, 3] = 255
    # janela do sedativo (verde), no meio do corpo
    jx, jy = cx - (w - 10) // 2, y + int(corpo_h * 0.3)
    arr[jy:jy + int(corpo_h * 0.42), jx:jx + max(2, w - 10), :3] = remedio[None, :, :]
    # colar de gelatina, logo antes da agulha
    y += corpo_h
    arr[y:y + max(3, w // 7), x0 - 2:x0 + w + 2, :3] = laranja[None, np.linspace(0, w - 1, w + 4).astype(int), :] * 0.8
    arr[y:y + max(3, w // 7), x0 - 2:x0 + w + 2, 3] = 255
    # agulha
    y += max(3, w // 7)
    aw = max(4, w // 5)
    ax = cx - aw // 2
    arr[y:y + agulha_h, ax:ax + aw, :3] = cyl_shade(aw, (170, 174, 180), (245, 248, 255))[None, :, :]
    arr[y:y + agulha_h, ax:ax + aw, 3] = 255
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


# Munição de pistola: 3 cartuchos 9mm curtos
p = Image.new("RGBA", (S, S), (0, 0, 0, 0))
for i, cx in enumerate((150, 256, 362)):
    p = cartucho(p, cx, 150 + (i % 2) * 20, 84, 170, 90)
p = contorno(p)
salvar(p, f"{OUT}/municao_pistola.png")

# Munição de fuzil: 2 cartuchos longos com pescoço
r = Image.new("RGBA", (S, S), (0, 0, 0, 0))
for cx in (195, 317):
    r = cartucho(r, cx, 40, 78, 300, 140, neck=1)
r = contorno(r)
salvar(r, f"{OUT}/municao_fuzil.png")
# Munição de sniper: 2 cartuchos .338 (mais longos e grossos, ogiva comprida)
sn = Image.new("RGBA", (S, S), (0, 0, 0, 0))
for cx in (190, 322):
    sn = cartucho(sn, cx, 18, 96, 336, 158, neck=1)
sn = contorno(sn)
salvar(sn, f"{OUT}/municao_sniper.png")

# Dardo tranquilizante: 2 dardos (penacho laranja, corpo de alumínio, agulha)
dt = Image.new("RGBA", (S, S), (0, 0, 0, 0))
for cx in (190, 322):
    dt = dardo(dt, cx, 40, 76, 230, 70, 120)
dt = contorno(dt)
salvar(dt, f"{OUT}/dardo.png")

if PREV:
    faixa((p, r, sn, dt), f"{PREV}/municao.png")
print("ok")
