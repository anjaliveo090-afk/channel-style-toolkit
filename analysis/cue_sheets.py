#!/usr/bin/env python3
"""One frame per SRT line (start, middle, end) with the line printed under it,
so each sentence can be matched to its visual. Usage: cue_sheets.py video.mp4 subs.srt out_prefix"""
import subprocess, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assembler"))
from assemble import parse_srt

TW = 200


def grab(video, t):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                          "-vf", f"scale={TW}:-1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(out)).convert("RGB")


def main(video, srt, prefix, per_sheet=12):
    cues = parse_srt(srt)
    font = ImageFont.load_default(size=14)
    for n in range(0, len(cues), per_sheet):
        chunk = cues[n:n + per_sheet]
        tiles = []
        for k, (a, b, txt) in enumerate(chunk, n + 1):
            ims = [grab(video, a + 0.05), grab(video, (a + b) / 2), grab(video, max(a, b - 0.08))]
            h = ims[0].height
            tile = Image.new("RGB", (TW * 3 + 8, h + 70), "white")
            for i, im in enumerate(ims):
                tile.paste(im, (i * (TW + 4), 0))
            d = ImageDraw.Draw(tile)
            d.text((4, h + 4), f"#{k} {a:.1f}-{b:.1f}s", fill="red", font=font)
            for j, line in enumerate(textwrap.wrap(txt, 70)[:3]):
                d.text((4, h + 20 + j * 16), line, fill="black", font=font)
            tiles.append(tile)
        cols = 2
        rows = (len(tiles) + cols - 1) // cols
        W, H = tiles[0].size
        sheet = Image.new("RGB", (W * cols, H * rows), "grey")
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * W, (i // cols) * H))
        sheet.save(f"{prefix}_{n // per_sheet + 1}.jpg", quality=85)
        print(f"{prefix}_{n // per_sheet + 1}.jpg")


if __name__ == "__main__":
    main(*sys.argv[1:4])
