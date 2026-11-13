"""Backgrounds, props and on-screen graphics for the Paper Billions style, measured on V1 frames
(1280x720). Colours are the medians sampled from the reference (see style_bible.md)."""
import math
import random

import cairo

from style import INK, _rrect, hexc, mix

SCRIPT = "Caveat Brush"   # black text cards + name tags (OFL, assets/fonts); drawn slanted ~11 deg
SLANT = -0.25             # x-skew (~14 deg) measured on V1 0:05
WIDEN = 1.12              # the reference letters are 12% wider than Caveat Brush


def glow(ctx, x, y, r, col, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(0.3, *col, a * 0.5)
    g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def _fill_line(ctx, col, w):
    ctx.set_source_rgb(*col)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(w)
    ctx.stroke()


# ------------------------------------------------------------------ restaurant pieces
def wood_wall(ctx, W=1280, H=720, rail_y=470, panel=(470, 870)):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *hexc("#1f1008"))
    g.add_color_stop_rgb(0.45, *hexc("#3b170b"))
    g.add_color_stop_rgb(1, *hexc("#2a0f07"))
    ctx.set_source(g)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    # recessed centre panel and vertical boards
    ctx.rectangle(panel[0], 30, panel[1] - panel[0], rail_y - 30)
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.fill()
    ctx.set_line_width(4)
    for x in range(-W, 2 * W, 95):
        ctx.move_to(x, -H)
        ctx.line_to(x, rail_y)
        ctx.set_source_rgba(0.05, 0.02, 0.01, 0.4)
        ctx.stroke()
    ctx.rectangle(-W, 18, 3 * W, 10)
    ctx.set_source_rgb(*hexc("#4a2210"))
    ctx.fill()
    ctx.rectangle(-W, rail_y, 3 * W, 14)
    ctx.set_source_rgb(*hexc("#5a2a12"))
    ctx.fill()
    ctx.rectangle(-W, rail_y + 14, 3 * W, H)
    ctx.set_source_rgb(*hexc("#2a0f07"))
    ctx.fill()


def night_window(ctx, x0, y0, x1, y1, t, seed=5):
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *hexc("#04071b"))
    g.add_color_stop_rgb(1, *hexc("#0c1a44"))
    ctx.set_source(g)
    ctx.paint()
    rnd = random.Random(seed)
    for _ in range(60):
        x, y = x0 + rnd.random() * (x1 - x0), y0 + rnd.random() * (y1 - y0)
        ctx.arc(x, y, 1.5 + rnd.random() * 2, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0.95, 0.75, 0.5 + 0.4 * rnd.random())
        ctx.fill()
    for _ in range(14):
        x, y = x0 + rnd.random() * (x1 - x0), y0 + rnd.random() * (y1 - y0)
        r = 18 + rnd.random() * 34
        tw = 0.5 + 0.5 * math.sin(t * 1.1 + x)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        c = rnd.choice([(0.3, 0.55, 0.55), (0.45, 0.6, 0.9), (0.85, 0.8, 0.6)])
        ctx.set_source_rgba(*c, 0.16 + 0.1 * tw)
        ctx.fill()
    ctx.restore()
    ctx.set_source_rgb(*hexc("#140804"))
    ctx.set_line_width(9)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.stroke()
    ctx.set_line_width(6)
    mx = (x0 + x1) / 2
    ctx.move_to(mx, y0)
    ctx.line_to(mx, y1)
    ctx.move_to(x0, (y0 + y1) * 0.5)
    ctx.line_to(x1, (y0 + y1) * 0.5)
    ctx.stroke()


def curtain(ctx, x0, x1, y_bot):
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgb(0, *hexc("#460b0c"))
    g.add_color_stop_rgb(0.45, *hexc("#d0201f"))
    g.add_color_stop_rgb(1, *hexc("#5a0c0e"))
    ctx.set_source(g)
    ctx.move_to(x0, -20)
    ctx.line_to(x1, -20)
    ctx.curve_to(x1 + 5, y_bot * 0.5, x1 - 5, y_bot * 0.8, x1, y_bot)
    ctx.line_to(x0, y_bot)
    ctx.close_path()
    ctx.fill()


