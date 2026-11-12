"""Extra props for speedrun2.py (v2 of the 10-second speedrun story): monitor screens,
keyboard + hands, perspective obby, boss health bar, loot chest, shop front + cart, glass
case, toaster with the kid's hair, billboard, incubator, rarity banner, secret wall,
comment-section phone. Generic blocky game look, no real logos."""
import math
import random

import cairo

import home as hm
import speed as sp
from arcade import box
from engine import PI, ellipse, glow, hexc, lerp, lerpc, rrect, src, text
from style2 import OUT, _shade_fill

TEAL, TEAL_D = "#4fb3a9", "#2f8a82"
SKIN = "#fce7d6"


def _clip(ctx, x, y, w, h, r=4):
    rrect(ctx, x, y, w, h, r)
    ctx.clip()


# ---------------------------------------------------------------- real-life desk
def monitor(ctx, x, y, s, T, screen_fn, on=1.0):
    """Desk monitor standing at (x, y); screen_fn(ctx, sx, sy, sw, sh, T) draws the screen."""
    hm.box(ctx, x - 14 * s, y - 64 * s, 28 * s, 64 * s, "#5a5f6e", "#3c4050", r=4 * s, lw=3 * s)
    hm.box(ctx, x - 70 * s, y - 10 * s, 140 * s, 14 * s, "#5a5f6e", "#3c4050", r=6 * s, lw=3 * s)
    hm.box(ctx, x - 140 * s, y - 250 * s, 280 * s, 196 * s, "#3a3f55", "#262a3a", r=14 * s, lw=4 * s)
    sx, sy, sw, sh = x - 127 * s, y - 237 * s, 254 * s, 170 * s
    ctx.save()
    _clip(ctx, sx, sy, sw, sh, 4 * s)
    screen_fn(ctx, sx, sy, sw, sh, T)
    ctx.restore()
    glow(ctx, x, y - 150 * s, 300 * s, (0.5, 0.75, 1), 0.25 * on)
    return sx, sy, sw, sh


def scr_world(ctx, sx, sy, sw, sh, T, play=0.0, spawn=False, avatar=True):
    """The game as seen on the monitor: sky, grass, the kid's teal avatar, optional PLAY button."""
    g = cairo.LinearGradient(0, sy, 0, sy + sh)
    g.add_color_stop_rgb(0, *hexc("#58a8ff"))
    g.add_color_stop_rgb(1, *hexc("#bfe6ff"))
    ctx.set_source(g)
    ctx.rectangle(sx, sy, sw, sh)
    ctx.fill()
    for k in range(3):
        ctx.rectangle(sx + sw * (0.1 + 0.3 * k), sy + sh * (0.12 + 0.07 * (k % 2)), sw * 0.16, sh * 0.06)
    ctx.set_source_rgba(1, 1, 1, 0.9)
    ctx.fill()
    ctx.rectangle(sx, sy + sh * 0.72, sw, sh * 0.3)
    ctx.set_source_rgb(*hexc("#8fd16a"))
    ctx.fill()
    if spawn:
        ellipse(ctx, sx + sw * 0.5, sy + sh * 0.82, sw * 0.16, sh * 0.05)
        ctx.set_source_rgba(0.4, 1, 0.8, 0.8)
        ctx.fill()
    if avatar:
        hm.avatar(ctx, sx + sw * (0.5 if spawn else 0.32), sy + sh * 0.84, sh / 330, shirt=TEAL, hair="curly",
                  t=T, wave=not spawn)
    if play > 0:
        bx, by, bw, bh = sx + sw * 0.52, sy + sh * 0.36, sw * 0.4, sh * 0.24
        hm.box(ctx, bx, by, bw, bh, "#4fd16a", "#2e9c46", r=bh * 0.3, lw=max(2, sh * 0.02))
        text(ctx, "PLAY ▶", bx + bw / 2, by + bh / 2, bh * 0.5, (1, 1, 1), outline=False)


