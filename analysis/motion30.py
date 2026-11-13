#!/usr/bin/env python3
"""Frame-by-frame camera + transition analysis at the video's native fps (any aspect ratio).

For every pair of consecutive frames it measures
  - the global camera move: zoom factor, pan x/y (px of the full frame), rotation  (ECC affine,
    falling back to ORB+RANSAC), and how well that model fits;
  - picture change (mean abs difference), sharpness (Laplacian variance, drops in whip-pans),
    mean brightness (black text cards).
Then it segments the video into shots and labels every boundary:
  cut       one-frame jump
  dissolve  several frames that are blends of the shot before and after
  whip      fast pan with motion blur (sharpness collapses, big horizontal move)
  black     black card in/out (text cards)
  zoom-thru the camera zooms hard into an object and the next shot starts (push-through)
and gives per shot: length, total zoom, zoom speed, pan speed, and the speed curve (ease).

Usage: motion30.py video.mp4 out_prefix [srt]   ->  out_prefix.json, out_prefix_plot.png
"""
import json
import subprocess
import sys

import cv2
import numpy as np

AW = 320  # analysis width


def read_frames(path):
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                         "stream=width,height,r_frame_rate", "-of", "csv=p=0", path],
                        capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(pr[0]), int(pr[1])
    num, den = pr[2].split("/")
    fps = float(num) / float(den)
    ah = int(round(AW * h / w / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={AW}:{ah}", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, ah, AW, 3)
    return fr, fps, w, h


def global_move(a, b):
    """affine (2x3) mapping a->b on gray float images, plus fit quality 0..1"""
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        cc, warp = cv2.findTransformECC(a, b, warp, cv2.MOTION_AFFINE,
                                        (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 60, 1e-5), None, 5)
        return warp, float(cc)
    except cv2.error:
        pass
    orb = cv2.ORB_create(600)
    ka, da = orb.detectAndCompute((a * 255).astype(np.uint8), None)
    kb, db = orb.detectAndCompute((b * 255).astype(np.uint8), None)
    if da is None or db is None or len(ka) < 8 or len(kb) < 8:
        return None, 0.0
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db)
    if len(m) < 8:
        return None, 0.0
    pa = np.float32([ka[x.queryIdx].pt for x in m])
    pb = np.float32([kb[x.trainIdx].pt for x in m])
    M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=2.0)
    if M is None:
        return None, 0.0
    return M.astype(np.float32), float(inl.mean())


def decompose(M, cx, cy, scale_to_full):
    """zoom factor, pan (full-frame px) of the frame centre, rotation (deg)"""
    s = float(np.sqrt(abs(np.linalg.det(M[:, :2]))))
    rot = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    c2 = M[:, :2] @ np.array([cx, cy]) + M[:, 2]
    # camera pan is opposite to the image motion of the centre
    dx, dy = (c2[0] - cx) * scale_to_full, (c2[1] - cy) * scale_to_full
    return s, dx, dy, rot


