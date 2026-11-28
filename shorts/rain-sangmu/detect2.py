"""Licence-plate finder v2: yellow plates by colour, any plate by its row of characters."""
import cv2
import numpy as np

Y0, Y1 = 880, 1120  # band where plates of nearby cars appear


def yellow_plates(hsv, gray):
    m = cv2.inRange(hsv, (18, 90, 130), (36, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3)))
    out = []
    for c in cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
        x, y, w, h = cv2.boundingRect(c)
        if 24 <= w <= 220 and 7 <= h <= 70 and 1.8 <= w / h <= 6.5 \
                and cv2.contourArea(c) / (w * h) > 0.45:
            roi = gray[y:y + h, x:x + w]
            if (roi < roi.mean() - 30).mean() > 0.05:
                out.append((x, y, w, h))
    return out


def text_rows(gray):
    """Rows of >=4 dark, similar-sized glyphs on a bright background."""
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 18)
    n, _, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    comps = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if 7 <= h <= 42 and 2 <= w <= 34 and 0.8 <= h / max(w, 1) <= 5 and a >= 0.2 * w * h:
            comps.append((x, y, w, h))
    comps.sort()
    used = [False] * len(comps)
    rows = []
    for i, (x, y, w, h) in enumerate(comps):
        if used[i]:
            continue
        grp = [i]
        cy, ch, right = y + h / 2, h, x + w
        for j in range(i + 1, len(comps)):
            xj, yj, wj, hj = comps[j]
            if xj - right > 1.6 * ch:
                if xj > right + 4 * ch:
                    break
                continue
            if abs((yj + hj / 2) - cy) < 0.35 * ch and 0.6 < hj / ch < 1.6:
                grp.append(j)
                right = max(right, xj + wj)
        if len(grp) >= 4:
            xs = [comps[k][0] for k in grp]; ys = [comps[k][1] for k in grp]
            xe = [comps[k][0] + comps[k][2] for k in grp]; ye = [comps[k][1] + comps[k][3] for k in grp]
            X, Y, W, H = min(xs), min(ys), max(xe) - min(xs), max(ye) - min(ys)
            if not (1.8 <= W / H <= 9 and W <= 170 and H <= 36):
                continue
            pad = int(H * 0.5)
            bg = gray[max(0, Y - pad):Y + H + pad, max(0, X - pad):X + W + pad]
            if bg.size and np.percentile(bg, 70) > 120:
                for k in grp:
                    used[k] = True
                rows.append((X, Y, W, H))
    return rows


def find_plates(frame):
    band = frame[Y0:Y1]
    gray = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
    boxes = yellow_plates(hsv, gray) + text_rows(gray)
    return [(x, y + Y0, w, h) for (x, y, w, h) in boxes]


if __name__ == "__main__":
    import glob, sys
    files = sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else "kf/t*.png"))
    tiles = []
    for p in files:
        f = cv2.imread(p)
        for (x, y, w, h) in find_plates(f):
            cv2.rectangle(f, (x - 4, y - 4), (x + w + 4, y + h + 4), (0, 0, 255), 4)
        crop = cv2.resize(f[700:1500], (540, 400))
        cv2.putText(crop, p.split('/')[-1][1:4], (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        tiles.append(crop)
    for s in range(0, len(tiles), 6):
        grid = np.zeros((800, 1620, 3), np.uint8)
        for i, t in enumerate(tiles[s:s + 6]):
            grid[(i // 3) * 400:(i // 3) * 400 + 400, (i % 3) * 540:(i % 3) * 540 + 540] = t
        cv2.imwrite(f"d2_{s // 6}.png", grid)