def scr_loading(ctx, sx, sy, sw, sh, T, frac):
    ctx.rectangle(sx, sy, sw, sh)
    ctx.set_source_rgb(*hexc("#101322"))
    ctx.fill()
    text(ctx, "LOADING...", sx + sw / 2, sy + sh * 0.36, sh * 0.13, (1, 1, 1), outline=False)
    bx, by, bw, bh = sx + sw * 0.12, sy + sh * 0.55, sw * 0.76, sh * 0.11
    rrect(ctx, bx, by, bw, bh, bh / 2)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(max(2, sh * 0.015))
    ctx.stroke()
    rrect(ctx, bx + 3, by + 3, max(1, (bw - 6) * frac), bh - 6, (bh - 6) / 2)
    ctx.set_source_rgb(*hexc("#4fd16a"))
    ctx.fill()
    text(ctx, f"{int(frac * 100)}%", sx + sw / 2, sy + sh * 0.8, sh * 0.12, hexc("#ffd84a"), outline=False)


def keyboard(ctx, x, y, s, T, mash=0.0, enter_k=0.0):
    """Keyboard seen from above; mash > 0 flickers keys, enter_k presses ENTER."""
    hm.box(ctx, x - 300 * s, y - 110 * s, 600 * s, 220 * s, "#3a3f55", "#262a3a", r=18 * s, lw=5 * s)
    rnd = random.Random(int(T * 30))
    for r in range(4):
        for c in range(10):
            kx, ky = x - 282 * s + c * 46 * s, y - 92 * s + r * 46 * s
            lit = mash > 0 and rnd.random() < 0.3 * mash
            col = ("#ffd84a", "#e0a93a") if lit else ("#eef1f7", "#b9bec7")
            hm.box(ctx, kx, ky + (5 * s if lit else 0), 40 * s, 40 * s, *col, r=8 * s, lw=2.5 * s)
    dy = 10 * s * enter_k
    col = ("#4fd16a", "#2e9c46") if enter_k > 0 else ("#eef1f7", "#b9bec7")
    hm.box(ctx, x + 180 * s, y - 92 * s + dy, 102 * s, 132 * s, *col, r=12 * s, lw=3 * s)
    text(ctx, "ENTER", x + 231 * s, y - 26 * s + dy, 24 * s, OUT, outline=False)
    hm.box(ctx, x - 180 * s, y + 92 * s - 40 * s, 300 * s, 36 * s, "#eef1f7", "#b9bec7", r=8 * s, lw=2.5 * s)


