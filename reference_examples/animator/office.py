"""Office sets and props in the user's background style (their kitchen / airport
sheets): lavender ceiling tiles, tiled walls, warm tan floor, thick dark outlines,
soft gradients, warm pendant-lamp glow."""
import math
import random

import cairo

from engine import PI, W, H, clock_face, ellipse, glow, hexc, lerpc, rrect, src, text
from style2 import OUT, _darker, _lighter, _shade_fill

LW = 4.0


def _box(ctx, x, y, w, h, col, r=6, lw=LW):
    rrect(ctx, x, y, w, h, r)
    _shade_fill(ctx, _lighter(col, 0.12), _darker(col, 0.08), y, y + h, lw)


def room(ctx, x0, x1, ceil_y, floor_y, wall="#7cc08a", floor="#e8c9a0", ceil="#b9b6dc", tiles=True):
    """Back wall + ceiling + floor of a room seen from the front."""
    wall, floor, ceil = hexc(wall), hexc(floor), hexc(ceil)
    # ceiling with tile grid
    ctx.rectangle(x0, ceil_y - 900, x1 - x0, 900)
    _shade_fill(ctx, _darker(ceil, 0.06), ceil, ceil_y - 400, ceil_y, 0)
    ctx.set_source_rgba(*OUT, 0.35)
    ctx.set_line_width(2.5)
    for x in range(int(x0) - int(x0) % 150, int(x1), 150):
        ctx.move_to(x, ceil_y - 900)
        ctx.line_to(x + (x - W / 2) * 0.15, ceil_y)
    for y in range(int(ceil_y) - 900, int(ceil_y), 110):
        ctx.move_to(x0, y)
        ctx.line_to(x1, y)
    ctx.stroke()
    # wall
    ctx.rectangle(x0, ceil_y, x1 - x0, floor_y - ceil_y)
    g = cairo.LinearGradient(0, ceil_y, 0, floor_y)
    g.add_color_stop_rgb(0, *_darker(wall, 0.05))
    g.add_color_stop_rgb(0.5, *wall)
    g.add_color_stop_rgb(1, *_darker(wall, 0.12))
    ctx.set_source(g)
    ctx.fill()
    if tiles:
        ctx.set_source_rgba(*_lighter(wall, 0.35), 0.55)
        ctx.set_line_width(2)
        for x in range(int(x0) - int(x0) % 70, int(x1), 70):
            ctx.move_to(x, ceil_y)
            ctx.line_to(x, floor_y)
        for y in range(int(ceil_y), int(floor_y), 70):
            ctx.move_to(x0, y)
            ctx.line_to(x1, y)
        ctx.stroke()
    ctx.move_to(x0, ceil_y)
    ctx.line_to(x1, ceil_y)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(LW)
    ctx.stroke()
    # baseboard + floor tiles in perspective
    ctx.rectangle(x0, floor_y - 18, x1 - x0, 18)
    _shade_fill(ctx, _darker(wall, 0.35), _darker(wall, 0.45), floor_y - 18, floor_y, LW * 0.6)
    ctx.rectangle(x0, floor_y, x1 - x0, 1400)
    _shade_fill(ctx, floor, _darker(floor, 0.12), floor_y, floor_y + 700, 0)
    ctx.set_source_rgba(*_darker(floor, 0.3), 0.6)
    ctx.set_line_width(2)
    y, step = floor_y, 40
    while y < floor_y + 1400:
        ctx.move_to(x0, y)
        ctx.line_to(x1, y)
        y += step
        step *= 1.25
    vx = (x0 + x1) / 2
    for k in range(-30, 31):
        ctx.move_to(vx + k * 90, floor_y)
        ctx.line_to(vx + k * 90 * 4, floor_y + 1400)
    ctx.stroke()


