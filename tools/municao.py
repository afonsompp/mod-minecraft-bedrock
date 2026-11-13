import sys
import numpy as np
from PIL import Image, ImageDraw
OUT = sys.argv[1]
PREV = sys.argv[2] if len(sys.argv) > 2 else None
S = 512

def cyl_shade(w, base, hi):
    x = np.linspace(-1, 1, w)
    l = np.clip(0.55 + 0.45 * np.cos((x + 0.35) * 1.4), 0, 1) ** 1.2
    spec = np.exp(-((x + 0.45) / 0.12) ** 2) * 0.6
    base = np.array(base, float); hi = np.array(hi, float)
    return np.clip(base * (0.35 + 0.65 * l)[:, None] + hi * spec[:, None], 0, 255)

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

def contorno(img):
    a = np.array(img)
    alpha = a[..., 3] > 0
    edge = np.zeros_like(alpha)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        edge |= np.roll(np.roll(alpha, dx, 1), dy, 0)
    out = a.copy()
    m = edge & ~alpha
    out[m] = (40, 28, 10, 255)
    return Image.fromarray(out, "RGBA")

# Munição de pistola: 3 cartuchos 9mm curtos
p = Image.new("RGBA", (S, S), (0, 0, 0, 0))
for i, cx in enumerate((150, 256, 362)):
    p = cartucho(p, cx, 150 + (i % 2) * 20, 84, 170, 90)
p = contorno(p)
p.resize((64, 64), Image.LANCZOS).save(f"{OUT}/municao_pistola.png")

# Munição de fuzil: 2 cartuchos longos com pescoço
r = Image.new("RGBA", (S, S), (0, 0, 0, 0))
for cx in (195, 317):
    r = cartucho(r, cx, 40, 78, 300, 140, neck=1)
r = contorno(r)
r.resize((64, 64), Image.LANCZOS).save(f"{OUT}/municao_fuzil.png")
prev = Image.new("RGBA", (260, 130), (139, 139, 139, 255))
prev.alpha_composite(p.resize((128, 128), Image.LANCZOS), (0, 1)); prev.alpha_composite(r.resize((128, 128), Image.LANCZOS), (130, 1))
if PREV:
    prev.save(f"{PREV}/municao.png")
print("ok")