def hand_up(ctx, x, y, s, ang=0.0, sleeve=TEAL, skin=SKIN, point=False):
    """A hand coming up from the bottom of the frame (palm away), fingers up."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    hm.box(ctx, -46 * s, 0, 92 * s, 320 * s, sleeve, lerpc(hexc(sleeve), (0, 0, 0), 0.25), r=22 * s, lw=4 * s)
    rrect(ctx, -50 * s, -96 * s, 100 * s, 110 * s, 36 * s)
    _shade_fill(ctx, hexc(skin), lerpc(hexc(skin), (0.6, 0.4, 0.3), 0.15), -96 * s, 14 * s, 4 * s)
    fingers = [(0, 112)] if point else [(-36, 62), (-12, 74), (12, 70), (36, 58)]
    for fx, fl in fingers:
        rrect(ctx, fx * s - 11 * s, -96 * s - fl * s, 22 * s, fl * s + 20 * s, 11 * s)
        _shade_fill(ctx, hexc(skin), lerpc(hexc(skin), (0.6, 0.4, 0.3), 0.15), -96 * s - fl * s, -76 * s, 3.5 * s)
    rrect(ctx, -70 * s, -60 * s, 34 * s, 60 * s, 16 * s)   # thumb
    _shade_fill(ctx, hexc(skin), lerpc(hexc(skin), (0.6, 0.4, 0.3), 0.15), -60 * s, 0, 3.5 * s)
    ctx.restore()


def wall_and_desk(ctx, y_desk=760, wall="#8fb7e8"):
    """Close-up background: blue bedroom wall and the wooden desk top."""
    box(ctx, -600, -900, 2000, y_desk + 900, wall, lerpc(hexc(wall), (0, 0, 0), 0.15), r=0, lw=0)
    box(ctx, -600, y_desk, 2000, 1400, "#c98a4a", "#8a5a33", r=0)
    for k in range(-8, 18):
        ctx.move_to(k * 90, y_desk)
        ctx.line_to(k * 140 - 300, y_desk + 1400)
    ctx.set_source_rgba(0, 0, 0, 0.07)
    ctx.set_line_width(4)
    ctx.stroke()


# ---------------------------------------------------------------- obby, seen down its length
def course_persp(ctx, T, n=24, horizon=430):
    hm.game_sky(ctx)
    g = cairo.LinearGradient(0, horizon, 0, 1500)
    g.add_color_stop_rgb(0, *hexc("#ffcf6a"))
    g.add_color_stop_rgb(1, *hexc("#e8432a"))
    ctx.set_source(g)
    ctx.rectangle(-2000, horizon, 5000, 3000)
    ctx.fill()
    for k in range(14):   # lava ripples in perspective
        y = horizon + (1500 - horizon) * ((k + (T * 0.6) % 1) / 14) ** 2
        ctx.move_to(-2000, y)
        ctx.line_to(3000, y)
    ctx.set_source_rgba(1, 0.95, 0.6, 0.25)
    ctx.set_line_width(3)
    ctx.stroke()
    pts = []
    for i in range(n):
        d = i / (n - 1)
        sc = 1 / (1 + d * 7)
        y = horizon + (1230 - horizon) * sc
        x = 360 + math.sin(i * 0.75) * 300 * sc
        pts.append((x, y, sc, i))
    fx, fy, fs, _ = pts[-1]
    ctx.move_to(fx, fy - 10)
    ctx.line_to(fx, fy - 120 * fs - 40)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(3)
    ctx.stroke()
    text(ctx, "100", fx + 22, fy - 120 * fs - 30, 22, hexc("#4fd16a"), outline=True)
    for x, y, sc, i in reversed(pts):
        hm.block(ctx, x - 110 * sc, y - 34 * sc, 220 * sc, 70 * sc, top=("#5dd06a", "#f2b84b", "#4fb3e8")[i % 3],
                 studs=sc > 0.3)
        if sc > 0.18:
            text(ctx, str(1 + round(i * 99 / (n - 1))), x, y + 8 * sc, 34 * sc, (1, 1, 1), outline=True)
    return pts


# ---------------------------------------------------------------- boss fight
def boss_bar(ctx, frac, name="NOOB KING", a=1.0, shake=0.0, y=272):
    """Boss health bar in screen space (under the timer)."""
    if a <= 0:
        return
    ctx.save()
    ctx.translate(math.sin(shake * 80) * 8 * shake, 0)
    ctx.push_group()
    box(ctx, 90, y - 34, 540, 72, "#1b1e30", "#101220", r=16, lw=4)
    text(ctx, name, 360, y - 12, 26, hexc("#ffd84a"), outline=False)
    rrect(ctx, 110, y + 6, 500, 20, 10)
    ctx.set_source_rgb(*hexc("#3a2030"))
    ctx.fill()
    if frac > 0:
        rrect(ctx, 110, y + 6, 500 * frac, 20, 10)
        g = cairo.LinearGradient(110, 0, 610, 0)
        g.add_color_stop_rgb(0, *hexc("#ff4f5a"))
        g.add_color_stop_rgb(1, *hexc("#ff9b3a"))
        ctx.set_source(g)
        ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    ctx.restore()


def noob_king(ctx, x, y, s, T, expr="angry"):
    """Classic 'noob' colours (yellow skin, blue shirt, green legs) with a cape and a crown."""
    sp.cape(ctx, x, y, s, T)
    hm.avatar(ctx, x, y, s, shirt="#2f6bd8", pants="#3fae4a", expr=expr, t=T)
    hm.crown(ctx, x, y - 218 * s, 0.55 * s)


def damage(ctx, x, y, k, txt="-9,999,999"):
    if k <= 0 or k > 1.4:
        return
    text(ctx, txt, x, y - 160 * k, 54, hexc("#ff4f5a"), outline=True, scale=min(1.0, k * 6))


def chest(ctx, x, y, s, T, open_k=0.0):
    if open_k > 0:
        glow(ctx, x, y - 220 * s, 420 * s, (1, 0.9, 0.4), 0.8 * open_k)
        for i in range(5):
            hm.robux_coin(ctx, x - 100 * s + i * 50 * s, y - 175 * s - (i % 2) * 18 * s, 0.6 * s, spin=T * 3 + i)
    hm.box(ctx, x - 160 * s, y - 170 * s, 320 * s, 170 * s, "#a8652a", "#6b3f16", r=14 * s, lw=6 * s)
    for dx in (-110, 110):
        hm.box(ctx, x + dx * s - 16 * s, y - 170 * s, 32 * s, 170 * s, "#ffd84a", "#d6a23a", r=4 * s, lw=4 * s)
    hm.box(ctx, x - 28 * s, y - 150 * s, 56 * s, 60 * s, "#ffd84a", "#d6a23a", r=10 * s, lw=4 * s)
    ctx.save()
    ctx.translate(x + 170 * s, y - 170 * s - 120 * s * open_k)
    ctx.rotate(-0.45 * open_k)
    ctx.translate(-x - 170 * s, -(y - 170 * s))
    hm.box(ctx, x - 170 * s, y - 262 * s, 340 * s, 96 * s, "#c27a36", "#8a5320", r=34 * s, lw=6 * s)
    for dx in (-110, 110):
        hm.box(ctx, x + dx * s - 16 * s, y - 262 * s, 32 * s, 96 * s, "#ffd84a", "#d6a23a", r=6 * s, lw=4 * s)
    ctx.restore()


# ---------------------------------------------------------------- shop
def shop_front(ctx, T):
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1040)
    box(ctx, 30, 380, 660, 662, "#f4e6c4", "#dcc597", r=10)
    for i in range(12):   # striped awning with scallops
        x0 = 20 + i * 57
        ctx.rectangle(x0, 540, 57, 70)
        src(ctx, hexc("#e8574a") if i % 2 == 0 else hexc("#ffffff"))
        ctx.fill()
        ctx.new_sub_path()
        ctx.arc(x0 + 28.5, 610, 28.5, 0, PI)
        src(ctx, hexc("#e8574a") if i % 2 == 0 else hexc("#ffffff"))
        ctx.fill()
    ctx.rectangle(20, 540, 684, 70)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(4)
    ctx.stroke()
    box(ctx, 120, 410, 480, 110, "#e8574a", "#b83a33", r=16)
    text(ctx, "PASS SHOP", 360, 466, 62, (1, 1, 1), outline=True)
    for wx in (60, 470):   # shop windows full of pass cards
        box(ctx, wx, 680, 190, 240, "#bfe6ff", "#8fc4e8", r=8)
        for k in range(4):
            col, g, lab = sp.PASSES[(k + wx) % len(sp.PASSES)]
            sp.gamepass(ctx, wx + 50 + (k % 2) * 90, 750 + (k // 2) * 110, 0.42, col, g, lab)
    box(ctx, 290, 700, 140, 342, "#2a2238", "#171225", r=8)
    glow(ctx, 360, 860, 200, (1, 0.85, 0.5), 0.6)


def cart(ctx, x, y, s, n, T):
    for dx in (-80, 70):   # wheels
        ctx.new_sub_path()
        ctx.arc(x + dx * s, y - 16 * s, 18 * s, 0, 2 * PI)
        _shade_fill(ctx, hexc("#3a3f55"), hexc("#262a3a"), y - 34 * s, y + 2 * s, 4 * s)
    rnd = random.Random(3)
    for i in range(n):   # pass cards piling up
        ctx.save()
        ctx.translate(x - 70 * s + (i % 5) * 36 * s, y - 150 * s - (i // 5) * 40 * s)
        ctx.rotate(rnd.uniform(-0.5, 0.5))
        col, g, lab = sp.PASSES[i % len(sp.PASSES)]
        sp.gamepass(ctx, 0, 0, 0.36 * s, col, g, lab)
        ctx.restore()
    ctx.move_to(x - 130 * s, y - 170 * s)
    ctx.line_to(x + 120 * s, y - 170 * s)
    ctx.line_to(x + 90 * s, y - 40 * s)
    ctx.line_to(x - 105 * s, y - 40 * s)
    ctx.close_path()
    ctx.set_source_rgba(0.85, 0.88, 0.95, 0.55)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(5 * s)
    ctx.stroke()
    for k in range(1, 6):
        xx = x - 130 * s + k * 42 * s
        ctx.move_to(xx, y - 170 * s)
        ctx.line_to(xx - 6 * s * k / 3, y - 40 * s)
    ctx.set_line_width(3 * s)
    ctx.stroke()
    ctx.move_to(x - 130 * s, y - 170 * s)   # handle
    ctx.line_to(x - 175 * s, y - 220 * s)
    ctx.line_to(x - 205 * s, y - 220 * s)
    ctx.set_line_width(7 * s)
    ctx.stroke()


def glass_case(ctx, x, y, s, T):
    ctx.move_to(x - 70 * s, -400)   # spotlight cone
    ctx.line_to(x + 70 * s, -400)
    ctx.line_to(x + 280 * s, y)
    ctx.line_to(x - 280 * s, y)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.7, 0.16)
    ctx.fill()
    hm.box(ctx, x - 180 * s, y - 120 * s, 360 * s, 120 * s, "#ffffff", "#d9dce6", r=14 * s, lw=5 * s)
    hm.box(ctx, x - 200 * s, y - 140 * s, 400 * s, 34 * s, "#ffd84a", "#d6a23a", r=10 * s, lw=4 * s)
    hm.box(ctx, x - 120 * s, y - 470 * s, 240 * s, 310 * s, "#fff3c0", "#f2c243", r=22 * s, lw=6 * s)
    sp.toaster(ctx, x, y - 270 * s, 0.5 * s, T, toast=1.0)
    text(ctx, "GIANT", x, y - 225 * s, 30 * s, hexc("#8a5a10"), outline=False)
    text(ctx, "TOASTER", x, y - 190 * s, 30 * s, hexc("#8a5a10"), outline=False)
    ctx.rectangle(x - 150 * s, y - 510 * s, 300 * s, 372 * s)
    ctx.set_source_rgba(0.8, 0.95, 1, 0.16)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.9)
    ctx.set_line_width(5 * s)
    ctx.stroke()
    ctx.move_to(x - 120 * s, y - 470 * s)
    ctx.line_to(x - 60 * s, y - 500 * s)
    ctx.move_to(x - 128 * s, y - 420 * s)
    ctx.line_to(x - 40 * s, y - 470 * s)
    ctx.set_line_width(6 * s)
    ctx.stroke()


def toaster_you(ctx, x, y, s, T, toast=1.0, mad=False):
    """The giant toaster wearing the kid's brown hair, so it is clearly 'you'."""
    sp.toaster(ctx, x, y, s, T, toast=toast, mad=mad)
    if s <= 0.02:
        return
    ctx.move_to(x - 158 * s, y - 150 * s)
    ctx.line_to(x - 158 * s, y - 205 * s)
    n = 7
    for k in range(n):
        xa = x - 158 * s + k * 316 * s / n
        ctx.curve_to(xa, y - 245 * s, xa + 316 * s / n, y - 245 * s, xa + 316 * s / n, y - 205 * s)
    ctx.line_to(x + 158 * s, y - 150 * s)
    for k in range(n, 0, -1):
        xa = x - 158 * s + k * 316 * s / n
        ctx.line_to(xa - 316 * s / (2 * n), y - 168 * s)
        ctx.line_to(xa - 316 * s / n, y - 150 * s)
    ctx.close_path()
    _shade_fill(ctx, hexc("#9a5a2a"), hexc("#6d381c"), y - 245 * s, y - 150 * s, 5 * s)


