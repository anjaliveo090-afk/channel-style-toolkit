"""Thumbnail for the Nvidia CEO story, built to the measured thumbnail formula (channel_breakdown.md A2):
top: 2-4 words in heavy sans caps, a red dollar figure + a white noun; middle: the main character with an
extreme expression (shock, sweat) + one symbolic prop (the jacket on its stand, the chip in the spy's hand);
background: a dramatic lit setting. Original characters only, no real-person likeness.

  python3 animator/thumbnail.py [out.png]   -> 1280x720 png + jpg (rendered at 2x, downscaled)
"""
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("PB_SCALE", "2")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cairo  # noqa: E402
import cv2  # noqa: E402
import numpy as np  # noqa: E402

import nvidia_ceo as n  # noqa: E402
import places2 as P2  # noqa: E402
import render16 as R  # noqa: E402
import sets  # noqa: E402

W, H = 1280, 720
HEAVY = "Inter Display Black"


def heavy_text(c, txt, x, y, size, col, outline=14, shadow=12):
    c.select_font_face(HEAVY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    if shadow:
        c.move_to(x + shadow, y + shadow)
        c.text_path(txt)
        c.set_source_rgba(0, 0, 0, 0.55)
        c.fill()
    c.move_to(x, y)
    c.text_path(txt)
    c.set_source_rgb(0.02, 0.02, 0.03)
    c.set_line_width(outline)
    c.stroke_preserve()
    c.set_source_rgb(*sets.hexc(col))
    c.fill()
    return c.text_extents(txt).x_advance


def sweat(c, x, y, s=1.0, angle=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    c.scale(s, s)
    c.move_to(0, -34)
    c.curve_to(14, -10, 20, 4, 20, 12)
    c.arc(0, 12, 20, 0, math.pi)
    c.curve_to(-20, 4, -14, -10, 0, -34)
    c.close_path()
    sets._fill_line(c, sets.hexc("#9fd8ff"), 5)
    c.arc(-7, 8, 5, 0, 2 * math.pi)
    c.set_source_rgba(1, 1, 1, 0.9)
    c.fill()
    c.restore()


def chip(c, x, y, s=1.0, t=0.0):
    sets.glow(c, x, y, 150 * s, sets.hexc("#5aff7a"), 0.55)
    c.save()
    c.translate(x, y)
    c.rotate(-0.25)
    c.scale(s, s)
    for sd in (-1, 1):
        for i in range(-3, 4):
            c.rectangle(i * 18 - 5, sd * 60 - (0 if sd < 0 else 14), 10, 14)
            c.rectangle(sd * 60 - (0 if sd < 0 else 14), i * 18 - 5, 14, 10)
    c.set_source_rgb(*sets.hexc("#c9a032"))
    c.fill()
    sets._rrect(c, -60, -60, 120, 120, 10)
    sets._fill_line(c, sets.hexc("#153a1f"), 6)
    sets._rrect(c, -34, -34, 68, 68, 6)
    sets._fill_line(c, sets.hexc("#3dff7a"), 4)
    c.restore()


def main(out):
    bg, fg, ov = R.layers()
    # ---- background: night boardroom, darkened, lit cold from the window and hot red from the right
    c = cairo.Context(bg)
    R.cam(c, 1.3, 640, 330)
    P2.boardroom(c, 0.0)
    c.identity_matrix()
    c.rectangle(0, 0, W, H)
    c.set_source_rgba(0, 0, 0, 0.5)
    c.fill()
    sets.glow(c, 1050, 420, 760, sets.hexc("#ff3a2a"), 0.42)
    sets.glow(c, 230, 260, 640, sets.hexc("#4a8aff"), 0.32)
    # ---- middle: the jacket on its stand, the spy behind with the chip, the founder in front in shock
    c = cairo.Context(fg)
    P2.leather_jacket(c, 1130, 700, 1.45)
    alice = n.CAST["ALICE"]
    alice.scene(ambient=(0.85, 0.78, 1.0), rim="#ff7a5a")
    alice.draw(c, 950, 320 + 4.0 * 40 * 4.0, 4.0, pose="sit", expr="smirk", look=-0.35, arms="present_l", t=1.0)
    chip(c, 700, 630, 0.8)
    jensen = n.CAST["JENSEN"]
    jensen.scene(ambient=(0.95, 0.9, 1.0), rim="#9fd0ff")
    jensen.draw(c, 400, 430 + 4.0 * 40 * 5.7, 5.7, pose="sit", expr="scared", look=0.3, lean=-0.03, t=1.0)
    for (x, y, s, a) in ((640, 300, 1.3, 0.35), (600, 410, 1.0, 0.5), (190, 320, 1.1, -0.4)):
        sweat(c, x, y, s, a)
    # ---- top: heavy sans caps, white noun + red dollar figure
    c = cairo.Context(ov)
    heavy_text(c, "NVIDIA", 44, 150, 118, "#ffffff")
    heavy_text(c, "-$428 BILLION", 44, 290, 128, "#ff2a1e")
    img = R.compose(bg, fg, ov, dof=2.2, bloom=1.1)
    img = R.post(img, grain=0.004)
    img = np.clip(img, 0, 1)
    small = cv2.resize((img * 255).astype(np.uint8), (1280, 720), interpolation=cv2.INTER_AREA)
    out = Path(out)
    cv2.imwrite(str(out), small)
    cv2.imwrite(str(out.with_suffix(".jpg")), small, [cv2.IMWRITE_JPEG_QUALITY, 93])
    cv2.imwrite(str(out.with_name(out.stem + "_2x.png")), (img * 255).astype(np.uint8))
    print("wrote", out, out.with_suffix(".jpg"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else n.OUT / "thumbnail.png")
