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
import places as P  # noqa: E402
import places2 as P2  # noqa: E402
import render16 as R  # noqa: E402
import sets  # noqa: E402

W, H = 1280, 720
FONT = "DejaVu Sans"   # closest installed match to the reference caps (widths within 2%)


def heavy_text(c, txt, x, y, size, col, outline=14, shadow=12):
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
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


def ray_burst(c, x, y, r, n=14, col="#7dff3a", a=0.5):
    for i in range(n):
        ang = i * 2 * math.pi / n + 0.2
        c.move_to(x, y)
        c.line_to(x + r * math.cos(ang - 0.06), y + r * math.sin(ang - 0.06))
        c.line_to(x + r * math.cos(ang + 0.06), y + r * math.sin(ang + 0.06))
        c.close_path()
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *sets.hexc(col), a)
    g.add_color_stop_rgba(1, *sets.hexc(col), 0)
    c.set_source(g)
    c.fill()


def glowing_email(c, x, y, s=1.0, angle=-0.18):
    """the Sunday memo: an envelope torn open, green light bursting out (one prop, like the reference)"""
    sets.glow(c, x, y, 260 * s, sets.hexc("#6ad822"), 0.75)
    ray_burst(c, x, y - 20 * s, 330 * s)
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    c.scale(s, s)
    c.rectangle(-70, -150, 140, 120)                       # the letter sliding out
    sets._fill_line(c, sets.hexc("#fbf8ef"), 5)
    for i in range(4):
        c.rectangle(-50, -130 + i * 22, 100 - (i == 3) * 40, 7)
        c.set_source_rgb(*sets.hexc("#3a3a3a"))
        c.fill()
    c.rectangle(-120, -70, 240, 150)                       # envelope
    sets._fill_line(c, sets.hexc("#f2ead6"), 6)
    c.move_to(-120, -70)
    c.line_to(0, 20)
    c.line_to(120, -70)
    c.set_source_rgb(*sets.INK)
    c.set_line_width(5)
    c.stroke()
    c.restore()
    rnd = np.random.default_rng(3)                        # paper fragments flying out
    for fx, fy, fr in rnd.random((6, 3)):
        px, py = x + (fx - 0.5) * 420 * s, y - 120 * s - fy * 200 * s
        c.save()
        c.translate(px, py)
        c.rotate(fr * 3)
        c.rectangle(-12, -8, 24, 16)
        sets._fill_line(c, sets.hexc("#d8ffb8"), 3)
        c.restore()


def bokeh(c, seed=5):
    rnd = np.random.default_rng(seed)
    for x0, y0, r0, w in rnd.random((26, 4)):
        col = "#ffb24a" if w < 0.7 else "#ff5a3a"
        sets.glow(c, 60 + x0 * 1160, 180 + y0 * 420, 18 + r0 * 46, sets.hexc(col), 0.55)


def fit_text(c, parts, x_max_w, cap_target):
    """size so the whole line fits x_max_w with cap height <= cap_target"""
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(100)
    cap = -c.text_extents("H").y_bearing / 100
    adv = sum(c.text_extents(t).x_advance for t, _ in parts) / 100
    return min(cap_target / cap, x_max_w / adv)


def main(out, hook="ONE EMAIL.", number="-$428 BILLION"):
    bg, fg, ov = R.layers()
    # ---- background: night office, hard blur, warm lamp bokeh, dark (reference: 52-62% of pixels < 0.2 lum)
    c = cairo.Context(bg)
    R.cam(c, 1.25, 640, 330)
    P.night_office(c, 1.0)
    c.identity_matrix()
    c.rectangle(0, 0, W, H)
    c.set_source_rgba(0, 0, 0, 0.45)
    c.fill()
    bokeh(c)
    # ---- the one face, huge (head ~55% H, centre 0.33 W / 0.55 H), turned to the prop, sweating
    c = cairo.Context(fg)
    jensen = n.CAST["JENSEN"]
    jensen.scene(ambient=(0.95, 0.92, 0.98), rim="#a8ff7a")
    jensen.draw(c, 420, 400 + 4.0 * 40 * 6.0, 6.0, pose="sit", expr="scared", look=0.3, lean=-0.03, t=1.0)
    glowing_email(c, 860, 560, 1.15)
    for (x, y, s_, a) in ((660, 300, 1.4, 0.35), (630, 420, 1.0, 0.5), (190, 330, 1.2, -0.4)):
        sweat(c, x, y, s_, a)
    # ---- one line of text across the top: white hook + red number, black stroke + drop shadow
    c = cairo.Context(ov)
    parts = [(hook + " ", "#f5f4ed"), (number, "#fd3b31")]
    size = fit_text(c, parts, 0.86 * W, 94)
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    total = sum(c.text_extents(t).x_advance for t, _ in parts)
    x = (W - total) / 2
    cap = -c.text_extents("H").y_bearing
    base = 0.11 * H + cap / 2
    for t, col in parts:
        x += heavy_text(c, t, x, base, size, col, outline=0.075 * size, shadow=0.09 * size)
    empty = R.surface()
    img = R.compose(bg, fg, empty, dof=8.0, bloom=1.1)
    img = R.post(img, grain=0.004)
    o = R.arr(ov)                                    # text goes on after the vignette: it stays full white/red
    img = np.clip(img, 0, 1) * (1 - o[..., 3:4]) + o[..., :3]
    img = np.clip(img, 0, 1)
    small = cv2.resize((img * 255).astype(np.uint8), (1280, 720), interpolation=cv2.INTER_AREA)
    out = Path(out)
    cv2.imwrite(str(out), small)
    cv2.imwrite(str(out.with_suffix(".jpg")), small, [cv2.IMWRITE_JPEG_QUALITY, 93])
    print("wrote", out, out.with_suffix(".jpg"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else n.OUT / "thumbnail.png")