def town(ctx, horizon=980):
    hm.game_sky(ctx)
    hm.baseplate(ctx, horizon)
    rnd = random.Random(5)
    for i in range(9):   # little block houses behind
        x = -80 + i * 110
        h = rnd.uniform(90, 170)
        col = rnd.choice(["#e8574a", "#4fb3e8", "#f2b84b", "#9d7fd6", "#7cc08a"])
        box(ctx, x, horizon - h, 90, h, col, lerpc(hexc(col), (0, 0, 0), 0.25), r=6)
        ctx.move_to(x - 8, horizon - h)
        ctx.line_to(x + 45, horizon - h - 50)
        ctx.line_to(x + 98, horizon - h)
        ctx.close_path()
        _shade_fill(ctx, hexc("#8a5a33"), hexc("#6b4422"), horizon - h - 50, horizon - h, 3)


# ---------------------------------------------------------------- plaza + billboard
def billboard(ctx, x, y, w, h, T, content_fn):
    for dx in (-w * 0.3, w * 0.3):
        hm.box(ctx, x + dx - 16, y + h, 32, 520, "#8a8f9a", "#5a5f6a", r=4)
    hm.box(ctx, x - w / 2 - 18, y - 18, w + 36, h + 36, "#2a2e40", "#171a2a", r=16, lw=5)
    ctx.save()
    _clip(ctx, x - w / 2, y, w, h, 6)
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *hexc("#1c2550"))
    g.add_color_stop_rgb(1, *hexc("#3b2f6b"))
    ctx.set_source(g)
    ctx.paint()
    content_fn(ctx, x - w / 2, y, w, h, T)
    ctx.restore()
    glow(ctx, x, y + h / 2, w * 0.7, (0.6, 0.7, 1), 0.25)


