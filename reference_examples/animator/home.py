"""Sets and props for the 'mom owns the block game' story, in the office.py / style2 look
(outlined shapes, soft top-lit gradients). The game world is a generic blocky game:
no real logos or characters."""
import math
import random

import cairo

from arcade import box, check, red_x
from engine import PI, ellipse, glow, hexc, lerp, lerpc, rrect, src, text
from style2 import OUT, _shade_fill

LW = 4.0


# ---------------------------------------------------------------- the blocky game world
def game_sky(ctx, night=0.0):
    g = cairo.LinearGradient(0, -1500, 0, 1500)
    g.add_color_stop_rgb(0, *lerpc(hexc("#58a8ff"), hexc("#141a48"), night))
    g.add_color_stop_rgb(1, *lerpc(hexc("#bfe6ff"), hexc("#3b3170"), night))
    ctx.set_source(g)
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.fill()
    rnd = random.Random(3)
    for _ in range(7):   # square clouds
        x, y, w = rnd.uniform(-600, 1300), rnd.uniform(-500, 420), rnd.uniform(120, 240)
        for k in range(3):
            ctx.rectangle(x + k * w * 0.3, y - (k % 2) * 30, w * 0.5, 60)
        ctx.set_source_rgba(1, 1, 1, 0.85 * (1 - night * 0.7))
        ctx.fill()


