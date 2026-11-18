"""Animações do bicho, declaradas como **poses** e derivadas daí.

A regra que mantém prévia e jogo honestos: os quadros-chave são escritos uma vez, em Python, e dali
saem as **duas** coisas — o JSON de animação do Bedrock e a interpolação que a prévia usa. Não há
como divergirem, porque não existe uma segunda fonte.

Só interpolação linear, de propósito: suavidade vem de **mais quadros**, resolvidos exatos, e não de
`lerp_mode: catmullrom`. Assim a prévia não precisa reimplementar a curva do motor do jogo — é o
mesmo caminho que o `caminho_mira()` das armas já seguia.
"""
from typing import NamedTuple

from nucleo.esqueleto import Transf


class Quadro(NamedTuple):
    t: float            # 0..1, fração do ciclo
    pose: dict          # {osso: Transf} — só os ossos que se mexem


class Clipe(NamedTuple):
    nome: str
    duracao: float      # segundos do ciclo
    quadros: list
    loop: bool = True
    tempo: str | None = None    # anim_time_update (ex.: andar pelo passo, não pelo relógio)


def _t(rot=(0.0, 0.0, 0.0), pos=(0.0, 0.0, 0.0)):
    return Transf(rot, pos)


def _perna(dianteira, coxa, canela, pe):
    """Mesma perna, os dois lados, defasados meio ciclo — quem defasa é o chamador."""
    lado = "_d" if dianteira else "_e"
    return {f"coxa{lado}": _t((coxa, 0, 0)), f"canela{lado}": _t((canela, 0, 0)),
            f"pe{lado}": _t((pe, 0, 0))}


def _passada(fase, amplitude, altura):
    """Um instante da passada: o ângulo de cada junta da perna direita, em graus.

    `fase` 0 = pé plantado à frente, 0.5 = pé no ar atrás. Os valores saem de olhar um bípede: a
    coxa oscila em volta do repouso, o joelho dobra no recuo e o pé acompanha para não arrastar."""
    import math
    a = 2 * math.pi * fase
    coxa = math.cos(a) * amplitude
    canela = max(0.0, -math.cos(a)) * amplitude * 1.5 + math.sin(a) * amplitude * 0.35
    pe = -coxa * 0.55 - canela * 0.45 + math.sin(a) * altura
    return coxa, canela, pe


def _ciclo_andar(nome, duracao, amplitude, altura, balanco, inclinacao, quadros=8, tempo=None):
    """Monta um ciclo de caminhada completo: pernas alternadas, cauda e corpo contrabalançando."""
    import math
    qs = []
    for i in range(quadros + 1):
        f = i / quadros
        pose = {}
        for lado, defasagem in (("_d", 0.0), ("_e", 0.5)):
            coxa, canela, pe = _passada((f + defasagem) % 1.0, amplitude, altura)
            pose[f"coxa{lado}"] = _t((coxa, 0, 0))
            pose[f"canela{lado}"] = _t((canela, 0, 0))
            pose[f"pe{lado}"] = _t((pe, 0, 0))
        giro = math.sin(2 * math.pi * f) * balanco
        pose["quadril"] = _t((0, giro * 0.6, 0), (0, abs(math.sin(2 * math.pi * f)) * altura * 0.06, 0))
        pose["corpo"] = _t((inclinacao, -giro * 0.4, 0))
        pose["cauda1"] = _t((0, -giro * 1.6, 0))
        pose["cauda2"] = _t((0, -giro * 1.9, 0))
        pose["cauda3"] = _t((0, -giro * 2.1, 0))
        pose["pescoco"] = _t((0, giro * 0.8, 0))
        qs.append(Quadro(f, pose))
    return Clipe(nome, duracao, qs, tempo=tempo)


