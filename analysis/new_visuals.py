#!/usr/bin/env python3
"""Count "new visuals" (hard cuts AND the soft ~0.25 s cross-dissolves the references use,
which ffmpeg's scene detector misses): compare each frame with the one 0.3 s earlier
(colour histogram + small-image difference) and count the peaks.
Usage: new_visuals.py video.mp4 [...]"""
import subprocess
import sys

import cv2
import numpy as np


def changes(path, fps=10):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale=90:160", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90, 3)
    fr = fr[:, np.r_[0:96, 128:160]]          # skip the caption band
    hs = [cv2.normalize(cv2.calcHist([f], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3), None).flatten() for f in fr]
    lag = 3
    score = np.zeros(len(fr))
    for i in range(lag, len(fr)):
        h = 1 - cv2.compareHist(hs[i], hs[i - lag], cv2.HISTCMP_CORREL)
        d = np.abs(fr[i].astype(np.int16) - fr[i - lag]).mean() / 255
        score[i] = h + 2 * d
    peaks = [i for i in range(1, len(score) - 1) if score[i] >= score[i - 1] and score[i] > score[i + 1]
             and score[i] > 0.35]
    out = []
    for p in peaks:                           # merge peaks closer than 0.6 s (one transition)
        if not out or p - out[-1] > 6:
            out.append(p)
    return [p / fps for p in out], len(fr) / fps


if __name__ == "__main__":
    for p in sys.argv[1:]:
        t, dur = changes(p)
        gaps = np.diff([0] + t + [dur])
        print(f"{p.split('/')[-1][:40]:40s} {len(t):3d} new visuals in {dur:.0f}s = every {dur / (len(t) + 1):.2f}s "
              f"(median gap {np.median(gaps):.2f}s, 90% under {np.percentile(gaps, 90):.2f}s)")