# ---------------------------------------------------------------- hatchery
def incubator(ctx, x, y, s, T, crack=0.0, glow_k=0.0):
    hm.box(ctx, x - 190 * s, y - 70 * s, 380 * s, 130 * s, "#8a8f9a", "#5a5f6a", r=34 * s, lw=6 * s)
    ellipse(ctx, x, y - 70 * s, 170 * s, 30 * s)
    ctx.set_source_rgba(0.6, 1, 0.9, 0.5 + 0.3 * math.sin(T * 6))
    ctx.fill()
    sp.egg(ctx, x, y - 75 * s, 0.85 * s, T, crack=crack, glow_k=glow_k)
    ctx.new_sub_path()
    ctx.arc(x, y - 70 * s, 220 * s, PI, 2 * PI)
    ctx.close_path()
    ctx.set_source_rgba(0.8, 0.95, 1, 0.16)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.85)
    ctx.set_line_width(5 * s)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x, y - 70 * s, 190 * s, PI * 1.12, PI * 1.32)
    ctx.set_line_width(8 * s)
    ctx.stroke()


def rarity_banner(ctx, x, y, s, txt, T, sc=1.0):
    if sc <= 0.02:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    w, h = 520 * s, 116 * s
    rrect(ctx, -w / 2, -h / 2, w, h, h * 0.3)
    g = cairo.LinearGradient(-w / 2, 0, w / 2, 0)
    for k, c in enumerate(("#ff4f4f", "#ff9b3a", "#ffe14a", "#5dd06a", "#4fb3e8", "#6b6bff", "#c26bff")):
        g.add_color_stop_rgb(k / 6, *hexc(c))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip_preserve()
    sx = -w / 2 + ((T * 0.9) % 1.6) * w
    ctx.new_path()
    ctx.move_to(sx, -h)
    ctx.line_to(sx + 60 * s, -h)
    ctx.line_to(sx - 20 * s, h)
    ctx.line_to(sx - 80 * s, h)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.55)
    ctx.fill()
    ctx.restore()
    rrect(ctx, -w / 2, -h / 2, w, h, h * 0.3)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(6 * s)
    ctx.stroke()
    text(ctx, txt, 0, 2 * s, 62 * s, (1, 1, 1), outline=True)
    ctx.restore()