def pendant(ctx, x, y, s=1.0, on=True):
    ctx.move_to(x, y - 500)
    ctx.line_to(x, y)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(5 * s)
    ctx.stroke()
    if on:
        glow(ctx, x, y + 40 * s, 420 * s, (1, 0.88, 0.55), 0.35)
    ctx.move_to(x - 70 * s, y + 55 * s)
    ctx.curve_to(x - 70 * s, y - 5 * s, x + 70 * s, y - 5 * s, x + 70 * s, y + 55 * s)
    ctx.close_path()
    _shade_fill(ctx, hexc("#ffd45e"), hexc("#e8a93a"), y, y + 55 * s, LW)
    ellipse(ctx, x, y + 55 * s, 55 * s, 10 * s)
    src(ctx, (1, 0.97, 0.85))
    ctx.fill()


def wall_clock(ctx, x, y, r, h, m, eyes=None):
    clock_face(ctx, x, y, r, h, m, rim="#d64a3a", face="#fbf6ea", lw=max(3, r * 0.07), eyes=eyes)


def desk(ctx, x, y, w=260, s=1.0, top="#c9cdd6", body="#aeb3bf", drawers=True):
    """Office desk, front view slightly from above. (x, y) = centre of the front edge of the top."""
    top, body = hexc(top), hexc(body)
    d = 34 * s
    ctx.move_to(x - w / 2, y)
    ctx.line_to(x - w / 2 + 22 * s, y - d)
    ctx.line_to(x + w / 2 - 22 * s, y - d)
    ctx.line_to(x + w / 2, y)
    ctx.close_path()
    _shade_fill(ctx, _lighter(top, 0.25), top, y - d, y, LW)
    ctx.rectangle(x - w / 2, y, w, 14 * s)
    _shade_fill(ctx, top, _darker(top, 0.12), y, y + 14 * s, LW)
    if drawers:
        _box(ctx, x + w / 2 - 92 * s, y + 14 * s, 84 * s, 115 * s, body, 3)
        for k in range(3):
            ctx.move_to(x + w / 2 - 70 * s, y + (40 + k * 34) * s)
            ctx.line_to(x + w / 2 - 30 * s, y + (40 + k * 34) * s)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(4 * s)
            ctx.stroke()
    for lx in (x - w / 2 + 14 * s,):
        ctx.rectangle(lx, y + 14 * s, 12 * s, 115 * s)
        _shade_fill(ctx, body, _darker(body, 0.1), y, y + 130 * s, LW * 0.8)


def chair(ctx, x, y, s=1.0, col="#3f4a73", tucked=False):
    """Office chair, (x, y) = floor point under the seat."""
    col = hexc(col)
    seat_y = y - 92 * s
    ctx.move_to(x, seat_y + 10 * s)
    ctx.line_to(x, y - 22 * s)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(9 * s)
    ctx.stroke()
    for dx in (-40, 0, 40):
        ctx.move_to(x, y - 22 * s)
        ctx.line_to(x + dx * s, y - 6 * s)
        ctx.stroke()
        ellipse(ctx, x + dx * s, y - 4 * s, 7 * s, 6 * s)
        src(ctx, OUT)
        ctx.fill()
    if not tucked:
        rrect(ctx, x - 48 * s, seat_y - 130 * s, 96 * s, 120 * s, 22 * s)
        _shade_fill(ctx, _lighter(col, 0.15), col, seat_y - 130 * s, seat_y, LW)
    rrect(ctx, x - 55 * s, seat_y - 6 * s, 110 * s, 24 * s, 10 * s)
    _shade_fill(ctx, _lighter(col, 0.2), col, seat_y - 6 * s, seat_y + 18 * s, LW)


def monitor(ctx, x, y, s=1.0, screen=None, t=0.0):
    """Computer monitor standing on a desk top at (x, y)."""
    ctx.rectangle(x - 8 * s, y - 40 * s, 16 * s, 40 * s)
    _shade_fill(ctx, hexc("#5a5f6e"), hexc("#3c4050"), y - 40 * s, y, LW * 0.7)
    rrect(ctx, x - 30 * s, y - 6 * s, 60 * s, 8 * s, 3)
    src(ctx, OUT)
    ctx.fill()
    rrect(ctx, x - 80 * s, y - 140 * s, 160 * s, 104 * s, 8 * s)
    _shade_fill(ctx, hexc("#4a4f60"), hexc("#30333f"), y - 140 * s, y - 36 * s, LW)
    rrect(ctx, x - 70 * s, y - 131 * s, 140 * s, 84 * s, 4 * s)
    if screen == "photo":
        _shade_fill(ctx, hexc("#9fd0ff"), hexc("#7ab36a"), y - 131 * s, y - 47 * s, 0)
    else:
        _shade_fill(ctx, hexc("#7fb2f0"), hexc("#4f7fd0"), y - 131 * s, y - 47 * s, 0)


