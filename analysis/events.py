#!/usr/bin/env python3
"""Every-frame "what moves besides the camera" detector.

For each frame: estimate the camera move from the previous frame (ECC affine), warp the previous frame
by it, and diff. What is left is animation inside the shot (pop-ins, mouths, blinks, props, labels).
Residual blobs are grouped into events with a size and a place; cuts/black frames are skipped.

Usage: events.py video.mp4 out_prefix [srt]  ->  out_prefix_events.json + printed summary
"""
import json
import subprocess
import sys

import cv2
import numpy as np

AW = 320


def main(path, prefix, srt=None):
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                         "stream=width,height,r_frame_rate", "-of", "csv=p=0", path],
                        capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(pr[0]), int(pr[1])
    num, den = pr[2].split("/")
    fps = float(num) / float(den)
    ah = int(round(AW * h / w / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={AW}:{ah}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, ah, AW).astype(np.float32) / 255
    n = len(fr)
    per = []
    for i in range(1, n):
        a, b = fr[i - 1], fr[i]
        if a.mean() < 0.03 or b.mean() < 0.03:
            per.append({"f": i, "kind": "black", "res": 0.0, "area": 0.0})
            continue
        warp = np.eye(2, 3, dtype=np.float32)
        ok = True
        try:
            _, warp = cv2.findTransformECC(a, b, warp, cv2.MOTION_AFFINE,
                                           (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 1e-5), None, 5)
        except cv2.error:
            ok = False
        if not ok or np.abs(b - a).mean() > 0.09:
            per.append({"f": i, "kind": "cut", "res": float(np.abs(b - a).mean()), "area": 1.0})
            continue
        aw = cv2.warpAffine(a, warp, (AW, ah), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        d = np.abs(b - aw)
        d[:4], d[-4:], d[:, :4], d[:, -4:] = 0, 0, 0, 0
        m = (cv2.GaussianBlur(d, (0, 0), 1.2) > 0.06).astype(np.uint8)
        k, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
        blobs = [(int(st[j, 4]), float(cen[j, 0] / AW), float(cen[j, 1] / ah)) for j in range(1, k) if st[j, 4] >= 3]
        area = sum(bb[0] for bb in blobs) / (AW * ah)
        per.append({"f": i, "kind": "anim" if area > 0.0004 else "still", "res": float(d.mean()), "area": round(area, 5),
                    "blobs": sorted(blobs, reverse=True)[:3]})
    # group consecutive animated frames into events
    events = []
    cur = None
    for p in per:
        if p["kind"] == "anim":
            if cur and p["f"] - cur["end"] <= 2:
                cur["end"] = p["f"]
                cur["peak_area"] = max(cur["peak_area"], p["area"])
                cur["frames"] += 1
            else:
                cur = {"start": p["f"], "end": p["f"], "peak_area": p["area"], "frames": 1,
                       "where": p["blobs"][0][1:] if p["blobs"] else None}
                events.append(cur)
        elif cur and p["f"] - cur["end"] > 2:
            cur = None
    for e in events:
        e["t"] = round(e["start"] / fps, 3)
        e["dur"] = round((e["end"] - e["start"] + 1) / fps, 3)
        a = e["peak_area"]
        e["size"] = "small" if a < 0.004 else "medium" if a < 0.03 else "large"
    dur = n / fps
    cuts = sum(1 for p in per if p["kind"] == "cut")
    still = sum(1 for p in per if p["kind"] == "still") / max(1, len(per))
    sizes = {s: sum(1 for e in events if e["size"] == s) for s in ("small", "medium", "large")}
    summary = {"video": path, "fps": fps, "frames": n, "duration": round(dur, 2),
               "anim_events": len(events), "anim_events_per_10s": round(len(events) / dur * 10, 1),
               "by_size": sizes,
               "median_event_dur_s": round(float(np.median([e["dur"] for e in events])) if events else 0, 3),
               "frames_fully_still_share": round(still, 3), "cut_frames": cuts,
               "longest_gap_without_animation_s": round(max(
                   [(b["t"] - (a["t"] + a["dur"])) for a, b in zip(events, events[1:])] or [0]), 2)}
    json.dump({"summary": summary, "events": events}, open(prefix + "_events.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
