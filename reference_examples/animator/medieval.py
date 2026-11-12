"""Sets and props for the "medieval kingdoms" reference style: painted sky with
soft clouds, blue mountains with snow, castles with red/teal roofs, patchwork
fields, sunlit stone floor with long diagonal shadows, banners, anvil, barrel of
spears, flip-number sign, helmets with flowers, armies, aerial river + bridge."""
import math
import random

import cairo
import numpy as np

from engine import PI, W, H, ellipse, glow, hexc, lerp, lerpc, rrect, src, text
from style3 import OUT, Char3, darker, lighter, shade, shield

RED = hexc("#c9403a")
TEAL = hexc("#1f8a92")
LW = 3.5


def sky(ctx, y0=-800, y1=1100, top="#5f88d0", bottom="#a9cdf3"):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *hexc(top))
    g.add_color_stop_rgb(1, *hexc(bottom))
    ctx.set_source(g)
    ctx.rectangle(-3000, -5000, W + 6000, H + 10000)
    ctx.fill()


def cloud(ctx, x, y, s=1.0, t=0.0):
    x += t * 6
    puffs = [(-70, 10, 45), (-25, -25, 60), (35, -15, 55), (80, 15, 40), (0, 20, 50)]
    for dx, dy, rr in puffs:  # lavender underside first
        ctx.new_sub_path()
        ctx.arc(x + dx * s, y + (dy + 10) * s, rr * s, 0, 2 * PI)
    src(ctx, hexc("#b9c4e6"))
    ctx.fill()
    for dx, dy, rr in puffs:
        ctx.new_sub_path()
        ctx.arc(x + dx * s, y + dy * s, rr * s * 0.95, 0, 2 * PI)
    src(ctx, hexc("#ffffff"))
    ctx.fill()


def mountains(ctx, base, s=1.0, x0=-600, x1=W + 600, seed=2, col="#8aa4d6"):
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        w = rnd.uniform(220, 360) * s
        h = rnd.uniform(160, 300) * s
        px = x + w / 2
        ctx.move_to(x, base)
        ctx.line_to(px, base - h)
        ctx.line_to(x + w, base)
        ctx.close_path()
        shade(ctx, lighter(hexc(col), 0.1), darker(hexc(col), 0.05), base - h, base, 0)
        ctx.move_to(px - w * 0.14, base - h * 0.72)
        ctx.line_to(px, base - h)
        ctx.line_to(px + w * 0.14, base - h * 0.72)
        ctx.line_to(px + w * 0.05, base - h * 0.78)
        ctx.line_to(px - w * 0.03, base - h * 0.7)
        ctx.close_path()
        src(ctx, hexc("#f4f6fb"))
        ctx.fill()
        x += w * 0.7


def castle(ctx, x, base, s=1.0, roof=RED, haze=0.35):
    wall = lerpc(hexc("#eeeae4"), hexc("#a9cdf3"), haze)
    roofc = lerpc(roof, hexc("#a9cdf3"), haze)
    ctx.rectangle(x - 60 * s, base - 70 * s, 120 * s, 70 * s)
    src(ctx, wall)
    ctx.fill()
    for k, (dx, h) in enumerate(((-60, 130), (0, 170), (60, 130))):
        ctx.rectangle(x + dx * s - 14 * s, base - h * s, 28 * s, h * s)
        src(ctx, wall)
        ctx.fill()
        ctx.move_to(x + dx * s - 18 * s, base - h * s)
        ctx.line_to(x + dx * s, base - (h + 45) * s)
        ctx.line_to(x + dx * s + 18 * s, base - h * s)
        ctx.close_path()
        src(ctx, roofc)
        ctx.fill()
        ctx.move_to(x + dx * s, base - (h + 45) * s)
        ctx.line_to(x + dx * s, base - (h + 62) * s)
        ctx.set_source_rgb(*roofc)
        ctx.set_line_width(2 * s)
        ctx.stroke()


