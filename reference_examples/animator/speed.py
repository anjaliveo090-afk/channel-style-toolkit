"""Props and sets for the 10-second speedrun story (generic blocky game, no real logos).
Same look as home.py / arcade.py: outlined shapes, soft top-lit gradients."""
import math
import random

import cairo

import home as hm
from arcade import box
from engine import PI, ellipse, glow, hexc, lerp, lerpc, rrect, src, text
from style2 import OUT, _shade_fill

LW = 4.0


def ease01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def burst_bg(ctx, T, c1="#ffe9b0", c2="#f2a65a", cx=360, cy=640, rays=True, a=0.18):
    g = cairo.RadialGradient(cx, cy, 50, cx, cy, 1000)
    g.add_color_stop_rgb(0, *hexc(c1))
    g.add_color_stop_rgb(1, *hexc(c2))
    ctx.set_source(g)
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.fill()
    if rays:
        for k in range(14):
            ang = k * PI / 7 + T * 0.3
            ctx.move_to(cx, cy)
            ctx.line_to(cx + math.cos(ang) * 1600, cy + math.sin(ang) * 1600)
            ctx.line_to(cx + math.cos(ang + 0.12) * 1600, cy + math.sin(ang + 0.12) * 1600)
            ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.fill()


def dark_bg(ctx, top="#1c1f33", bottom="#2b2250"):
    g = cairo.LinearGradient(0, -400, 0, 1700)
    g.add_color_stop_rgb(0, *hexc(top))
    g.add_color_stop_rgb(1, *hexc(bottom))
    ctx.set_source(g)
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.fill()


def speed_lines(ctx, T, cx=360, cy=640, n=30, r0=260, r1=1500, a=0.55, col=(1, 1, 1), seed=5):
    rnd = random.Random(seed)
    for _ in range(n):
        ang = rnd.uniform(0, 2 * PI)
        w = rnd.uniform(0.008, 0.03)
        off = (T * 3 + rnd.random()) % 1
        a0 = r0 + (r1 - r0) * off * 0.4
        ctx.move_to(cx + math.cos(ang) * a0, cy + math.sin(ang) * a0)
        ctx.line_to(cx + math.cos(ang - w) * r1, cy + math.sin(ang - w) * r1)
        ctx.line_to(cx + math.cos(ang + w) * r1, cy + math.sin(ang + w) * r1)
        ctx.close_path()
    ctx.set_source_rgba(*col, a)
    ctx.fill()


def starburst(ctx, x, y, r, k, c1="#fff3a8", c2="#ff7a2a", spikes=14, rot=0.0):
    if k <= 0:
        return
    r = r * (1 + 0.25 * math.exp(-6 * k)) * min(1.0, k * 8)
    pts = []
    for i in range(spikes * 2):
        a = rot + i * PI / spikes
        rr = r if i % 2 == 0 else r * 0.55
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    _shade_fill(ctx, hexc(c1), hexc(c2), y - r, y + r, LW * 1.5)


def shockwave(ctx, x, y, k, col=(1, 1, 1), r_max=520):
    if k <= 0 or k > 1:
        return
    for j in range(3):
        kk = k - j * 0.12
        if kk <= 0:
            continue
        ctx.new_sub_path()
        ctx.arc(x, y, r_max * ease01(kk), 0, 2 * PI)
        ctx.set_source_rgba(*col, (1 - kk) * 0.9)
        ctx.set_line_width(26 * (1 - kk) + 4)
        ctx.stroke()


def stopwatch(ctx, x, y, r, frac, num, T=0.0, ring="#e8574a", num_col=None):
    """Big stopwatch: frac = remaining fraction of the red ring, num = digits in the middle."""
    hm.box(ctx, x - 0.14 * r, y - 1.32 * r, 0.28 * r, 0.3 * r, "#c9ced8", "#8f97a5", r=0.05 * r, lw=0.05 * r)
    ctx.new_sub_path()
    ctx.arc(x, y, r * 1.08, 0, 2 * PI)
    _shade_fill(ctx, hexc("#f4f6fa"), hexc("#b9bec7"), y - r, y + r, 0.07 * r)
    ctx.new_sub_path()
    ctx.arc(x, y, r * 0.88, 0, 2 * PI)
    ctx.set_source_rgb(*hexc("#fbfbfd"))
    ctx.fill()
    for k in range(12):
        a = k * PI / 6 - PI / 2
        ctx.move_to(x + math.cos(a) * r * 0.74, y + math.sin(a) * r * 0.74)
        ctx.line_to(x + math.cos(a) * r * 0.84, y + math.sin(a) * r * 0.84)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(0.04 * r)
    ctx.stroke()
    if frac > 0:
        ctx.new_sub_path()
        ctx.arc(x, y, r * 0.96, -PI / 2, -PI / 2 + 2 * PI * frac)
        ctx.set_source_rgb(*hexc(ring))
        ctx.set_line_width(0.13 * r)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    text(ctx, num, x, y + 0.02 * r, r * 0.85, hexc(num_col or "#1d1830"), outline=False)


