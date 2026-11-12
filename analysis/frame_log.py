#!/usr/bin/env python3
"""Dense contact sheets for frame-by-frame study: N frames per second, 2 s per row,
each frame stamped with its time and the subtitle line being spoken.
Usage: frame_log.py video.mp4 [subs.srt] out_prefix [fps=4] [seconds_per_sheet=10]"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assembler"))
from assemble import parse_srt  # noqa: E402

TW = 120


def main(video, srt, prefix, fps=4, per_sheet=10):
    cues = parse_srt(srt) if srt else []
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", video], capture_output=True, text=True).stdout.split(",")
    w, h = int(probe[0]), int(probe[1])
    th = int(TW * h / w) // 2 * 2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale={TW}:{th}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, th, TW, 3)
    font = ImageFont.load_default(size=11)
    cols = 2 * fps
    per = per_sheet * fps
    for n in range(0, len(frames), per):
        chunk = frames[n:n + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (TW + 2), rows * (th + 30)), "white")
        d = ImageDraw.Draw(sheet)
        for k, f in enumerate(chunk):
            t = (n + k) / fps
            x, y = (k % cols) * (TW + 2), (k // cols) * (th + 30)
            sheet.paste(Image.fromarray(f), (x, y))
            line = next((c for a, b, c in cues if a <= t < b), "")
            d.text((x + 2, y + th + 1), f"{t:.2f}", fill="red", font=font)
            d.text((x + 2, y + th + 14), line[:20], fill="blue", font=font)
        sheet.save(f"{prefix}_{n // fps:03d}s.png")


if __name__ == "__main__":
    a = sys.argv[1:]
    srt = a[1] if len(a) > 2 and a[1].endswith(".srt") else None
    rest = a[2:] if srt else a[1:]
    main(a[0], srt, rest[0], *(int(x) for x in rest[1:]))
