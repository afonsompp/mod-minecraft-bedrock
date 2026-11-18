"""Fonte única das armas do modpack.

Até a v1.7.1 a mesma lista se repetia em sete lugares — `modelos.ARMAS`, o laço do `attachables.py`,
os `NOMES`, o `PLACE`, a condição Molang do `pose.py`, a ordem do site e os alvos do `ajuste.py` — e
cada arma nova obrigava a lembrar de todos. Aqui cada arma é **uma entrada**, e quem precisa da lista
importa daqui.

Arma nova = a função de modelo em `modelos.py` + uma linha em `ARMAS`.
"""
from dataclasses import dataclass
from typing import Callable

import numpy as np

from dominios.armas import modelos


@dataclass(frozen=True)
class Arma:
    """Tudo o que o resto do projeto precisa saber sobre uma arma."""

    id: str
    """Sem o namespace: `glock` vira o item `joao:glock`, a geometria `geometry.joao.glock` etc."""

    nome: str
    """Como aparece na tela do jogo e no site."""

    tipo: str
    """`fuzil`, `pistola`, `sniper` ou `besta`. Decide as mãos, o recuo e a pose de 3ª pessoa."""

    modelo: Callable
    """A função de `modelos.py` que desenha os cubos."""

    place: dict
    """Posição em 1ª pessoa: punho na tela (direita, cima, profundidade), ângulos, cadência e mira.

    `olho` é a distância do olho ao ponto de trás da linha de visada na pose de mira (em unidades de
    câmera, 1/16 de bloco); numa luneta, é o alívio de olho. `atirando` é a fração do caminho
    quadril → mira que a arma percorre ao atirar em pé. `intervalo` e `fov_mira` **têm de bater** com
    a tabela do `packs/BP/scripts/armas/index.js`."""

    traseira: float
    """Onde a traseira da arma deve cair na tela — só o `ajuste.py` usa, para resolver o `place`."""

    site: int
    """Ordem no topo do site de downloads (1 = primeiro)."""


# A ordem aqui é a ordem de geração.
ARMAS = (
    Arma("glock", "Glock", "pistola", modelos.glock, traseira=-3, site=5,
         place=dict(grip=(4.70, -3.93, 5.42), yaw=5.8, pitch=1.0, roll=-3,
                    intervalo=5, olho=2.5, atirando=0.3)),
    Arma("ak47", "AK-47", "fuzil", modelos.ak47, traseira=-6, site=4,
         place=dict(grip=(8.19, -6.12, 7.30), yaw=5.7, pitch=1.0, roll=-4,
                    intervalo=3, olho=7.5, atirando=0.45)),
    Arma("m4a4", "M4A4", "fuzil", modelos.m4a4, traseira=-6, site=3,
         place=dict(grip=(7.77, -6.09, 6.82), yaw=5.7, pitch=1.0, roll=-4,
                    intervalo=3, olho=3.5, atirando=0.45)),
    Arma("awp", "AWP", "sniper", modelos.awp, traseira=-6, site=2,
         place=dict(grip=(8.19, -6.12, 7.30), yaw=5.7, pitch=1.0, roll=-4,
                    intervalo=25, olho=2.0, atirando=0.3)),
    # Besta: ciclo de 0,75 s (a corda volta nesse tempo) e luneta de média distância, com zoom
    # moderado e furo mais largo que o da AWP. Ela é larga (53 cm de ponta a ponta dos arcos): com a
    # posição dos fuzis, os arcos — que são a cara dela — ficavam fora da tela. Fica mais ao centro,
    # mais longe e com bastante toe-in, de modo que os dois lados caibam no quadro.
    Arma("besta", "Besta", "besta", modelos.besta, traseira=-6, site=1,
         place=dict(grip=(6.40, -5.50, 6.40), yaw=12.0, pitch=1.0, roll=-4,
                    intervalo=15, olho=2.0, atirando=0.3, fov_mira=40.0)),
)

POR_ID = {a.id: a for a in ARMAS}
IDS = tuple(a.id for a in ARMAS)


def do_tipo(*tipos):
    """Os ids das armas de um ou mais tipos, na ordem de geração."""
    return tuple(a.id for a in ARMAS if a.tipo in tipos)


def por_site():
    """As armas na ordem em que aparecem no topo do site."""
    return sorted(ARMAS, key=lambda a: a.site)


def build(nome):
    """Desenha a arma e devolve `(corpo, maos, info, tipo)` com tudo relativo ao **punho**.

    As funções de `modelos.py` trabalham em coordenadas de projeto; aqui tudo é transladado para que
    `info["grip"]` seja a origem, e os pontos de referência ganham a versão `_rel`."""
    arma = POR_ID[nome]
    corpo, info = arma.modelo()
    g = np.array(info["grip"], float)

    def shift(cs):
        out = []
        for c in cs:
            c = dict(c)
            c["o"] = tuple(np.array(c["o"]) - g)
            if "p" in c:
                c["p"] = tuple(np.array(c["p"]) - g)
            out.append(c)
        return out

    info = dict(info)
    info["muzzle_rel"] = tuple(np.array(info["muzzle"]) - g)
    if "handguard" in info:
        info["handguard_rel"] = tuple(np.array(info["handguard"]) - g)
    # linha de visada (trás, frente): para luneta, centro da ocular -> centro da objetiva
    info["visada_rel"] = tuple(tuple(np.array(v) - g) for v in info["visada"])
    if "alca_pivo" in info:
        info["alca_pivo_rel"] = tuple(np.array(info["alca_pivo"]) - g)
    # ossos animados do modelo (corda, dardo...): só o pivô muda de referencial
    info["ossos_rel"] = {n: dict(o, pivo=tuple(np.array(o["pivo"]) - g))
                         for n, o in info.get("ossos", {}).items()}
    return shift(corpo), modelos.maos(info, arma.tipo), info, arma.tipo