def digital(ctx, x, y, s, txt, col="#4fe3ff", glow_a=0.5, size=90):
    hm.box(ctx, x - 230 * s, y - 80 * s, 460 * s, 160 * s, "#2b2f45", "#171a2a", r=20 * s, lw=6 * s)
    hm.box(ctx, x - 208 * s, y - 60 * s, 416 * s, 120 * s, "#0b0d16", None, r=10 * s, lw=3 * s)
    glow(ctx, x, y, 240 * s, hexc(col), glow_a * 0.6)
    text(ctx, txt, x, y + 2 * s, size * s, hexc(col), outline=False)


# ---------------------------------------------------------------- obby
def course(ctx, T, n=16, x0=-80, dx=190, y_base=900, numbers=True, lava_on=True):
    hm.game_sky(ctx)
    if lava_on:
        hm.lava(ctx, 1160, T)
    for i in range(n):
        x = x0 + i * dx
        y = y_base - 70 * math.sin(i * 0.9) - (i % 3) * 34
        hm.block(ctx, x, y, 150, 74, top=("#5dd06a", "#f2b84b", "#4fb3e8")[i % 3])
        if numbers:
            text(ctx, str(i * 7 + 1), x + 75, y + 46, 30, (1, 1, 1), outline=True)
    return [(x0 + i * dx, y_base - 70 * math.sin(i * 0.9) - (i % 3) * 34) for i in range(n)]


def finish(ctx, x, y, s, T, confetti=0.0):
    for dx in (-130, 130):
        hm.box(ctx, x + dx * s - 14 * s, y - 330 * s, 28 * s, 330 * s, "#e9edf2", "#b9bec7", r=6 * s)
    hm.box(ctx, x - 150 * s, y - 380 * s, 300 * s, 80 * s, "#ffffff", "#e9edf2", r=8 * s)
    for i in range(10):   # checkered banner
        for j in range(2):
            if (i + j) % 2 == 0:
                ctx.rectangle(x - 150 * s + i * 30 * s, y - 380 * s + j * 40 * s, 30 * s, 40 * s)
    ctx.set_source_rgb(*OUT)
    ctx.fill()
    ctx.move_to(x, y - 380 * s)
    ctx.line_to(x, y - 470 * s)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(8 * s)
    ctx.stroke()
    ctx.move_to(x, y - 470 * s)
    ctx.line_to(x + 90 * s, y - 440 * s + math.sin(T * 9) * 8 * s)
    ctx.line_to(x, y - 410 * s)
    ctx.close_path()
    _shade_fill(ctx, hexc("#4fd16a"), hexc("#2e9c46"), y - 470 * s, y - 410 * s, 4 * s)
    if confetti > 0:
        rnd = random.Random(7)
        for i in range(36):
            px = x + rnd.uniform(-300, 300)
            py = y - 600 + ((T - confetti) * rnd.uniform(250, 480) + rnd.uniform(0, 500)) % 900
            ctx.save()
            ctx.translate(px, py)
            ctx.rotate(T * 6 + i)
            ctx.rectangle(-9, -5, 18, 10)
            ctx.set_source_rgb(*hexc(rnd.choice(["#e8574a", "#4fb3a9", "#f2b84b", "#9d7fd6", "#ffffff"])))
            ctx.fill()
            ctx.restore()