def photo_frame(ctx, x, y, s=1.0, people=3):
    """Small family photo frame standing on a desk at (x, y)."""
    rrect(ctx, x - 34 * s, y - 52 * s, 68 * s, 52 * s, 4 * s)
    _shade_fill(ctx, hexc("#c58b4e"), hexc("#9c6a36"), y - 52 * s, y, LW * 0.8)
    rrect(ctx, x - 26 * s, y - 45 * s, 52 * s, 38 * s, 2 * s)
    _shade_fill(ctx, hexc("#bfe3ff"), hexc("#9ad08a"), y - 45 * s, y - 7 * s, 0)
    for k in range(people):
        px = x + (k - (people - 1) / 2) * 15 * s
        ctx.new_sub_path()
        ctx.arc(px, y - 27 * s, 5.5 * s, 0, 2 * PI)
        src(ctx, hexc("#fef2e8"))
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(1.5)
        ctx.stroke()
        ctx.rectangle(px - 5 * s, y - 21 * s, 10 * s, 13 * s)
        src(ctx, hexc(("#e57373", "#88b3fb", "#f2b84b")[k % 3]))
        ctx.fill()


def plant(ctx, x, y, s=1.0):
    for k, (a, l) in enumerate(((-0.9, 60), (-0.4, 75), (0.1, 70), (0.6, 62), (1.0, 50))):
        ctx.save()
        ctx.translate(x, y - 45 * s)
        ctx.rotate(a)
        ellipse(ctx, 0, -l * 0.5 * s, 13 * s, l * 0.5 * s)
        _shade_fill(ctx, hexc("#5fbf5a"), hexc("#2f8a3a"), -l * s, 0, LW * 0.7)
        ctx.restore()
    ctx.move_to(x - 30 * s, y - 50 * s)
    ctx.line_to(x + 30 * s, y - 50 * s)
    ctx.line_to(x + 22 * s, y)
    ctx.line_to(x - 22 * s, y)
    ctx.close_path()
    _shade_fill(ctx, hexc("#f7efe3"), hexc("#d9cbb5"), y - 50 * s, y, LW * 0.8)


def door(ctx, x, y, w=150, h=300, open_frac=0.0, col="#4f76d8", sign=None):
    """Door in a wall; (x, y) = bottom-left. open_frac swings it inward (shows the dark gap)."""
    col = hexc(col)
    ctx.rectangle(x - 10, y - h - 10, w + 20, h + 10)
    _shade_fill(ctx, hexc("#f2eadf"), hexc("#d8ccbb"), y - h, y, LW)
    ctx.rectangle(x, y - h, w, h)
    src(ctx, hexc("#2a2638"))
    ctx.fill()
    dw = w * (1 - 0.8 * open_frac)
    ctx.rectangle(x, y - h, dw, h)
    _shade_fill(ctx, _lighter(col, 0.15), col, y - h, y, LW)
    rrect(ctx, x + dw * 0.3, y - h + 40, dw * 0.4, 80, 4)
    _shade_fill(ctx, hexc("#cfe6ff"), hexc("#a8c8f0"), y - h + 40, y - h + 120, LW * 0.7)
    ctx.new_sub_path()
    ctx.arc(x + dw - 22, y - h * 0.48, 8, 0, 2 * PI)
    src(ctx, hexc("#e8c45a"))
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(2.5)
    ctx.stroke()
    if sign:
        rrect(ctx, x + dw / 2 - 52, y - h + 140, 104, 40, 6)
        _shade_fill(ctx, hexc("#fffaf0"), hexc("#efe6d6"), y - h + 140, y - h + 180, LW * 0.7)
        text(ctx, sign, x + dw / 2, y - h + 160, 22, OUT, outline=False)


