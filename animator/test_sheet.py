"""Character test sheet: reference crops next to our characters, all views, all expressions,
and scene-light tints. Run: python3 animator/test_sheet.py -> output/test_sheet/*.png"""
import math
import sys
from pathlib import Path

import cairo
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from style import EXPRESSIONS, Char  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "test_sheet"

# original characters built on the reference construction rules
MAYA = Char(body="#e2805a", hair="bun", hair_col="#1d1716", collar="shirt", pants="#3a2f30", light=(-1, -0.15))
OMAR = Char(body="#c9c6c0", hair="bowl", hair_col="#1d1716", glasses="round", collar="shirt", pants="#2f3a55",
            light=(-1, -0.15))
RAY = Char(body="#7a5530", hair="short", hair_col="#3a2a20", collar="round", mustache="#3a2a20", creases=True,
           pants="#34302e", light=(-1, -0.2))
CAST = [MAYA, OMAR, RAY,
        Char(body="#23436b", hair="side", hair_col="#5a4030", glasses="rect", tie="#a3161d", lapels=True,
             collar="shirt", pants="#1b2333"),
        Char(body="#2f7a4f", hair="curly", hair_col="#2a1c14", glasses="round", collar="round", pants="#2c2f2a"),
        Char(body="#f0c33c", hair="long", hair_col="#6b3e22", collar="round", pants="#3b3330", earrings="#e8c050")]


def room(ctx, W, H):
    g = cairo.LinearGradient(0, 0, W, 0)
    g.add_color_stop_rgb(0, 0.95, 0.66, 0.38)
    g.add_color_stop_rgb(1, 0.86, 0.62, 0.42)
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H * 0.66)
    ctx.fill()
    ctx.set_source_rgb(0.62, 0.38, 0.2)
    ctx.rectangle(0, H * 0.66, W, H)
    ctx.fill()
    ctx.set_source_rgb(0.2, 0.08, 0.02)
    ctx.set_line_width(3)
    ctx.move_to(0, H * 0.66)
    ctx.line_to(W, H * 0.66)
    ctx.stroke()


def surf(W, H):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    return s, cairo.Context(s)


def label(img, text, x, y, size=22):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("/root/.fonts/Kalam-Bold.ttf", size)
    d.text((x, y), text, fill=(255, 255, 0), font=f, stroke_width=3, stroke_fill=(0, 0, 0))


def to_pil(s):
    s.flush()
    return Image.frombuffer("RGBA", (s.get_width(), s.get_height()), bytes(s.get_data()), "raw", "BGRA", 0, 1).convert("RGB")


def compare_living_room():
    """our two characters at the reference's measured positions (V1 1:01.5: heads ~ (467,369) and (790,362), R~50)"""
    W, H = 1280, 720
    s, c = surf(W, H)
    room(c, W, H)
    MAYA.draw(c, 467, 650, 1.27, expr="happy", t=0.3, look=0.35)
    OMAR.draw(c, 790, 645, 1.27, expr="happy", t=1.0, look=-0.3)
    ours = to_pil(s)
    ref = Image.open(ROOT / "output/v1_peek/f_61.5.png").convert("RGB")
    a = ref.crop((380, 250, 900, 700))
    b = ours.crop((380, 250, 900, 700))
    out = Image.new("RGB", (a.width * 2 + 10, a.height), "white")
    out.paste(a, (0, 0))
    out.paste(b, (a.width + 10, 0))
    label(out, "REFERENCE", 10, 8)
    label(out, "OURS", a.width + 20, 8)
    out.save(OUT / "1_compare_living_room.png")


def views():
    W, H = 1500, 560
    s, c = surf(W, H)
    room(c, W, H)
    poses = [("front", dict(look=0)), ("3/4 right", dict(look=0.5)), ("3/4 left", dict(look=-0.5)),
             ("side right", dict(look=1.0)), ("back", dict(pose="back")), ("walk", dict(pose="walk", t=0.35)),
             ("point", dict(arms="point_r", look=0.6)), ("hold paper", dict(arms="hold", item="paper", item_hand="r"))]
    for i, (name, kw) in enumerate(poses):
        ch = CAST[i % len(CAST)]
        x = 95 + i * 185
        args = dict(expr="neutral", t=0.5)
        args.update(kw)
        ch.draw(c, x, 500, 1.4, **args)
    img = to_pil(s)
    for i, (name, _) in enumerate(poses):
        label(img, name, 40 + i * 185, 10, 20)
    img.save(OUT / "2_views.png")


def expressions():
    W, H = 1500, 880
    s, c = surf(W, H)
    c.set_source_rgb(0.95, 0.72, 0.48)
    c.paint()
    for i, e in enumerate(EXPRESSIONS):
        ch = CAST[i % 3]
        x = 75 + (i % 8) * 185
        ch.draw(c, x, 400 + (i // 8) * 440, 1.5, expr=e, t=0.42, shadow=False)
    img = to_pil(s)
    for i, e in enumerate(EXPRESSIONS):
        label(img, e, 30 + (i % 8) * 185, 405 + (i // 8) * 440, 20)
    img.save(OUT / "3_expressions.png")


def night():
    W, H = 900, 500
    s, c = surf(W, H)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.08, 0.12, 0.25)
    g.add_color_stop_rgb(1, 0.03, 0.05, 0.12)
    c.set_source(g)
    c.paint()
    a = Char(body="#1c1c22", hair="bowl", hair_col="#111", collar="shirt", lapels=True).scene(
        ambient=(0.62, 0.68, 0.9), rim="#bcd4ff", light=(0.6, -1))
    b = Char(body="#3c5a80", hair="bowl", hair_col="#111", glasses="round", collar="round").scene(
        ambient=(0.62, 0.68, 0.9), rim="#bcd4ff", light=(-0.6, -1))
    a.draw(c, 330, 460, 2.0, expr="smirk", t=0.3, look=0.4)
    b.draw(c, 600, 460, 2.0, expr="blush", t=0.3, look=-0.4, arms="hold", item="paper", item_hand="l")
    img = to_pil(s)
    label(img, "night / blue scene light", 10, 8)
    img.save(OUT / "4_night.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    compare_living_room()
    views()
    expressions()
    night()
    print(OUT)
