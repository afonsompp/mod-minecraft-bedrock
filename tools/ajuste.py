"""Calcula a posição da arma em 1ª pessoa para que o cano e a traseira caiam em pontos-alvo da tela.

Uso: python3 tools/ajuste.py   (imprime os valores para colar em PLACE no gerar.py)
"""
import numpy as np
import modelos
from gerar import first_person, PIV, ESCALA, TB, R_BASE, CAM, BC, VFOV
from bt import vec_bb
from scipy.optimize import minimize
W,H=1300,600
fy=(H/2)/np.tan(np.radians(VFOV/2))
def screen(nome, x):
    gx,gy,gz,yaw,pitch=x
    corpo, maos, info, tipo = modelos.build(nome)
    fp=first_person(dict(grip=(gx,gy,gz),yaw=yaw,pitch=pitch,roll=-4))
    def cam(p_bed):
        q=vec_bb(np.array(p_bed)+PIV)[None,:]
        A = PIV + fp["T_bb"] + (fp["R_g"] @ (ESCALA * (q - PIV).T)).T
        Wd = TB + (R_BASE @ A.T).T
        c=((Wd - CAM) @ BC)[0]
        return np.array([W/2+c[0]/c[2]*fy, H/2-c[1]/c[2]*fy]), c
    return cam, info
def solve(nome, tm, tr, rear_z, x0):
    def f(x):
        cam,info=screen(nome,x)
        m,cm=cam(info['muzzle_rel']); r,cr=cam((0,info['muzzle_rel'][1],rear_z))
        e=np.sum(((m-tm)/W)**2)+np.sum(((r-tr)/W)**2)
        e+= 0.002*(x[3]-6)**2/36 + 0.002*(x[4]-1)**2
        if cr[2]<4: e+=10
        return e
    res=minimize(f,x0,method='Nelder-Mead',options=dict(maxiter=4000,xatol=1e-3,fatol=1e-9))
    return res.x, res.fun


if __name__ == "__main__":
    for nome, rear in (("ak47", -6), ("m4a4", -6), ("glock", -3)):
        corpo, maos, info, tipo = modelos.build(nome)
        rear_rel = rear - modelos.ARMAS[nome][0]()[1]["grip"][2]
        if tipo == "fuzil":
            tm = np.array([0.64 * W, 0.64 * H]); tr = np.array([0.93 * W, 0.97 * H])
        else:
            tm = np.array([0.66 * W, 0.66 * H]); tr = np.array([0.80 * W, 0.84 * H])
        x, fun = solve(nome, tm, tr, rear_rel, [8, -8, 15, 6, 1])
        print(f'"{nome}": dict(grip=({x[0]:.2f}, {x[1]:.2f}, {x[2]:.2f}), yaw={x[3]:.1f}, pitch={x[4]:.1f}),  # erro {fun:.2e}')
