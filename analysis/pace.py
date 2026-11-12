#!/usr/bin/env python3
"""Pace metrics: visual changes per minute (cuts + dissolves) and on-screen motion
that is NOT camera (character/object movement after removing the camera move).
Usage: pace.py video.mp4 [more.mp4 ...]"""
import sys
import cv2
import numpy as np


def pace(path, fps=15):
    cap = cv2.VideoCapture(path)
    step = max(1, round(cap.get(cv2.CAP_PROP_FPS) / fps))
    orb = cv2.ORB_create(800)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    prev, i, n, t_end = None, 0, 0, 0
    changes, motion, last_change = 0, [], -9
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % step:
            i += 1
            continue
        t = i / cap.get(cv2.CAP_PROP_FPS)
        g = cv2.cvtColor(cv2.resize(f, (270, 480)), cv2.COLOR_BGR2GRAY)
        mask = np.full(g.shape, 255, np.uint8)
        mask[int(480 * 0.6):int(480 * 0.8)] = 0
        kp, des = orb.detectAndCompute(g, mask)
        if prev is not None:
            pg, pkp, pdes = prev
            M = None
            if des is not None and pdes is not None and len(kp) > 15 and len(pkp) > 15:
                m = bf.match(pdes, des)
                if len(m) >= 10:
                    a = np.float32([pkp[x.queryIdx].pt for x in m])
                    b = np.float32([kp[x.trainIdx].pt for x in m])
                    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=3)
                    if M is not None and inl.mean() < 0.35:
                        M = None
            if M is None:
                if t - last_change > 0.5:
                    changes += 1
                    last_change = t
            else:
                warped = cv2.warpAffine(pg, M, (270, 480))
                d = np.abs(warped.astype(int) - g.astype(int))
                d[int(480 * 0.6):int(480 * 0.8)] = 0
                d[:12], d[-12:], d[:, :12], d[:, -12:] = 0, 0, 0, 0
                motion.append(float((d > 25).mean()))
        prev = (g, kp, des)
        t_end = t
        i += 1
    mins = t_end / 60
    # median ignores dissolve frames, which would otherwise count as motion
    return changes / mins, 60 * mins / max(changes, 1), float(np.mean(motion)) * 100, float(np.median(motion)) * 100


if __name__ == "__main__":
    for p in sys.argv[1:]:
        cpm, sec, mot, med = pace(p)
        print(f"{p.split('/')[-1][:45]:45s} changes/min {cpm:5.1f}  sec/visual {sec:4.1f}  motion mean {mot:5.2f}%  median {med:5.2f}%")