def sconce(ctx, x, y, s=1.0):
    glow(ctx, x, y, 150 * s, hexc("#eea15b"), 0.38)
    ctx.set_source_rgb(*hexc("#3a1a08"))
    ctx.rectangle(x - 3 * s, y, 6 * s, 34 * s)
    ctx.fill()
    ctx.set_line_width(4 * s)
    ctx.move_to(x - 26 * s, y + 18 * s)
    ctx.curve_to(x - 20 * s, y + 34 * s, x + 20 * s, y + 34 * s, x + 26 * s, y + 18 * s)
    ctx.stroke()
    for d in (-26, 26):
        ctx.move_to(x + (d - 13) * s, y + 14 * s)
        ctx.line_to(x + (d + 13) * s, y + 14 * s)
        ctx.line_to(x + (d + 9) * s, y - 14 * s)
        ctx.line_to(x + (d - 9) * s, y - 14 * s)
        ctx.close_path()
        ctx.set_source_rgb(*hexc("#fde39a"))
        ctx.fill()


def booth_side(ctx, x0, x1, y0, H=720, studs_x=None, studs=(), flip=False):
    """Red velvet booth back with gold piping; studs down one edge."""
    ctx.new_path()
    r = 60
    if not flip:
        ctx.move_to(x0, H + 10)
        ctx.line_to(x0, y0 + r)
        ctx.curve_to(x0, y0, x0 + r, y0, x0 + r, y0)
        ctx.line_to(x1, y0)
        ctx.line_to(x1, H + 10)
    else:
        ctx.move_to(x1, H + 10)
        ctx.line_to(x1, y0 + r)
        ctx.curve_to(x1, y0, x1 - r, y0, x1 - r, y0)
        ctx.line_to(x0, y0)
        ctx.line_to(x0, H + 10)
    ctx.close_path()
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgb(0, *hexc("#8c0f15"))
    g.add_color_stop_rgb(0.5, *hexc("#65090f"))
    g.add_color_stop_rgb(1, *hexc("#4a060b"))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hexc("#c8963a"))
    ctx.set_line_width(14)
    ctx.stroke()
    ctx.set_line_width(4)
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.stroke()
    for y in studs:
        ctx.arc(studs_x, y, 7, 0, 2 * math.pi)
        ctx.set_source_rgb(*hexc("#b78c45"))
        ctx.fill_preserve()
        ctx.set_source_rgb(*hexc("#3a2408"))
        ctx.set_line_width(2)
        ctx.stroke()


def tablecloth(ctx, cx, top, rx, ry, H=720, glow_x=None):
    """Round table with a white cloth; lit warm-yellow around the candle, falling to tan."""
    gx = cx if glow_x is None else glow_x
    ctx.new_path()
    ctx.move_to(cx - rx, top)
    ctx.line_to(cx - rx * 0.92, H + 20)
    ctx.line_to(cx + rx * 0.92, H + 20)
    ctx.line_to(cx + rx, top)
    ctx.close_path()
    g = cairo.RadialGradient(gx, top, 10, gx, top + 60, rx)
    g.add_color_stop_rgb(0, *hexc("#fff8b0"))
    g.add_color_stop_rgb(0.35, *hexc("#f2dca0"))
    g.add_color_stop_rgb(1, *hexc("#a88a6a"))
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(0.35, 0.22, 0.12, 0.35)
    ctx.set_line_width(4)
    for k in (-0.8, -0.35, 0.3, 0.8):
        x = cx + k * rx
        ctx.move_to(x, top + 50)
        ctx.curve_to(x + 5, top + 100, x - 5, top + 140, x + 3, H + 20)
        ctx.stroke()
    ctx.new_path()
    ctx.save()
    ctx.translate(cx, top)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    g = cairo.RadialGradient(gx, top, 5, gx, top, rx)
    g.add_color_stop_rgb(0, *hexc("#fffbb8"))
    g.add_color_stop_rgb(0.45, *hexc("#f4e2ac"))
    g.add_color_stop_rgb(1, *hexc("#c9ae86"))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(5)
    ctx.stroke()