def tree(ctx, x, y, s=1.0, pine=False, haze=0.0):
    col = lerpc(hexc("#5fa35a" if not pine else "#3f7f55"), hexc("#a9cdf3"), haze)
    if pine:
        for k in range(3):
            ctx.move_to(x - (30 - k * 7) * s, y - k * 22 * s)
            ctx.line_to(x, y - (45 + k * 22) * s)
            ctx.line_to(x + (30 - k * 7) * s, y - k * 22 * s)
            ctx.close_path()
            src(ctx, darker(col, k * -0.05))
            ctx.fill()
    else:
        for dx, dy, rr in ((-14, -30, 20), (12, -34, 22), (0, -50, 22)):
            ctx.new_sub_path()
            ctx.arc(x + dx * s, y + dy * s, rr * s, 0, 2 * PI)
        src(ctx, col)
        ctx.fill()


def landscape(ctx, horizon=560, t=0.0, castles=((120, RED), (600, TEAL)), seed=4):
    """Painted backdrop: sky, clouds, mountains, castles, green hills, trees."""
    sky(ctx, horizon - 1300, horizon + 200)
    for k, (cx, cy, cs) in enumerate(((150, horizon - 380, 1.1), (520, horizon - 470, 0.9), (650, horizon - 250, 0.8))):
        cloud(ctx, cx, cy, cs, t)
    mountains(ctx, horizon - 40, 1.0, seed=seed)
    ctx.rectangle(-3000, horizon - 60, W + 6000, 3000)
    shade(ctx, hexc("#a7c99a"), hexc("#7fb06a"), horizon - 60, horizon + 300, 0)
    for x, col in castles:
        castle(ctx, x, horizon - 30, 0.7, col)
    rnd = random.Random(seed)
    for k in range(26):
        tree(ctx, rnd.uniform(-300, W + 300), horizon + rnd.uniform(0, 120), rnd.uniform(0.6, 1.0),
             pine=rnd.random() < 0.4, haze=0.3)


def stone_floor(ctx, y0, y1=H + 600, vx=W / 2, col="#d6bd9f", shadow_dir=(0.9, 0.35)):
    c = hexc(col)
    ctx.rectangle(-3000, y0, W + 6000, y1 - y0 + 3000)
    shade(ctx, lighter(c, 0.08), darker(c, 0.05), y0, y1, 0)
    ctx.set_source_rgba(*hexc("#8a777b"), 0.7)
    ctx.set_line_width(2.5)
    y, step, row = y0, 28, 0
    while y < y1 + 800:
        ctx.move_to(-3000, y)
        ctx.line_to(W + 3000, y)
        ny = y + step
        off = (row % 2) * 0.5
        for k in range(-20, 21):
            fx = vx + (k + off) * 70 * (1 + (y - y0) / 260)
            ctx.move_to(fx, y)
            ctx.line_to(fx + (fx - vx) * step / 260, ny)
        y = ny
        step *= 1.22
        row += 1
    ctx.stroke()


def cast_shadow(ctx, x, y, w, length=260, dx=0.9, dy=0.3, a=0.32):
    """Long soft shadow on the floor from an object of width w standing at (x, y)."""
    ctx.move_to(x - w / 2, y)
    ctx.line_to(x + w / 2, y)
    ctx.line_to(x + w / 2 + length * dx, y + length * dy)
    ctx.line_to(x - w / 2 + length * dx, y + length * dy)
    ctx.close_path()
    ctx.set_source_rgba(0.28, 0.2, 0.32, a)
    ctx.fill()


