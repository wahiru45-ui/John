"""Blur every licence plate: per-frame detector + CSRT trackers seeded by hand."""
import subprocess
from collections import defaultdict

import cv2

from detect2 import find_plates

SRC, OUT, FPS = "mid.mp4", "blurred.mp4", 30
LAST = 59 * FPS  # keep the first 59 seconds
HOLD = 5  # keep a detected box this many frames before and after

# (frame, (x, y, w, h), frames to track backward, frames to track forward)
SEEDS = [
    (0, (593, 957, 107, 28), 0, 360),          # white car ahead, 49두
    (12 * FPS, (600, 975, 160, 40), 60, 150),  # same car, re-seed
    (16 * FPS, (545, 922, 95, 28), 40, 70),
    (18 * FPS, (575, 928, 95, 28), 30, 60),
    (20 * FPS, (695, 932, 95, 28), 30, 75),
    (30 * FPS, (10, 1000, 105, 28), 60, 50),   # left car, 30 s
    (29 * FPS, (190, 940, 60, 20), 30, 20),    # dark sedan left, 29 s
    (32 * FPS, (115, 960, 70, 28), 40, 50),    # left car, 32 s
    (38 * FPS, (998, 893, 90, 24), 50, 60),    # right SUV, 38 s
    (40 * FPS, (100, 980, 72, 22), 60, 70),    # white Mercedes, 40 s
    (48 * FPS, (126, 948, 52, 18), 70, 40),    # white Mercedes, 48 s
]

boxes = defaultdict(list)
cap = cv2.VideoCapture(SRC)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


def read_range(a, b):
    cap.set(cv2.CAP_PROP_POS_FRAMES, a)
    out = []
    for _ in range(a, b):
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out


def track(frames, idx0, box, step):
    """Run a tracker from frames[idx0] in direction step, yield (i, box)."""
    t = cv2.TrackerCSRT_create()
    t.init(frames[idx0], box)
    yield idx0, box
    i = idx0 + step
    while 0 <= i < len(frames):
        ok, nb = t.update(frames[i])
        if not ok:
            break
        x, y, w, h = (int(v) for v in nb)
        if x < -w // 2 or y < 0 or x + w // 2 > W or w < 12:
            break
        yield i, (x, y, w, h)
        i += step


for start, box, back, fwd in SEEDS:
    a, b = max(0, start - back), min(LAST, start + fwd + 1)
    frames = read_range(a, b)
    rel = start - a
    for step in (1, -1):
        for i, bx in track(frames, rel, box, step):
            boxes[a + i].append(bx)
    del frames

# per-frame detector with a short hold
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
for n in range(LAST):
    ok, f = cap.read()
    if not ok:
        break
    for bx in find_plates(f):
        for k in range(max(0, n - HOLD), min(LAST, n + HOLD + 1)):
            boxes[k].append(bx)

enc = subprocess.Popen(
    ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
     "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
     "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
for n in range(LAST):
    ok, f = cap.read()
    if not ok:
        break
    for (x, y, w, h) in boxes[n]:
        px, py = int(w * 0.6) + 8, int(h * 0.7) + 8
        x0, y0 = max(0, x - px), max(0, y - py)
        x1, y1 = min(W, x + w + px), min(H, y + h + py)
        if x1 > x0 and y1 > y0:
            f[y0:y1, x0:x1] = cv2.GaussianBlur(f[y0:y1, x0:x1], (0, 0), 14)
    enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait()
print("done", sum(len(v) for v in boxes.values()), "boxes")
