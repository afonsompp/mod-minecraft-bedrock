"""Sintetiza sons de tiro (estampido + corpo grave + cauda/eco) e clique de arma vazia."""
import subprocess
import sys
from pathlib import Path
import numpy as np
import wave

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
SR = 44100
rng = np.random.default_rng(3)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def tiro(dur, crack_f, body_f, body_amt, tail, punch, seed):
    r = np.random.default_rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    noise = r.normal(0, 1, n)
    # estalo inicial (onda de choque): muito curto e brilhante
    crack = highpass(noise, crack_f) * np.exp(-t / 0.004)
    # corpo do estampido: ruído filtrado com decaimento médio
    body = lowpass(noise, body_f) * np.exp(-t / 0.045) * body_amt
    # soco grave (pressão)
    thump = np.sin(2 * np.pi * (punch * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.06) * 0.9
    # cauda: reverberação ao ar livre (ecos esparsos que somem)
    tail_sig = lowpass(r.normal(0, 1, n), 1800) * np.exp(-t / tail) * 0.28
    s = crack * 0.9 + body + thump + tail_sig
    # ataque instantâneo, leve saturação
    s = np.tanh(s * 1.8)
    s /= np.max(np.abs(s)) + 1e-9
    fade = np.ones(n)
    fade[-2000:] = np.linspace(1, 0, 2000)
    return s * fade * 0.95


def corda(dur, corpo_f, aperto, assobio, seed):
    """Estalo de corda de besta: nada do tiro(), que é todo pólvora (estampido, soco grave e eco).

    Aqui a energia é mecânica: um "toc" de madeira/fibra, a corda e os arcos vibrando por um instante
    (duas parciais que somem depressa) e o assobio curto do dardo saindo. Sem cauda: besta é arma
    silenciosa, e é por isso que se usa para dardo."""
    r = np.random.default_rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    ruido = r.normal(0, 1, n)
    toc = lowpass(ruido, corpo_f) * np.exp(-t / 0.012)                 # impacto do arco contra o batente
    estalo = highpass(ruido, 5000) * np.exp(-t / 0.0025) * 0.55        # a corda saindo do gatilho
    # vibração: a fundamental do arco e uma parcial, ambas decaindo rápido
    vibra = (np.sin(2 * np.pi * aperto * t) * np.exp(-t / 0.045)
             + 0.45 * np.sin(2 * np.pi * aperto * 2.7 * t) * np.exp(-t / 0.022))
    sibilo = highpass(r.normal(0, 1, n), 2600) * np.exp(-t / assobio) * 0.3   # o dardo cortando o ar
    s = toc * 1.1 + estalo + vibra * 0.5 + sibilo
    s = np.tanh(s * 1.5)
    s /= np.max(np.abs(s)) + 1e-9
    fade = np.ones(n)
    fade[-1500:] = np.linspace(1, 0, 1500)
    return s * fade * 0.9


def catraca(voltas, seed):
    """Manivela de armar: cliques de catraca em sequência, acelerando um pouco."""
    r = np.random.default_rng(seed)
    passos = []
    for k in range(voltas):
        n = int(SR * (0.085 - 0.004 * k))
        t = np.arange(n) / SR
        c = highpass(r.normal(0, 1, n), 2600) * np.exp(-t / 0.0035)
        c += np.sin(2 * np.pi * (1500 + 60 * k) * t) * np.exp(-t / 0.005) * 0.4
        passos.append(c)
    s = np.concatenate(passos)
    s /= np.max(np.abs(s)) + 1e-9
    return s * 0.5


def toque(dur, freq, seed):
    """Dardo acertando: um toc curto e abafado, sem nada de metálico (é agulha em couro)."""
    r = np.random.default_rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = lowpass(r.normal(0, 1, n), 1100) * np.exp(-t / 0.018)
    s += np.sin(2 * np.pi * freq * np.exp(-t / 0.03) * t) * np.exp(-t / 0.025) * 0.7
    s /= np.max(np.abs(s)) + 1e-9
    fade = np.ones(n)
    fade[-800:] = np.linspace(1, 0, 800)
    return s * fade * 0.8


def clique():
    n = int(SR * 0.08)
    t = np.arange(n) / SR
    s = highpass(rng.normal(0, 1, n), 3000) * np.exp(-t / 0.003)
    s += np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.006) * 0.5
    s /= np.max(np.abs(s))
    return s * 0.6


def salvar(nome, s):
    wav = OUT / f"{nome}.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "5",
                    str(OUT / f"{nome}.ogg")], check=True)
    wav.unlink()


# AK: mais grave e encorpado; M4: mais seco e estalado; Glock: curto e mais agudo
for i in range(3):
    salvar(f"ak47_{i}", tiro(0.9, 2500, 900, 1.3, 0.22, 70 + i * 4, 10 + i))
    salvar(f"m4a4_{i}", tiro(0.8, 3500, 1300, 1.0, 0.18, 85 + i * 4, 20 + i))
    salvar(f"glock_{i}", tiro(0.6, 4000, 1600, 0.8, 0.12, 110 + i * 5, 30 + i))
    salvar(f"awp_{i}", tiro(1.3, 2000, 700, 1.6, 0.35, 52 + i * 3, 40 + i))
    # Besta: estalo mecânico seco, sem eco. Muito mais baixa que as armas de fogo, de propósito.
    salvar(f"besta_{i}", corda(0.45, 900, 148 + i * 9, 0.05, 50 + i))
    salvar(f"dardo_{i}", toque(0.25, 240 + i * 20, 60 + i))
salvar("besta_recarga", catraca(7, 70))
salvar("vazio", clique())
print("ok")
