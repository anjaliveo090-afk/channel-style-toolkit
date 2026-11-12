#!/usr/bin/env python3
"""Measure shots in a reference video: cuts/dissolves, camera move per shot
(zoom, pan, tilt from ORB feature tracking) and lighting (brightness, warmth,
saturation). Usage: shots.py video.mp4 out.json"""
import json, sys
import cv2
import numpy as np

FPS = 10


def frames(path):
    cap = cv2.VideoCapture(path)
    src_fps = cap.get(cv2.CAP_PROP_FPS)
    step = max(1, round(src_fps / FPS))
    i = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % step == 0:
            h, w = f.shape[:2]
            yield i / src_fps, cv2.resize(f, (360, int(360 * h / w)))
        i += 1


def main(path, out):
    orb = cv2.ORB_create(800)
    mask = None
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    rows, prev = [], None
    for t, f in frames(path):
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        b, gg, r = [float(c.mean()) for c in cv2.split(f)]
        row = dict(t=round(t, 2), bright=round(float(g.mean()) / 255, 3),
                   warm=round((r - b) / 255, 3), sat=round(float(hsv[:, :, 1].mean()) / 255, 3),
                   scale=1.0, dx=0.0, dy=0.0, inl=0.0, diff=0.0)
        if mask is None:
            # ignore the burned-in caption band so static text does not hide the camera move
            mask = np.full(g.shape, 255, np.uint8)
            mask[int(g.shape[0] * 0.6):int(g.shape[0] * 0.8), :] = 0
        kp, des = orb.detectAndCompute(g, mask)
        if prev is not None:
            pg, pkp, pdes = prev
            row["diff"] = round(float(np.abs(g.astype(int) - pg.astype(int)).mean()) / 255, 4)
            if des is not None and pdes is not None and len(kp) > 20 and len(pkp) > 20:
                m = bf.match(pdes, des)
                if len(m) >= 12:
                    a = np.float32([pkp[x.queryIdx].pt for x in m])
                    b2 = np.float32([kp[x.trainIdx].pt for x in m])
                    M, inl = cv2.estimateAffinePartial2D(a, b2, method=cv2.RANSAC, ransacReprojThreshold=3)
                    if M is not None:
                        s = float(np.hypot(M[0, 0], M[1, 0]))
                        row.update(scale=round(s, 4), dx=round(float(M[0, 2]) / 360, 4),
                                   dy=round(float(M[1, 2]) / g.shape[0], 4), inl=round(float(inl.mean()), 3))
        rows.append(row)
        prev = (g, kp, des)

    # shot boundaries: tracking lost or a big jump in pixels
    cuts = [0]
    for i, r in enumerate(rows[1:], 1):
        if (r["inl"] < 0.35 or r["diff"] > 0.12) and i - cuts[-1] >= 4:
            cuts.append(i)
    cuts.append(len(rows))
    shots = []
    for a, b in zip(cuts, cuts[1:]):
        seg = rows[a:b]
        good = [r for r in seg[1:] if r["inl"] >= 0.35]
        zoom = float(np.prod([r["scale"] for r in good])) if good else 1.0
        panx = sum(r["dx"] for r in good)
        pany = sum(r["dy"] for r in good)
        dur = seg[-1]["t"] - seg[0]["t"] + 1 / FPS
        if zoom > 1.06:
            move = "push-in"
        elif zoom < 0.94:
            move = "pull-out"
        elif abs(panx) > 0.12:
            move = "pan-left" if panx > 0 else "pan-right"
        elif abs(pany) > 0.12:
            move = "tilt-up" if pany > 0 else "tilt-down"
        elif abs(zoom - 1) > 0.02 or abs(panx) > 0.04 or abs(pany) > 0.04:
            move = "slow drift"
        else:
            move = "static/hold"
        shots.append(dict(start=seg[0]["t"], end=round(seg[0]["t"] + dur, 2), dur=round(dur, 2),
                          move=move, zoom=round(zoom, 3), panx=round(panx, 3), pany=round(pany, 3),
                          bright=round(float(np.mean([r["bright"] for r in seg])), 2),
                          warm=round(float(np.mean([r["warm"] for r in seg])), 3),
                          sat=round(float(np.mean([r["sat"] for r in seg])), 2)))
    json.dump(dict(shots=shots, frames=rows), open(out, "w"))
    for s in shots:
        print(f'{s["start"]:6.1f}-{s["end"]:6.1f} {s["dur"]:4.1f}s {s["move"]:12s} zoom {s["zoom"]:.2f} '
              f'pan {s["panx"]:+.2f},{s["pany"]:+.2f} bright {s["bright"]:.2f} warm {s["warm"]:+.2f} sat {s["sat"]:.2f}')


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