def plate(ctx, cx, cy, rx=105, ry=22):
    ctx.new_path()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    _fill_line(ctx, hexc("#f6efe0"), 3)
    ctx.new_path()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx * 0.72, ry * 0.65)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0.6, 0.5, 0.35, 0.35)
    ctx.set_line_width(2)
    ctx.stroke()
    # steak
    sx, sy = cx - rx * 0.05, cy - ry * 0.35
    ctx.new_path()
    ctx.move_to(sx - rx * 0.4, sy + ry * 0.2)
    ctx.curve_to(sx - rx * 0.42, sy - ry * 1.3, sx + rx * 0.42, sy - ry * 1.3, sx + rx * 0.4, sy + ry * 0.2)
    ctx.close_path()
    _fill_line(ctx, hexc("#9a2a0c"), 3)
    ctx.set_source_rgba(0.25, 0.05, 0.0, 0.6)
    ctx.set_line_width(3)
    for k in (-0.2, 0.0, 0.2):
        ctx.move_to(sx + rx * (k - 0.06), sy - ry * 0.55)
        ctx.line_to(sx + rx * (k + 0.06), sy - ry * 0.15)
        ctx.stroke()
    for px, col in ((sx + rx * 0.5, "#e8642a"), (sx + rx * 0.62, "#d9c23a")):
        ctx.arc(px, sy + ry * 0.1, ry * 0.32, 0, 2 * math.pi)
        _fill_line(ctx, hexc(col), 2)
    ctx.move_to(sx, sy - ry * 1.0)
    ctx.line_to(sx - 6, sy - ry * 1.6)
    ctx.line_to(sx + 7, sy - ry * 1.4)
    ctx.close_path()
    ctx.set_source_rgb(*hexc("#3e8c2a"))
    ctx.fill()


def standing_wine(ctx, x, base_y, h=150):
    bw, bh = h * 0.22, h * 0.42
    ctx.new_path()
    ctx.save()
    ctx.translate(x, base_y)
    ctx.scale(bw * 0.9, bw * 0.22)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    _fill_line(ctx, (0.94, 0.92, 0.86), 2.5)
    ctx.set_source_rgb(0.94, 0.92, 0.86)
    ctx.set_line_width(5)
    ctx.move_to(x, base_y)
    ctx.line_to(x, base_y - h * 0.5)
    ctx.stroke()
    top = base_y - h
    ctx.new_path()
    ctx.move_to(x - bw, top)
    ctx.curve_to(x - bw * 1.05, base_y - h * 0.38, x + bw * 1.05, base_y - h * 0.38, x + bw, top)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.new_path()
    ctx.move_to(x - bw * 0.97, top + bh * 0.4)
    ctx.curve_to(x - bw, base_y - h * 0.4, x + bw, base_y - h * 0.4, x + bw * 0.97, top + bh * 0.4)
    ctx.close_path()
    ctx.set_source_rgb(*hexc("#932a27"))
    ctx.fill()


def roses_candle(ctx, cx, base_y, t, s=1.0):
    """Glass vase holding a pillar candle, a bunch of red roses above. base_y = table level."""
    fl = 1 + 0.05 * math.sin(t * 15) + 0.03 * math.sin(t * 27)
    glow(ctx, cx, base_y - 70 * s, 300 * s * fl, hexc("#ffc45a"), 0.55)
    glow(ctx, cx, base_y - 55 * s, 190 * s, (1, 1, 0.82), 1.0)
    vw, vh = 52 * s, 110 * s
    ctx.new_path()
    _rrect(ctx, cx - vw, base_y - vh, 2 * vw, vh, 10 * s)
    ctx.set_source_rgba(1, 0.97, 0.8, 0.35)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK, 0.5)
    ctx.set_line_width(3 * s)
    ctx.stroke()
    ctx.rectangle(cx - 22 * s, base_y - 60 * s, 44 * s, 55 * s)
    ctx.set_source_rgb(*hexc("#fefeaa"))
    ctx.fill()
    for k in range(-2, 3):
        ctx.move_to(cx + k * 9 * s, base_y - vh)
        ctx.curve_to(cx + k * 12 * s, base_y - vh - 30 * s, cx + k * 16 * s, base_y - vh - 50 * s, cx + k * 18 * s, base_y - vh - 60 * s)
        ctx.set_source_rgb(*hexc("#3e7a2a"))
        ctx.set_line_width(3 * s)
        ctx.stroke()
    rr = 24 * s
    for (dx, dy) in ((-55, -150), (0, -158), (55, -150), (-30, -195), (30, -195), (0, -232), (-75, -112), (75, -112)):
        x, y = cx + dx * s * 0.95, base_y + dy * s * 0.98
        ctx.new_path()
        ctx.arc(x, y, rr, 0, 2 * math.pi)
        _fill_line(ctx, hexc("#fc301b"), 3 * s)
        ctx.new_path()
        ctx.arc(x + 2 * s, y + 2 * s, rr * 0.45, 0.3, 4.6)
        ctx.set_source_rgb(*hexc("#9d1208"))
        ctx.set_line_width(3 * s)
        ctx.stroke()


