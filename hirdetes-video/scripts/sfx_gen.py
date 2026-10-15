"""
Hangeffekt-konyvtar szintetizalasa -> assets/sfx/*.wav

Miert szintetizalt, es nem letoltott: nincs licenckerdes, barmikor
ujragyarthato, es a hosszuk/szintjuk a hirdetes-ritmushoz van szabva.
Ha jobb, valodi felvetel kell (pl. Pixabay), tedd a PROJEKT sfx/ mappajaba
ugyanazzal a nevvel -- a make.py azt veszi elore.

    python sfx_gen.py          # ujragyartja az osszeset
"""
import os
import wave

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "assets", "sfx"))
rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def env_ad(n, attack, decay_tau):
    """Gyors felfutas, exponencialis lecsenges."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attack, 0) / decay_tau)


def sweep_sine(f0, f1, dur, curve=1.0):
    t = t_axis(dur)
    p = (t / dur) ** curve
    f = f0 + (f1 - f0) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def bandnoise(dur, f_lo, f_hi):
    """Savszurt zaj FFT-vel; f_lo/f_hi lehet idoben valtozo (tomb) is."""
    n = int(SR * dur)
    x = rng.standard_normal(n)
    # idoben valtozo szuro: darabonkent (20 ms) mas savot engedunk at
    out = np.zeros(n)
    win = int(SR * 0.02)
    lo = np.broadcast_to(f_lo, (n,)) if np.ndim(f_lo) else np.full(n, f_lo)
    hi = np.broadcast_to(f_hi, (n,)) if np.ndim(f_hi) else np.full(n, f_hi)
    hann = np.hanning(win * 2)
    for s in range(0, n, win):
        seg = x[s:s + win * 2]
        if len(seg) < 8:
            break
        F = np.fft.rfft(seg * hann[:len(seg)])
        fr = np.fft.rfftfreq(len(seg), 1 / SR)
        m = min(s + win, n - 1)
        F[(fr < lo[m]) | (fr > hi[m])] = 0
        y = np.fft.irfft(F, len(seg))
        out[s:s + len(y)] += y
    return out


def norm(x, peak_db=-3.0):
    m = np.max(np.abs(x)) or 1.0
    return x / m * 10 ** (peak_db / 20)


def fade_edges(x, ms=4):
    k = int(SR * ms / 1000)
    if len(x) > 2 * k:
        x[:k] *= np.linspace(0, 1, k)
        x[-k:] *= np.linspace(1, 0, k)
    return x


def save(name, mono, width=0.0):
    """width > 0: enyhe sztereo szelesites (a jobb csatorna par ms-mal kesik)."""
    mono = fade_edges(norm(mono))
    d = int(SR * width)
    left = mono
    right = np.concatenate([np.zeros(d), mono])[:len(mono)] if d else mono
    st = np.stack([left, right], axis=1)
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


# ---------------------------------------------------------------------------

def whoosh(dur=0.42, lo=(300, 1800), hi=(1500, 6500)):
    n = int(SR * dur)
    p = np.linspace(0, 1, n)
    x = bandnoise(dur, lo[0] + (lo[1] - lo[0]) * p, hi[0] + (hi[1] - hi[0]) * p)
    e = np.sin(np.pi * p) ** 1.6          # kozepen a csucs, mint egy elsuhano targy
    return x * e


def pop():
    s = sweep_sine(1100, 380, 0.09, curve=0.5) * env_ad(int(SR * 0.09), 0.002, 0.03)
    click = bandnoise(0.01, 2000, 9000) * np.linspace(1, 0, int(SR * 0.01))
    out = np.zeros(int(SR * 0.12)); out[:len(s)] += s; out[:len(click)] += click * 0.5
    return out


def ding():
    """Ket hangu ertesites (SMS)."""
    def note(f, dur):
        t = t_axis(dur)
        x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.01 * t)
             + 0.12 * np.sin(2 * np.pi * f * 3.0 * t))
        return x * env_ad(len(t), 0.003, 0.22)
    a, b = note(1318.5, 0.55), note(1975.5, 0.7)
    out = np.zeros(int(SR * 0.85)); out[:len(a)] += a
    off = int(SR * 0.11); out[off:off + len(b)] += b * 0.9
    return out


def click():
    n = int(SR * 0.03)
    x = bandnoise(0.03, 1500, 8000) * env_ad(n, 0.0005, 0.004)
    x += np.sin(2 * np.pi * 2400 * t_axis(0.03)) * env_ad(n, 0.0005, 0.006) * 0.6
    return x


def tick():
    n = int(SR * 0.02)
    return np.sin(2 * np.pi * 3200 * t_axis(0.02)) * env_ad(n, 0.0003, 0.003)


def ring():
    """Modern, puha csengo: ket rovid trilla. Nem regi mechanikus csengo."""
    seg = []
    for _ in range(2):
        t = t_axis(0.42)
        f = np.where((t * 18).astype(int) % 2 == 0, 1046.5, 1318.5)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.01, 0.5)
        x *= np.clip((0.42 - t) / 0.05, 0, 1)
        seg += [x, np.zeros(int(SR * 0.18))]
    return np.concatenate(seg)


def riser(dur=1.2):
    n = int(SR * dur); p = np.linspace(0, 1, n)
    x = bandnoise(dur, 400 + 2000 * p, 2000 + 9000 * p) * 0.7
    x += sweep_sine(180, 900, dur, curve=2.0) * 0.4
    return x * p ** 2.2


def hit():
    """Tompa utes a fordulatra / villanasra."""
    n = int(SR * 0.5)
    body = sweep_sine(95, 42, 0.5, curve=0.4) * env_ad(n, 0.002, 0.16)
    trans = bandnoise(0.04, 800, 6000) * env_ad(int(SR * 0.04), 0.001, 0.01)
    out = body.copy(); out[:len(trans)] += trans * 0.5
    return out


def coin():
    t = t_axis(0.6)
    x = (np.sin(2 * np.pi * 2637 * t) + 0.6 * np.sin(2 * np.pi * 3520 * t)) * env_ad(len(t), 0.001, 0.14)
    off = int(SR * 0.07)
    y = np.zeros(len(t) + off); y[:len(x)] += x; y[off:off + len(x)] += x * 0.7
    return y


LIB = {
    "whoosh": (lambda: whoosh(), 0.004),
    "whoosh-soft": (lambda: whoosh(0.6, (200, 900), (900, 3500)), 0.004),
    "pop": (pop, 0.0),
    "ding": (ding, 0.003),
    "click": (click, 0.0),
    "tick": (tick, 0.0),
    "ring": (ring, 0.002),
    "riser": (riser, 0.006),
    "hit": (hit, 0.0),
    "coin": (coin, 0.002),
}

if __name__ == "__main__":
    for name, (fn, width) in LIB.items():
        save(name, fn(), width)
        print("  sfx:", name)
    print("->", OUT)