def clipes():
    """Os cinco clipes do bicho. Acrescentar um é acrescentar uma entrada aqui."""
    import math
    # ---- parado: respira e olha em volta. Amplitude pequena; bicho parado não gesticula. ----
    parado = []
    for i in range(9):
        f = i / 8
        r = math.sin(2 * math.pi * f)
        parado.append(Quadro(f, {
            "corpo": _t((r * 1.2, 0, 0)),
            "peito": _t((r * 0.8, 0, 0)),
            "pescoco": _t((-r * 1.6, math.sin(2 * math.pi * f + 1.1) * 4.0, 0)),
            "cabeca": _t((r * 1.4, math.sin(2 * math.pi * f + 2.2) * 5.0, 0)),
            "cauda1": _t((r * 0.9, math.sin(2 * math.pi * f + 0.7) * 3.0, 0)),
            "cauda2": _t((0, math.sin(2 * math.pi * f + 1.4) * 4.0, 0)),
            "cauda3": _t((0, math.sin(2 * math.pi * f + 2.1) * 5.0, 0)),
        }))

    # ---- ataque: recua, avança e abocanha. Não é ciclo: acontece uma vez. ----
    ataque = [
        Quadro(0.0, {}),
        Quadro(0.22, {"pescoco": _t((10, 0, 0)), "cabeca": _t((-6, 0, 0)), "mandibula": _t((8, 0, 0)),
                      "corpo": _t((3, 0, 0))}),
        Quadro(0.48, {"pescoco": _t((-22, 0, 0)), "cabeca": _t((12, 0, 0)), "mandibula": _t((34, 0, 0)),
                      "corpo": _t((-6, 0, 0)), "peito": _t((-4, 0, 0))}),
        Quadro(0.62, {"pescoco": _t((-14, 0, 0)), "cabeca": _t((8, 0, 0)), "mandibula": _t((2, 0, 0)),
                      "corpo": _t((-3, 0, 0))}),
        Quadro(1.0, {}),
    ]

    # ---- dormir: deita de verdade. É o que a família joao:sedavel promete desde a v1.7.0. ----
    deitado = {
        "quadril": _t((0, 0, 0), (0, -9.5, 0)),
        "corpo": _t((4, 0, 0)),
        "peito": _t((3, 0, 0)),
        "pescoco": _t((36, 0, -22)),
        "cabeca": _t((-24, 0, 0)),
        "coxa_d": _t((-52, 0, 0)), "canela_d": _t((104, 0, 0)), "pe_d": _t((-52, 0, 0)),
        "coxa_e": _t((-52, 0, 0)), "canela_e": _t((104, 0, 0)), "pe_e": _t((-52, 0, 0)),
        "cauda1": _t((2, 16, 0)), "cauda2": _t((0, 20, 0)), "cauda3": _t((0, 18, 0)),
    }
    dormir = []
    for i in range(5):
        f = i / 4
        r = math.sin(2 * math.pi * f) * 0.9      # respiração lenta de bicho apagado
        pose = dict(deitado)
        pose["corpo"] = _t((4 + r, 0, 0))
        pose["pescoco"] = _t((36 - r * 0.6, 0, -22))
        dormir.append(Quadro(f, pose))

    return [
        Clipe("parado", 4.2, parado),
        # o tempo vem da distância andada, não do relógio: assim o passo nunca patina
        _ciclo_andar("andar", 1.0, 26.0, 2.6, 5.0, 1.5,
                     tempo="q.modified_distance_moved * 0.33"),
        _ciclo_andar("correr", 1.0, 42.0, 4.4, 8.0, 7.0,
                     tempo="q.modified_distance_moved * 0.22"),
        Clipe("atacar", 0.8, ataque, loop=False),
        Clipe("dormir", 6.0, dormir),
    ]


def amostra(clipe, t):
    """A pose do clipe no instante `t` (0..1), interpolada linearmente — igual ao que o jogo faz.

    É esta função que as prévias usam. Como o JSON sai dos mesmos quadros, prévia e jogo não têm
    como discordar."""
    qs = clipe.quadros
    if t <= qs[0].t:
        return dict(qs[0].pose)
    for a, b in zip(qs, qs[1:]):
        if t <= b.t:
            u = 0.0 if b.t == a.t else (t - a.t) / (b.t - a.t)
            fora = {}
            for nome in set(a.pose) | set(b.pose):
                ta = a.pose.get(nome, Transf())
                tb = b.pose.get(nome, Transf())
                fora[nome] = Transf(
                    tuple(x + (y - x) * u for x, y in zip(ta.rot, tb.rot)),
                    tuple(x + (y - x) * u for x, y in zip(ta.pos, tb.pos)),
                    tuple(x + (y - x) * u for x, y in zip(ta.escala, tb.escala)))
            return fora
    return dict(qs[-1].pose)


def bedrock(clipe, especie):
    """O JSON Bedrock do clipe — um despejo dos mesmos quadros, sem nenhuma decisão nova."""
    ossos = {}
    for q in clipe.quadros:
        for nome, t in q.pose.items():
            alvo = ossos.setdefault(nome, {})
            tempo = round(q.t * clipe.duracao, 4)
            if any(abs(v) > 1e-9 for v in t.rot) or "rotation" in alvo:
                alvo.setdefault("rotation", {})[str(tempo)] = [round(v, 3) for v in t.rot]
            if any(abs(v) > 1e-9 for v in t.pos) or "position" in alvo:
                alvo.setdefault("position", {})[str(tempo)] = [round(v, 3) for v in t.pos]
    # um osso que só aparece em alguns quadros precisa de valor nos demais, senão o jogo segura o
    # último e a pose "vaza" para fora do trecho em que foi escrita
    for nome, canais in ossos.items():
        for canal, quadros in canais.items():
            for q in clipe.quadros:
                quadros.setdefault(str(round(q.t * clipe.duracao, 4)),
                                   [0.0, 0.0, 0.0])
            canais[canal] = {k: quadros[k] for k in sorted(quadros, key=float)}

    saida = {"loop": bool(clipe.loop), "animation_length": clipe.duracao, "bones": ossos}
    if clipe.tempo:
        saida["anim_time_update"] = clipe.tempo
    return f"animation.joao.{especie}.{clipe.nome}", saida