def block(ctx, x, y, w, h, top="#5dd06a", side="#9a6a3c", studs=True):
    """A grass/dirt block platform; (x, y) = top-left."""
    box(ctx, x, y, w, h, side, lerpc(hexc(side), (0, 0, 0), 0.25), r=6)
    box(ctx, x, y, w, min(26, h * 0.3), top, lerpc(hexc(top), (0, 0, 0), 0.15), r=6)
    if studs:
        for k in range(int(w // 34)):
            ellipse(ctx, x + 17 + k * 34, y + 8, 9, 4)
            ctx.set_source_rgba(1, 1, 1, 0.35)
            ctx.fill()


def baseplate(ctx, y, col="#8fd16a"):
    box(ctx, -3000, y, 7000, 2000, col, lerpc(hexc(col), (0, 0, 0), 0.25), r=0)
    for k in range(-40, 80):
        ctx.move_to(k * 60, y)
        ctx.line_to(k * 60 - 400, y + 2000)
    ctx.set_source_rgba(0, 0, 0, 0.06)
    ctx.set_line_width(3)
    ctx.stroke()


def lava(ctx, y, t):
    box(ctx, -3000, y, 7000, 2000, "#ff7a2a", "#c8321a", r=0)
    for k in range(30):
        x = -600 + k * 80 + math.sin(t * 2 + k) * 20
        ellipse(ctx, x, y + 30 + (k % 3) * 40, 26, 10)
        ctx.set_source_rgba(1, 0.9, 0.4, 0.6)
        ctx.fill()


def avatar(ctx, x, y, s=1.0, shirt="#e8574a", pants="#2b45a6", hair=None, expr="happy", t=0.0,
           walk=0.0, jump=0.0, wave=False, mom=False, sleep=False):
    """Generic blocky avatar standing on (x, y). hair: None, 'curly' (brown wavy), 'bun'."""
    y = y - jump
    sw = math.sin(walk * 2 * PI) * 0.5 if walk else 0.0
    skin = hexc("#ffd36a")
    # legs
    for side, a in ((-1, sw), (1, -sw)):
        ctx.save()
        ctx.translate(x + side * 15 * s, y - 70 * s)
        ctx.rotate(a)
        box(ctx, -14 * s, 0, 28 * s, 70 * s, pants, None, r=3 * s, lw=3 * s)
        ctx.restore()
    # body
    box(ctx, x - 32 * s, y - 140 * s, 64 * s, 72 * s, shirt, None, r=4 * s, lw=3.5 * s)
    if mom:   # apron
        box(ctx, x - 22 * s, y - 120 * s, 44 * s, 52 * s, "#ffffff", "#e8e8f0", r=4 * s, lw=2.5 * s)
    # arms
    for side, a in ((-1, -sw), (1, sw)):
        ctx.save()
        ctx.translate(x + side * 44 * s, y - 136 * s)
        ang = a
        if wave and side > 0:
            ang = -2.6 + math.sin(t * 12) * 0.35
        ctx.rotate(ang)
        box(ctx, -12 * s, 0, 24 * s, 64 * s, skin, None, r=3 * s, lw=3 * s)
        ctx.restore()
    # head
    hx, hy = x, y - 176 * s
    if hair == "bun":
        ctx.new_sub_path()
        ctx.arc(hx, hy - 44 * s, 16 * s, 0, 2 * PI)
        _shade_fill(ctx, hexc("#6d381c"), hexc("#4a2410"), hy - 60 * s, hy - 28 * s, 3 * s)
    box(ctx, hx - 30 * s, hy - 32 * s, 60 * s, 64 * s, "#ffd36a", "#f2b84b", r=10 * s, lw=3.5 * s)
    if hair == "curly":   # brown wavy hair
        ctx.move_to(hx - 33 * s, hy - 6 * s)
        for k in range(6):
            ctx.curve_to(hx - 33 * s + k * 11 * s, hy - 46 * s, hx - 22 * s + k * 11 * s, hy - 46 * s,
                         hx - 22 * s + k * 11 * s, hy - 26 * s)
        ctx.line_to(hx + 33 * s, hy - 6 * s)
        ctx.line_to(hx + 30 * s, hy - 32 * s)
        ctx.line_to(hx - 30 * s, hy - 32 * s)
        ctx.close_path()
        _shade_fill(ctx, hexc("#9a5a2a"), hexc("#6d381c"), hy - 46 * s, hy - 6 * s, 3 * s)
    elif hair == "bun":
        box(ctx, hx - 32 * s, hy - 36 * s, 64 * s, 20 * s, "#6d381c", "#4a2410", r=8 * s, lw=3 * s)
    # face
    ctx.set_source_rgb(*OUT)
    if sleep or expr == "sleep":
        for sx in (-1, 1):
            ctx.move_to(hx + sx * 13 * s - 6 * s, hy - 2 * s)
            ctx.line_to(hx + sx * 13 * s + 6 * s, hy - 2 * s)
        ctx.set_line_width(3 * s)
        ctx.stroke()
    else:
        for sx in (-1, 1):
            ellipse(ctx, hx + sx * 13 * s, hy - 4 * s, 4 * s, 6 * s)
            ctx.fill()
    if expr in ("happy", "grin"):
        ctx.arc(hx, hy + 8 * s, 13 * s, 0.2, PI - 0.2)
        ctx.set_line_width(3 * s)
        ctx.stroke()
    elif expr == "shock":
        ellipse(ctx, hx, hy + 14 * s, 7 * s, 9 * s)
        ctx.fill()
    elif expr in ("sad", "angry"):
        ctx.arc(hx, hy + 24 * s, 11 * s, PI + 0.4, 2 * PI - 0.4)
        ctx.set_line_width(3 * s)
        ctx.stroke()
    else:
        ctx.move_to(hx - 8 * s, hy + 14 * s)
        ctx.line_to(hx + 8 * s, hy + 14 * s)
        ctx.set_line_width(3 * s)
        ctx.stroke()


def obby(ctx, T, homework=0.0):
    """Obstacle course of floating blocks over lava; homework 0..1 turns them into notebooks."""
    game_sky(ctx)
    lava(ctx, 1150, T)
    plats = [(-60, 980, 200), (200, 860, 150), (420, 760, 150), (620, 660, 150), (860, 560, 180)]
    for i, (x, y, w) in enumerate(plats):
        k = max(0.0, min(1.0, homework * 1.6 - i * 0.15))
        if k < 0.5:
            block(ctx, x, y, w, 70)
        else:
            notebook(ctx, x + w / 2, y + 30, w / 170, page="A+" if i % 2 else "2+2")
    return plats


def notebook(ctx, x, y, s=1.0, page="2+2"):
    box(ctx, x - 85 * s, y - 35 * s, 170 * s, 70 * s, "#f6f1e2", "#ddd3b8", r=6 * s)
    for k in range(3):
        ctx.move_to(x - 70 * s, y - 15 * s + k * 15 * s)
        ctx.line_to(x + 70 * s, y - 15 * s + k * 15 * s)
    ctx.set_source_rgba(0.3, 0.45, 0.8, 0.6)
    ctx.set_line_width(2)
    ctx.stroke()
    box(ctx, x - 85 * s, y - 35 * s, 18 * s, 70 * s, "#e8574a", "#b83a33", r=3 * s, lw=3)
    text(ctx, page, x + 10 * s, y, 26 * s, hexc("#d63c3c"), outline=False)


def mini_game(ctx, x, y, w, h, T, on=1.0, seed=0, label_txt=None):
    """A small game window (one server): sky, ground, two avatars. on=0 -> black screen."""
    box(ctx, x - 8, y - 8, w + 16, h + 16, "#3a3f55", "#262a3a", r=8)
    ctx.save()
    rrect(ctx, x, y, w, h, 4)
    ctx.clip()
    if on > 0:
        g = cairo.LinearGradient(0, y, 0, y + h)
        g.add_color_stop_rgb(0, *hexc("#58a8ff"))
        g.add_color_stop_rgb(1, *hexc("#bfe6ff"))
        ctx.set_source(g)
        ctx.paint()
        ctx.rectangle(x, y + h * 0.7, w, h * 0.3)
        ctx.set_source_rgb(*hexc("#8fd16a"))
        ctx.fill()
        rnd = random.Random(seed)
        for k in range(2):
            ax = x + w * (0.3 + 0.4 * k) + math.sin(T * 2 + seed + k) * w * 0.08
            avatar(ctx, ax, y + h * 0.78, h / 330, shirt=rnd.choice(["#e8574a", "#4fb3a9", "#f2b84b", "#9d7fd6"]),
                   t=T, walk=T * 1.5 + k)
        if on < 1:
            ctx.set_source_rgba(0, 0, 0, 1 - on)
            ctx.paint()
    else:
        ctx.set_source_rgb(*hexc("#101018"))
        ctx.paint()
        if label_txt:
            text(ctx, label_txt, x + w / 2, y + h / 2, w * 0.09, hexc("#e8574a"), outline=False)
    ctx.restore()


def server_wall(ctx, T, off_times, cols=3, rows=4, label_txt="OFFLINE"):
    """Wall of game windows; each switches off at its time in off_times."""
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.set_source_rgb(*hexc("#1c1f33"))
    ctx.fill()
    w, h = 190, 150
    k = 0
    for r in range(rows):
        for c in range(cols):
            x, y = 70 + c * 205, 300 + r * 175
            t_off = off_times[k % len(off_times)]
            on = 1.0 if T < t_off else max(0.0, 1 - (T - t_off) / 0.12)
            mini_game(ctx, x, y, w, h, T, on=on, seed=k, label_txt=label_txt if on <= 0 else None)
            k += 1


# ---------------------------------------------------------------- home
def bedroom(ctx, T, night=0.0, messy=0.0, light_on=True):
    """Kid's bedroom: blue wall, window, posters, bed on the right, desk with PC on the left."""
    from office import room, pendant
    room(ctx, -400, 1100, 230, 1000, wall="#8fb7e8", floor="#d9b48a", ceil="#c9d4f0")
    # window
    box(ctx, 420, 330, 230, 230, "#ffffff", "#e8e8f0", r=6)
    g = cairo.LinearGradient(0, 345, 0, 545)
    g.add_color_stop_rgb(0, *lerpc(hexc("#7fb7f2"), hexc("#141a48"), night))
    g.add_color_stop_rgb(1, *lerpc(hexc("#f4c7a8"), hexc("#4a3a7a"), night))
    ctx.set_source(g)
    ctx.rectangle(435, 345, 200, 200)
    ctx.fill()
    if night > 0.5:
        ctx.new_sub_path()
        ctx.arc(590, 390, 24, 0, 2 * PI)
        ctx.set_source_rgb(0.97, 0.95, 0.85)
        ctx.fill()
        glow(ctx, 590, 390, 90, (0.8, 0.85, 1), 0.4)
    ctx.move_to(535, 345)
    ctx.line_to(535, 545)
    ctx.move_to(435, 445)
    ctx.line_to(635, 445)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(5)
    ctx.stroke()
    # poster of a block avatar
    box(ctx, 90, 330, 150, 190, "#ffe27a", "#f2b84b", r=4)
    avatar(ctx, 165, 500, 0.75, shirt="#e8574a", hair="curly", t=T)
    if light_on:
        pendant(ctx, 360, 230)
    if messy > 0:
        rnd = random.Random(4)
        for i in range(12):
            if rnd.random() < messy:
                x, y = rnd.uniform(-100, 820), rnd.uniform(1050, 1250)
                c = rnd.choice(["#e8574a", "#4fb3a9", "#f2b84b", "#9d7fd6", "#ffffff"])
                ctx.save()
                ctx.translate(x, y)
                ctx.rotate(rnd.uniform(-0.6, 0.6))
                box(ctx, -45, -16, 90, 32, c, None, r=10, lw=3)   # clothes / toys on the floor
                ctx.restore()
    if night:
        ctx.set_source_rgba(0.04, 0.05, 0.18, 0.55 * night)
        ctx.rectangle(-3000, -3000, 7000, 7000)
        ctx.fill()


def bed(ctx, x, y, s=1.0, blanket="#e8574a"):
    box(ctx, x - 180 * s, y - 230 * s, 40 * s, 230 * s, "#b07a4a", "#8a5a33", r=6 * s)
    box(ctx, x - 160 * s, y - 120 * s, 340 * s, 80 * s, "#ffffff", "#e8e8f0", r=12 * s)
    box(ctx, x - 150 * s, y - 165 * s, 110 * s, 50 * s, "#ffffff", "#dfe3ee", r=18 * s)
    box(ctx, x - 60 * s, y - 135 * s, 250 * s, 90 * s, blanket, lerpc(hexc(blanket), (0, 0, 0), 0.25), r=20 * s)
    box(ctx, x - 165 * s, y - 45 * s, 360 * s, 45 * s, "#b07a4a", "#8a5a33", r=6 * s)


def pc(ctx, x, y, s=1.0, T=0.0, screen="game", on=1.0):
    """Monitor on a desk top at (x, y) showing the game (or a dialog / black)."""
    ctx.rectangle(x - 10 * s, y - 50 * s, 20 * s, 50 * s)
    _shade_fill(ctx, hexc("#5a5f6e"), hexc("#3c4050"), y - 50 * s, y, LW * 0.7)
    box(ctx, x - 140 * s, y - 240 * s, 280 * s, 195 * s, "#3a3f55", "#262a3a", r=12 * s)
    sx, sy, sw, sh = x - 125 * s, y - 226 * s, 250 * s, 166 * s
    if screen == "game" and on > 0:
        mini_game(ctx, sx, sy, sw, sh, T, on=on, seed=5)
    else:
        rrect(ctx, sx, sy, sw, sh, 4 * s)
        ctx.set_source_rgb(*hexc("#101018"))
        ctx.fill()
    glow(ctx, x, y - 140 * s, 300 * s, (0.5, 0.75, 1), 0.25 * on)


def owner_office(ctx, T):
    """Mom's big office: dark wood, a giant screen with the block game behind the desk."""
    from office import room
    room(ctx, -400, 1100, 230, 1000, wall="#6b4a7a", floor="#5a3f4a", ceil="#4a3a5a")
    box(ctx, 60, 300, 600, 380, "#2a2e40", "#1b1e2c", r=14)
    mini_game(ctx, 80, 320, 560, 340, T, seed=9)
    glow(ctx, 360, 490, 500, (0.6, 0.8, 1), 0.25)


def big_desk(ctx, y, plate=None, plate_k=1.0):
    box(ctx, -60, y, 840, 70, "#8a5a33", "#6b4422", r=8)
    box(ctx, -40, y + 70, 800, 500, "#6b4422", "#4a2e16", r=0)
    if plate and plate_k > 0:
        ctx.save()
        ctx.translate(360, y + 36)
        ctx.scale(plate_k, plate_k)
        box(ctx, -150, -38, 300, 76, "#ffe27a", "#d6a23a", r=8)
        text(ctx, plate, 0, 0, 40, hexc("#5a3a10"), outline=False)
        ctx.restore()


def crown(ctx, x, y, s=1.0):
    ctx.move_to(x - 60 * s, y)
    for px, py in ((-60, -60), (-30, -25), (0, -75), (30, -25), (60, -60), (60, 0)):
        ctx.line_to(x + px * s, y + py * s)
    ctx.close_path()
    _shade_fill(ctx, hexc("#ffe27a"), hexc("#e0a93a"), y - 75 * s, y, LW * s)
    for px in (-60, 0, 60):
        ctx.new_sub_path()
        ctx.arc(x + px * s, y - (60 if px else 75) * s, 9 * s, 0, 2 * PI)
        src(ctx, hexc("#e8574a"))
        ctx.fill()


def day_card(ctx, T, n, t0):
    """Big tear-off calendar 'DAY n' on a soft background (the time-marker shot)."""
    g = cairo.RadialGradient(360, 620, 50, 360, 620, 900)
    g.add_color_stop_rgb(0, *hexc("#ffe9b0"))
    g.add_color_stop_rgb(1, *hexc("#f2a65a"))
    ctx.set_source(g)
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.fill()
    for k in range(14):   # sun rays turning
        a = k * PI / 7 + T * 0.3
        ctx.move_to(360, 620)
        ctx.line_to(360 + math.cos(a) * 1400, 620 + math.sin(a) * 1400)
        ctx.line_to(360 + math.cos(a + 0.12) * 1400, 620 + math.sin(a + 0.12) * 1400)
        ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.18)
    ctx.fill()
    box(ctx, 180, 420, 360, 400, "#ffffff", "#ecebf2", r=18)
    box(ctx, 180, 420, 360, 100, "#e8574a", "#c63d33", r=18)
    text(ctx, "DAY", 360, 470, 54, (1, 1, 1), outline=False)
    flip = max(0.0, min(1.0, (T - t0) / 0.3))
    text(ctx, str(n), 360, 680, 190, OUT, outline=False)
    if flip < 1:   # the previous page tearing away
        ctx.save()
        ctx.translate(360, 520)
        ctx.rotate(-flip * 1.2)
        ctx.translate(flip * 500, -flip * 300)
        box(ctx, -180, 0, 360, 300, "#f4f2f8", "#d9d6e4", r=12)
        text(ctx, str(max(0, n - 1)) if n > 1 else "", 0, 160, 190, hexc("#b9b6c8"), outline=False)
        ctx.restore()
    for x in (240, 480):   # rings
        ctx.new_sub_path()
        ctx.arc(x, 420, 16, 0, 2 * PI)
        src(ctx, hexc("#3a3f55"))
        ctx.fill()


def robux_coin(ctx, x, y, s=1.0, spin=0.0):
    """Generic gold game coin with 'R$'."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(0.15, abs(math.cos(spin))) * s, s)
    pts = [(math.cos(a) * 48, math.sin(a) * 48) for a in [k * PI / 3 + PI / 6 for k in range(6)]]
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    _shade_fill(ctx, hexc("#ffe27a"), hexc("#e0a93a"), -48, 48, LW)
    text(ctx, "R$", 0, 0, 30, hexc("#8a5a10"), outline=False)
    ctx.restore()


def coin_rain(ctx, T, n=18, seed=2, y0=-300, y1=1400):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(-60, 780)
        sp = rnd.uniform(300, 520)
        y = y0 + (T * sp + rnd.uniform(0, y1 - y0)) % (y1 - y0)
        robux_coin(ctx, x, y, 0.55, spin=T * 5 + x)


def like_button(ctx, x, y, s=1.0, pressed=0.0):
    if s <= 0.02:
        return
    col = lerpc(hexc("#e9edf2"), hexc("#4f8bff"), pressed)
    box(ctx, x - 120 * s, y - 60 * s, 240 * s, 120 * s, col, lerpc(col, (0, 0, 0), 0.15), r=60 * s)
    # thumbs up
    ctx.save()
    ctx.translate(x - 40 * s, y)
    ctx.scale(s, s)
    rrect(ctx, -30, -10, 22, 46, 5)
    _shade_fill(ctx, (1, 1, 1), hexc("#dfe3ee"), -10, 36, 3)
    rrect(ctx, -6, -12, 52, 48, 10)
    _shade_fill(ctx, (1, 1, 1), hexc("#dfe3ee"), -12, 36, 3)
    ctx.move_to(4, -12)
    ctx.line_to(14, -46)
    ctx.line_to(30, -40)
    ctx.line_to(24, -12)
    ctx.close_path()
    _shade_fill(ctx, (1, 1, 1), hexc("#dfe3ee"), -46, -12, 3)
    ctx.restore()
    text(ctx, "LIKE", x + 40 * s, y, 36 * s, OUT if pressed < 0.5 else (1, 1, 1), outline=False)


def subscribe_button(ctx, x, y, s=1.0, pressed=0.0):
    if s <= 0.02:
        return
    col = lerpc(hexc("#e8323a"), hexc("#8a8f9a"), pressed)
    box(ctx, x - 190 * s, y - 55 * s, 380 * s, 110 * s, col, lerpc(col, (0, 0, 0), 0.2), r=20 * s)
    text(ctx, "SUBSCRIBED" if pressed > 0.5 else "SUBSCRIBE", x, y, 42 * s, (1, 1, 1), outline=False)


def cursor(ctx, x, y, s=1.0, click=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (1 - 0.15 * click), s * (1 - 0.15 * click))
    ctx.move_to(0, 0)
    for px, py in ((0, 70), (18, 54), (32, 84), (44, 78), (30, 50), (52, 48)):
        ctx.line_to(px, py)
    ctx.close_path()
    _shade_fill(ctx, (1, 1, 1), hexc("#dfe3ee"), 0, 84, 4)
    ctx.restore()


def checklist(ctx, x, y, items, T):
    """Clipboard with items [(text, t_done)] that get ticked at their times."""
    box(ctx, x - 230, y - 60, 460, 120 + 110 * len(items), "#c98a4a", "#a86a32", r=14)
    box(ctx, x - 205, y - 30, 410, 70 + 110 * len(items), "#ffffff", "#eef1f7", r=6)
    box(ctx, x - 70, y - 80, 140, 40, "#9aa1ad", "#6d7380", r=8)
    for i, (txt, t_done) in enumerate(items):
        yy = y + 40 + i * 110
        box(ctx, x - 180, yy - 30, 60, 60, "#ffffff", "#eef1f7", r=8, lw=4)
        text(ctx, txt, x + 50, yy, 36, OUT, outline=False)
        check(ctx, x - 150, yy - 5, 34, (T - t_done) / 0.25)


def chat_banner(ctx, x, y, msg, s=1.0, col="#ffd84a"):
    box(ctx, x - 300 * s, y - 40 * s, 600 * s, 80 * s, "#1b1e30", "#101220", r=12 * s)
    text(ctx, msg, x, y, 30 * s, hexc(col), outline=False)


def router(ctx, x, y, s=1.0, T=0.0, on=1.0, plug_out=0.0):
    """Wi-Fi router on a shelf with blinking lights and its power cable."""
    for side in (-1, 1):   # antennas
        ctx.move_to(x + side * 70 * s, y - 40 * s)
        ctx.line_to(x + side * 95 * s, y - 170 * s)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(14 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    box(ctx, x - 140 * s, y - 50 * s, 280 * s, 90 * s, "#e9edf2", "#b9bec7", r=18 * s)
    for k in range(5):
        lit = on > 0.5 and (k + int(T * 6)) % 2 == 0
        ctx.new_sub_path()
        ctx.arc(x - 80 * s + k * 40 * s, y, 8 * s, 0, 2 * PI)
        src(ctx, hexc("#4fd16a") if lit else (hexc("#e8574a") if on <= 0.5 else hexc("#2e6b3a")))
        ctx.fill()
    if on > 0.5:   # wifi waves
        for k in range(3):
            ph = (T * 1.5 + k / 3) % 1
            ctx.new_sub_path()
            ctx.arc(x, y - 60 * s, (40 + ph * 140) * s, -PI * 0.75, -PI * 0.25)
            ctx.set_source_rgba(0.3, 0.6, 1, 1 - ph)
            ctx.set_line_width(8 * s)
            ctx.stroke()
    # cable to the plug
    px = x + 200 * s + plug_out * 200 * s
    py = y + 260 * s - plug_out * 120 * s
    ctx.move_to(x + 120 * s, y + 40 * s)
    ctx.curve_to(x + 160 * s, y + 160 * s, px - 60 * s, py - 20 * s, px, py)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(9 * s)
    ctx.stroke()
    box(ctx, px - 20 * s, py - 18 * s, 50 * s, 36 * s, "#3a3f55", "#262a3a", r=6 * s)
    box(ctx, x + 170 * s, y + 230 * s, 90 * s, 70 * s, "#ffffff", "#e8e8f0", r=8 * s)   # wall socket


def wifi_icon(ctx, x, y, s=1.0, crossed=0.0):
    for k in range(3):
        ctx.new_sub_path()
        ctx.arc(x, y + 40 * s, (30 + k * 32) * s, -PI * 0.75, -PI * 0.25)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(22 * s)
        ctx.stroke_preserve()
        src(ctx, hexc("#4f8bff"))
        ctx.set_line_width(12 * s)
        ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x, y + 40 * s, 10 * s, 0, 2 * PI)
    src(ctx, hexc("#4f8bff"))
    ctx.fill()
    red_x(ctx, x, y, 120 * s, crossed)


def dialog(ctx, x, y, title, yes_no=("YES", "NO"), pick=None, s=1.0):
    box(ctx, x - 230 * s, y - 120 * s, 460 * s, 240 * s, "#ffffff", "#e8ebf2", r=14 * s)
    box(ctx, x - 230 * s, y - 120 * s, 460 * s, 60 * s, "#4f8bff", "#3a6fe0", r=14 * s)
    text(ctx, title, x, y - 90 * s, 30 * s, (1, 1, 1), outline=False)
    for i, lab in enumerate(yes_no):
        bx = x + (i - 0.5) * 220 * s
        col = "#4fd16a" if i == 0 else "#e8574a"
        if pick == i:
            glow(ctx, bx, y + 40 * s, 120 * s, hexc(col), 0.5)
        box(ctx, bx - 90 * s, y + 10 * s, 180 * s, 64 * s, col, None, r=12 * s)
        text(ctx, lab, bx, y + 42 * s, 30 * s, (1, 1, 1), outline=False)