def window_city(ctx, x, y, w, h, night=0.0, t=0.0):
    """Window onto a city skyline; (x, y) = top-left."""
    ctx.save()
    rrect(ctx, x, y, w, h, 8)
    ctx.clip()
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *lerpc(hexc("#7fb7f2"), hexc("#1d2457"), night))
    g.add_color_stop_rgb(1, *lerpc(hexc("#f4c7a8"), hexc("#7a4f9a"), night))
    ctx.set_source(g)
    ctx.paint()
    rnd = random.Random(int(x) + int(y))
    bx = x - 10
    while bx < x + w:
        bw = rnd.uniform(40, 80)
        bh = rnd.uniform(0.3, 0.75) * h
        ctx.rectangle(bx, y + h - bh, bw, bh)
        src(ctx, lerpc(hexc("#8e9bc4"), hexc("#2c2f5a"), night))
        ctx.fill()
        for wy in range(int(y + h - bh + 10), int(y + h), 18):
            for wx in range(int(bx + 6), int(bx + bw - 6), 14):
                if rnd.random() < 0.4 + 0.4 * night:
                    ctx.rectangle(wx, wy, 6, 9)
                    src(ctx, lerpc(hexc("#c7d3f0"), hexc("#ffd36a"), night))
                    ctx.fill()
        bx += bw + 4
    ctx.restore()
    rrect(ctx, x, y, w, h, 8)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(LW * 1.5)
    ctx.stroke()
    ctx.move_to(x + w / 2, y)
    ctx.line_to(x + w / 2, y + h)
    ctx.move_to(x, y + h / 2)
    ctx.line_to(x + w, y + h / 2)
    ctx.set_line_width(LW * 1.2)
    ctx.stroke()


def calendar(ctx, x, y, s, top_txt, mid_txt, num, flip=1.0):
    """Wall calendar; flip 0->1 animates the new page dropping in."""
    rrect(ctx, x - 70 * s, y, 140 * s, 170 * s, 8 * s)
    _shade_fill(ctx, hexc("#ffffff"), hexc("#ecebf2"), y, y + 170 * s, LW)
    ctx.rectangle(x - 70 * s, y, 140 * s, 42 * s)
    _shade_fill(ctx, hexc("#e8574a"), hexc("#c63d33"), y, y + 42 * s, LW)
    text(ctx, top_txt, x, y + 21 * s, 22 * s, (1, 1, 1), outline=False)
    text(ctx, mid_txt, x, y + 66 * s, 24 * s, hexc("#c63d33"), outline=False)
    text(ctx, num, x, y + 120 * s, 64 * s, OUT, outline=False)
    if flip < 1:
        ctx.save()
        ctx.translate(x, y + 42 * s)
        ctx.scale(1, 1 - flip)
        rrect(ctx, -70 * s, 0, 140 * s, 128 * s, 6 * s)
        _shade_fill(ctx, hexc("#f4f2f8"), hexc("#d9d6e4"), 0, 128 * s, LW)
        ctx.restore()


def phone(ctx, x, y, s=1.0, screen="inbox", t=0.0):
    """Phone held up to camera, centred at (x, y)."""
    rrect(ctx, x - 62 * s, y - 115 * s, 124 * s, 230 * s, 18 * s)
    _shade_fill(ctx, hexc("#3a3f4f"), hexc("#262a36"), y - 115 * s, y + 115 * s, LW)
    rrect(ctx, x - 52 * s, y - 100 * s, 104 * s, 200 * s, 10 * s)
    _shade_fill(ctx, hexc("#ffffff"), hexc("#eef1f7"), y - 100 * s, y + 100 * s, 0)
    if screen == "inbox":
        text(ctx, "Inbox", x, y - 78 * s, 20 * s, OUT, outline=False)
        text(ctx, "0", x, y - 20 * s, 64 * s, hexc("#c63d33"), outline=False)
        # tumbleweed rolling across the empty screen
        tx = x - 60 * s + ((t * 0.6) % 1) * 120 * s
        ctx.save()
        ctx.translate(tx, y + 55 * s)
        ctx.rotate(t * 6)
        for k in range(6):
            ctx.new_sub_path()
            ctx.arc(0, 0, (6 + k * 3) * s, k, k + 4.5)
        ctx.set_source_rgb(*hexc("#a8865a"))
        ctx.set_line_width(2.5 * s)
        ctx.stroke()
        ctx.restore()
    elif screen == "game":
        _box(ctx, x - 45 * s, y - 80 * s, 90 * s, 150 * s, hexc("#7fd38a"), 6)
        for k in range(3):
            ctx.new_sub_path()
            ctx.arc(x + math.sin(t * 3 + k * 2) * 25 * s, y - 40 * s + k * 45 * s, 10 * s, 0, 2 * PI)
            src(ctx, hexc(("#f2b84b", "#e8574a", "#88b3fb")[k]))
            ctx.fill()