# ---------------------------------------------------------------- noob king arena
def arena(ctx, T, crack=0.0):
    dark_bg(ctx, "#1b1235", "#3a1f4a")
    for x in (60, 660):   # torches
        hm.box(ctx, x - 14, 480, 28, 240, "#6b4422", "#4a2e16", r=6)
        glow(ctx, x, 440, 200, (1, 0.6, 0.25), 0.55 + 0.15 * math.sin(T * 12 + x))
        ctx.move_to(x - 28, 480)
        ctx.curve_to(x - 34, 400, x - 6, 410, x, 340 + math.sin(T * 14) * 8)
        ctx.curve_to(x + 6, 410, x + 34, 400, x + 28, 480)
        ctx.close_path()
        _shade_fill(ctx, hexc("#ffe27a"), hexc("#ff6a2a"), 340, 480, 4)
    box(ctx, -600, 900, 2000, 900, "#5a4a72", "#2f2545", r=0)
    for r in range(8):   # stone tiles
        ctx.move_to(-600, 900 + r * 90 + r * r * 4)
        ctx.line_to(1400, 900 + r * 90 + r * r * 4)
    for k in range(-8, 16):
        ctx.move_to(360 + (k - 3.5) * 40, 900)
        ctx.line_to(360 + (k - 3.5) * 190, 1900)
    ctx.set_source_rgba(0, 0, 0, 0.3)
    ctx.set_line_width(4)
    ctx.stroke()
    if crack > 0:
        rnd = random.Random(2)
        ctx.move_to(360, 960)
        for i in range(8):
            ctx.line_to(360 + rnd.uniform(-90, 90) * (1 + i * 0.3) * crack, 960 + i * 55 * crack)
        ctx.set_source_rgb(1, 0.6, 0.2)
        ctx.set_line_width(9)
        ctx.stroke()
        glow(ctx, 360, 1000, 260 * crack, (1, 0.5, 0.2), 0.5 * crack)


def cape(ctx, x, y, s, T, col="#d63c3c"):
    sway = math.sin(T * 5) * 10 * s
    ctx.move_to(x - 36 * s, y - 138 * s)
    ctx.line_to(x + 36 * s, y - 138 * s)
    ctx.curve_to(x + 70 * s, y - 80 * s, x + 82 * s + sway, y - 20 * s, x + 66 * s + sway, y + 6 * s)
    ctx.line_to(x - 66 * s + sway, y + 6 * s)
    ctx.curve_to(x - 82 * s + sway, y - 20 * s, x - 70 * s, y - 80 * s, x - 36 * s, y - 138 * s)
    ctx.close_path()
    _shade_fill(ctx, hexc(col), lerpc(hexc(col), (0, 0, 0), 0.35), y - 138 * s, y, 3.5 * s)


def stars_around(ctx, x, y, r, T, n=3):
    for i in range(n):
        a = T * 5 + i * 2 * PI / n
        text(ctx, "★", x + math.cos(a) * r, y + math.sin(a) * r * 0.35, 40, hexc("#ffd84a"), outline=True)


# ---------------------------------------------------------------- shop
def gamepass(ctx, x, y, s, col, glyph, lab, owned=0.0):
    hm.box(ctx, x - 70 * s, y - 95 * s, 140 * s, 190 * s, "#ffffff", "#e4e7ef", r=14 * s, lw=4 * s)
    hm.box(ctx, x - 58 * s, y - 83 * s, 116 * s, 110 * s, col, lerpc(hexc(col), (0, 0, 0), 0.25), r=10 * s, lw=3 * s)
    text(ctx, glyph, x, y - 30 * s, 64 * s, (1, 1, 1), outline=True)
    text(ctx, lab, x, y + 52 * s, 17 * s, hexc("#1d1830"), outline=False)
    hm.box(ctx, x - 50 * s, y + 66 * s, 100 * s, 24 * s, "#4fd16a" if owned < 0.5 else "#9aa1ad",
           None, r=8 * s, lw=2.5 * s)
    text(ctx, "BUY" if owned < 0.5 else "OWNED", x, y + 78 * s, 15 * s, (1, 1, 1), outline=False)


PASSES = [("#e8574a", "★", "VIP"), ("#4f8bff", "♥", "LIFE+"), ("#9d7fd6", "♦", "RICH"), ("#f2b84b", "☀", "LUCK"),
          ("#4fb3a9", "♣", "PETS"), ("#ff4f8b", "♫", "DANCE"), ("#7cc08a", "✦", "FAST"), ("#e57373", "♠", "BOSS")]


