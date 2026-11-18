"""Calibra a câmera real de 1ª pessoa (CALIB em attachables.py) a partir de um print do jogo segurando a M4A4.

Uso: python tools/dominios/armas/calibrar.py print.png BOCA_X BOCA_Y MASSA_X MASSA_Y
  BOCA = centro da boca do quebra-chama; MASSA = topo da torre da massa de mira (pixels do print).
O print precisa ser da versão ATUAL (usa o PLACE atual). Imprime o CALIB novo para colar em attachables.py
e salva <print>.fit.png (vermelho = print, verde = modelo, amarelo = os dois; azul = manga).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # para rodar o arquivo direto
import numpy as np
from PIL import Image, ImageDraw
from dominios.armas import attachables as G, modelos
from nucleo.geometria import cube_face_quads
from nucleo.bt import rot_bb
from scipy.optimize import minimize

SHOT = sys.argv[1]
SC = 4
im = Image.open(SHOT).convert('RGB')
Wg, Hg = im.size
w, h = Wg // SC, Hg // SC
a = np.asarray(im.resize((w, h), Image.BOX)).astype(int)
alvo = (a.max(2) < 80) & (np.ptp(a, 2) < 22)
cuidado = np.ones((h, w), bool)
def fora(x0, y0, x1, y1):  # HUD: não conta
    cuidado[int(y0*h):int(y1*h), int(x0*w):int(x1*w)] = False
fora(0.28, 0.88, 0.72, 1.0)   # hotbar
fora(0.44, 0.0, 0.56, 0.08)   # botões topo
fora(0.79, 0.32, 0.96, 0.68)  # botões direita
fora(0.07, 0.38, 0.23, 0.72)  # dpad
fora(0.3, 0.6, 0.7, 0.75)    # actionbar
yy, xx = np.mgrid[0:h, 0:w]
alvo &= (xx > 0.6*w) & (yy > 0.45*h)
alvo &= cuidado
Image.fromarray((alvo*255).astype(np.uint8)).save(SHOT + '.mask.png')

corpo, maos, info, tipo = modelos.build('m4a4')
cubos = [c for c in G.offset(corpo, G.PIV)] + [c for c in G.offset(maos, G.PIV) if c['m'] == 'luva']
mangas = [c for c in G.offset(maos, G.PIV) if c['m'] == 'manga']
fp = G.first_person(G.PLACE['m4a4'])
def mundo(q):
    A = G.PIV + fp['T_bb'] + (fp['R_g'] @ (G.ESCALA * (q - G.PIV).T)).T
    return G.TB + (G.R_BASE @ A.T).T
QS = [np.array([mundo(q) for q in cube_face_quads(c).values()]) for c in cubos]
QM = [np.array([mundo(q) for q in cube_face_quads(c).values()]) for c in mangas]

def camera(x):
    cam = G.CAM + x[:3]
    R = rot_bb(x[3:6]) @ G.BC
    fov = x[6]
    return cam, R, fov

def mascara(x, quads):
    cam, BC, fov = camera(x)
    fy = (h/2)/np.tan(np.radians(fov/2))
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for Q in quads:
        c = (Q - cam) @ BC
        for f in c:
            if np.any(f[:, 2] < 0.5): continue
            pts = [(w/2 + p[0]/p[2]*fy, h/2 - p[1]/p[2]*fy) for p in f]
            d.polygon(pts, fill=255)
    return np.asarray(m) > 0

from nucleo.bt import vec_bb
g = np.array(modelos.m4a4()[1]['grip'])
a_ = [float(v) for v in sys.argv[2:6]]
PONTOS = [((0, 4.25, 37), (a_[0], a_[1])), ((0, 10.5, 28.1), (a_[2], a_[3]))]
PW = np.array([mundo(vec_bb(np.array(p) - g + G.PIV)[None, :])[0] for p, _ in PONTOS])
PS = np.array([s for _, s in PONTOS]) / SC
def perda(x):
    r = mascara(x, QS); mg = mascara(x, QM) & ~r
    i = (r & alvo & cuidado).sum(); u = ((r | alvo | mg) & cuidado).sum()
    cam, BC, fov = camera(x); fy = (h/2)/np.tan(np.radians(fov/2))
    c = (PW - cam) @ BC
    if np.any(c[:, 2] < 1): return 9
    uv = np.stack([w/2 + c[:, 0]/c[:, 2]*fy, h/2 - c[:, 1]/c[:, 2]*fy], 1)
    return 1 - i/max(u, 1) + 0.5*np.mean(np.sum(((uv - PS)/w)**2, 1))*100

x0 = np.array([0, 0, 0, 0, 0, 0, G.VFOV])
print('perda atual', perda(x0))
melhor = (perda(x0), x0)
rng = np.random.default_rng(1)
inicios = [x0] + [x0 + np.r_[rng.normal(0, 6, 3), rng.normal(0, 8, 3), rng.normal(0, 8)] for _ in range(31)]
for s in inicios:
    r = minimize(perda, s, method='Nelder-Mead', options=dict(maxiter=1500, xatol=1e-2, fatol=1e-5, initial_simplex=None))
    if r.fun < melhor[0]: melhor = (r.fun, r.x); print('melhor', r.fun, np.round(r.x, 3), flush=True)
x = melhor[1]
r = minimize(perda, x, method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-3, fatol=1e-6))
x = r.x if r.fun < melhor[0] else x
print('FINAL', perda(x), json.dumps([round(float(v), 4) for v in x]))
cam, BC, fov = camera(x)
from nucleo.bt import euler_from_bb
rot = euler_from_bb(rot_bb(x[3:6]) @ rot_bb(G.CALIB[3:6]))
novo = list(np.array(G.CALIB[:3]) + x[:3]) + list(rot) + [x[6]]
print('CALIB =', json.dumps([round(float(v), 3) for v in novo]))
# sobreposição para conferência
ov = np.zeros((h, w, 3), np.uint8); ov[..., 0] = alvo*255; ov[..., 1] = mascara(x, QS)*255; ov[..., 2] = mascara(x, QM)*160
Image.blend(im.resize((w, h)), Image.fromarray(ov), 0.55).resize((w*2, h*2)).save(SHOT + '.fit.png')
np.save(SHOT + '.x.npy', x)