def law_book(ctx, x, y, s=1.0, locked=True):
    """Big law book with a padlock, (x, y) = centre."""
    rrect(ctx, x - 110 * s, y - 140 * s, 220 * s, 280 * s, 12 * s)
    _shade_fill(ctx, hexc("#c0392b"), hexc("#8e2a20"), y - 140 * s, y + 140 * s, LW * 1.2)
    rrect(ctx, x + 85 * s, y - 132 * s, 22 * s, 264 * s, 6 * s)
    _shade_fill(ctx, hexc("#f6efe0"), hexc("#ddd3bd"), y - 132 * s, y + 132 * s, LW * 0.7)
    text(ctx, "LABOR", x - 8 * s, y - 70 * s, 36 * s, hexc("#ffd36a"), outline=False)
    text(ctx, "LAW", x - 8 * s, y - 28 * s, 36 * s, hexc("#ffd36a"), outline=False)
    if locked:
        ctx.new_sub_path()
        ctx.arc(x - 8 * s, y + 45 * s, 30 * s, PI, 2 * PI)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(14 * s)
        ctx.stroke()
        ctx.new_sub_path()
        ctx.arc(x - 8 * s, y + 45 * s, 30 * s, PI, 2 * PI)
        ctx.set_source_rgb(*hexc("#c9ced8"))
        ctx.set_line_width(7 * s)
        ctx.stroke()
        rrect(ctx, x - 52 * s, y + 45 * s, 88 * s, 70 * s, 10 * s)
        _shade_fill(ctx, hexc("#ffd36a"), hexc("#e0a93a"), y + 45 * s, y + 115 * s, LW)
        ctx.new_sub_path()
        ctx.arc(x - 8 * s, y + 75 * s, 8 * s, 0, 2 * PI)
        src(ctx, OUT)
        ctx.fill()


def stamp(ctx, x, y, s=1.0, word="FIRED"):
    """Rubber stamp; (x, y) = bottom of the stamp face."""
    rrect(ctx, x - 70 * s, y - 34 * s, 140 * s, 34 * s, 6 * s)
    _shade_fill(ctx, hexc("#e8574a"), hexc("#b83a30"), y - 34 * s, y, LW)
    rrect(ctx, x - 50 * s, y - 70 * s, 100 * s, 38 * s, 8 * s)
    _shade_fill(ctx, hexc("#8a5a33"), hexc("#6b4422"), y - 70 * s, y - 32 * s, LW)
    ellipse(ctx, x, y - 120 * s, 32 * s, 46 * s)
    _shade_fill(ctx, hexc("#a8713f"), hexc("#7d5229"), y - 166 * s, y - 74 * s, LW)