def shop_wall(ctx, T, bought_at=None, x0=-120, cols=6, rows=3):
    dark_bg(ctx, "#2a2e55", "#1c1f33")
    hm.box(ctx, -300, 360, 1400, 840, "#3a3f6a", "#262a4a", r=0)
    for r in range(rows):
        hm.box(ctx, -300, 500 + r * 270 + 90, 1400, 22, "#b07a4a", "#8a5a33", r=4)
        for c in range(cols):
            i = r * cols + c
            owned = 0.0
            if bought_at is not None:
                owned = 1.0 if T > bought_at + i * 0.1 else 0.0
            col, g, lab = PASSES[i % len(PASSES)]
            gamepass(ctx, x0 + 130 + c * 165, 500 + r * 270, 0.62, col, g, lab, owned)


def toaster(ctx, x, y, s, T, toast=0.0, mad=False):
    """Cute chrome toaster with a face; toast pops from the slots."""
    if s <= 0.02:
        return
    for dx in (-110, 110):   # feet
        hm.box(ctx, x + dx * s - 24 * s, y - 10 * s, 48 * s, 26 * s, "#3a3f55", "#262a3a", r=8 * s, lw=3 * s)
    for k, dx in enumerate((-60, 60)):   # toast
        up = (math.sin(T * 4 + k * 1.6) * 0.5 + 0.5) * 60 * s * toast
        rrect(ctx, x + dx * s - 42 * s, y - 250 * s - up, 84 * s, 90 * s, 18 * s)
        _shade_fill(ctx, hexc("#f2c685"), hexc("#c98a4a"), y - 250 * s - up, y - 160 * s - up, 4 * s)
    hm.box(ctx, x - 150 * s, y - 210 * s, 300 * s, 210 * s, "#e9edf2", "#a9afbc", r=40 * s, lw=6 * s)
    hm.box(ctx, x - 110 * s, y - 222 * s, 100 * s, 22 * s, "#3a3f55", "#171a2a", r=10 * s, lw=3 * s)
    hm.box(ctx, x + 10 * s, y - 222 * s, 100 * s, 22 * s, "#3a3f55", "#171a2a", r=10 * s, lw=3 * s)
    hm.box(ctx, x + 150 * s, y - 150 * s, 30 * s, 60 * s, "#c9ced8", "#8f97a5", r=8 * s, lw=3 * s)
    ctx.move_to(x - 126 * s, y - 175 * s)   # chrome highlight
    ctx.line_to(x - 40 * s, y - 175 * s)
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(10 * s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    for dx in (-52, 52):   # eyes
        ellipse(ctx, x + dx * s, y - 120 * s, 22 * s, 28 * s)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(4 * s)
        ctx.stroke()
        ctx.new_sub_path()
        ctx.arc(x + dx * s + math.sin(T * 3) * 4 * s, y - 118 * s, 9 * s, 0, 2 * PI)
        ctx.fill()
    ctx.set_source_rgb(*OUT)
    if mad:
        for dx, sg in ((-52, 1), (52, -1)):
            ctx.move_to(x + (dx - 24) * s, y - 160 * s + sg * 10 * s)
            ctx.line_to(x + (dx + 24) * s, y - 160 * s - sg * 10 * s)
        ctx.set_line_width(7 * s)
        ctx.stroke()
    ctx.arc(x, y - 66 * s, 30 * s, 0.2, PI - 0.2)
    ctx.set_line_width(6 * s)
    ctx.stroke()


# ---------------------------------------------------------------- egg, pet
def egg(ctx, x, y, s, T, crack=0.0, glow_k=0.0):
    glow(ctx, x, y - 140 * s, 360 * s, (1, 0.9, 0.5), 0.35 + 0.5 * glow_k)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.sin(T * (10 + 20 * crack)) * (0.03 + 0.1 * crack))
    ctx.move_to(0, 0)
    ctx.curve_to(-150 * s, 0, -140 * s, -300 * s, 0, -330 * s)
    ctx.curve_to(140 * s, -300 * s, 150 * s, 0, 0, 0)
    ctx.close_path()
    _shade_fill(ctx, hexc("#fff6e0"), hexc("#e8c98a"), -330 * s, 0, 6 * s)
    for sx, sy, c in ((-60, -120, "#4fb3e8"), (50, -190, "#ff4f8b"), (60, -80, "#9d7fd6"), (-40, -240, "#4fd16a")):
        ctx.new_sub_path()
        ctx.arc(sx * s, sy * s, 22 * s, 0, 2 * PI)
        src(ctx, hexc(c))
        ctx.fill()
    if crack > 0:
        rnd = random.Random(4)
        ctx.move_to(-110 * s, -170 * s)
        n = 9
        for i in range(1, int(n * crack) + 1):
            ctx.line_to((-110 + i * 220 / n) * s, (-170 + (i % 2) * 70 - rnd.uniform(0, 30)) * s)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(7 * s)
        ctx.stroke()
        glow(ctx, 0, -170 * s, 200 * s, (1, 0.95, 0.6), 0.8 * crack)
    ctx.restore()


