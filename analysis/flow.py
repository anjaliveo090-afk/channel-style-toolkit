#!/usr/bin/env python3
"""Texture-fair motion measure: optical flow on edge pixels only, split into the
camera part (best-fit zoom/pan) and the rest (characters, objects, parallax),
in % of frame width per second. Usage: flow.py video.mp4 [...]"""
import sys
import cv2
import numpy as np

W, H, FPS = 270, 480, 10


def measure(path):
    cap = cv2.VideoCapture(path)
    step = max(1, round(cap.get(cv2.CAP_PROP_FPS) / FPS))
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    keep = np.ones((H, W), bool)
    keep[int(H * 0.6):int(H * 0.8)] = False  # caption band
    prev, cam, res, i = None, [], [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % step:
            i += 1
            continue
        i += 1
        g = cv2.cvtColor(cv2.resize(f, (W, H)), cv2.COLOR_BGR2GRAY)
        if prev is not None:
            if np.abs(g.astype(int) - prev.astype(int)).mean() > 30:  # hard cut
                prev = g
                continue
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 21, 3, 5, 1.1, 0)
            gx = cv2.Sobel(prev, cv2.CV_32F, 1, 0)
            gy = cv2.Sobel(prev, cv2.CV_32F, 0, 1)
            edge = (np.hypot(gx, gy) > 60) & keep
            if edge.sum() > 300:
                src = np.stack([xs[edge], ys[edge]], 1)
                dst = src + fl[edge]
                M, _ = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2)
                if M is not None:
                    pred = src @ M[:, :2].T + M[:, 2]
                    r = np.linalg.norm(dst - pred, axis=1)
                    c = np.linalg.norm(pred - src, axis=1)
                    res.append(np.median(r[r > 0.5]) * (r > 0.5).mean() if (r > 0.5).any() else 0.0)
                    cam.append(float(np.median(c)))
        prev = g
    k = 100 * FPS / W
    return np.median(cam) * k, np.mean(cam) * k, np.mean(res) * k


if __name__ == "__main__":
    for p in sys.argv[1:]:
        cm, ca, r = measure(p)
        print(f"{p.split('/')[-1][:40]:40s} camera speed median {cm:5.2f}  mean {ca:5.2f}   non-camera motion {r:5.2f}  (% width/s)")