def paper(ctx, x, y, s=1.0, mark=None):
    """Sheet of paper lying on a desk, (x, y) = centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.06)
    rrect(ctx, -90 * s, -60 * s, 180 * s, 120 * s, 4 * s)
    _shade_fill(ctx, hexc("#ffffff"), hexc("#efeef5"), -60 * s, 60 * s, LW * 0.8)
    for k in range(4):
        ctx.move_to(-65 * s, (-35 + k * 20) * s)
        ctx.line_to(55 * s, (-35 + k * 20) * s)
    ctx.set_source_rgba(0.5, 0.55, 0.7, 0.6)
    ctx.set_line_width(3 * s)
    ctx.stroke()
    if mark:
        ctx.rotate(-0.15)
        rrect(ctx, -70 * s, -24 * s, 140 * s, 48 * s, 6 * s)
        ctx.set_source_rgba(0.85, 0.2, 0.18, 0.85)
        ctx.set_line_width(5 * s)
        ctx.stroke()
        text(ctx, mark, 0, 0, 34 * s, (0.85, 0.2, 0.18), outline=False)
    ctx.restore()


def shield(ctx, x, y, s=1.0, a=1.0):
    """Glowing shield that blocks the stamp."""
    glow(ctx, x, y, 200 * s, (0.5, 0.8, 1.0), 0.5 * a)
    ctx.move_to(x, y - 110 * s)
    ctx.curve_to(x + 60 * s, y - 85 * s, x + 95 * s, y - 90 * s, x + 95 * s, y - 90 * s)
    ctx.curve_to(x + 95 * s, y + 10 * s, x + 60 * s, y + 80 * s, x, y + 115 * s)
    ctx.curve_to(x - 60 * s, y + 80 * s, x - 95 * s, y + 10 * s, x - 95 * s, y - 90 * s)
    ctx.curve_to(x - 95 * s, y - 90 * s, x - 60 * s, y - 85 * s, x, y - 110 * s)
    ctx.close_path()
    g = cairo.LinearGradient(0, y - 110 * s, 0, y + 115 * s)
    g.add_color_stop_rgba(0, 0.65, 0.88, 1.0, a)
    g.add_color_stop_rgba(1, 0.3, 0.55, 0.95, a)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgba(*OUT, a)
    ctx.set_line_width(LW * 1.2)
    ctx.stroke()
    text(ctx, "LAW", x, y - 5 * s, 40 * s, (1, 1, 1), scale=1.0)


def coins(ctx, t, x0, x1, y0, y1, n=18, seed=3):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        sp = rnd.uniform(250, 420)
        y = y0 + ((t * sp + rnd.uniform(0, y1 - y0)) % (y1 - y0))
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(abs(math.cos(t * 5 + x)) * 0.8 + 0.2, 1)
        ctx.new_sub_path()
        ctx.arc(0, 0, 18, 0, 2 * PI)
        _shade_fill(ctx, hexc("#ffe08a"), hexc("#e0a93a"), -18, 18, 3)
        text(ctx, "¥", 0, 0, 20, hexc("#a86f12"), outline=False)
        ctx.restore()


def building(ctx, cx, base, s, t, night=1.0, dark_window=None):
    """Tall office tower exterior. dark_window = (col, row) of the one unlit small window."""
    w, h = 420 * s, 1500 * s
    x0, y0 = cx - w / 2, base - h
    ctx.rectangle(x0, y0, w, h + 400)
    _shade_fill(ctx, lerpc(hexc("#8fa3c9"), hexc("#2c3462"), night), lerpc(hexc("#6d7fb0"), hexc("#1d2348"), night),
                y0, base, LW)
    cols, rows = 6, 26
    cw, rh = (w - 40 * s) / cols, (h - 80 * s) / rows
    rnd = random.Random(5)
    for r in range(rows):
        for c in range(cols):
            wx, wy = x0 + 20 * s + c * cw + 5 * s, y0 + 40 * s + r * rh + 5 * s
            lit = rnd.random() < 0.8
            if dark_window and (c, r) == dark_window:
                col = hexc("#3b3550")
            else:
                col = lerpc(hexc("#cfe0f5"), hexc("#ffd36a") if lit else hexc("#3a3f66"), night)
            ctx.rectangle(wx, wy, cw - 10 * s, rh - 10 * s)
            src(ctx, col)
            ctx.fill()
    ctx.rectangle(x0 - 20 * s, y0 - 40 * s, w + 40 * s, 50 * s)
    _shade_fill(ctx, hexc("#5a6699"), hexc("#3f4a7a"), y0 - 40 * s, y0 + 10 * s, LW)