def pet(ctx, x, y, s, T):
    """Legendary golden block cat with wings and a halo."""
    if s <= 0.02:
        return
    for k in range(7):   # rainbow aura
        c = ("#ff4f4f", "#ff9b3a", "#ffe14a", "#5dd06a", "#4fb3e8", "#6b6bff", "#c26bff")[k]
        ctx.new_sub_path()
        ctx.arc(x, y - 150 * s, (330 - k * 22) * s, PI, 2 * PI)
        ctx.set_source_rgba(*hexc(c), 0.55)
        ctx.set_line_width(22 * s)
        ctx.stroke()
    glow(ctx, x, y - 160 * s, 420 * s, (1, 0.95, 0.6), 0.55)
    wing = math.sin(T * 8) * 0.18
    for side in (-1, 1):   # wings
        ctx.save()
        ctx.translate(x + side * 80 * s, y - 150 * s)
        ctx.rotate(side * (0.5 + wing))
        ctx.move_to(0, 0)
        ctx.curve_to(side * 140 * s, -40 * s, side * 210 * s, -130 * s, side * 170 * s, -210 * s)
        ctx.curve_to(side * 120 * s, -150 * s, side * 60 * s, -120 * s, 0, -60 * s)
        ctx.close_path()
        _shade_fill(ctx, hexc("#ffffff"), hexc("#bfe6ff"), -210 * s, 0, 5 * s)
        ctx.restore()
    hm.box(ctx, x + 70 * s, y - 120 * s, 120 * s, 28 * s, "#ffd84a", "#d6a23a", r=12 * s, lw=4 * s)   # tail
    hm.box(ctx, x - 110 * s, y - 150 * s, 220 * s, 150 * s, "#ffd84a", "#d6a23a", r=26 * s, lw=6 * s)   # body
    for dx in (-60, 60):
        hm.box(ctx, x + dx * s - 24 * s, y - 20 * s, 48 * s, 36 * s, "#ffe27a", "#d6a23a", r=12 * s, lw=4 * s)
    hm.box(ctx, x - 120 * s, y - 330 * s, 240 * s, 190 * s, "#ffe27a", "#e0a93a", r=34 * s, lw=6 * s)    # head
    for dx in (-1, 1):   # ears
        ctx.move_to(x + dx * 50 * s, y - 330 * s)
        ctx.line_to(x + dx * 108 * s, y - 330 * s)
        ctx.line_to(x + dx * 100 * s, y - 410 * s)
        ctx.close_path()
        _shade_fill(ctx, hexc("#ffe27a"), hexc("#e0a93a"), y - 410 * s, y - 330 * s, 5 * s)
    for dx in (-1, 1):   # star eyes
        text(ctx, "★", x + dx * 52 * s, y - 250 * s, 58 * s, hexc("#ff4f8b"), outline=True)
    ctx.arc(x, y - 200 * s, 20 * s, 0.2, PI - 0.2)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(6 * s)
    ctx.stroke()
    ellipse(ctx, x, y - 340 * s - 26 * s, 90 * s, 16 * s)     # halo
    ctx.set_source_rgba(1, 0.95, 0.5, 0.9)
    ctx.set_line_width(10 * s)
    ctx.stroke()