def main(path, prefix, srt=None):
    fr, fps, W, H = read_frames(path)
    n = len(fr)
    ah = fr.shape[1]
    k = W / AW
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255 for f in fr]
    small = [cv2.resize(f, (80, int(80 * ah / AW))).astype(np.float32) / 255 for f in fr]
    lum = np.array([g.mean() for g in gray])
    sharp = np.array([cv2.Laplacian(g, cv2.CV_32F).var() for g in gray])
    diff = np.zeros(n)
    zoom = np.ones(n)
    pan = np.zeros((n, 2))
    rot = np.zeros(n)
    fit = np.zeros(n)
    for i in range(1, n):
        diff[i] = float(np.abs(small[i] - small[i - 1]).mean())
        if lum[i] < 0.03 or lum[i - 1] < 0.03:
            continue
        M, q = global_move(gray[i - 1], gray[i])
        fit[i] = q
        if M is not None and q > 0.6:
            s, dx, dy, r = decompose(M, AW / 2, ah / 2, k)
            if 0.8 < s < 1.25 and abs(dx) < W * 0.5:
                zoom[i], pan[i], rot[i] = s, (dx, dy), r

    # ---------------- boundaries
    events = []
    med_sharp = np.median(sharp[lum > 0.05]) if (lum > 0.05).any() else 1
    i = 1
    while i < n:
        black_now, black_prev = lum[i] < 0.03, lum[i - 1] < 0.03
        if black_now != black_prev:
            events.append({"t": round(i / fps, 3), "frame": i, "kind": "black-in" if black_now else "black-out",
                           "len": 1 / fps})
            i += 1
            continue
        if black_now:
            i += 1
            continue
        if sharp[i] < 0.35 * med_sharp and np.hypot(*pan[i]) > 0.02 * W or (sharp[i] < 0.25 * med_sharp and diff[i] > 0.04):
            j = i
            while j < n and sharp[j] < 0.5 * med_sharp:
                j += 1
            events.append({"t": round(i / fps, 3), "frame": i, "kind": "whip", "len": round((j - i) / fps, 3)})
            i = j + 1
            continue
        if diff[i] > 0.09 and fit[i] < 0.6:
            # dissolve if the neighbours are also changing, cut if it is a single jump
            j = i
            while j + 1 < n and diff[j + 1] > 0.015 and fit[j + 1] < 0.9 and j - i < int(fps):
                j += 1
            a0, b0 = max(0, i - 2), min(n - 1, j + 1)
            blend_err = 1.0
            if j > i:
                mid = (i + j) // 2
                wgt = (mid - a0) / max(1, b0 - a0)
                blend = small[a0] * (1 - wgt) + small[b0] * wgt
                blend_err = float(np.abs(small[mid] - blend).mean() / (np.abs(small[b0] - small[a0]).mean() + 1e-6))
            kind = "dissolve" if (j > i and blend_err < 0.5) else "cut"
            # zoom-through: big zoom just before the change
            zb = np.prod(zoom[max(1, i - int(0.4 * fps)):i])
            if zb > 1.25:
                kind = "zoom-thru"
            events.append({"t": round(i / fps, 3), "frame": i, "kind": kind, "len": round((j - i + 1) / fps, 3)})
            i = j + 1
            continue
        i += 1

    # ---------------- shots
    bounds = [0] + [e["frame"] for e in events] + [n]
    shots = []
    for a, b in zip(bounds, bounds[1:]):
        if b - a < 2:
            continue
        seg = slice(a + 1, b)
        is_black = lum[a:b].mean() < 0.03
        z = float(np.prod(zoom[seg]))
        px = float(pan[seg, 0].sum())
        py = float(pan[seg, 1].sum())
        dur = (b - a) / fps
        zr = np.log(zoom[seg])
        speed = np.abs(zr) * fps
        prof = ""
        if len(speed) >= 6 and speed.sum() > 0:
            th = np.array_split(speed, 3)
            m = [float(x.mean()) for x in th]
            prof = "accelerate" if m[2] > 1.3 * m[0] else "decelerate" if m[0] > 1.3 * m[2] else "constant"
            if m[1] > 1.3 * max(m[0], m[2]):
                prof = "ease-in-out"
        shots.append({"start": round(a / fps, 3), "end": round(b / fps, 3), "dur": round(dur, 3),
                      "black_card": bool(is_black), "zoom_total": round(z, 3),
                      "zoom_per_s": round(z ** (1 / max(dur, 1e-3)), 4),
                      "pan_x_px": round(px), "pan_y_px": round(py),
                      "pan_px_per_s": round(float(np.hypot(px, py)) / max(dur, 1e-3), 1),
                      "zoom_profile": prof, "brightness": round(float(lum[a:b].mean()), 3)})

    vis = [s for s in shots if not s["black_card"]]
    durs = [s["dur"] for s in shots]
    summary = {
        "video": path, "fps": fps, "frames": n, "duration": round(n / fps, 2),
        "boundaries": len(events),
        "kinds": {k: sum(1 for e in events if e["kind"] == k) for k in sorted({e["kind"] for e in events})},
        "shot_len_median": round(float(np.median(durs)), 2) if durs else None,
        "shot_len_mean": round(float(np.mean(durs)), 2) if durs else None,
        "visual_change_every_s": round(n / fps / max(1, len(shots)), 2),
        "push_in_share": round(sum(1 for s in vis if s["zoom_total"] > 1.02) / max(1, len(vis)), 2),
        "pull_out_share": round(sum(1 for s in vis if s["zoom_total"] < 0.98) / max(1, len(vis)), 2),
        "static_share": round(sum(1 for s in vis if 0.98 <= s["zoom_total"] <= 1.02 and s["pan_px_per_s"] < 15)
                              / max(1, len(vis)), 2),
        "zoom_per_s_median_moving": round(float(np.median([s["zoom_per_s"] for s in vis if abs(s["zoom_total"] - 1) > 0.02] or [1])), 4),
        "pan_px_per_s_median": round(float(np.median([s["pan_px_per_s"] for s in vis] or [0])), 1),
    }
    out = {"summary": summary, "events": events, "shots": shots,
           "per_frame": {"zoom": [round(float(x), 5) for x in zoom], "pan_x": [round(float(x), 2) for x in pan[:, 0]],
                         "pan_y": [round(float(x), 2) for x in pan[:, 1]], "diff": [round(float(x), 4) for x in diff],
                         "sharp": [round(float(x), 5) for x in sharp], "lum": [round(float(x), 3) for x in lum]}}
    with open(prefix + ".json", "w") as f:
        json.dump(out, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = np.arange(n) / fps
    fig, ax = plt.subplots(4, 1, figsize=(16, 9), sharex=True)
    ax[0].plot(t, diff, lw=0.7)
    ax[0].set_ylabel("change")
    ax[1].plot(t, (zoom - 1) * fps * 100, lw=0.7)
    ax[1].set_ylabel("zoom %/s")
    ax[2].plot(t, pan[:, 0] * fps, lw=0.7, label="x")
    ax[2].plot(t, pan[:, 1] * fps, lw=0.7, label="y")
    ax[2].set_ylabel("pan px/s")
    ax[2].legend()
    ax[3].plot(t, sharp / med_sharp, lw=0.7)
    ax[3].plot(t, lum, lw=0.7)
    ax[3].set_ylabel("sharp, lum")
    col = {"cut": "r", "dissolve": "g", "whip": "m", "black-in": "k", "black-out": "k", "zoom-thru": "orange"}
    for e in events:
        for a_ in ax:
            a_.axvline(e["t"], color=col.get(e["kind"], "b"), lw=0.6, alpha=0.6)
    if srt:
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent / "assembler"))
        from assemble import parse_srt
        for s_, e_, txt in parse_srt(srt):
            ax[0].axvspan(s_, e_, color="y", alpha=0.12)
    ax[3].set_xlabel("s")
    fig.tight_layout()
    fig.savefig(prefix + "_plot.png", dpi=80)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