def parapet(ctx, y_top, y_floor, col="#e4d6c1", tallies=0):
    c = hexc(col)
    ctx.rectangle(-3000, y_top, W + 6000, y_floor - y_top)
    shade(ctx, lighter(c, 0.08), darker(c, 0.1), y_top, y_floor, 0)
    ctx.set_source_rgba(*hexc("#a8958a"), 0.8)
    ctx.set_line_width(2)
    for k, y in enumerate(range(int(y_top), int(y_floor), 34)):
        ctx.move_to(-3000, y)
        ctx.line_to(W + 3000, y)
        for x in range(-600 + (k % 2) * 45, W + 600, 90):
            ctx.move_to(x, y)
            ctx.line_to(x, min(y + 34, y_floor))
    ctx.stroke()
    ctx.rectangle(-3000, y_top - 14, W + 6000, 18)
    shade(ctx, lighter(c, 0.15), c, y_top - 14, y_top + 4, 0)
    for k in range(tallies):  # scratched tally marks: years passing
        x = 40 + (k // 5) * 70 + (k % 5) * 9
        ctx.move_to(x, y_top + 30)
        ctx.line_to(x - 2, y_top + 62)
        if k % 5 == 4:
            ctx.move_to(x - 40, y_top + 40)
            ctx.line_to(x + 4, y_top + 56)
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(2.5)
    ctx.stroke()


def banner(ctx, x, y, s=1.0, col=RED, emblem="arrow", t=0.0):
    ctx.move_to(x, y - 30 * s)
    ctx.line_to(x, y + 560 * s)
    ctx.set_source_rgb(*hexc("#6b4a2a"))
    ctx.set_line_width(7 * s)
    ctx.stroke()
    wave = math.sin(t * 2.2) * 6 * s
    ctx.move_to(x + 6 * s, y)
    ctx.line_to(x + 120 * s, y + wave * 0.3)
    ctx.line_to(x + 120 * s + wave, y + 230 * s)
    ctx.line_to(x + 63 * s + wave, y + 190 * s)
    ctx.line_to(x + 6 * s + wave * 0.5, y + 230 * s)
    ctx.close_path()
    shade(ctx, lighter(col, 0.1), darker(col, 0.2), y, y + 230 * s, LW)
    cx, cy = x + 63 * s + wave * 0.5, y + 95 * s
    if emblem == "arrow":
        ctx.move_to(cx, cy + 45 * s)
        ctx.line_to(cx, cy - 40 * s)
        ctx.move_to(cx - 15 * s, cy - 22 * s)
        ctx.line_to(cx, cy - 42 * s)
        ctx.line_to(cx + 15 * s, cy - 22 * s)
        ctx.set_source_rgb(*hexc("#f2c443"))
        ctx.set_line_width(6 * s)
        ctx.stroke()
    else:
        ctx.new_sub_path()
        ctx.arc(cx, cy, 28 * s, 0, 2 * PI)
        src(ctx, hexc("#e9edf2"))
        ctx.fill()
        ctx.new_sub_path()
        ctx.arc(cx, cy, 11 * s, 0, 2 * PI)
        src(ctx, darker(col, 0.3))
        ctx.fill()


def anvil(ctx, x, y, s=1.0, spark_t=None):
    """Anvil on a tree stump; (x, y) = stump bottom centre."""
    ctx.move_to(x - 55 * s, y)
    ctx.line_to(x - 50 * s, y - 120 * s)
    ctx.line_to(x + 50 * s, y - 120 * s)
    ctx.line_to(x + 55 * s, y)
    ctx.close_path()
    shade(ctx, hexc("#c08447"), hexc("#8a5a2b"), y - 120 * s, y, LW)
    ellipse(ctx, x, y - 120 * s, 50 * s, 14 * s)
    shade(ctx, hexc("#e2b27a"), hexc("#c08a52"), y - 134 * s, y - 106 * s, LW)
    ctx.move_to(x - 30 * s, y - 128 * s)
    ctx.line_to(x - 22 * s, y - 165 * s)
    ctx.line_to(x - 75 * s, y - 175 * s)
    ctx.line_to(x - 85 * s, y - 195 * s)
    ctx.line_to(x + 85 * s, y - 195 * s)
    ctx.curve_to(x + 120 * s, y - 192 * s, x + 130 * s, y - 182 * s, x + 135 * s, y - 175 * s)
    ctx.line_to(x + 22 * s, y - 165 * s)
    ctx.line_to(x + 30 * s, y - 128 * s)
    ctx.close_path()
    shade(ctx, hexc("#b7bcc6"), hexc("#6d727c"), y - 195 * s, y - 128 * s, LW)
    if spark_t is not None and spark_t >= 0:
        rnd = random.Random(int(spark_t * 8))
        for k in range(8):
            a = rnd.uniform(-PI * 0.9, -PI * 0.1)
            ln = rnd.uniform(20, 60) * s * min(1, spark_t * 6)
            ctx.move_to(x + 20 * s, y - 198 * s)
            ctx.line_to(x + 20 * s + math.cos(a) * ln, y - 198 * s + math.sin(a) * ln)
        ctx.set_source_rgba(1, 0.8, 0.3, max(0, 1 - spark_t * 3))
        ctx.set_line_width(3 * s)
        ctx.stroke()


def barrel(ctx, x, y, s=1.0, spears=3):
    """Barrel (with spears standing in it); (x, y) = bottom centre."""
    for k in range(spears):
        sx = x + (k - (spears - 1) / 2) * 22 * s
        ctx.move_to(sx, y - 60 * s)
        ctx.line_to(sx + (k - 1) * 6 * s, y - 330 * s)
        ctx.set_source_rgb(*hexc("#b07a3a"))
        ctx.set_line_width(7 * s)
        ctx.stroke()
        tx, ty = sx + (k - 1) * 6 * s, y - 330 * s
        ctx.move_to(tx, ty - 65 * s)
        ctx.curve_to(tx + 14 * s, ty - 40 * s, tx + 12 * s, ty - 15 * s, tx, ty)
        ctx.curve_to(tx - 12 * s, ty - 15 * s, tx - 14 * s, ty - 40 * s, tx, ty - 65 * s)
        shade(ctx, hexc("#eef1f5"), hexc("#a5abb8"), ty - 65 * s, ty, 2.5 * s)
    ctx.move_to(x - 50 * s, y - 150 * s)
    ctx.curve_to(x - 62 * s, y - 100 * s, x - 62 * s, y - 50 * s, x - 50 * s, y)
    ctx.line_to(x + 50 * s, y)
    ctx.curve_to(x + 62 * s, y - 50 * s, x + 62 * s, y - 100 * s, x + 50 * s, y - 150 * s)
    ctx.close_path()
    shade(ctx, hexc("#c48a52"), hexc("#8a5a2b"), y - 150 * s, y, LW)
    for f in (0.15, 0.5, 0.85):
        ctx.move_to(x - 58 * s, y - 150 * s * f)
        ctx.line_to(x + 58 * s, y - 150 * s * f)
    ctx.set_source_rgb(*hexc("#80858f"))
    ctx.set_line_width(8 * s)
    ctx.stroke()


def round_table(ctx, x, y, s=1.0):
    """Foreground round war-table edge (red/teal halves) at the bottom of a frame."""
    ellipse(ctx, x, y, 330 * s, 120 * s)
    shade(ctx, hexc("#e2b54a"), hexc("#b5862a"), y - 120 * s, y + 120 * s, LW)
    ctx.save()
    ellipse(ctx, x, y, 290 * s, 100 * s)
    ctx.clip()
    ctx.rectangle(x - 400 * s, y - 200 * s, 400 * s, 400 * s)
    src(ctx, RED)
    ctx.fill()
    ctx.rectangle(x, y - 200 * s, 400 * s, 400 * s)
    src(ctx, TEAL)
    ctx.fill()
    ctx.restore()


def years_sign(ctx, x, y, s=1.0, number="100", flip=1.0):
    """'YEARS AT WAR' board with flip digits; (x, y) = bottom of the left post."""
    for px in (x, x + 380 * s):
        ctx.rectangle(px - 10 * s, y - 560 * s, 26 * s, 560 * s)
        shade(ctx, hexc("#a36a35"), hexc("#7a4c22"), y - 560 * s, y, LW)
    ctx.rectangle(x - 30 * s, y - 520 * s, 440 * s, 290 * s)
    shade(ctx, hexc("#b9824a"), hexc("#94622f"), y - 520 * s, y - 230 * s, LW)
    ctx.rectangle(x - 30 * s, y - 520 * s, 220 * s, 80 * s)
    src(ctx, hexc("#c13a2f"))
    ctx.fill()
    ctx.rectangle(x + 190 * s, y - 520 * s, 220 * s, 80 * s)
    src(ctx, TEAL)
    ctx.fill()
    text(ctx, "YEARS AT WAR", x + 180 * s, y - 480 * s, 44 * s, hexc("#fff5e6"), outline=True)
    ctx.rectangle(x + 70 * s, y - 420 * s, 240 * s, 140 * s)
    src(ctx, OUT)
    ctx.fill()
    for k, ch in enumerate(number):
        cx = x + 110 * s + k * 80 * s
        rrect(ctx, cx - 32 * s, y - 408 * s, 64 * s, 116 * s, 6 * s)
        shade(ctx, hexc("#fff4dc"), hexc("#e4d2ad"), y - 408 * s, y - 292 * s, 2.5 * s)
        if flip < 1 and k == len(number) - 1:
            continue
        text(ctx, ch, cx, y - 350 * s, 80 * s, OUT, outline=False)


def helmet_flower(ctx, x, y, s=1.0, flower="#e8574a"):
    ellipse(ctx, x, y, 60 * s, 14 * s)
    ctx.set_source_rgba(0.25, 0.2, 0.3, 0.35)
    ctx.fill()
    ctx.new_sub_path()
    ctx.arc(x, y, 50 * s, PI, 2 * PI)
    ctx.close_path()
    shade(ctx, hexc("#c3c8d1"), hexc("#80858f"), y - 50 * s, y, LW)
    for k in range(3):  # rust spots
        ctx.new_sub_path()
        ctx.arc(x - 20 * s + k * 18 * s, y - 20 * s - (k % 2) * 12 * s, 5 * s, 0, 2 * PI)
        src(ctx, hexc("#b0643a"))
        ctx.fill()
    ctx.move_to(x, y - 45 * s)
    ctx.curve_to(x + 5 * s, y - 80 * s, x - 5 * s, y - 100 * s, x + 2 * s, y - 120 * s)
    ctx.set_source_rgb(*hexc("#4f9a43"))
    ctx.set_line_width(4 * s)
    ctx.stroke()
    for k in range(3):
        ctx.new_sub_path()
        ctx.arc(x + 2 * s + (k - 1) * 9 * s, y - 124 * s - (k % 2) * 6 * s, 8 * s, 0, 2 * PI)
        src(ctx, hexc(flower))
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(1.5 * s)
        ctx.stroke()


SOLDIER_T = Char3("#3aa6a0", outfit="tunic", helmet=True)
SOLDIER_R = Char3("#d9534a", outfit="tunic", helmet=True)


def army_rows(ctx, vx, vy, x_near, y_near, rows=10, per_row=1, side=TEAL, s_near=0.9, t=0.0):
    """A line of soldiers receding toward a vanishing point (low ground angle)."""
    ch = SOLDIER_T if side is TEAL else SOLDIER_R
    for k in reversed(range(rows)):
        f = k / rows
        x = lerp(x_near, vx, f ** 0.6)
        y = lerp(y_near, vy, f ** 0.6)
        s = s_near * (1 - f ** 0.6) + 0.04
        ch.draw(ctx, x, y, s, "neutral", t + k, arms=("down", "hold"), bob=0.2, shadow=False)
        shield(ctx, x + 0.45 * 64 * s, y - 1.6 * 64 * s, 0.55 * 64 * s,
               teal="#55c1ba" if side is TEAL else "#e8574a")


def crowd_aerial(ctx, x0, y0, x1, y1, col, flag_col, seed=1, t=0.0, density=1.0):
    """Top-down army: dense dots of helmets with shields, plus flags."""
    rnd = random.Random(seed)
    step = 11 / max(0.3, density)
    y = y0
    while y < y1:
        x = x0 + rnd.uniform(0, step)
        while x < x1:
            ctx.new_sub_path()
            ctx.arc(x, y, 4, 0, 2 * PI)
            src(ctx, hexc("#e9edf2"))
            ctx.fill()
            ctx.new_sub_path()
            ctx.arc(x + 2, y + 3, 2.6, 0, 2 * PI)
            src(ctx, col)
            ctx.fill()
            x += step
        y += step
    for k in range(int((x1 - x0) * (y1 - y0) / 9000)):
        fx, fy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        ctx.move_to(fx, fy)
        ctx.line_to(fx, fy - 40)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(2)
        ctx.stroke()
        w = math.sin(t * 3 + fx) * 3
        ctx.rectangle(fx, fy - 40, 16 + w, 22)
        src(ctx, flag_col)
        ctx.fill()


def river_aerial(ctx, t=0.0, bridge_y=760, ducks=True):
    """High aerial: river running away from camera (narrower far up the frame),
    armies on both banks, stone bridge across the bottom third."""
    def wx(x, y):  # fake perspective: squeeze toward the vertical centre line far away
        f = 0.45 + 0.55 * min(1.2, max(0.0, (y + 300) / 1500))
        return W / 2 + (x - W / 2) * f
    ctx.rectangle(-3000, -5000, W + 6000, H + 10000)
    src(ctx, hexc("#9cc26a"))
    ctx.fill()
    rnd = random.Random(9)
    for k in range(70):  # patchwork fields
        x, y = rnd.uniform(-500, W + 500), rnd.uniform(-300, H + 400)
        f = 0.45 + 0.55 * min(1.2, max(0.0, (y + 300) / 1500))
        ctx.save()
        ctx.translate(wx(x, y), y)
        ctx.rotate(rnd.uniform(-0.25, 0.25))
        ctx.rectangle(-80 * f, -40 * f, 160 * f, 80 * f)
        src(ctx, hexc(rnd.choice(["#d9c46a", "#b8cf6f", "#8fbb5c", "#e2c57a", "#a9c96a"])))
        ctx.fill()
        ctx.restore()
    pts_l = [(wx(250, y), y) for y in range(-400, 1800, 100)]
    pts_r = [(wx(470, y), y) for y in range(1700, -500, -100)]
    ctx.move_to(*pts_l[0])
    for p in pts_l[1:] + pts_r:
        ctx.line_to(*p)
    ctx.close_path()
    shade(ctx, hexc("#a9d0e8"), hexc("#7fb1d4"), -400, 1700, LW)
    for k in range(18):  # ripples
        y = (k * 120 + t * 70) % 2200 - 400
        x = wx(300 + (k % 3) * 40, y)
        ctx.move_to(x, y)
        ctx.line_to(x + 25, y + 20)
    ctx.set_source_rgba(1, 1, 1, 0.55)
    ctx.set_line_width(3)
    ctx.stroke()
    for k in range(60):  # forest band far away
        side = rnd.choice((-1, 1))
        x = rnd.uniform(-300, 230) if side < 0 else rnd.uniform(490, 1020)
        y = rnd.uniform(-400, 120)
        tree(ctx, wx(x, y), y, 0.9, pine=rnd.random() < 0.6)
    for (x0, x1, col) in ((-420, 210, RED), (510, 1140, TEAL)):
        y = 160
        while y < 640:
            f = 0.45 + 0.55 * min(1.2, max(0.0, (y + 300) / 1500))
            x = x0
            while x < x1:
                px = wx(x, y)
                ctx.new_sub_path()
                ctx.arc(px, y, 4.2 * f, 0, 2 * PI)
                src(ctx, hexc("#eef1f5"))
                ctx.fill()
                ctx.new_sub_path()
                ctx.arc(px + 1.5 * f, y + 4 * f, 3.4 * f, 0, 2 * PI)
                src(ctx, col)
                ctx.fill()
                x += 12
            y += 12 * f
        for k in range(14):  # banners in the crowd
            fx0, fy = rnd.uniform(x0 + 40, x1 - 40), rnd.uniform(200, 620)
            fx = wx(fx0, fy)
            ctx.move_to(fx, fy)
            ctx.line_to(fx, fy - 46)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(2.5)
            ctx.stroke()
            wv = math.sin(t * 3 + fx) * 3
            ctx.move_to(fx, fy - 46)
            ctx.line_to(fx + 18 + wv, fy - 44)
            ctx.line_to(fx + 18 + wv, fy - 20)
            ctx.line_to(fx + 9, fy - 26)
            ctx.line_to(fx, fy - 20)
            ctx.close_path()
            src(ctx, col)
            ctx.fill()
    # bridge
    ctx.rectangle(-60, bridge_y - 50, W + 120, 100)
    shade(ctx, hexc("#ead6ad"), hexc("#c9a97c"), bridge_y - 50, bridge_y + 50, LW)
    ctx.set_source_rgba(*hexc("#a8865a"), 0.8)
    ctx.set_line_width(2)
    for k, y in enumerate(range(bridge_y - 50, bridge_y + 50, 20)):
        ctx.move_to(-60, y)
        ctx.line_to(W + 60, y)
        for x in range(-60 + (k % 2) * 25, W + 60, 50):
            ctx.move_to(x, y)
            ctx.line_to(x, y + 20)
    ctx.stroke()
    ctx.rectangle(-60, bridge_y + 50, W + 120, 70)
    shade(ctx, hexc("#c4ab83"), hexc("#97805b"), bridge_y + 50, bridge_y + 120, LW)
    for ax in (150, 570):
        ctx.new_sub_path()
        ctx.arc(ax, bridge_y + 125, 120, PI, 2 * PI)
        ctx.close_path()
        src(ctx, hexc("#2a4566"))
        ctx.fill()
    if ducks:
        dx = 360 + math.sin(t * 0.5) * 20
        dy = 1100 - t * 25
        for k in range(5):
            ellipse(ctx, dx - k * 18, dy + k * 6, 7 if k else 10, 5 if k else 7)
            src(ctx, hexc("#f2c443") if k else hexc("#7a5a3a"))
            ctx.fill()


def field_ground(ctx, horizon, vx, y_bottom=H + 400):
    """Low-angle farmland: crop rows and a dirt track converging to the vanishing point."""
    ctx.rectangle(-3000, horizon, W + 6000, 4000)
    shade(ctx, hexc("#b6c48a"), hexc("#7fa63a"), horizon, y_bottom, 0)
    for k in range(-14, 15):
        ctx.move_to(vx + k * 6, horizon)
        ctx.line_to(vx + k * 140, y_bottom)
    ctx.set_source_rgba(*hexc("#5f8a2f"), 0.5)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.move_to(vx - 3, horizon)
    ctx.line_to(vx + 8, horizon)
    ctx.line_to(vx + 520, y_bottom)
    ctx.line_to(vx + 240, y_bottom)
    ctx.close_path()
    shade(ctx, hexc("#e2b981"), hexc("#c78f55"), horizon, y_bottom, 0)
    for off in (300, 470):
        ctx.move_to(vx + 2, horizon)
        ctx.line_to(vx + off, y_bottom)
    ctx.set_source_rgba(*hexc("#8a5a33"), 0.6)
    ctx.set_line_width(7)
    ctx.stroke()


def flowers_foreground(ctx, y, t=0.0, seed=6, x0=-200, x1=W + 200):
    """Big grass blades and flowers close to a low camera."""
    rnd = random.Random(seed)
    for k in range(70):
        x = rnd.uniform(x0, x1)
        h = rnd.uniform(120, 320)
        sway = math.sin(t * 2 + x * 0.05) * 8
        ctx.move_to(x, y + rnd.uniform(0, 160))
        ctx.curve_to(x + sway, y - h * 0.5, x + sway * 1.5, y - h * 0.8, x + sway * 2, y - h)
        ctx.set_source_rgb(*hexc(rnd.choice(["#6fa84a", "#89b94f", "#4f8f3f"])))
        ctx.set_line_width(rnd.uniform(4, 8))
        ctx.stroke()
    for k in range(9):
        x = rnd.uniform(x0, x1)
        fy = y - rnd.uniform(80, 260)
        col = rnd.choice(["#e8574a", "#5b7fe0"])
        ctx.move_to(x, y + 100)
        ctx.line_to(x, fy)
        ctx.set_source_rgb(*hexc("#4f8f3f"))
        ctx.set_line_width(4)
        ctx.stroke()
        for p in range(5):
            a = p * 2 * PI / 5
            ctx.new_sub_path()
            ctx.arc(x + math.cos(a) * 16, fy + math.sin(a) * 16, 15, 0, 2 * PI)
        src(ctx, hexc(col))
        ctx.fill()


def blurred(ctx, fn, sigma=3.0, haze=0.18):
    """Draw a backdrop out of focus (depth of field), like the reference's painted
    backgrounds: render it with the current camera, blur it, lay a light haze."""
    import cv2
    m = ctx.get_matrix()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c2 = cairo.Context(surf)
    c2.set_matrix(m)
    fn(c2)
    if haze:
        c2.identity_matrix()
        c2.set_source_rgba(0.86, 0.91, 0.98, haze)
        c2.paint()
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    a[:] = cv2.GaussianBlur(a, (0, 0), sigma)
    surf.mark_dirty()
    ctx.save()
    ctx.identity_matrix()
    ctx.set_source_surface(surf, 0, 0)
    ctx.paint()
    ctx.restore()
