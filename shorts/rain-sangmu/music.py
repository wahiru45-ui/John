"""Synthesize an original, calm lo-fi piano loop for a rainy-night clip (no samples used)."""
import numpy as np
from scipy.io import wavfile

SR = 44100
BPM = 70
BEAT = 60 / BPM
DUR = 59.0
rng = np.random.default_rng(7)


def note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


def epiano(freq, length, vel=0.5):
    t = np.arange(int(length * SR)) / SR
    env = np.exp(-t * 2.2) * (1 - np.exp(-t * 400))
    tone = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 4)
            + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 6))
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    return vel * env * tone * trem


def pad(freqs, length):
    t = np.arange(int(length * SR)) / SR
    env = np.minimum(1, t / 1.2) * np.minimum(1, (length - t) / 1.2)
    s = sum(np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.003 * t) for f in freqs)
    return 0.05 * env * s / len(freqs)


def add(buf, sig, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[:j - i]


# Fmaj7 - Em7 - Dm7 - Cmaj7 (+ G6 turnaround), voiced in the middle register
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
bass = [41, 40, 38, 36]
mel_pool = [72, 74, 76, 79, 81, 76, 74, 72, 69, 67]

out = np.zeros(int(DUR * SR) + SR)
bar = 4 * BEAT
t0 = 0.0
k = 0
while t0 < DUR:
    ch = chords[k % 4]
    add(out, pad([note(n) for n in ch], bar + 0.4), t0)
    add(out, epiano(note(bass[k % 4]), bar, 0.35), t0)
    # broken-chord arpeggio on eighths, slightly humanised
    for e in range(8):
        n = ch[[0, 1, 2, 3, 2, 1, 2, 3][e]] + 12
        jitter = rng.normal(0, 0.008)
        add(out, epiano(note(n), 1.6, 0.16 + 0.04 * (e % 2 == 0)), t0 + e * BEAT / 2 + jitter)
    # sparse melody from the second phrase on
    if k >= 2:
        for b in (0, 1.5, 3):
            if rng.random() < 0.75:
                add(out, epiano(note(rng.choice(mel_pool)), 2.0, 0.22), t0 + b * BEAT)
    # soft brushed hat on off-beats
    for b in range(4):
        hat = rng.normal(0, 1, int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90)
        add(out, 0.025 * hat, t0 + (b + 0.5) * BEAT)
    t0 += bar
    k += 1

out = out[:int(DUR * SR)]
# simple room reverb: a few decaying echoes
rev = out.copy()
for d, g in ((0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2), (0.173, 0.15)):
    s = int(d * SR)
    rev[s:] += g * out[:-s]
out = rev
# fade in/out and normalise
fade = int(2.0 * SR)
out[:fade] *= np.linspace(0, 1, fade)
out[-int(3 * SR):] *= np.linspace(1, 0, int(3 * SR))
out = out / np.max(np.abs(out)) * 0.8
st = np.stack([out, np.roll(out, int(0.012 * SR)) * 0.95], axis=1)
wavfile.write("music.wav", SR, (st * 32767).astype(np.int16))
print("ok", len(out) / SR)