# ------------------------------------------------------------------ graphics (screen space)
def _slanted_font(ctx, size, family=SCRIPT):
    ctx.select_font_face(family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_matrix(cairo.Matrix(size * WIDEN, 0, SLANT * size, size, 0, 0))


def name_tag(ctx, text, x, y, w, h, k, accent="#7ab51d"):
    """Lower-third tag (measured frame by frame on V1 0:06): the dark box + accent bar appear first,
    then the name TYPES ON about one letter per frame. k is progress where 1.0 = 0.35 s
    (callers pass (t - start) / 0.35); full name shown by k ~ 1.4 (~0.5 s)."""
    if k <= 0:
        return
    a = min(1.0, k / 0.15)
    _rrect(ctx, x, y, w, h, 6)
    ctx.set_source_rgba(0.09, 0.06, 0.05, 0.86 * a)
    ctx.fill()
    ctx.rectangle(x, y, 9, h)
    ctx.set_source_rgba(*hexc(accent), a)
    ctx.fill()
    ctx.move_to(x - 4, y + h)
    ctx.line_to(x + 13, y + h)
    ctx.line_to(x + 4.5, y + h + 14)
    ctx.close_path()
    ctx.fill()
    n = max(0, min(len(text), int((k - 0.15) / 1.25 * len(text)) + 1)) if k > 0.15 else 0
    _slanted_font(ctx, h * 0.46)
    ctx.move_to(x + 34, y + h * 0.66)
    ctx.set_source_rgb(*hexc("#f4ecd6"))
    ctx.show_text(text[:n])


def pop_label(ctx, text, x, y, k, col="#e23b2e", size=64, angle=-0.06):
    """Hand-lettered label that pops in with overshoot (k = seconds since start)."""
    if k <= 0:
        return
    sc = (1 + 0.35 * math.exp(-k * 9) * math.cos(k * 22)) * min(1, k / 0.08)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(sc, sc)
    _slanted_font(ctx, size)
    ext = ctx.text_extents(text)
    ctx.move_to(-ext.x_advance / 2, ext.height / 2)
    ctx.text_path(text)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(0.08, 0.04, 0.03)
    ctx.set_line_width(size * 0.14)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc(col))
    ctx.fill()
    ctx.restore()


def text_card(ctx, text, t, W=1280, H=720, cps=16.0, size=64):
    """Black card, white slanted brush script typed on letter by letter, centred
    (measured V1 0:04-0:06: 64 px tall, 12% wide, ~14 deg slant at 720p; text centre y = 0.47 H)."""
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    n = max(0, min(len(text), int(t * cps) + 1)) if t >= 0 else 0
    _slanted_font(ctx, size)
    full = ctx.text_extents(text)
    ctx.move_to((W - full.x_advance) / 2, H * 0.47 + size * 0.28)
    ctx.set_source_rgb(0.98, 0.98, 0.98)
    ctx.show_text(text[:n])
    return n