# ---------------------------------------------------------------- secret room
def secret_wall(ctx, T, crack=0.0, hole=0.0, cx=430, cy=760):
    sp.dark_bg(ctx, "#140f22", "#241a3a")
    box(ctx, -600, 300, 2000, 760, "#4a3f66", "#2f2745", r=0, lw=0)
    for r in range(18):   # stone blocks
        off = 60 if r % 2 else 0
        for c in range(-6, 16):
            ctx.rectangle(-600 + c * 120 + off, 300 + r * 44, 116, 40)
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.set_line_width(3)
    ctx.stroke()
    box(ctx, -600, 1040, 2000, 900, "#3a2f55", "#1c1630", r=0)
    glow(ctx, 80, 520, 260, (1, 0.6, 0.25), 0.45 + 0.1 * math.sin(T * 11))
    if hole > 0:
        g = cairo.RadialGradient(cx, cy, 0, cx, cy, 240 * hole)
        g.add_color_stop_rgb(0, *hexc("#d8ffe0"))
        g.add_color_stop_rgb(0.6, *hexc("#4fd16a"))
        g.add_color_stop_rgb(1, *hexc("#1b5a2a"))
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(1, 1.3)
        ctx.arc(0, 0, 170 * hole, 0, 2 * PI)
        ctx.restore()
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(6)
        ctx.stroke()
    if crack > 0:
        rnd = random.Random(3)
        for k in range(9):
            a = k * 2 * PI / 9 + rnd.uniform(-0.2, 0.2)
            ctx.move_to(cx, cy)
            r = 0
            for _ in range(4):
                r += 70 * crack
                ctx.line_to(cx + math.cos(a) * r + rnd.uniform(-14, 14), cy + math.sin(a) * r + rnd.uniform(-14, 14))
        ctx.set_source_rgb(*hexc("#b8ffc8"))
        ctx.set_line_width(6)
        ctx.stroke()
        glow(ctx, cx, cy, 300 * crack, (0.5, 1, 0.6), 0.5 * crack)


