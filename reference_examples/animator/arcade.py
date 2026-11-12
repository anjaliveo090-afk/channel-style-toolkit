"""Sets and props for the pachinko story, in the office.py / style2 look:
outlined shapes with soft top-lit gradient fills, warm lamp glows."""
import math
import random

import cairo

from engine import PI, ellipse, glow, hexc, lerp, lerpc, rrect, src, text
from style2 import OUT, _shade_fill

LW = 4.0
NEON = ["#ff4f8b", "#ffd84a", "#4fe3ff", "#9b6bff", "#5dff8a"]


def _col(c):
    return c if isinstance(c, tuple) else hexc(c)


def box(ctx, x, y, w, h, top, bottom=None, r=6, lw=LW):
    """Outlined rounded box with a top-lit gradient; colours as hex strings or rgb tuples."""
    rrect(ctx, x, y, w, h, r)
    _shade_fill(ctx, _col(top), _col(bottom if bottom is not None else top), y, y + h, lw)


def night_sky(ctx, y0=-1500, y1=1400):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *hexc("#0f1440"))
    g.add_color_stop_rgb(0.7, *hexc("#3b2a6b"))
    g.add_color_stop_rgb(1, *hexc("#7a3f7a"))
    ctx.set_source(g)
    ctx.rectangle(-3000, y0, 7000, y1 - y0 + 3000)
    ctx.fill()


def neon_text(ctx, s, x, y, size, col, on=1.0, t=0.0):
    c = hexc(col)
    if on <= 0:
        text(ctx, s, x, y, size, lerpc(c, (0.2, 0.2, 0.25), 0.75), outline=False)
        return
    flick = 0.85 + 0.15 * math.sin(t * 31 + x)
    glow(ctx, x, y, size * 2.6, c, 0.45 * on * flick)
    text(ctx, s, x, y, size, lerpc(c, (1, 1, 1), 0.45 * on), outline=True)


