"""Gera o pack_icon.png dos três packs a partir das vistas laterais renderizadas pelo gerar.py.

Uso: python3 tools/icone.py <pasta_previews>
"""
import sys
from pathlib import Path
from PIL import Image

PREV = Path(sys.argv[1])
PACKS = Path(__file__).resolve().parent.parent / "packs"

ic = Image.new("RGBA", (256, 256), (30, 34, 38, 255))
for y in range(256):
    for x in range(256):
        if (x // 32 + y // 32) % 2:
            ic.putpixel((x, y), (36, 41, 46, 255))
ak = Image.open(PREV / "lado_t_ak47.png").resize((300, 300), Image.LANCZOS)
gl = Image.open(PREV / "lado_t_glock.png").resize((140, 140), Image.LANCZOS)
ic.alpha_composite(ak, (-30, -40))
ic.alpha_composite(gl, (110, 120))
for pasta in ("BP", "RP", "POSE_RP"):
    ic.save(PACKS / pasta / "pack_icon.png")
print("ícones ok")