# ---------------------------------------------------------------- comments
COMMENTS = [("blox_ninja", "LOOP", "#e8574a", "12K"), ("speedy_sam", "loop!! 3 times", "#4f8bff", "8.1K"),
            ("mom_is_watching", "LOOP x10", "#9d7fd6", "5.6K"), ("noobking99", "loop (i lost)", "#f2b84b", "3.2K"),
            ("toaster_fan", "LOOP", "#4fd16a", "2.9K"), ("pet_hatcher", "loop forever", "#ff4f8b", "1.7K")]


def phone_comments(ctx, x, y, s, T, t0, typed=0.0):
    hm.box(ctx, x - 240 * s, y - 440 * s, 480 * s, 880 * s, "#2a2e40", "#171a2a", r=56 * s, lw=6 * s)
    sx, sy, sw, sh = x - 214 * s, y - 400 * s, 428 * s, 800 * s
    ctx.save()
    _clip(ctx, sx, sy, sw, sh, 30 * s)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    off = max(0.0, T - t0) * 34 * s
    for i, (name, msg, col, likes) in enumerate(COMMENTS * 2):
        ry = sy + 120 * s + i * 120 * s - off
        if ry < sy - 120 * s or ry > sy + sh:
            continue
        ctx.new_sub_path()
        ctx.arc(sx + 50 * s, ry + 30 * s, 28 * s, 0, 2 * PI)
        _shade_fill(ctx, hexc(col), lerpc(hexc(col), (0, 0, 0), 0.25), ry, ry + 60 * s, 3 * s)
        ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(20 * s)
        ctx.set_source_rgb(0.45, 0.45, 0.5)
        ctx.move_to(sx + 92 * s, ry + 14 * s)
        ctx.show_text("@" + name)
        ctx.set_font_size(34 * s)
        ctx.set_source_rgb(0.1, 0.1, 0.15)
        ctx.move_to(sx + 92 * s, ry + 54 * s)
        ctx.show_text(msg)
        ctx.set_font_size(20 * s)
        ctx.set_source_rgb(0.45, 0.45, 0.5)
        ctx.move_to(sx + 92 * s, ry + 86 * s)
        ctx.show_text("♥ " + likes)
    box(ctx, sx, sy, sw, 90 * s, "#ffffff", "#f2f3f7", r=0, lw=0)   # header
    ctx.set_font_size(30 * s)
    ctx.set_source_rgb(0.1, 0.1, 0.15)
    ctx.move_to(sx + 26 * s, sy + 58 * s)
    ctx.show_text("Comments  99K")
    box(ctx, sx, sy + sh - 100 * s, sw, 100 * s, "#ffffff", "#f2f3f7", r=0, lw=0)   # typing box
    hm.box(ctx, sx + 20 * s, sy + sh - 82 * s, sw - 40 * s, 64 * s, "#f2f3f7", "#e4e6ee", r=30 * s, lw=3 * s)
    word = "LOOP"[:int(round(4 * max(0.0, min(1.0, typed))))]
    ctx.set_font_size(32 * s)
    ctx.set_source_rgb(0.1, 0.1, 0.15) if word else ctx.set_source_rgb(0.6, 0.6, 0.65)
    ctx.move_to(sx + 46 * s, sy + sh - 38 * s)
    ctx.show_text(word if word else "Add a comment...")
    if word and int(T * 3) % 2 == 0:
        e = ctx.text_extents(word)
        ctx.rectangle(sx + 50 * s + e.x_advance, sy + sh - 68 * s, 4 * s, 38 * s)
        ctx.fill()
    ctx.restore()