# ------------------------------------------------------------------ maps, places, documents, effects
def paper_map(ctx, t, W=1280, H=720, seed=11, highlight=None):
    """Paper-map look (V1 0:53): light-blue sea, sand land with dark outline, soft white clouds.
    The land shapes are invented (stylised), not a real map. highlight = (x, y, r) region painted orange."""
    ctx.set_source_rgb(*hexc("#a9d3e3"))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    rnd = random.Random(seed)
    blobs = [(-200, 120, 520, 420), (380, -120, 560, 330), (640, 230, 420, 300), (1050, 40, 420, 520),
             (180, 560, 380, 260)]
    for bx, by, bw, bh in blobs:
        ctx.new_path()
        n = 26
        for k in range(n + 1):
            a = 2 * math.pi * k / n
            r = 0.5 + 0.08 * math.sin(a * 3 + bx) + 0.05 * math.sin(a * 7 + by) + rnd.uniform(-0.03, 0.03)
            px, py = bx + bw / 2 + math.cos(a) * bw * r, by + bh / 2 + math.sin(a) * bh * r
            (ctx.move_to if k == 0 else ctx.line_to)(px, py)
        ctx.close_path()
        ctx.set_source_rgb(*hexc("#efe2c2"))
        ctx.fill_preserve()
        ctx.set_source_rgb(*hexc("#5b4a32"))
        ctx.set_line_width(3)
        ctx.stroke()
    if highlight:
        hx, hy, hr = highlight
        ctx.new_path()
        for k in range(21):
            a = 2 * math.pi * k / 20
            r = hr * (0.8 + 0.2 * math.sin(a * 4 + 1))
            (ctx.move_to if k == 0 else ctx.line_to)(hx + math.cos(a) * r * 0.7, hy + math.sin(a) * r * 1.2)
        ctx.close_path()
        ctx.set_source_rgb(*hexc("#f29a3a"))
        ctx.fill_preserve()
        ctx.set_source_rgb(*hexc("#5b4a32"))
        ctx.set_line_width(3)
        ctx.stroke()
    for k in range(7):
        cx = (rnd.random() * 1600 - 160 + t * 12) % 1700 - 200
        cy = rnd.random() * 650
        for j in range(4):
            ctx.arc(cx + j * 38, cy + (j % 2) * -14, 34 + 6 * (j % 2), 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.55)
            ctx.fill()


