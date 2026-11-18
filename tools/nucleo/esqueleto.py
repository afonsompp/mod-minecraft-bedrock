"""Esqueleto articulado: hierarquia de ossos, pose de repouso e composição para as prévias.

Até a v1.8.0 o projeto só tinha hierarquia de **um nível**: um osso raiz e filhos diretos (a arma e
a corda da besta). Um bicho precisa de quadril → corpo → pescoço → cabeça e coxa → canela → pé, e
isso trouxe três decisões que valem como regra:

1. **O osso nunca leva `rotation` no JSON.** A pose de repouso é declarada aqui, em Python, e
   **assada nos cubos** (`assar`). O motivo é concreto: `origin`/`size` de um cubo são espaço do
   **modelo**, e é de onde saem a oclusão ambiente (`_caixa`/`sdf_cubos`) e o renderizador de
   prévias. Com `rotation` no osso, o que o jogo desenha deixa de ser onde os cubos estão escritos —
   a sombra passaria a ser calculada numa pose que não existe em lugar nenhum.
2. **Por tabela, o valor da animação é o delta puro** em relação ao desenho. Sem `rotation` de osso
   não há dúvida sobre se o Bedrock pré ou pós-multiplica as duas rotações.
3. **Espelhar um membro é operação de dados** (`espelhar_x`), nunca escala negativa num osso: com o
   determinante negativo a orientação das faces inverte e o membro **some** inteiro da prévia.
"""
from typing import NamedTuple

import numpy as np

from nucleo.bt import bone_matrix, euler_from_bb, rot_bb, vec_bb


class Osso(NamedTuple):
    """Um osso do esqueleto. É uma tupla de 4 ou mais, então `build_geometry` aceita as duas formas."""

    nome: str
    pai: str | None
    pivo: tuple
    """Ponto em volta do qual o osso gira, em coordenadas **absolutas** do modelo (Bedrock)."""
    cubos: list
    repouso: tuple = (0.0, 0.0, 0.0)
    """Rotação da pose parada, **relativa ao pai**, em graus Bedrock. Assada nos cubos ao gerar."""
    grupo: str | None = None
    """Grupo de oclusão. Ossos de grupos diferentes não lançam sombra um no outro."""


class Transf(NamedTuple):
    """Um quadro-chave: o que a animação faz com um osso, relativo à pose desenhada."""

    rot: tuple = (0.0, 0.0, 0.0)
    pos: tuple = (0.0, 0.0, 0.0)
    escala: tuple = (1.0, 1.0, 1.0)


def _osso(o):
    """Aceita `Osso` ou a tupla de 4 que o resto do projeto usa."""
    return o if isinstance(o, Osso) else Osso(*o)


def ordenar(ossos):
    """Pai antes de filho, e reclama alto de nome repetido, pai inexistente ou ciclo.

    O Bedrock resolve `parent` por nome e, quando não acha, não diz nada — o osso simplesmente fica
    para trás no espaço do modelo."""
    ossos = [_osso(o) for o in ossos]
    por_nome = {}
    for o in ossos:
        if o.nome in por_nome:
            raise ValueError(f"osso repetido: {o.nome}")
        por_nome[o.nome] = o
    saida, visto = [], {}

    def visitar(o):
        estado = visto.get(o.nome)
        if estado == 2:
            return
        if estado == 1:
            raise ValueError(f"ciclo de ossos em {o.nome}")
        visto[o.nome] = 1
        if o.pai is not None:
            if o.pai not in por_nome:
                raise ValueError(f"osso {o.nome}: pai '{o.pai}' não existe")
            visitar(por_nome[o.pai])
        visto[o.nome] = 2
        saida.append(o)

    for o in ossos:
        visitar(o)
    return saida