# ---------------------------------------------------------------- street
def storefront(ctx, x, base, w, h, col, sign=None, sign_col="#ff4f8b", on=1.0, t=0.0, doors=0.0, seed=1):
    """A shop front; `sign` lights up when on > 0; doors 0..1 slide open."""
    rrect(ctx, x, base - h, w, h, 6)
    _shade_fill(ctx, hexc(col), lerpc(hexc(col), (0, 0, 0), 0.3), base - h, base, LW)
    rnd = random.Random(seed)
    for r in range(int((h - 260) // 70)):
        for c in range(int((w - 40) // 70)):
            wx, wy = x + 30 + c * 70, base - h + 30 + r * 70
            ctx.rectangle(wx, wy, 40, 44)
            src(ctx, hexc("#ffd36a") if rnd.random() < 0.6 else hexc("#3a3f66"))
            ctx.fill_preserve()
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(2.5)
            ctx.stroke()
    # glass entrance
    ex, ew, eh = x + w / 2 - 90, 180, 200
    box(ctx, ex, base - eh, ew, eh, "#ffe9b0", "#ffb86a", r=4)
    if on > 0:
        glow(ctx, x + w / 2, base - 100, 220, (1, 0.8, 0.45), 0.5 * on)
    for side in (-1, 1):
        off = doors * 80 * side
        ctx.rectangle(x + w / 2 + (side - 1) * 45 + off, base - eh + 6, 90, eh - 6)
        ctx.set_source_rgba(0.75, 0.9, 1, 0.35)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(3)
        ctx.stroke()
    if sign:
        sy = base - h + (h - 200) * 0.82
        box(ctx, x + 20, sy - 50, w - 40, 100, "#1b1630", "#120e22", r=10)
        neon_text(ctx, sign, x + w / 2, sy, 54, sign_col, on, t)
        if on > 0:   # chasing bulbs around the sign
            n = int((w - 40) / 26)
            for k in range(n):
                lit = (k + int(t * 12)) % 3 == 0
                for yy in (sy - 50, sy + 50):
                    ctx.new_sub_path()
                    ctx.arc(x + 33 + k * 26, yy, 6, 0, 2 * PI)
                    src(ctx, hexc("#fff3b0") if lit else hexc("#b0883a"))
                    ctx.fill()


def street(ctx, T, neon_on=0.0, doors=0.0, ground=1500):
    """Night shopping street; the middle shop is the pachinko arcade."""
    night_sky(ctx)
    storefront(ctx, -560, ground, 420, 1300, "#55507a", "RAMEN", "#ffd84a", 1.0, T, seed=2)
    storefront(ctx, -120, ground, 520, 1100, "#5e3f6e", "PACHINKO", "#ff4f8b", neon_on, T, doors, seed=3)
    storefront(ctx, 420, ground, 420, 1400, "#3f5a7a", "KARAOKE", "#4fe3ff", 1.0, T, seed=4)
    storefront(ctx, 860, ground, 420, 1200, "#6e4f3f", "SUSHI", "#5dff8a", 1.0, T, seed=5)
    ctx.rectangle(-3000, ground, 7000, 2000)
    _shade_fill(ctx, hexc("#3b3858"), hexc("#26243a"), ground, ground + 600, 0)
    for k in range(-6, 10):   # sidewalk lines + neon reflections
        ctx.move_to(k * 160, ground)
        ctx.line_to(k * 160 - 120, ground + 600)
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.set_line_width(3)
    ctx.stroke()
    if neon_on:
        glow(ctx, 140, ground + 80, 300, hexc("#ff4f8b"), 0.25 * neon_on)


def city_aerial(ctx, T, lit_times, t0=0.0):
    """Top-down blocks; a pink neon arcade lights up on each street corner at its time."""
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.set_source_rgb(*hexc("#2a2847"))
    ctx.fill()
    rnd = random.Random(8)
    k = 0
    for gy in range(-4, 7):
        for gx in range(-3, 6):
            x, y = gx * 260, gy * 260
            box(ctx, x + 30, y + 30, 200, 200, "#5b5a86", "#464570", r=8)
            for i in range(6):
                rx, ry = x + 50 + rnd.uniform(0, 140), y + 50 + rnd.uniform(0, 140)
                ctx.rectangle(rx, ry, 18, 18)
                src(ctx, hexc("#ffd36a") if rnd.random() < 0.5 else hexc("#33365c"))
                ctx.fill()
            # corner arcade
            if (gx + gy) % 2 == 0:
                tl = lit_times[k % len(lit_times)] + (k // len(lit_times)) * 0.07
                on = 1.0 if T >= tl else 0.0
                cx, cy = x + 205, y + 205
                box(ctx, cx - 38, cy - 38, 56, 56, "#ff4f8b" if on else "#4a3550", None, r=6, lw=3)
                if on:
                    glow(ctx, cx - 10, cy - 10, 90, hexc("#ff4f8b"), 0.55)
                    text(ctx, "¥", cx - 10, cy - 10, 30, (1, 1, 1), outline=False)
                k += 1
    # glowing street lines
    for gx in range(-3, 7):
        ctx.rectangle(gx * 260 - 2, -3000, 4, 7000)
    for gy in range(-4, 8):
        ctx.rectangle(-3000, gy * 260 - 2, 7000, 4)
    ctx.set_source_rgba(1, 0.85, 0.5, 0.35)
    ctx.fill()


# ---------------------------------------------------------------- inside the arcade
def machine(ctx, x, base, s=1.0, T=0.0, blink=1.0, balls=True, seed=0):
    """Pachinko machine: tall cabinet, glass playfield with pins, lights, handle."""
    w, h = 220 * s, 420 * s
    x0, y0 = x - w / 2, base - h
    box(ctx, x0, y0, w, h, "#e8e2f4", "#b9b1d6", r=14 * s)
    # top light bar
    for k in range(7):
        on = blink and (k + int(T * 10 + seed)) % 3 == 0
        c = hexc(NEON[(k + seed) % len(NEON)])
        ctx.new_sub_path()
        ctx.arc(x0 + 25 * s + k * 28 * s, y0 + 22 * s, 9 * s, 0, 2 * PI)
        src(ctx, c if on else lerpc(c, (0.3, 0.3, 0.35), 0.6))
        ctx.fill()
        if on:
            glow(ctx, x0 + 25 * s + k * 28 * s, y0 + 22 * s, 30 * s, c, 0.6)
    # round playfield
    cx, cy, R = x, y0 + 170 * s, 92 * s
    ctx.new_sub_path()
    ctx.arc(cx, cy, R, 0, 2 * PI)
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, R)
    g.add_color_stop_rgb(0, *hexc("#7fd0ff"))
    g.add_color_stop_rgb(1, *hexc("#3a5fc0"))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(LW * s)
    ctx.stroke()
    rnd = random.Random(seed + 1)
    for _ in range(26):   # pins
        a, d = rnd.uniform(0, 2 * PI), rnd.uniform(0, R * 0.85)
        ctx.new_sub_path()
        ctx.arc(cx + math.cos(a) * d, cy + math.sin(a) * d, 2.2 * s, 0, 2 * PI)
        ctx.set_source_rgb(0.95, 0.85, 0.5)
        ctx.fill()
    # centre screen (slot reels)
    box(ctx, cx - 40 * s, cy - 30 * s, 80 * s, 55 * s, "#1b1630", None, r=6 * s, lw=3 * s)
    for k in range(3):
        n = (int(T * 14) + k * 3 + seed) % 9 + 1 if blink else 7
        text(ctx, str(n), cx - 25 * s + k * 25 * s, cy - 2 * s, 24 * s, hexc(NEON[k]), outline=False)
    if balls:
        for k in range(7):   # balls bouncing down the field
            ph = (T * 1.3 + k / 7 + seed * 0.13) % 1
            bx = cx + math.sin(ph * 9 + k) * R * 0.6
            by = cy - R * 0.85 + ph * R * 1.7
            ctx.new_sub_path()
            ctx.arc(bx, by, 4.5 * s, 0, 2 * PI)
            _shade_fill(ctx, (1, 1, 1), hexc("#9aa1ad"), by - 5, by + 5, 1.2 * s)
    # tray + handle
    box(ctx, x0 + 15 * s, base - 120 * s, w - 30 * s, 50 * s, "#c9c2e0", "#a59bc8", r=10 * s)
    for k in range(9):
        ctx.new_sub_path()
        ctx.arc(x0 + 40 * s + k * 17 * s, base - 102 * s, 7 * s, 0, 2 * PI)
        _shade_fill(ctx, (1, 1, 1), hexc("#8f97a5"), 0, 1, 1.5 * s)
    ctx.new_sub_path()
    ctx.arc(x0 + w - 30 * s, base - 45 * s, 20 * s, 0, 2 * PI)
    _shade_fill(ctx, hexc("#ffd84a"), hexc("#d9a020"), base - 65 * s, base - 25 * s, LW * s)


def aisle(ctx, T, blink=1.0):
    """One-point view down a long aisle of machines, red carpet, ceiling lights."""
    vx, vy = 360, 560
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.set_source_rgb(*hexc("#2a1f3d"))
    ctx.fill()
    ctx.move_to(-900, 2000)
    ctx.line_to(vx - 20, vy + 30)
    ctx.line_to(vx + 20, vy + 30)
    ctx.line_to(1620, 2000)
    ctx.close_path()
    _shade_fill(ctx, hexc("#d6404a"), hexc("#8a1f33"), vy, 2000, 0)
    for k in range(14):   # carpet pattern lines
        f = (k / 14 + T * 0.05) % 1
        y = vy + 30 + (2000 - vy) * f ** 2
        hw = 20 + (1240) * f ** 2
        ctx.move_to(vx - hw, y)
        ctx.line_to(vx + hw, y)
    ctx.set_source_rgba(1, 0.85, 0.4, 0.35)
    ctx.set_line_width(3)
    ctx.stroke()
    # ceiling strip lights
    for k in range(8):
        f = 0.15 + k * 0.11
        y = vy - 60 - (1 - f) * 1100
        w = 260 * (1 - f) + 16
        ctx.rectangle(vx - w / 2, y, w, 22 * (1 - f) + 4)
        ctx.set_source_rgb(1, 0.95, 0.8)
        ctx.fill()
    # two walls of machines, far to near
    for k in range(9, -1, -1):
        f = 0.12 + k * 0.1
        z = 1 / (1 - f * 0.9) * 0.25
        for side in (-1, 1):
            x = vx + side * (90 + 900 * (z - 0.25))
            base = vy + 60 + 1500 * (z - 0.25)
            machine(ctx, x, base, z, T, blink, balls=z > 0.6, seed=k * 2 + (side > 0))
    glow(ctx, vx, vy, 500, (1, 0.6, 0.8), 0.25)


def bucket(ctx, x, base, s=1.0, fill=1.0, overflow=0.0, T=0.0, seed=2):
    """Plastic bucket of silver pachinko balls. overflow > 0 spills balls over the rim."""
    w0, w1, h = 150 * s, 115 * s, 150 * s
    top = base - h
    rnd = random.Random(seed)
    level = top + h * (1 - fill)
    # balls inside (drawn first, clipped by bucket outline)
    ctx.save()
    ctx.move_to(x - w0 / 2, top)
    ctx.line_to(x + w0 / 2, top)
    ctx.line_to(x + w1 / 2, base)
    ctx.line_to(x - w1 / 2, base)
    ctx.close_path()
    _shade_fill(ctx, hexc("#ffb03a"), hexc("#e0782a"), top, base, LW * s)
    ctx.restore()
    if fill > 0.05:
        n = int(30 * fill)
        for i in range(n + int(overflow * 30)):
            extra = i >= n
            bx = x + rnd.uniform(-w0 / 2 + 10 * s, w0 / 2 - 10 * s)
            by = level + rnd.uniform(-12, 10) * s - (rnd.uniform(5, 40) * s * overflow if extra else 0)
            ctx.new_sub_path()
            ctx.arc(bx, by, 10 * s, 0, 2 * PI)
            _shade_fill(ctx, (1, 1, 1), hexc("#8f97a5"), by - 10 * s, by + 10 * s, 2 * s)
    if overflow > 0:   # balls rolling down the sides
        for i in range(10):
            ph = (T * 1.2 + i / 10) % 1
            side = -1 if i % 2 else 1
            bx = x + side * (w0 / 2 + ph * 60 * s + i * 3)
            by = top + ph * ph * (h + 40 * s)
            ctx.new_sub_path()
            ctx.arc(bx, by, 9 * s, 0, 2 * PI)
            _shade_fill(ctx, (1, 1, 1), hexc("#8f97a5"), by - 9 * s, by + 9 * s, 2 * s)
    rrect(ctx, x - w0 / 2 - 6 * s, top - 6 * s, w0 + 12 * s, 14 * s, 6 * s)
    _shade_fill(ctx, hexc("#ffc36a"), hexc("#e0882a"), top - 6 * s, top + 8 * s, LW * s)


def ball(ctx, x, y, r):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * PI)
    _shade_fill(ctx, (1, 1, 1), hexc("#8f97a5"), y - r, y + r, max(1.5, r * 0.12))
    ctx.new_sub_path()
    ctx.arc(x - r * 0.35, y - r * 0.35, r * 0.25, 0, 2 * PI)
    ctx.set_source_rgba(1, 1, 1, 0.9)
    ctx.fill()


# ---------------------------------------------------------------- prizes
def candy(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for side in (-1, 1):
        ctx.move_to(side * 30, 0)
        ctx.line_to(side * 58, -20)
        ctx.line_to(side * 58, 20)
        ctx.close_path()
        _shade_fill(ctx, hexc("#ff8fc0"), hexc("#e05a9a"), -20, 20, LW)
    ellipse(ctx, 0, 0, 38, 26)
    _shade_fill(ctx, hexc("#ff6fa8"), hexc("#d43f86"), -26, 26, LW)
    for k in (-1, 0, 1):
        ctx.move_to(k * 14 - 8, -20)
        ctx.line_to(k * 14 + 8, 20)
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def chocolate(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    box(ctx, -45, -65, 90, 130, "#7a4a2a", "#5a321a", r=6)
    box(ctx, -45, -10, 90, 75, "#e8574a", "#b83a33", r=4)
    text(ctx, "CHOCO", 0, 28, 17, (1, 1, 1), outline=False)
    for r in range(2):
        for c in range(2):
            box(ctx, -38 + c * 40, -58 + r * 23, 34, 19, "#8a5a33", "#6b4422", r=3, lw=2)
    ctx.restore()


def shampoo(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    box(ctx, -12, -95, 24, 25, "#ffffff", "#d9dce6", r=4)
    box(ctx, -40, -72, 80, 140, "#6fd0e0", "#3aa0c0", r=18)
    box(ctx, -28, -30, 56, 60, "#ffffff", "#eef1f7", r=6, lw=2.5)
    text(ctx, "SHAMPOO", 0, 0, 10, hexc("#2b6f8a"), outline=False)
    ctx.restore()


def token(ctx, x, y, s=1.0, rot=0.0, shine=0.0):
    """Small gold plastic token (rectangular chip with a star)."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    box(ctx, -32, -20, 64, 40, "#ffe27a", "#e0a93a", r=8)
    rrect(ctx, -24, -12, 48, 24, 5)
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.set_line_width(2)
    ctx.stroke()
    text(ctx, "★", 0, 0, 22, hexc("#b5781a"), outline=False)
    if shine > 0:
        glow(ctx, 0, 0, 70, (1, 0.95, 0.6), 0.6 * shine)
    ctx.restore()


def yen_note(ctx, x, y, s=1.0, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    box(ctx, -70, -34, 140, 68, "#cfe8c4", "#a9cf9a", r=6)
    ctx.new_sub_path()
    ctx.arc(30, 0, 20, 0, 2 * PI)
    ctx.set_source_rgba(0.3, 0.5, 0.3, 0.4)
    ctx.fill()
    text(ctx, "¥10000", -18, 0, 20, hexc("#2f6b3a"), outline=False)
    ctx.restore()


def cash_stack(ctx, x, y, s=1.0, n=8):
    for k in range(n):
        yen_note(ctx, x + (k % 2) * 3 * s, y - k * 9 * s, s, rot=(k % 3 - 1) * 0.02)
    box(ctx, x - 12 * s, y - n * 9 * s - 10 * s, 24 * s, n * 9 * s + 40 * s, "#ffffff", "#e6e6ee", r=3, lw=2.5)


def counter(ctx, y, x0=-800, x1=1600, col="#c9a06a"):
    box(ctx, x0, y, x1 - x0, 90, col, "#9a7246", r=0)
    box(ctx, x0, y + 90, x1 - x0, 900, "#8a5a33", "#6b4422", r=0)


def shelves(ctx, T, x0=-200, x1=920, y0=200, rows=4, seed=4):
    """Back wall of a prize counter: shelves full of colourful boxes."""
    box(ctx, x0, y0 - 60, x1 - x0, rows * 150 + 80, "#fff1d6", "#f0d9b0", r=0)
    rnd = random.Random(seed)
    cols = ["#e8574a", "#f2b84b", "#4fb3a9", "#88b3fb", "#9d7fd6", "#7cc08a", "#ff8fc0"]
    for r in range(rows):
        y = y0 + r * 150
        x = x0 + 10
        while x < x1 - 60:
            w = rnd.uniform(40, 80)
            h = rnd.uniform(60, 110)
            box(ctx, x, y + 110 - h, w, h, rnd.choice(cols), None, r=5, lw=3)
            x += w + 8
        box(ctx, x0, y + 110, x1 - x0, 18, "#b98a5a", "#8a5a33", r=0, lw=3)


# ---------------------------------------------------------------- the back alley window
def alley(ctx, T, lamp=1.0):
    """Narrow back alley at night: brick walls, pipes, a lamp, wet ground."""
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.set_source_rgb(*hexc("#1a1830"))
    ctx.fill()
    box(ctx, -600, -900, 2000, 2200, "#6a4a5e", "#4a3346", r=0)
    for r in range(-20, 30):   # bricks
        off = 30 if r % 2 else 0
        for c in range(-10, 30):
            ctx.rectangle(-600 + c * 80 + off, -900 + r * 44, 76, 40)
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.set_line_width(3)
    ctx.stroke()
    for px in (70, 650):   # pipes
        box(ctx, px, -900, 26, 2200, "#8a8fa0", "#5a5f70", r=10)
    box(ctx, -600, 1180, 2000, 900, "#2c2a40", "#1c1a2c", r=0)
    for k in range(6):   # puddles
        ellipse(ctx, -100 + k * 190, 1260 + (k % 2) * 60, 70, 14)
        ctx.set_source_rgba(1, 0.75, 0.5, 0.18 * lamp)
        ctx.fill()
    glow(ctx, 520, 280, 420, (1, 0.75, 0.45), 0.35 * lamp)
    box(ctx, 500, 250, 40, 30, "#ffe9b0", "#ffc36a", r=6)


def hatch(ctx, x, y, s=1.0, open_k=0.0, label_text=None):
    """Tiny window in the wall: frame, frosted sliding glass, a small counter ledge."""
    w, h = 190 * s, 150 * s
    box(ctx, x - w / 2 - 16 * s, y - h / 2 - 16 * s, w + 32 * s, h + 32 * s, "#3a3346", "#2a2436", r=8)
    rrect(ctx, x - w / 2, y - h / 2, w, h, 4)
    ctx.set_source_rgb(*hexc("#ffcf7a"))
    ctx.fill()
    glow(ctx, x, y, 200 * s, (1, 0.8, 0.45), 0.5)
    gx = x - w / 2 + w * open_k
    ctx.save()
    rrect(ctx, x - w / 2, y - h / 2, w, h, 4)
    ctx.clip()
    ctx.rectangle(gx, y - h / 2, w, h)
    ctx.set_source_rgba(0.85, 0.9, 1, 0.75)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.restore()
    box(ctx, x - w / 2 - 30 * s, y + h / 2 + 4 * s, w + 60 * s, 22 * s, "#8a8f9a", "#5a5f6a", r=4)
    if label_text:
        text(ctx, label_text, x, y - h / 2 - 60 * s, 28 * s, (1, 1, 1), outline=True)


def hand(ctx, x, y, s=1.0, flip=1, col="#fce7d6"):
    """A hand (with sleeve) reaching in from the side, palm down."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * flip, s)
    box(ctx, -260, -34, 200, 68, "#3a3f55", "#2a2e40", r=14)
    rrect(ctx, -70, -30, 90, 60, 26)
    _shade_fill(ctx, hexc(col), lerpc(hexc(col), (0.6, 0.4, 0.3), 0.15), -30, 30, LW)
    for k in range(3):
        rrect(ctx, 0 + k * 4, -28 + k * 19, 46, 17, 8)
        _shade_fill(ctx, hexc(col), lerpc(hexc(col), (0.6, 0.4, 0.3), 0.15), 0, 1, 3)
    ctx.restore()


def handcuffs(ctx, x, y, s=1.0, swing=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(swing)
    ctx.scale(s, s)
    for side in (-1, 1):
        ctx.new_sub_path()
        ctx.arc(side * 55, 60, 40, 0, 2 * PI)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(20)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc("#c9ced8"))
        ctx.set_line_width(12)
        ctx.stroke()
    for k in range(3):
        ctx.new_sub_path()
        ellipse(ctx, -20 + k * 20, 15, 11, 7)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(7)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc("#c9ced8"))
        ctx.set_line_width(3)
        ctx.stroke()
    ctx.restore()


def red_x(ctx, x, y, size, k=1.0, w=26):
    if k <= 0:
        return
    for i, (a, b) in enumerate((((-1, -1), (1, 1)), ((1, -1), (-1, 1)))):
        p = max(0.0, min(1.0, k * 2 - i))
        if p <= 0:
            continue
        ctx.move_to(x + a[0] * size, y + a[1] * size)
        ctx.line_to(x + lerp(a[0], b[0], p) * size, y + lerp(a[1], b[1], p) * size)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(w + 10)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc("#e8323a"))
        ctx.set_line_width(w)
        ctx.stroke()


def check(ctx, x, y, size, k=1.0):
    if k <= 0:
        return
    pts = [(x - size, y), (x - size * 0.3, y + size * 0.7), (x + size, y - size * 0.8)]
    ctx.move_to(*pts[0])
    p = min(1, k)
    seg = p * 2
    ctx.line_to(lerp(pts[0][0], pts[1][0], min(1, seg)), lerp(pts[0][1], pts[1][1], min(1, seg)))
    if seg > 1:
        ctx.line_to(lerp(pts[1][0], pts[2][0], seg - 1), lerp(pts[1][1], pts[2][1], seg - 1))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(size * 0.32)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc("#4fd16a"))
    ctx.set_line_width(size * 0.2)
    ctx.stroke()