def map_pin(ctx, x, y, k, label=None, col="#d8342a"):
    """Pin that drops in with overshoot (k = seconds since start) + hand-lettered label."""
    if k <= 0:
        return
    drop = max(0.0, 1 - k / 0.18)
    sc = 1 + 0.25 * math.exp(-k * 10) * math.sin(k * 30)
    ctx.save()
    ctx.translate(x, y - drop * 60)
    ctx.scale(sc, sc)
    ctx.move_to(0, 0)
    ctx.curve_to(-20, -26, -18, -52, 0, -52)
    ctx.curve_to(18, -52, 20, -26, 0, 0)
    _fill_line(ctx, hexc(col), 3)
    ctx.arc(0, -36, 7, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.restore()
    if label and k > 0.15:
        pop_label(ctx, label, x, y + 34, k - 0.15, col="#2b2b2b", size=34, angle=-0.03)


def mill_exterior(ctx, t, W=1280, H=720, ground=560):
    """Daylight paper mill in a pine forest: sky, far pines, red mill with chimney smoke."""
    g = cairo.LinearGradient(0, 0, 0, ground)
    g.add_color_stop_rgb(0, *hexc("#8cc4e8"))
    g.add_color_stop_rgb(1, *hexc("#e7f1ee"))
    ctx.set_source(g)
    ctx.rectangle(-W, -H, 3 * W, H + ground)
    ctx.fill()
    rnd = random.Random(4)
    for layer, (col, base, hgt) in enumerate((("#5f8a6a", ground - 40, 150), ("#3d6b4c", ground - 10, 190))):
        for _ in range(26):
            x = rnd.random() * (W + 400) - 200
            hh = hgt * (0.7 + rnd.random() * 0.5)
            ctx.move_to(x, base - hh)
            ctx.line_to(x - hh * 0.28, base)
            ctx.line_to(x + hh * 0.28, base)
            ctx.close_path()
            _fill_line(ctx, hexc(col), 2.5)
    ctx.rectangle(-W, ground, 3 * W, H)
    ctx.set_source_rgb(*hexc("#8fb36a"))
    ctx.fill()
    ctx.rectangle(-W, ground, 3 * W, 6)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    # mill
    mx, mw, mh = 360, 560, 250
    ctx.rectangle(mx, ground - mh, mw, mh)
    _fill_line(ctx, hexc("#b5482f"), 4)
    ctx.move_to(mx - 20, ground - mh)
    ctx.line_to(mx + mw / 2, ground - mh - 110)
    ctx.line_to(mx + mw + 20, ground - mh)
    ctx.close_path()
    _fill_line(ctx, hexc("#4a3a35"), 4)
    for r in range(2):
        for c in range(6):
            ctx.rectangle(mx + 30 + c * 88, ground - mh + 40 + r * 90, 50, 56)
            _fill_line(ctx, hexc("#f6f0dc"), 3)
    ctx.rectangle(mx + mw - 110, ground - mh - 190, 60, 200)
    _fill_line(ctx, hexc("#8a3a26"), 4)
    for k in range(5):
        ph = (t * 0.35 + k / 5) % 1
        r = 26 + ph * 50
        ctx.arc(mx + mw - 80 + ph * 70, ground - mh - 200 - ph * 220, r, 0, 2 * math.pi)
        ctx.set_source_rgba(0.97, 0.97, 0.97, 0.85 * (1 - ph))
        ctx.fill()
    _rrect(ctx, mx + mw / 2 - 110, ground - mh - 60, 220, 50, 8)
    _fill_line(ctx, hexc("#f4ecd6"), 3)
    _slanted_font(ctx, 34)
    ext = ctx.text_extents("PAPERWORKS")
    ctx.move_to(mx + mw / 2 - ext.x_advance / 2, ground - mh - 24)
    ctx.set_source_rgb(*INK)
    ctx.show_text("PAPERWORKS")


def contract_doc(ctx, x, y, w, h, amount, k_amount, t):
    """A contract on a desk; the dollar amount rolls up to `amount` (k_amount 0..1) in green."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.03)
    ctx.rectangle(-w / 2 + 12, -h / 2 + 14, w, h)
    ctx.set_source_rgba(0, 0, 0, 0.3)
    ctx.fill()
    ctx.rectangle(-w / 2, -h / 2, w, h)
    _fill_line(ctx, hexc("#fbf7ec"), 4)
    _slanted_font(ctx, 54)
    ext = ctx.text_extents("CONTRACT")
    ctx.move_to(-ext.x_advance / 2, -h / 2 + 80)
    ctx.set_source_rgb(*INK)
    ctx.show_text("CONTRACT")
    ctx.set_source_rgba(*INK, 0.35)
    ctx.set_line_width(3)
    for j in range(5):
        ctx.move_to(-w / 2 + 50, -h / 2 + 130 + j * 34)
        ctx.line_to(w / 2 - 50 - (j % 2) * 80, -h / 2 + 130 + j * 34)
        ctx.stroke()
    v = int(amount * (1 - (1 - min(1, max(0, k_amount))) ** 3))
    txt = f"${v:,}"
    _slanted_font(ctx, 78)
    ext = ctx.text_extents(txt)
    glow(ctx, 0, h / 2 - 95, 260, hexc("#9cff5a"), 0.25 * min(1, k_amount * 2))
    ctx.move_to(-ext.x_advance / 2, h / 2 - 70)
    ctx.text_path(txt)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(9)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc("#3d8b2f"))
    ctx.fill()
    ctx.move_to(w / 2 - 230, h / 2 - 25)
    ctx.curve_to(w / 2 - 190, h / 2 - 55, w / 2 - 150, h / 2 - 5, w / 2 - 110, h / 2 - 40)
    ctx.set_source_rgb(*hexc("#2a3f9a"))
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.restore()


def impact_flash(ctx, k, W=1280, H=720, cx=None, cy=None):
    """Manga speed-line burst (V1 4:13): white radial wedges on black, 2-3 frames (k = 0..1)."""
    if not 0 <= k <= 1:
        return
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    ctx.set_source_rgb(1, 1, 1) if k < 0.5 else ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    rnd = random.Random(int(k * 10))
    ctx.set_source_rgb(0, 0, 0) if k < 0.5 else ctx.set_source_rgb(1, 1, 1)
    for _ in range(46):
        a = rnd.random() * 2 * math.pi
        da = 0.02 + rnd.random() * 0.04
        r0 = 120 + rnd.random() * 160
        ctx.move_to(cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        ctx.line_to(cx + math.cos(a - da) * 1600, cy + math.sin(a - da) * 1600)
        ctx.line_to(cx + math.cos(a + da) * 1600, cy + math.sin(a + da) * 1600)
        ctx.close_path()
        ctx.fill()
