"""Stills of every explaining device: python3 animator/devices_sheet.py -> output/devices/devices.jpg"""
import sys
from pathlib import Path

import cairo
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import devices as D  # noqa: E402
import places as P  # noqa: E402
import render16 as R  # noqa: E402
import sets  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "output" / "devices"


def tile(draw):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    c = cairo.Context(s)
    draw(c)
    img = R.post(R.flat(s))
    return Image.fromarray((img.clip(0, 1)[..., ::-1] * 255).astype("uint8")).resize((640, 360))


def bg(c, col="#2a3550"):
    c.set_source_rgb(*sets.hexc(col))
    c.paint()


def chip(c, x, y):
    c.rectangle(x - 34, y - 34, 68, 40)
    c.set_source_rgb(0.2, 0.7, 0.3)
    c.fill()


def car(c, x, y):
    c.rectangle(x - 50, y - 40, 100, 34)
    c.set_source_rgb(0.25, 0.5, 0.9)
    c.fill()
    for dx in (-30, 30):
        c.arc(x + dx, y - 6, 12, 0, 6.3)
        c.set_source_rgb(0.1, 0.1, 0.1)
        c.fill()


T = [
    ("name tag (typing)", lambda c: (bg(c, "#3b170b"), sets.name_tag(c, "FELIX BRANDT", 400, 300, 415, 108, 0.8))),
    ("counter box", lambda c: (bg(c), D.counter_box(c, 640, 330, 0.7, 8_000_000_000, sub="FROM EVERY $1"))),
    ("pie plate 95%", lambda c: (bg(c, "#6a1a1a"), D.pie_plate(c, 640, 380, 0.5, 95))),
    ("balance scale", lambda c: (bg(c, "#16244a"), D.balance_scale(c, 640, 330, 1.0, chip, car, label="ONE CHIP = ?", s=0.9))),
    ("stamp + strike", lambda c: (bg(c, "#f2e6d0"), P.whiteboard(c, 300, 150, 680, 300, ("CHINA CHIPS: OK",), 1.0),
                                  D.strike(c, 330, 200, 640, 0.3), D.stamp(c, 820, 400, 0.2, "BLOCKED"))),
    ("marker circle", lambda c: (bg(c, "#b07a40"), D.marker_circle(c, 640, 360, 150, 110, 0.35))),
    ("checkbox form", lambda c: (bg(c, "#c8312c"), D.checkbox_form(c, 640, 360, 0.6, ["DAY SCHOOL", "BOARDING", "REFORM PROGRAM"], 2))),
    ("sticky label", lambda c: (P.tech_office(c, 1.0), D.sticky_label(c, 640, 0.5, "A YEAR LATER"))),
    ("route arc on map", lambda c: (sets.paper_map(c, 1.0), D.route_arc(c, 300, 450, 1000, 300, 0.7, label0="SANTA CLARA", label1="WASHINGTON"))),
    ("live TV set", lambda c: D.live_tv(c, 0.0)),
    ("glow label", lambda c: (bg(c, "#081008"), D.glow_label(c, 640, 360, 0.5, "$ BILLIONS"))),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ims = [tile(fn) for _, fn in T]
    cols = 4
    sheet = Image.new("RGB", (640 * cols, 360 * ((len(ims) + cols - 1) // cols)), "white")
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype("/root/.fonts/Kalam-Bold.ttf", 26)
    for i, (im, (name, _)) in enumerate(zip(ims, T)):
        ImageDraw.Draw(im).text((10, 6), name, fill=(255, 255, 0), font=f, stroke_width=3, stroke_fill=(0, 0, 0))
        sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
    sheet.save(OUT / "devices.jpg", quality=86)
    print(OUT / "devices.jpg")


if __name__ == "__main__":
    main()