def sparkles(ctx, T, cx, cy, spread=420, n=16, seed=3):
    rnd = random.Random(seed)
    for _ in range(n):
        x = cx + rnd.uniform(-spread, spread)
        y = cy + rnd.uniform(-spread, spread)
        ph = (T * 1.4 + rnd.random()) % 1
        text(ctx, "✦", x, y, 34 * (1 - abs(ph - 0.5) * 1.4), (1, 0.96, 0.6), outline=False)


# ---------------------------------------------------------------- secret button
def secret_button(ctx, x, y, s, T, pressed=0.0):
    glow(ctx, x, y - 100 * s, 520 * s, (0.5, 1, 0.6), 0.45 + 0.1 * math.sin(T * 6))
    hm.box(ctx, x - 190 * s, y - 20 * s, 380 * s, 220 * s, "#5a5f6e", "#3c4050", r=18 * s, lw=6 * s)   # pedestal
    hm.box(ctx, x - 160 * s, y - 40 * s, 320 * s, 60 * s, "#8a8f9a", "#5a5f6a", r=14 * s, lw=5 * s)
    dy = 36 * s * pressed
    ctx.save()
    ctx.translate(0, dy)
    hm.box(ctx, x - 130 * s, y - 130 * s, 260 * s, 100 * s, "#4fd16a", "#2e9c46", r=40 * s, lw=6 * s)
    hm.box(ctx, x - 110 * s, y - 120 * s, 220 * s, 40 * s, "#9bf0a8", "#5fd27a", r=20 * s, lw=0)
    text(ctx, "+10s", x, y - 78 * s, 54 * s, (1, 1, 1), outline=True)
    ctx.restore()


# ---------------------------------------------------------------- misc
def loop_arrow(ctx, x, y, r, T, col="#ffd84a"):
    for k in range(2):
        a0 = T * 2.5 + k * PI
        ctx.new_sub_path()
        ctx.arc(x, y, r, a0, a0 + PI * 0.8)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(48)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc(col))
        ctx.set_line_width(32)
        ctx.stroke()
        ea = a0 + PI * 0.8
        px, py = x + math.cos(ea) * r, y + math.sin(ea) * r
        tx, ty = -math.sin(ea), math.cos(ea)
        nx, ny = math.cos(ea), math.sin(ea)
        ctx.move_to(px + tx * 60, py + ty * 60)
        ctx.line_to(px + nx * 55, py + ny * 55)
        ctx.line_to(px - nx * 55, py - ny * 55)
        ctx.close_path()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(10)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc(col))
        ctx.fill()


def comment_bubble(ctx, x, y, s, lines, T=0.0):
    if s <= 0.02:
        return
    hm.box(ctx, x - 270 * s, y - 120 * s, 540 * s, 240 * s, "#ffffff", "#eef1f7", r=34 * s, lw=6 * s)
    ctx.move_to(x - 120 * s, y + 118 * s)
    ctx.line_to(x - 170 * s, y + 190 * s)
    ctx.line_to(x - 60 * s, y + 118 * s)
    ctx.close_path()
    ctx.set_source_rgb(*hexc("#eef1f7"))
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(6 * s)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x - 210 * s, y - 60 * s, 34 * s, 0, 2 * PI)
    _shade_fill(ctx, hexc("#4fb3a9"), hexc("#2f8a82"), y - 94 * s, y - 26 * s, 4 * s)
    text(ctx, lines[0], x + 30 * s, y - 60 * s, 44 * s, hexc("#1d1830"), outline=False)
    text(ctx, lines[1], x, y + 40 * s, 74 * s, hexc("#e8574a"), outline=False)


def hud(ctx, txt, bump=0.0, urgent=False):
    """Timer pill in screen space (top centre, inside the Shorts safe zone)."""
    k = 1 + 0.35 * bump
    ctx.save()
    ctx.translate(360, 186)
    ctx.scale(k, k)
    box(ctx, -125, -30, 250, 60, "#1b1e30", "#101220", r=30, lw=4)
    ctx.new_sub_path()
    ctx.arc(-86, 0, 17, 0, 2 * PI)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.move_to(-86, 0)
    ctx.line_to(-86, -11)
    ctx.move_to(-86, 0)
    ctx.line_to(-79, 4)
    ctx.stroke()
    col = "#ff4f5a" if urgent else "#ffe14a"
    text(ctx, txt, 28, 2, 44, hexc(col), outline=False)
    ctx.restore()
