"""Matemática de transformações de ossos do Bedrock (convertida para espaço Blockbench, destro).

Convenção (verificada contra o Blockbench):
  x_bb = -x_bedrock (posições, pivôs e offsets de animação)
  R_bb = Rz(rz) · Ry(-ry) · Rx(-rx)   para rotação Bedrock [rx, ry, rz] em graus
  ponto no osso: p' = P + T + R (p - P), depois o pai.
No espaço bb: frente = -Z, direita = +X, cima = +Y.
"""
import numpy as np


def Rx(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def rot_bb(r):
    rx, ry, rz = r
    return Rz(rz) @ Ry(-ry) @ Rx(-rx)


def vec_bb(v):
    return np.array([-v[0], v[1], v[2]], dtype=float)


def bone_matrix(pivot_bed, rot_bed=(0, 0, 0), pos_bed=(0, 0, 0)):
    """Matriz 4x4 (espaço bb) do osso, relativa ao espaço do modelo do pai."""
    P = vec_bb(pivot_bed); T = vec_bb(pos_bed); R = rot_bb(rot_bed)
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = P + T - R @ P
    return M


def apply(M, p):
    return (M @ np.append(np.asarray(p, float), 1.0))[:3]


def euler_from_bb(R):
    """Encontra [rx, ry, rz] Bedrock tal que rot_bb(...) == R.
    R = Rz(c)·Ry(b)·Rx(a) com a=-rx, b=-ry, c=rz."""
    # R = Rz(c) Ry(b) Rx(a)
    b = np.degrees(np.arcsin(-R[2, 0]))
    a = np.degrees(np.arctan2(R[2, 1], R[2, 2]))
    c = np.degrees(np.arctan2(R[1, 0], R[0, 0]))
    return [-a, -b, c]
