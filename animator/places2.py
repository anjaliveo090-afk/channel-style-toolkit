"""More sets and props for news stories (boardroom, trading floor, stock chart, newspaper, filing, corkboard,
sports field, stage with a jacket, car + key, envelope, laptop email). Same look rules as places.py.
Every set returns {"floor": y}. Newspaper/filing are generic (no real mastheads or logos)."""
import math
import random

import cairo

from places import _grad, _rect, _text, glow
from sets import _fill_line, _slanted_font
from style import INK, _rrect, hexc

W, H = 1280, 720


# ------------------------------------------------------------------ boardroom at night
def boardroom(ctx, t, lamp=True):
    floor = 600
    ctx.set_source(_grad(ctx, 0, 0, 0, H, [(0, "#2a1810"), (1, "#140a06")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    for x in range(-W, 2 * W, 110):
        ctx.rectangle(x, 0, 6, floor)
        ctx.set_source_rgba(0, 0, 0, 0.35)
        ctx.fill()
    # window to night city
    ctx.save()
    ctx.rectangle(360, 60, 560, 260)
    ctx.clip()
    ctx.set_source(_grad(ctx, 0, 60, 0, 320, [(0, "#0a1230"), (1, "#26305e")]))
    ctx.paint()
    rnd = random.Random(8)
    x = 360
    while x < 920:
        bw, bh = 30 + rnd.random() * 60, 60 + rnd.random() * 160
        ctx.rectangle(x, 320 - bh, bw, bh)
        ctx.set_source_rgb(*hexc("#151d40"))
        ctx.fill()
        for wy in range(int(330 - bh), 315, 16):
            for wx in range(int(x + 6), int(x + bw - 6), 12):
                if rnd.random() < 0.4:
                    ctx.rectangle(wx, wy, 5, 7)
                    ctx.set_source_rgba(1, 0.86, 0.5, 0.8 + 0.2 * math.sin(t * 3 + wx))
                    ctx.fill()
        x += bw + 4
    ctx.restore()
    ctx.rectangle(360, 60, 560, 260)
    ctx.set_source_rgb(*hexc("#0e0805"))
    ctx.set_line_width(10)
    ctx.stroke()
    if lamp:
        fl = 1 + 0.03 * math.sin(t * 9)
        glow(ctx, 640, 380, 520 * fl, hexc("#ffcf80"), 0.45)
        ctx.move_to(640, -10)
        ctx.line_to(640, 300)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(4)
        ctx.stroke()
        ctx.move_to(570, 300)
        ctx.line_to(710, 300)
        ctx.line_to(680, 270)
        ctx.line_to(600, 270)
        ctx.close_path()
        _fill_line(ctx, hexc("#2f6b48"), 3)
    # long table (front edge)
    ctx.move_to(-40, floor - 40)
    ctx.line_to(W + 40, floor - 40)
    ctx.line_to(W + 40, H + 40)
    ctx.line_to(-40, H + 40)
    ctx.close_path()
    ctx.set_source(_grad(ctx, 0, floor - 40, 0, H, [(0, "#6b3a1e"), (1, "#3a1d0c")]))
    ctx.fill()
    ctx.rectangle(-40, floor - 44, W + 80, 10)
    ctx.set_source_rgb(*hexc("#8a4f28"))
    ctx.fill()
    for px in (300, 640, 980):
        _rect(ctx, px - 50, floor - 34, 100, 14, "#f4f1ea", 2)
    return {"floor": floor + 60, "table": floor - 40}


# ------------------------------------------------------------------ trading floor
def trading_floor(ctx, t, red=True, ticker="NVDA"):
    floor = 600
    ctx.set_source(_grad(ctx, 0, 0, 0, H, [(0, "#0d1626"), (1, "#060a12")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    rnd = random.Random(2)
    for r in range(2):
        for c in range(-1, 8):
            x, y = c * 180 + (r * 90), 70 + r * 170
            _rrect(ctx, x, y, 160, 110, 6)
            _fill_line(ctx, hexc("#111a2c"), 3)
            ctx.save()
            ctx.rectangle(x + 8, y + 8, 144, 94)
            ctx.clip()
            ctx.set_source_rgb(*hexc("#04121a"))
            ctx.paint()
            col = hexc("#ff4a3a") if (red and (c + r) % 3) else hexc("#3dff7a")
            ctx.move_to(x + 8, y + 30)
            v = 30.0
            for k in range(1, 15):
                v += rnd.uniform(-8, 10) if not red else rnd.uniform(-6, 12)
                ph = (k + t * 6) % 15
                ctx.line_to(x + 8 + k * 10, y + min(95, max(15, v)) + 2 * math.sin(ph))
            ctx.set_source_rgb(*col)
            ctx.set_line_width(3)
            ctx.stroke()
            ctx.restore()
    glow(ctx, 640, 260, 600, hexc("#ff5a4a") if red else hexc("#5aff9a"), 0.12)
    # ticker strip
    ctx.rectangle(-W, 420, 3 * W, 44)
    ctx.set_source_rgb(*hexc("#05070c"))
    ctx.fill()
    _slanted_font(ctx, 30)
    ctx.set_source_rgb(*(hexc("#ff4a3a") if red else hexc("#3dff7a")))
    tw = ctx.text_extents(ticker).x_advance
    unit = tw + 90                                  # "NVDA" + a drawn arrow (the font has no arrow glyph)
    x = -W - ((t * 140) % unit)
    while x < 2 * W:
        ctx.move_to(x, 452)
        ctx.show_text(ticker)
        ax = x + tw + 26
        if red:
            ctx.move_to(ax - 11, 432)
            ctx.line_to(ax + 11, 432)
            ctx.line_to(ax, 450)
        else:
            ctx.move_to(ax - 11, 450)
            ctx.line_to(ax + 11, 450)
            ctx.line_to(ax, 432)
        ctx.close_path()
        ctx.fill()
        x += unit
    ctx.rectangle(-W, floor - 40, 3 * W, H)
    ctx.set_source(_grad(ctx, 0, floor - 40, 0, H, [(0, "#2a2f3a"), (1, "#14171e")]))
    ctx.fill()
    return {"floor": floor + 80}


# ------------------------------------------------------------------ stock chart (big screen)
def stock_chart(ctx, k, values, ticker="NVDA", price=None, change=None, x=150, y=110, w=980, h=480, bg=True):
    """Line chart drawn left->right as k goes 0..1; last point gets a price tag."""
    if bg:
        _rrect(ctx, x - 20, y - 20, w + 40, h + 40, 14)
        _fill_line(ctx, hexc("#0b1220"), 5)
    ctx.set_source_rgba(1, 1, 1, 0.07)
    ctx.set_line_width(2)
    for i in range(1, 5):
        ctx.move_to(x, y + h * i / 5)
        ctx.line_to(x + w, y + h * i / 5)
        ctx.stroke()
    _slanted_font(ctx, 40)
    ctx.move_to(x + 10, y + 46)
    ctx.set_source_rgb(0.85, 0.9, 1)
    ctx.show_text(ticker)
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1

    def P(i):
        return x + w * i / (len(values) - 1), y + 70 + (h - 100) * (1 - (values[i] - lo) / span)
    kk = max(0.0, min(1.0, k))
    n = (len(values) - 1) * kk
    i0 = int(n)
    pts = [P(i) for i in range(i0 + 1)]
    if i0 < len(values) - 1:
        a, b = P(i0), P(i0 + 1)
        f = n - i0
        pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    down = values[-1] < values[0]
    col = hexc("#ff4a3a") if down else hexc("#3dff7a")
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_source_rgb(*col)
    ctx.set_line_width(7)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    ex, ey = pts[-1]
    glow(ctx, ex, ey, 60, col, 0.6)
    ctx.arc(ex, ey, 9, 0, 2 * math.pi)
    ctx.set_source_rgb(*col)
    ctx.fill()
    if kk >= 1 and price:
        _rrect(ctx, ex - 220, ey + 20, 200, 90, 10)
        _fill_line(ctx, col, 3)
        _text(ctx, price, ex - 120, ey + 62, 40, "#ffffff")
        if change:
            _text(ctx, change, ex - 120, ey + 98, 28, "#ffffff")


# ------------------------------------------------------------------ newspaper slamming in
def newspaper(ctx, k, headline, sub="", paper="THE DAILY LEDGER", x=640, y=360, angle=-0.06, s=1.0):
    """Generic newspaper spins in and lands (~0.35 s). Never a real masthead."""
    if k <= 0:
        return
    p = min(1.0, k / 0.35)
    e = 1 - (1 - p) ** 3
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle + (1 - e) * 6.0)
    sc = s * (0.15 + 0.85 * e)
    ctx.scale(sc, sc)
    w, h = 760, 500
    ctx.rectangle(-w / 2 + 14, -h / 2 + 16, w, h)
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.fill()
    ctx.rectangle(-w / 2, -h / 2, w, h)
    _fill_line(ctx, hexc("#f3efe3"), 4)
    _text(ctx, paper, 0, -h / 2 + 62, 52)
    ctx.rectangle(-w / 2 + 30, -h / 2 + 80, w - 60, 4)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    size = 54 if len(headline) < 26 else 42
    words, lines, cur = headline.split(), [], ""
    for wd in words:
        if len(cur + " " + wd) > (24 if size == 54 else 32):
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    for i, ln in enumerate(lines[:3]):
        _text(ctx, ln, 0, -h / 2 + 160 + i * size * 1.1, size, "#1a1010")
    if sub:
        _text(ctx, sub, 0, -h / 2 + 170 + len(lines[:3]) * size * 1.1, 28, "#5a4a40")
    ctx.set_source_rgba(0.3, 0.25, 0.2, 0.35)
    ctx.set_line_width(3)
    for c in range(3):
        for r in range(5):
            yy = h / 2 - 150 + r * 24
            ctx.move_to(-w / 2 + 40 + c * 240, yy)
            ctx.line_to(-w / 2 + 230 + c * 240, yy)
            ctx.stroke()
    ctx.restore()


# ------------------------------------------------------------------ filing document (8-K style, generic)
def filing(ctx, k, title, lines, highlight=None, x=640, y=380, s=1.0, cps=40):
    """Official filing on a desk; lines type on (k s); `highlight` = index of a line to highlight."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    w, h = 640, 560
    ctx.rectangle(-w / 2 + 12, -h / 2 + 14, w, h)
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.fill()
    ctx.rectangle(-w / 2, -h / 2, w, h)
    _fill_line(ctx, hexc("#fbfaf6"), 4)
    _text(ctx, title, 0, -h / 2 + 70, 46)
    ctx.rectangle(-w / 2 + 40, -h / 2 + 92, w - 80, 3)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    n = int(max(0, k) * cps)
    yy = -h / 2 + 150
    for i, ln in enumerate(lines):
        m = min(len(ln), n)
        n -= m
        if highlight == i and m == len(ln):
            _slanted_font(ctx, 30)
            e = ctx.text_extents(ln)
            ctx.rectangle(-w / 2 + 44, yy - 30, e.x_advance + 12, 40)
            ctx.set_source_rgba(1, 0.88, 0.2, 0.75)
            ctx.fill()
        _text(ctx, ln[:m], -w / 2 + 50, yy, 30, "#2a1a10", center=False)
        yy += 52
    ctx.restore()


# ------------------------------------------------------------------ corkboard
def corkboard(ctx, t):
    ctx.set_source(_grad(ctx, 0, 0, 0, H, [(0, "#b07a40"), (1, "#8a5a2c")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    rnd = random.Random(5)
    for _ in range(900):
        ctx.arc(rnd.random() * W, rnd.random() * H, 1.5, 0, 6.3)
        ctx.set_source_rgba(0.35, 0.2, 0.08, 0.35)
        ctx.fill()
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(*hexc("#5a3a1c"))
    ctx.set_line_width(30)
    ctx.stroke()
    return {"floor": None}


def pinned_photo(ctx, x, y, draw, label=None, angle=0.0, w=240, h=200):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.rectangle(-w / 2 + 6, -h / 2 + 8, w, h + 40)
    ctx.set_source_rgba(0, 0, 0, 0.3)
    ctx.fill()
    ctx.rectangle(-w / 2, -h / 2, w, h + 40)
    _fill_line(ctx, hexc("#fafaf6"), 3)
    ctx.save()
    ctx.rectangle(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24)
    ctx.clip()
    draw(ctx, w - 24, h - 24, -w / 2 + 12, -h / 2 + 12)
    ctx.restore()
    if label:
        _text(ctx, label, 0, h / 2 + 26, 26)
    ctx.arc(0, -h / 2 + 4, 9, 0, 6.3)
    _fill_line(ctx, hexc("#d8342a"), 2)
    ctx.restore()


def red_string(ctx, a, b, k=1.0):
    p = max(0.0, min(1.0, k))
    mx, my = (a[0] + b[0]) / 2, max(a[1], b[1]) + 40
    pts = []
    for i in range(31):
        tt = i / 30 * p
        pts.append(((1 - tt) ** 2 * a[0] + 2 * (1 - tt) * tt * mx + tt * tt * b[0],
                    (1 - tt) ** 2 * a[1] + 2 * (1 - tt) * tt * my + tt * tt * b[1]))
    ctx.move_to(*pts[0])
    for q in pts[1:]:
        ctx.line_to(*q)
    ctx.set_source_rgb(*hexc("#c8241c"))
    ctx.set_line_width(4)
    ctx.stroke()


# ------------------------------------------------------------------ sports field
def sports_field(ctx, t):
    floor = 600
    ctx.set_source(_grad(ctx, 0, 0, 0, 330, [(0, "#1a2a50"), (1, "#3a4a7a")]))
    ctx.rectangle(-W, -H, 3 * W, H + 330)
    ctx.fill()
    rnd = random.Random(3)
    for r in range(4):
        for c in range(40):
            x = c * 36 - 30 + (r % 2) * 18
            y = 200 + r * 30
            ctx.arc(x, y, 12, 0, 6.3)
            ctx.set_source_rgb(*rnd.choice([hexc("#c8502e"), hexc("#3e6fa8"), hexc("#e0a23a"), hexc("#5c8a3c")]))
            ctx.fill()
    for lx in (200, 1080):
        glow(ctx, lx, 40, 300, hexc("#ffffff"), 0.4)
    ctx.rectangle(-W, 330, 3 * W, H)
    ctx.set_source(_grad(ctx, 0, 330, 0, H, [(0, "#3f9a4a"), (1, "#2a7a34")]))
    ctx.fill()
    for k in range(6):
        ctx.rectangle(-W, 330 + k * 70, 3 * W, 35)
        ctx.set_source_rgba(1, 1, 1, 0.05)
        ctx.fill()
    ctx.move_to(-W, 470)
    ctx.line_to(2 * W, 470)
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(5)
    ctx.stroke()
    return {"floor": floor + 20}


# ------------------------------------------------------------------ stage with a jacket on a stand
def stage(ctx, t, jacket=True, mark=True, screen=True, chip=True):
    floor = 560
    ctx.set_source_rgb(0.02, 0.02, 0.04)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    if screen:
        _rrect(ctx, 290, 60, 700, 330, 12)
        ctx.set_source(_grad(ctx, 0, 60, 0, 390, [(0, "#0b3a22"), (1, "#05160c")]))
        ctx.fill()
        if chip:
            glow(ctx, 640, 225, 200, hexc("#7dff8a"), 0.35 + 0.1 * math.sin(t * 2))
            _rrect(ctx, 560, 150, 160, 150, 12)
            _fill_line(ctx, hexc("#1d2a20"), 4)
            _rrect(ctx, 590, 180, 100, 90, 8)
            _fill_line(ctx, hexc("#7dff8a"), 3)
    g = cairo.LinearGradient(0, -100, 0, floor)
    g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.0)
    g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0.22)
    ctx.move_to(580, -100)
    ctx.line_to(700, -100)
    ctx.line_to(900, floor)
    ctx.line_to(380, floor)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()
    ctx.rectangle(-W, floor, 3 * W, H)
    ctx.set_source(_grad(ctx, 0, floor, 0, H, [(0, "#2a1a10"), (1, "#100804")]))
    ctx.fill()
    ctx.save()
    ctx.translate(640, floor + 40)
    ctx.scale(260, 40)
    ctx.arc(0, 0, 1, 0, 6.3)
    ctx.restore()
    ctx.set_source_rgba(1, 0.95, 0.8, 0.25)
    ctx.fill()
    if mark:
        ctx.set_source_rgb(*hexc("#f2d23a"))
        ctx.set_line_width(9)
        for sd in (-1, 1):
            ctx.move_to(640 - 34, floor + 40 - 14 * sd)
            ctx.line_to(640 + 34, floor + 40 + 14 * sd)
            ctx.stroke()
    if jacket:
        leather_jacket(ctx, 640, floor - 40)
    return {"floor": floor + 40}


def leather_jacket(ctx, x, y, s=1.0):
    """Black leather jacket hanging on a stand (y = foot of the stand)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 0)
    ctx.line_to(0, -330)
    ctx.set_source_rgb(0.75, 0.75, 0.78)
    ctx.set_line_width(8)
    ctx.stroke()
    ctx.move_to(-50, 0)
    ctx.line_to(50, 0)
    ctx.stroke()
    ctx.move_to(-70, -300)
    ctx.curve_to(-80, -240, -90, -170, -80, -130)
    ctx.line_to(80, -130)
    ctx.curve_to(90, -170, 80, -240, 70, -300)
    ctx.curve_to(30, -320, -30, -320, -70, -300)
    ctx.close_path()
    g = cairo.LinearGradient(-80, 0, 80, 0)
    g.add_color_stop_rgb(0, 0.08, 0.08, 0.09)
    g.add_color_stop_rgb(0.45, 0.22, 0.22, 0.24)
    g.add_color_stop_rgb(1, 0.06, 0.06, 0.07)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.move_to(-30, -305)
    ctx.line_to(0, -230)
    ctx.line_to(30, -305)
    ctx.set_source_rgb(0.4, 0.4, 0.42)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.move_to(0, -230)
    ctx.line_to(0, -135)
    ctx.set_source_rgb(0.6, 0.6, 0.62)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.restore()


# ------------------------------------------------------------------ car + key
def car(ctx, x, y, s=1.0, col="#c8312c"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-170, 0)
    ctx.line_to(-170, -60)
    ctx.curve_to(-160, -80, -120, -82, -100, -82)
    ctx.line_to(-60, -130)
    ctx.line_to(70, -130)
    ctx.line_to(120, -82)
    ctx.curve_to(150, -80, 170, -70, 170, -50)
    ctx.line_to(170, 0)
    ctx.close_path()
    _fill_line(ctx, hexc(col), 5)
    for wx in (-50, 50):
        ctx.rectangle(wx - 40 + (5 if wx > 0 else 0), -122, 80 - 10, 38)
        _fill_line(ctx, hexc("#bfe3ff"), 3)
    for wx in (-105, 105):
        ctx.arc(wx, 0, 36, 0, 6.3)
        _fill_line(ctx, hexc("#222222"), 4)
        ctx.arc(wx, 0, 14, 0, 6.3)
        ctx.set_source_rgb(0.75, 0.75, 0.78)
        ctx.fill()
    ctx.restore()


def driveway(ctx, t):
    floor = 600
    ctx.set_source(_grad(ctx, 0, 0, 0, 420, [(0, "#8cc4e8"), (1, "#e7f1ee")]))
    ctx.rectangle(-W, -H, 3 * W, H + 420)
    ctx.fill()
    _rect(ctx, 760, 120, 520, 360, "#f2e6d0", 5)
    ctx.move_to(740, 130)
    ctx.line_to(1020, -20)
    ctx.line_to(1300, 130)
    ctx.close_path()
    _fill_line(ctx, hexc("#8a3a26"), 5)
    _rect(ctx, 880, 300, 160, 180, "#c8a070", 4)
    ctx.rectangle(-W, 420, 3 * W, H)
    ctx.set_source_rgb(*hexc("#8fb36a"))
    ctx.fill()
    ctx.move_to(300, 720)
    ctx.line_to(820, 480)
    ctx.line_to(1100, 480)
    ctx.line_to(1100, 720)
    ctx.close_path()
    ctx.set_source_rgb(*hexc("#b8b0a2"))
    ctx.fill()
    return {"floor": floor + 40}


def key_prop(ctx, x, y, s=1.0, glow_on=True):
    if glow_on:
        glow(ctx, x, y, 90 * s, hexc("#ffd060"), 0.5)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.arc(0, -22, 18, 0, 6.3)
    ctx.set_source_rgb(0.98, 0.78, 0.2)
    ctx.set_line_width(9)
    ctx.stroke()
    ctx.move_to(0, -4)
    ctx.line_to(0, 50)
    ctx.move_to(0, 34)
    ctx.line_to(14, 34)
    ctx.move_to(0, 46)
    ctx.line_to(12, 46)
    ctx.stroke()
    ctx.restore()


# ------------------------------------------------------------------ envelope with an official seal
def envelope(ctx, x, y, k, label="CONGRESS OF THE U.S.", s=1.0):
    if k <= 0:
        return
    p = min(1.0, k / 0.3)
    e = 1 - (1 - p) ** 3
    ctx.save()
    ctx.translate(x + (1 - e) * 700, y - (1 - e) * 120)
    ctx.rotate(-0.08 + (1 - e) * 0.8)
    ctx.scale(s, s)
    w, h = 460, 280
    ctx.rectangle(-w / 2, -h / 2, w, h)
    _fill_line(ctx, hexc("#efe6cf"), 4)
    ctx.move_to(-w / 2, -h / 2)
    ctx.line_to(0, 10)
    ctx.line_to(w / 2, -h / 2)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.arc(0, 10, 34, 0, 6.3)
    _fill_line(ctx, hexc("#a3161d"), 3)
    _text(ctx, label, 0, h / 2 - 26, 22)
    ctx.restore()


# ------------------------------------------------------------------ laptop with an email
def laptop_email(ctx, x, y, k, subject, body, cps=30, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    _rrect(ctx, -330, -230, 660, 420, 16)
    _fill_line(ctx, hexc("#2a2d34"), 5)
    ctx.rectangle(-305, -205, 610, 370)
    ctx.set_source_rgb(*hexc("#f7f8fb"))
    ctx.fill()
    ctx.rectangle(-305, -205, 610, 50)
    ctx.set_source_rgb(*hexc("#2f6b48"))
    ctx.fill()
    _text(ctx, "INBOX  (1)", -285, -170, 28, "#ffffff", center=False)
    _text(ctx, "FROM: THE FOUNDER", -280, -110, 26, "#5a5a5a", center=False)
    _text(ctx, subject, -280, -70, 30, "#1a1a1a", center=False)
    n = int(max(0, k) * cps)
    yy = -20
    for ln in body:
        m = min(len(ln), n)
        n -= m
        _text(ctx, ln[:m], -280, yy, 28, "#2a2a2a", center=False)
        yy += 42
    ctx.move_to(-380, 190)
    ctx.line_to(380, 190)
    ctx.line_to(330, 240)
    ctx.line_to(-330, 240)
    ctx.close_path()
    _fill_line(ctx, hexc("#3a3e46"), 4)
    ctx.restore()


# ------------------------------------------------------------------ top-down desk (documents always lie in a place)
def desk_top(ctx, t, mug=True, phone=True, seed=3, wood="#6b4226"):
    """Top-down wooden desk (V1 f1704: documents are shown on a desk, never on a flat colour).
    Animated so the frame is never still: coffee steam curls, the lamp pool breathes, the phone buzzes."""
    rnd = random.Random(seed)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.set_source_rgb(*hexc(wood))
    ctx.fill()
    for k in range(-4, 16):                       # planks + grain
        y = k * 92
        ctx.rectangle(-W, y, 3 * W, 3)
        ctx.set_source_rgba(0, 0, 0, 0.28)
        ctx.fill()
        for _ in range(5):
            gy = y + 10 + rnd.random() * 72
            ctx.move_to(-W, gy)
            for x in range(-W, 2 * W + 1, 160):
                ctx.line_to(x, gy + 5 * math.sin(x * 0.01 + gy))
            ctx.set_source_rgba(0, 0, 0, 0.07 + rnd.random() * 0.06)
            ctx.set_line_width(2)
            ctx.stroke()
    br = 0.32 + 0.025 * math.sin(t * 3.1) * math.sin(t * 1.3)   # lamp pool breathes
    glow(ctx, 640, 330, 760, hexc("#ffdf9a"), br)
    if mug:                                       # coffee mug, top view, with steam
        mx, my = 150, 150
        ctx.arc(mx + 8, my + 10, 70, 0, 2 * math.pi)
        ctx.set_source_rgba(0, 0, 0, 0.3)
        ctx.fill()
        ctx.arc(mx, my, 70, 0, 2 * math.pi)
        _fill_line(ctx, hexc("#e8e4da"), 4)
        ctx.arc(mx, my, 54, 0, 2 * math.pi)
        _fill_line(ctx, hexc("#4a2a16"), 3)
        ctx.arc(mx - 14, my - 16, 14, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.fill()
        _rrect(ctx, mx + 62, my - 18, 40, 36, 14)
        _fill_line(ctx, hexc("#e8e4da"), 4)
        for i in range(3):                        # steam wisps rise and fade in a loop
            ph = (t * 0.45 + i / 3) % 1.0
            ctx.move_to(mx - 20 + i * 20, my - 10)
            for j in range(1, 9):
                yy = my - 10 - j * 16 - ph * 60
                ctx.line_to(mx - 20 + i * 20 + 14 * math.sin(j * 0.8 + t * 2.4 + i), yy)
            ctx.set_source_rgba(1, 1, 1, 0.32 * (1 - ph))
            ctx.set_line_width(9)
            ctx.stroke()
    if phone:                                     # phone buzzes for 0.6 s every 4.5 s
        ph = (t + 1.7) % 4.5
        buzz = ph < 0.6
        sx = 4 * math.sin(t * 90) if buzz else 0
        ctx.save()
        ctx.translate(1120 + sx, 560)
        ctx.rotate(0.22)
        _rrect(ctx, -58, -108, 116, 216, 16)
        _fill_line(ctx, hexc("#202024"), 4)
        _rrect(ctx, -48, -94, 96, 188, 8)
        ctx.set_source_rgb(*(hexc("#9fd0ff") if buzz else hexc("#14161c")))
        ctx.fill()
        if buzz:
            for side in (-1, 1):
                for r in (0, 1):
                    ctx.move_to(side * (72 + r * 14), -30)
                    ctx.line_to(side * (80 + r * 14), 0)
                    ctx.line_to(side * (72 + r * 14), 30)
                    ctx.set_source_rgb(*INK)
                    ctx.set_line_width(4)
                    ctx.stroke()
        ctx.restore()
    ctx.save()                                    # pen + paper stack
    ctx.translate(1080, 150)
    ctx.rotate(-0.5)
    _rrect(ctx, -110, -9, 220, 18, 8)
    _fill_line(ctx, hexc("#1d3f8a"), 3)
    ctx.restore()
    for i in range(3):
        ctx.save()
        ctx.translate(160, 610)
        ctx.rotate(-0.1 + i * 0.07)
        ctx.rectangle(-150, -110, 300, 220)
        _fill_line(ctx, hexc("#f2eee2"), 3)
        ctx.restore()
    return {"floor": None}


def paper_shadow(ctx, x, y, w, h, angle=0.0, lift=14):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.rectangle(-w / 2 + lift * 0.8, -h / 2 + lift, w, h)
    ctx.set_source_rgba(0, 0, 0, 0.32)
    ctx.fill()
    ctx.restore()


PLACES2 = {"boardroom": boardroom, "trading_floor": trading_floor, "corkboard": corkboard,
           "sports_field": sports_field, "stage": stage, "driveway": driveway, "desk_top": desk_top}