def matrizes(ossos, pose=None):
    """Matriz 4x4 (espaço bb) de cada osso, com a cadeia pai→filho já composta.

    Compõe **primeiro o repouso, depois a pose**: as duas giram em torno do mesmo pivô, então o
    produto das duas matrizes é a rotação composta em torno dele. Num esqueleto já achatado o
    repouso é identidade e sobra só a pose, que é o caso das prévias de animação."""
    pose = pose or {}
    fora = {}
    for o in ordenar(ossos):
        M = bone_matrix(o.pivo, o.repouso)
        t = pose.get(o.nome)
        if t is not None:
            M = M @ bone_matrix(o.pivo, t.rot, t.pos)
            if tuple(t.escala) != (1.0, 1.0, 1.0):
                P = vec_bb(o.pivo)
                S = np.eye(4)
                S[:3, :3] = np.diag(t.escala)
                S[:3, 3] = P - np.diag(t.escala) @ P
                M = M @ S
        fora[o.nome] = (fora[o.pai] @ M) if o.pai else M
    return fora


def vistas(ossos, pose, camera):
    """`{nome: callable(pts_bb) -> pts_camera}`, pronto para o `render`.

    O renderizador recebe um callable independente por osso e **não** compõe hierarquia sozinho —
    quem compõe é isto."""
    ms = matrizes(ossos, pose)

    def fazer(M):
        R, t = M[:3, :3], M[:3, 3]
        return lambda q: camera(np.asarray(q, float) @ R.T + t)

    return {nome: fazer(M) for nome, M in ms.items()}


def assar(cubos, M, pivo_osso):
    """Aplica a transformação `M` (4x4, bb) aos cubos, devolvendo cubos Bedrock equivalentes.

    A conta cabe num único cubo porque rotação de cubo já existe no formato:

        P' = M·P_c          novo pivô
        R' = M_R · R_c      nova rotação
        o' = o + (P' − P_c) a caixa alinhada ANDA; quem gira é o par (rotation, pivot)

    Identidade devolve os cubos intactos — é isso que mantém as armas byte-idênticas."""
    MR, Mt = M[:3, :3], M[:3, 3]
    identidade = np.allclose(M, np.eye(4), atol=1e-12)
    out = []
    for c in cubos:
        if identidade:
            out.append(c)
            continue
        p_bed = np.array(c.get("p", pivo_osso), float)
        Pc = vec_bb(p_bed)
        Rc = rot_bb(c["r"]) if "r" in c else np.eye(3)
        d = vec_bb((MR @ Pc + Mt) - Pc)          # deslocamento, de volta ao espaço Bedrock
        n = dict(c)
        n["o"] = tuple(np.array(c["o"], float) + d)
        n["p"] = tuple(p_bed + d)
        n["r"] = tuple(euler_from_bb(MR @ Rc))
        out.append(n)
    return out


def achatar(ossos):
    """Resolve a pose de repouso: devolve ossos com `repouso` zerado e os cubos já no lugar.

    Depois disto, o que está escrito nos cubos **é** o que o jogo desenha — que é a condição para a
    oclusão ambiente e as prévias dizerem a verdade, e para o valor de um quadro-chave ser o delta
    puro em relação ao desenho."""
    ms = matrizes(ossos)
    fora = []
    for o in ordenar(ossos):
        M = ms[o.nome]
        pivo = tuple(vec_bb(M[:3, :3] @ vec_bb(o.pivo) + M[:3, 3]))
        fora.append(o._replace(cubos=assar(o.cubos, M, o.pivo), pivo=pivo, repouso=(0.0, 0.0, 0.0)))
    return fora


def espelhar_x(cubos):
    """O mesmo membro do outro lado. Nega X nos dados — nunca com escala negativa num osso."""
    out = []
    for c in cubos:
        n = dict(c)
        n["o"] = (-(c["o"][0] + c["s"][0]), c["o"][1], c["o"][2])
        if "r" in c:
            n["r"] = (c["r"][0], -c["r"][1], -c["r"][2])
            n["p"] = (-c["p"][0], c["p"][1], c["p"][2])
        out.append(n)
    return out
