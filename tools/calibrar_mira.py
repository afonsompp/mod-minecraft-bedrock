"""Mede o desalinhamento da mira com luneta e devolve o AGACHADO corrigido.

Uso: python tools/calibrar_mira.py quadro.png [arma]
  quadro.png = um quadro do jogo com a luneta ativa (agachado, arma com `luneta=True`).

O painel da luneta é o instrumento mais preciso que temos para medir a câmera agachada: ele fica a ~1,7
unidades do olho, contra 7,5 da AK, então amplia qualquer resíduo umas 4 vezes. O círculo deveria estar
exatamente no centro da tela (é por ele que o jogador mira, e o tiro sai sempre do centro da tela).

Mede: centro e diâmetro do furo -> deslocamento (direita, cima, frente) da arma em relação ao esperado.
Esse deslocamento é o erro do AGACHADO, e o script imprime o valor corrigido para colar em gerar.py.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar as G
import modelos

QUADRO = sys.argv[1]
ARMA = sys.argv[2] if len(sys.argv) > 2 else "awp"

im = Image.open(QUADRO).convert("RGB")
a = np.asarray(im).astype(int)
h, w = a.shape[:2]

# o painel é preto; o furo é tudo o que não é preto. A cruz do retículo corta o furo em quatro, por isso
# o fechamento morfológico antes de procurar a região.
claro = ndimage.binary_closing(a.max(2) > 45, np.ones((25, 25)))
lab, n = ndimage.label(claro)
melhor = None
for i in range(1, n + 1):
    ys, xs = np.nonzero(lab == i)
    if len(ys) < 20000 or xs.min() <= 2 or xs.max() >= w - 3 or ys.min() <= 2 or ys.max() >= h - 3:
        continue                                    # descarta HUD e o que vaza pela borda
    if melhor is None or len(ys) > melhor[0]:
        melhor = (len(ys), xs, ys)
if melhor is None:
    raise SystemExit("não achei o furo da luneta: o quadro é de alguém agachado com a arma na mira?")
_, xs, ys = melhor
cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
diam = ((xs.max() - xs.min()) + (ys.max() - ys.min())) / 2
razao = (xs.max() - xs.min()) / (ys.max() - ys.min())

# o que era esperado
corpo, maos, info, tipo = modelos.build(ARMA)
cfg = G.PLACE[ARMA]
pl = G.painel_luneta(cfg, info)
d_esp = cfg["olho"] - 1.25 * G.ESCALA                 # distância do painel ao olho (unid. de câmera)
diam_esp = G.MIRA_CIRCULO * h

# posição real do centro do painel, em unidades de câmera
z = d_esp * diam_esp / diam                           # menor na tela = mais longe
meia_tela = np.tan(np.radians(G.VFOV / 2))
x = z * (cx - w / 2) / (h / 2) * meia_tela
y = z * -(cy - h / 2) / (h / 2) * meia_tela
resto = np.array([x, y, z - d_esp])

print(f"furo: {xs.max()-xs.min()} x {ys.max()-ys.min()} px (redondo = 1,00: {razao:.3f})")
print(f"centro ({cx:.0f}, {cy:.0f}) | centro da tela ({w//2}, {h//2})")
print(f"desvio: {np.degrees(np.arctan2(x, z)):+.2f}° na horizontal, {np.degrees(np.arctan2(y, z)):+.2f}° na vertical")
print(f"tamanho: {diam/diam_esp:.3f} do esperado -> painel a {z:.3f} em vez de {d_esp:.3f}")
print(f"\nerro da arma (direita, cima, frente): {np.round(resto, 3)}")
print(f"AGACHADO = {[round(float(v), 3) for v in np.array(G.AGACHADO) - resto]}")
