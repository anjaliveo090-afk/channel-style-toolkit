"""Story: the room where Japanese companies send people they cannot fire.
Same style as clock_tower2.py: keyframed camera landing on words every 2-4 words,
user's reference characters (style2) and background style (office.py)."""
import math
import sys

import cairo

import office as of
from engine import (W, H, clamp, ease, glow, hexc, keyed, label, lerp, lerpc, pop, render,
                    set_voice, sky, stars, text)
from style2 import Char2, back_figure, OUT

TOTAL = 81.84
C = (W / 2, H / 2)

YOU = Char2("#88b3fb", hair="bowl", hair_col="#2d2328", outfit="shirt", lanyard=True)
YOU_SHADES = Char2("#88b3fb", hair="bowl", hair_col="#2d2328", outfit="shirt", lanyard=True, shades=True)
BOSS = Char2("#2f3550", hair="side", hair_col="#9a9aa4", outfit="suit", tie="#c0392b")
CORNER = Char2("#4fb3a9", hair="bowl", hair_col="#6d381c", outfit="shirt", shades=True)
STRANGER = Char2("#f2b84b", hair="bowl", hair_col="#4a3a30", outfit="shirt", tie="#2b45a6")
COWORKERS = [Char2(c, hair="bowl", hair_col=h, outfit="shirt", lanyard=True) for c, h in (
    ("#e57373", "#2d2328"), ("#9d7fd6", "#6d381c"), ("#f2b84b", "#2d2328"),
    ("#7cc08a", "#4a3a30"), ("#88b3fb", "#6d381c"), ("#e8a0bf", "#2d2328"))]


def tint(ctx, rgb, a):
    if a > 0:
        ctx.set_source_rgba(*rgb, a)
        ctx.rectangle(-3000, -5000, 7000, 10000)
        ctx.fill()


def walk_x(T, t0, t1, x0, x1):
    return lerp(x0, x1, ease((T - t0) / (t1 - t0)))


# ---------------------------------------------------------------- hook
def s_hook(ctx, t, d):
    T = t
    of.room(ctx, -300, 1000, 230, 980, wall="#b98a66", floor="#d9b48a", tiles=False)
    of.window_city(ctx, 430, 300, 240, 300)
    of.plant(ctx, 110, 980, 1.3)
    of.pendant(ctx, 360, 230)
    expr = keyed(T, [(0, "smirk"), (0.5, "grin"), (1.95, "shock")])
    BOSS.draw(ctx, 360, 1000, 1.25, expr, T, arms=("down", "hold"), bob=0.4)
    of.desk(ctx, 360, 900, 560, 1.3, drawers=False)
    of.paper(ctx, 340, 878, 1.0)
    # the stamp slams at "Japan" and bounces off the law shield at "impossible"
    if T < 1.25:
        sy = lerp(640, 600, ease(T / 1.0))
    elif T < 1.5:
        sy = lerp(600, 800, ease((T - 1.25) / 0.25))
    else:
        k = T - 1.5
        sy = 800 - 260 * math.sin(min(k, 0.6) / 0.6 * math.pi / 2) + 30 * math.sin(k * 14) * math.exp(-k * 4)
    if T > 1.45:
        of.shield(ctx, 345, 840, 0.75, a=clamp((T - 1.45) / 0.15))
    of.stamp(ctx, 420, sy, 1.0)


# ---------------------------------------------------------------- building at night
def s_building(ctx, t, d):
    T = 2.74 + t
    sky(ctx, hexc("#121a45"), hexc("#4a3a7a"), -1200, 1500)
    stars(ctx, 4, 160, 0.9, T, 300, depth=0.2)
    of.building(ctx, -170, 1500, 0.75, T)
    of.building(ctx, 900, 1450, 0.8, T)
    of.building(ctx, 360, 1450, 1.0, T, dark_window=(4, 6))
    ctx.rectangle(-1000, 1440, 3000, 800)
    ctx.set_source_rgb(*hexc("#1b1b33"))
    ctx.fill()
    for k in range(10):
        x = (T * 120 + k * 160) % 1600 - 400
        glow(ctx, x, 1470, 40, (1, 0.85, 0.5), 0.5)


# ---------------------------------------------------------------- the plan (replaces s_building)
EXEC_L = Char2("#4a3f5c", hair="bald", hair_col="#8a8a94", outfit="suit", tie="#2b45a6", mustache="#6d6d6d")
EXEC_R = Char2("#3d5a4f", hair="bowl", hair_col="#2d2328", outfit="suit", tie="#e8a93a", glasses=True)


def _bulb(ctx, x, y, k):
    """Idea light bulb popping in (k = seconds since it appeared)."""
    if k <= 0:
        return
    sc = pop(k)
    glow(ctx, x, y, 110 * sc, (1, 0.92, 0.5), 0.6)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.new_sub_path()
    ctx.arc(0, 0, 26, 0, 2 * math.pi)
    ctx.set_source_rgb(*hexc("#ffe27a"))
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.rectangle(-12, 22, 24, 18)
    ctx.set_source_rgb(*hexc("#b9bcc6"))
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.stroke()
    for a in range(6):
        ang = a * math.pi / 3 + 0.3
        ctx.move_to(math.cos(ang) * 36, math.sin(ang) * 36)
        ctx.line_to(math.cos(ang) * 50, math.sin(ang) * 50)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.restore()


def _marker(ctx, pts, k, col=OUT, w=6):
    """Draw a marker stroke along pts, revealed by k (0..1)."""
    if k <= 0:
        return
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    left = total * clamp(k)
    ctx.move_to(*pts[0])
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        if left <= 0:
            break
        f = min(1, left / seg)
        ctx.line_to(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        left -= seg
    ctx.set_source_rgb(*col)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def s_plan(ctx, t, d):
    """'but companies figured out a way to make something even worse happen':
    three bosses at a meeting table get an idea and draw the plan on a whiteboard:
    a tiny room with one person in it. The light turns sinister on 'even worse'."""
    T = 2.74 + t
    evil = ease((T - 4.8) / 0.35)
    of.room(ctx, -400, 1100, 230, 980, wall="#9fb0e0", floor="#d9c2a3")
    of.pendant(ctx, 360, 200, on=evil < 0.5)
    # whiteboard with the plan
    bx, by, bw, bh = 130, 360, 460, 320
    ctx.rectangle(bx - 12, by - 12, bw + 24, bh + 24)
    ctx.set_source_rgb(*hexc("#b9bcc6"))
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.rectangle(bx, by, bw, bh)
    ctx.set_source_rgb(*hexc("#fbfbfd"))
    ctx.fill()
    text(ctx, "PLAN", bx + 70, by + 40, 30, hexc("#2b45a6"), outline=False)
    k = (T - 4.15) / 0.65  # the plan is drawn on "to make something"
    rx, ry, rw, rh = 290, 440, 150, 170
    _marker(ctx, [(rx, ry), (rx + rw, ry), (rx + rw, ry + rh), (rx, ry + rh), (rx, ry)], k * 1.6)
    _marker(ctx, [(rx + 20, ry + rh), (rx + 20, ry + 95), (rx + 60, ry + 95), (rx + 60, ry + rh)], k * 1.6 - 0.6, w=5)
    if k > 0.55:  # the lonely person inside
        px, py = rx + 105, ry + 120
        ctx.new_sub_path()
        ctx.arc(px, py - 32, 14, 0, 2 * math.pi)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(5)
        ctx.stroke()
        _marker(ctx, [(px, py - 18), (px, py + 20)], (k - 0.55) * 4, w=5)
        _marker(ctx, [(px - 14, py + 45), (px, py + 20), (px + 14, py + 45)], (k - 0.65) * 4, w=5)
    _marker(ctx, [(170, 650), (240, 600), (282, 560)], k * 1.5 - 0.7, col=hexc("#2b45a6"), w=6)
    _marker(ctx, [(262, 556), (282, 560), (276, 582)], k * 1.5 - 1.2, col=hexc("#2b45a6"), w=6)
    if T > 4.86:  # "even worse": red circle around the room
        c = clamp((T - 4.86) / 0.45)
        ctx.new_sub_path()
        ctx.arc(rx + rw / 2, ry + rh / 2, 125, -math.pi / 2, -math.pi / 2 + 2 * math.pi * c)
        ctx.set_source_rgb(*hexc("#d63c3c"))
        ctx.set_line_width(8)
        ctx.stroke()
    # three bosses behind the meeting table
    for i, (ch, x) in enumerate(((EXEC_L, 150), (BOSS, 360), (EXEC_R, 570))):
        expr = keyed(T, [(0, "sad" if ch is BOSS else "worried"), (3.38 + 0.08 * i, "shock"),
                         (3.65 + 0.08 * i, "grin"), (4.86, "cold")])
        arms = ("down", "up") if 3.4 < T < 4.1 and ch is BOSS else ("down", "down")
        ch.draw(ctx, x, 1120, 1.0, expr, T + i, arms=arms, look=(-0.4 if 4.2 < T < 4.86 else 0.0), bob=0.5)
        _bulb(ctx, x, 735, T - (3.38 + 0.08 * i) if T < 4.8 else 0)
    of.desk(ctx, 360, 1030, 700, 1.2, top="#8a5a33", body="#6b4422", drawers=False)
    for x in (150, 360, 570):
        ctx.rectangle(x - 20, 1000, 40, 22)  # coffee cups
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(3)
        ctx.stroke()
    tint(ctx, (0.25, 0.02, 0.1), 0.35 * evil)
    if evil:
        glow(ctx, 360, 1150, 520, (1, 0.25, 0.2), 0.3 * evil)


# ---------------------------------------------------------------- open office
OFFICE_DESKS = [0, 330, 660, 990, 1320]


def s_office(ctx, t, d, mode="walk", T0=6.12):
    T = T0 + t
    of.room(ctx, -500, 1900, 230, 980, wall="#a9c7ee", floor="#d7dbe6")
    for wx in (-260, 420, 1100):
        of.window_city(ctx, wx, 300, 300, 260)
    for lx in (160, 820, 1480):
        of.pendant(ctx, lx, 210, 0.8)
    of.door(ctx, 1500, 980, 120, 250, open_frac=clamp((T - 8.3) / 0.4) if mode == "walk" else 0.0)
    for i, x in enumerate(OFFICE_DESKS):
        if mode == "away":
            body = "#%02x%02x%02x" % tuple(int(v * 255) for v in COWORKERS[i].body)
            back_figure(ctx, x, 830, 55, ("#2d2328", "#6d381c")[i % 2], body)
        elif mode == "desk" and x == 660:
            STRANGER.draw(ctx, x, 1000, 0.9, keyed(T, [(0, "happy"), (38.6, "smirk")]), T,
                          pose="sit", arms=("hold", "hold"))
        elif not (mode == "desk" and x == 660):
            look = 0.0
            if mode == "walk":
                walker = walk_x(T, 6.6, 8.9, 100, 1250)
                look = clamp((walker - x) / 300, -0.8, 0.8)
            COWORKERS[i].draw(ctx, x, 1000, 0.9, "neutral" if mode != "walk" else "worried", T + i,
                              pose="sit", arms=("hold", "hold"), look=look, bob=0.5)
        of.desk(ctx, x, 960, 250)
        of.monitor(ctx, x - 40, 930, 0.8, screen="photo" if (mode == "desk" and x == 660) else None)
        if mode == "desk" and x == 660:
            for k, px in enumerate((560, 610, 720, 760)):
                of.photo_frame(ctx, px, 935, 0.9 + 0.1 * (k % 2), people=2 + k % 2)
    if mode == "walk":
        x = walk_x(T, 6.6, 8.9, 100, 1250)
        moving = 6.6 < T < 8.9
        BOSS.draw(ctx, x + 70, 1230, 1.05, "grin", T, pose="walk" if moving else "stand",
                  walk_phase=T * 1.8, look=0.6, arms=("down", "show") if T > 8.4 else ("down", "down"))
        YOU.draw(ctx, x - 70, 1240, 1.05, keyed(T, [(0, "neutral"), (8.0, "worried")]), T,
                 pose="walk" if moving else "stand", walk_phase=T * 1.8 + 0.3, look=0.6)
    if mode == "desk":
        YOU.draw(ctx, 300, 1240, 1.05, keyed(T, [(0, "neutral"), (37.3, "shock"), (38.9, "sad")]), T,
                 look=0.6, arms=("down", "down"))
    if mode == "away":
        YOU.draw(ctx, 360, 1240, 1.1, keyed(T, [(0, "worried"), (63.6, "sad")]), T, arms=("shrug", "shrug"))


# ---------------------------------------------------------------- the tiny room
def corner_state(T):
    if 58.4 < T < 77.8 or T >= 77.8:
        return None
    return "feetup"


def you_state(T):
    """(pose, x, y, expr, arms, shades, chair_tucked_for_you)"""
    if T < 13.3:
        return ("stand", 440, 1200, keyed(T, [(0, "neutral"), (9.7, "worried"), (12.2, "shock")]), ("shrug", "shrug") if T > 12.0 else ("down", "down"))
    if T < 25.3:
        return ("stand", 440, 1200, keyed(T, [(0, "worried"), (16.6, "shock"), (19.0, "worried")]), ("down", "down"))
    if T < 29.24:
        return ("stand", 440, 1200, keyed(T, [(0, "neutral"), (25.9, "shock"), (27.3, "grin"), (28.5, "happy")]), ("down", "down") if T < 27.3 else ("up", "up"))
    if T < 31.32:
        return ("feetup_alone", 300, 1140, "happy", ("hold", "hold"))
    if T < 39.59:
        return None
    if T < 50.9:
        return ("sit", 250, 1160, keyed(T, [(0, "neutral"), (43.3, "forced"), (44.8, "neutral")]), ("down", "down"))
    if T < 54.4:
        return ("sit", 250, 1160, keyed(T, [(0, "neutral"), (51.2, "smirk"), (53.4, "happy")]), ("down", "down") if T < 53.4 else ("shrug", "shrug"))
    if T < 57.7:
        return ("feetup", 430, 1075, "happy", ("hold", "hold"))
    if T < 64.6:
        return ("door", 120, 1000, keyed(T, [(0, "neutral"), (58.6, "shock"), (59.5, "worried")]), ("down", "down"))
    return ("sitsad", 250, 1160, "sad", ("down", "down"))


def s_room(ctx, t, d, T0=0.0, night=0.0):
    T = T0 + t
    cold = ease((T - 56.9) / 0.4) if 56.9 < T < 64.6 else 0.0
    of.room(ctx, -400, 1100, 230, 980)
    of.pendant(ctx, 360, 230, on=night < 0.5)
    # clock: normal ticking, sweeps to 6 o'clock at "until 6", spins at "sooner or later"
    if 24.25 < T < 24.82:
        h, m = lerp(2, 6, (T - 24.25) / 0.57), lerp(10, 0, (T - 24.25) / 0.57)
    elif T >= 24.82 and T < 39.0:
        h, m = 6, 0
    elif T >= 77.8:
        h, m = 9 + (T - 77.8) * 6, (T - 77.8) * 720 % 60
    else:
        h, m = 2, 10 + int(T) % 50
    of.wall_clock(ctx, 360, 420, 70, h, m)
    # calendar: FRI at "Every Friday", 3 YEARS of pages, MON at "one Monday"
    if T < 47.0:
        cal = ("OCT", "FRI", "25", 39.6)
    elif T < 56.7:
        cal = ("OCT", "FRI", "25", -1)
    else:
        cal = ("OCT", "MON", "28", 56.75)
    flip = clamp((T - cal[3]) / 0.35) if cal[3] > 0 else 1.0
    of.calendar(ctx, 610, 330, 0.8, cal[0], cal[1], cal[2], flip)
    if 47.0 < T < 48.4:
        for k in range(6):  # pages flying off for "3 whole years"
            ph = ((T - 47.0) * 2.5 + k / 6) % 1
            ctx.save()
            ctx.translate(610 + ph * 260, 400 - ph * 260)
            ctx.rotate(ph * 4)
            ctx.rectangle(-55, -50, 110, 100)
            ctx.set_source_rgba(1, 1, 1, 1 - ph)
            ctx.fill()
            ctx.restore()
    if 47.4 < T < 50.9:
        label(ctx, "3 YEARS", 610, 560, 40, hexc("#f2b84b"), fg=OUT, scale=pop(T - 47.45), tilt=0.05)
    # door, boss pops in
    boss_in = 19.9 < T < 25.3 or 40.4 < T < 44.77
    of.door(ctx, 40, 980, 150, 300, open_frac=0.7 if (boss_in or 57.7 < T < 64.6 or T < 13.3) else 0.0)
    if boss_in:
        lean = 0.0 if T < 25.3 else 0.25 * ease((T - 40.4) / 0.3)
        arms = ("down", "show") if 21.3 < T < 24.0 else (("down", "up") if 43.2 < T < 44.77 else ("down", "down"))
        BOSS.draw(ctx, 120, 1000, 1.0, keyed(T, [(0, "smirk"), (20.3, "grin")]), T, arms=arms, lean=lean)
    # the corner: chair, desk, the happy guy with his feet up
    cs = corner_state(T)
    of.chair(ctx, 560, 1060, 1.0, tucked=cs is None)
    if 44.8 < T < 50.9:
        glow(ctx, 600, 850, 320, (1, 0.85, 0.45), 0.45 * ease((T - 48.9) / 0.5))
    if cs and 18.5 < T < 19.9:
        glow(ctx, 600, 850, 300, (1, 0.8, 0.4), 0.35)  # "like he's on vacation"
    of.desk(ctx, 640, 930, 220)
    if cs:
        ctx.save()  # vacation drink with an umbrella
        ctx.rectangle(690, 860, 30, 45)
        ctx.set_source_rgba(1, 0.75, 0.3, 0.9)
        ctx.fill()
        ctx.move_to(705, 860)
        ctx.line_to(715, 820)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.move_to(690, 828)
        ctx.curve_to(700, 805, 730, 805, 740, 828)
        ctx.close_path()
        ctx.set_source_rgb(*hexc("#e8574a"))
        ctx.fill()
        ctx.restore()
        expr = "happy" if 48.9 < T < 50.9 or T > 54.4 else "smirk"
        CORNER.draw(ctx, 520, 1060, 1.0, expr, T, pose="feetup", arms=("hold", "hold"), lean=-0.25, bob=0.6)
        of.phone(ctx, 512, 905, 0.28, screen="game", t=T)
    # YOU
    ys = you_state(T)
    if ys:
        pose, x, y, expr, arms = ys
        if pose == "feetup_alone":
            of.chair(ctx, x + 40, y, 1.0)
            of.desk(ctx, 250 + 120, 1010, 200)
            YOU_SHADES.draw(ctx, x, y, 1.0, expr, T, pose="feetup", arms=arms, lean=-0.25)
        elif pose == "feetup":
            of.chair(ctx, x + 40, y, 1.0)
            YOU_SHADES.draw(ctx, x, y, 1.0, expr, T, pose="feetup", arms=arms, lean=-0.25)
        else:
            of.desk(ctx, 250, 1010, 260)
            if T < 13.3:  # empty desk: unplugged cable, an empty tray
                ctx.move_to(200, 990)
                ctx.curve_to(180, 1040, 230, 1080, 205, 1130)
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(5)
                ctx.stroke()
                ctx.rectangle(300, 968, 70, 18)
                ctx.set_source_rgb(*hexc("#c9cdd6"))
                ctx.fill_preserve()
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(3)
                ctx.stroke()
            if pose in ("sit", "sitsad"):
                of.chair(ctx, x, y, 1.0)
                YOU.draw(ctx, x, y, 1.0, expr, T, pose="sit", arms=arms, bob=0.4 if pose == "sit" else 0.1,
                         lean=0.12 if pose == "sitsad" else 0.0)
            else:
                of.chair(ctx, 250, 1160, 1.0, tucked=True)
                YOU.draw(ctx, x, y, 1.05, expr, T, arms=arms, look=(-0.4 if 15.4 < T < 19.9 else 0.0))
    else:
        of.desk(ctx, 250, 1010, 260)
        of.chair(ctx, 250, 1160, 1.0, tucked=True)
    if 27.0 < T < 31.32:
        of.coins(ctx, T, -100, 820, -100, 1300, n=26)
    if 29.24 < T < 31.32:
        label(ctx, "JACKPOT!", 360, 300, 60, hexc("#f2b84b"), fg=OUT, scale=pop(T - 30.6), tilt=-0.05)
    tint(ctx, (0.25, 0.35, 0.7), 0.22 * cold)
    tint(ctx, (0.04, 0.05, 0.18), 0.62 * night)
    if night:
        glow(ctx, 360, 420, 260, (1, 0.9, 0.7), 0.25)


# ---------------------------------------------------------------- hallway
def s_hall(ctx, t, d):
    T = 31.32 + t
    vx, vy = 360, 600
    col_w, col_f, col_c = hexc("#cfd8ee"), hexc("#b9c2d8"), hexc("#b9b6dc")
    ctx.rectangle(-600, -800, 2000, 3000)
    ctx.set_source_rgb(*col_w)
    ctx.fill()
    for poly, col in ((((-600, -800), (1320, -800), (420, 520), (300, 520)), col_c),
                      (((-600, 1800), (1320, 1800), (420, 700), (300, 700)), col_f),
                      (((-600, -800), (300, 520), (300, 700), (-600, 1800)), col_w),
                      (((1320, -800), (420, 520), (420, 700), (1320, 1800)), lerpc(col_w, (0, 0, 0), 0.08))):
        ctx.move_to(*poly[0])
        for p in poly[1:]:
            ctx.line_to(*p)
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(3)
        ctx.stroke()
    ctx.rectangle(300, 520, 120, 180)
    ctx.set_source_rgb(*hexc("#fff3d6"))
    ctx.fill()
    for k in range(5):  # ceiling light panels toward the vanishing point
        f = 0.25 + k * 0.18
        y = vy - 80 - (1 - f) * 900
        w = 200 * (1 - f) + 20
        ctx.rectangle(vx - w / 2, y, w, 30 * (1 - f) + 6)
        ctx.set_source_rgb(1, 0.97, 0.85)
        ctx.fill()
    # coworkers along both walls turn their heads together at "weird looks"
    turn = T > 32.9
    for i, (x, y, s) in enumerate(((120, 1240, 1.15), (230, 1000, 0.8), (290, 860, 0.55),
                                   (600, 1240, 1.15), (490, 1000, 0.8), (430, 860, 0.55))):
        side = -1 if x < 360 else 1
        expr = keyed(T, [(0, "neutral"), (32.9 + 0.05 * i, "smirk" if i % 2 else "worried")])
        COWORKERS[i].draw(ctx, x, y, s, expr, T + i, look=(-side * 0.7 if turn else side * 0.2), bob=0.5)
    s = lerp(0.55, 0.95, (T - 31.32) / 2.7)
    y = lerp(900, 1180, (T - 31.32) / 2.7)
    YOU.draw(ctx, 360, y, s, keyed(T, [(0, "neutral"), (33.0, "worried")]), T, pose="walk", walk_phase=T * 1.6)


# ---------------------------------------------------------------- phone insert
def s_phone(ctx, t, d):
    T = 34.25 + t
    s_room(ctx, t, d, T0=34.25)
    tint(ctx, (0.1, 0.1, 0.2), 0.35)
    of.phone(ctx, 360, 640, 2.2, screen="inbox", t=T)
    for side in (-1, 1):
        ctx.new_sub_path()
        ctx.arc(360 + side * 150, 700, 26, 0, 2 * math.pi)
        ctx.set_source_rgb(*OUT)
        ctx.fill()


# ---------------------------------------------------------------- the explanation (deep blue, one lamp)
def s_blue(ctx, t, d):
    T = 64.57 + t
    of.room(ctx, -400, 1100, 230, 980, wall="#33467f", floor="#283259", ceil="#252a4f")
    of.pendant(ctx, 360, 230)
    glow(ctx, 360, 520, 520, (1, 0.8, 0.45), 0.35)
    if T < 71.9:
        of.law_book(ctx, 360, 640, 1.0)
        if 66.8 < T < 68.6:  # firing is blocked again
            k = T - 66.8
            sy = lerp(330, 480, ease(k / 0.4)) if k < 0.4 else 480 - 120 * math.sin(min(k - 0.4, 0.5) / 0.5 * math.pi / 2)
            if k > 0.35:
                of.shield(ctx, 360, 560, 0.6, a=clamp((k - 0.35) / 0.1))
            of.stamp(ctx, 360, sy, 0.9)
    if T > 68.6:
        expr = keyed(T, [(0, "grin"), (70.4, "cold")])
        arms = ("down", "hold") if T > 76.5 else ("down", "down")
        BOSS.draw(ctx, 560, 1000, 1.0, expr, T, arms=arms, look=(-0.3 if T > 76.5 else 0.0))
    if T > 71.9:
        for k, x in enumerate((60, 330)):  # coworkers vanish at "your coworkers"
            sc = 0.7 * (1 - ease((T - 74.5 - k * 0.15) / 0.35))
            if sc > 0.02:
                COWORKERS[k].draw(ctx, x, 980, sc, "neutral", T + k, bob=0.3)
        of.desk(ctx, 200, 1010, 240)
        items = [(74.0, lambda: of.monitor(ctx, 160, 985, 0.75)),
                 (72.66, lambda: _folders(ctx, 270, 985)),
                 (73.0, lambda: of.plant(ctx, 110, 985, 0.7)),
                 (73.31, lambda: of.phone(ctx, 300, 950, 0.25, screen="game", t=T))]
        for gone, fn in items:
            k = 1 - ease((T - gone) / 0.25)
            if k > 0.02:
                ctx.save()
                ctx.translate(200, 980)
                ctx.scale(k, k)
                ctx.translate(-200, -980)
                fn()
                ctx.restore()
        of.chair(ctx, 200, 1160, 1.0)
        YOU.draw(ctx, 200, 1160, 1.0, keyed(T, [(0, "neutral"), (72.7, "worried"), (75.6, "sad")]), T,
                 pose="sit", lean=0.1 if T > 75.6 else 0.0, bob=0.3)
        if T < 76.4:  # "sense of purpose": a small light above YOU that fades and drops
            k = clamp((T - 75.4) / 0.9)
            glow(ctx, 200, 700 + 200 * k, 70, (1, 0.9, 0.5), 0.8 * (1 - k))
            ctx.new_sub_path()
            ctx.arc(200, 700 + 200 * k, 16, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.95, 0.6, 1 - k)
            ctx.fill()


def _folders(ctx, x, y):
    for k in range(3):
        ctx.rectangle(x - 40 + k * 4, y - 22 - k * 16, 80, 16)
        ctx.set_source_rgb(*hexc(("#e8574a", "#f2b84b", "#4fb3a9")[k]))
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(3)
        ctx.stroke()


def room_at(T0, night=0.0):
    return lambda ctx, t, d: s_room(ctx, t, d, T0=T0, night=night)


def office_at(T0, mode):
    return lambda ctx, t, d: s_office(ctx, t, d, mode=mode, T0=T0)


SHOTS = [
    dict(start=0.0, draw=s_hook, dof=2, shake=(1.5, 7), keys=[
        (0.05, 1.45, (360, 760)),                                   # "Getting fired"
        (0.75, 1.9, (380, 820), 0.5),                                # "in Japan" stamp over paper
        (1.9, 1.45, (360, 760), 0.35)]),                             # "impossible" shield, boss shocked
    dict(start=2.74, draw=s_plan, dof=2, keys=[
        (2.74, 1.9, (360, 880)),                                     # "But" the boss, still blocked
        (3.10, 1.05, (360, 800), 0.4),                               # "companies" three bosses
        (3.81, 1.35, (360, 820), 0.45),                              # "figured out a way" light bulbs
        (4.42, 1.6, (360, 530), 0.5),                                # "to make something" the plan
        (5.14, 2.3, (365, 525), 0.45),                               # "even worse" red circle
        (5.95, 4.6, (330, 560), 0.6)]),                              # "happen" into the drawn door
    dict(start=6.12, draw=office_at(6.12, "walk"), dof=2, keys=[
        (6.12, 1.1, (300, 860)),                                     # "Imagine"
        (7.06, 1.3, (420, 960), 0.6),                                # "your boss leads you"
        (8.01, 1.3, (880, 960), 0.7),                                # "away from your desk" tracking
        (8.73, 1.7, (1440, 860), 0.55),                              # "into a tiny office" door
        (9.3, 3.2, (1560, 860), 0.4)]),                              # through the door
    dict(start=9.4, draw=room_at(9.4), dof=2, keys=[
        (9.4, 1.0, (330, 760)),
        (9.98, 2.2, (230, 1000), 0.45),                              # "no computer"
        (10.82, 2.4, (335, 975), 0.4),                               # "no tasks"
        (12.23, 1.25, (400, 900), 0.6),                              # "absolutely nothing to do"
        (14.02, 2.4, (360, 420), 0.5),                               # "a clock ticking"
        (16.13, 1.6, (540, 840), 0.55),                              # "some guy in the corner"
        (17.06, 2.2, (640, 920), 0.4),                               # "feet on the desk"
        (18.37, 2.8, (520, 900), 0.4),                               # "scrolling through his phone"
        (19.22, 1.5, (560, 850), 0.45),                              # "like he's on vacation"
        (20.39, 1.9, (120, 760), 0.5),                               # "your boss smiles"
        (22.01, 1.2, (260, 850), 0.5),                               # "this is your new position"
        (23.86, 2.0, (250, 1060), 0.45),                             # "sit here"
        (24.82, 2.4, (360, 420), 0.45),                              # "until 6 o'clock"
        (26.10, 2.2, (440, 955), 0.45),                              # "seriously?"
        (27.33, 1.2, (400, 800), 0.45),                              # "getting paid" coins
        (28.59, 2.0, (440, 950), 0.4)]),                             # "absolutely nothing?"
    dict(start=29.24, draw=room_at(29.24), dof=2, keys=[
        (29.24, 1.3, (360, 900)), (30.69, 1.2, (360, 760), 0.45)]),  # "hit the jackpot"
    dict(start=31.32, draw=s_hall, dof=2, keys=[
        (31.32, 1.0, (360, 700)), (32.57, 1.3, (360, 760), 0.6),    # "coworkers start giving you"
        (33.32, 1.9, (540, 960), 0.4),                               # "weird looks"
        (33.9, 1.25, (360, 820), 0.35)]),                            # "in the hallway"
    dict(start=34.25, draw=s_phone, keys=[
        (34.25, 1.0, C), (35.58, 1.2, (360, 660), 0.5)]),           # "nobody sends you emails"
    dict(start=36.06, draw=office_at(36.06, "desk"), dof=2, keys=[
        (36.06, 1.2, (520, 820)), (36.62, 1.8, (640, 880), 0.45),   # "your old desk"
        (38.23, 2.6, (680, 900), 0.5),                               # "family pictures"
        (39.2, 1.7, (300, 960), 0.35)]),                             # YOU, sad
    dict(start=39.59, draw=room_at(39.59), dof=2, keys=[
        (39.59, 1.1, (400, 700)), (39.97, 2.3, (610, 410), 0.35),   # "Every Friday"
        (41.81, 2.0, (140, 760), 0.5),                               # "the biggest smile"
        (43.40, 1.3, (220, 860), 0.5),                               # "enjoying your"
        (44.12, 2.0, (250, 930), 0.4),                               # "new position" forced smile
        (45.85, 1.8, (540, 840), 0.5),                               # "the guy in the corner"
        (47.60, 2.0, (610, 450), 0.4),                               # "3 whole years"
        (49.38, 1.9, (540, 840), 0.45),                              # "happier"
        (50.46, 1.0, (380, 760), 0.45),                              # "than everyone else"
        (51.27, 2.0, (250, 930), 0.45),                              # "So you figure"
        (52.83, 1.6, (250, 900), 0.4),                               # "to do nothing"
        (53.75, 1.3, (300, 880), 0.4),                               # "why complain?"
        (55.52, 1.4, (520, 870), 0.5),                               # "put your feet up"
        (56.39, 1.7, (480, 850), 0.4),                               # "beside him"
        (57.01, 2.3, (610, 410), 0.4),                               # "one Monday"
        (57.93, 1.6, (130, 770), 0.4),                               # "you show up"
        (58.75, 1.5, (600, 900), 0.45),                              # "he's disappeared"
        (59.82, 2.2, (560, 990), 0.45),                              # "chair is neatly tucked in"
        (61.41, 2.0, (640, 900), 0.45)]),                            # "desk is completely empty"
    dict(start=62.81, draw=office_at(62.81, "away"), dof=2, keys=[
        (62.81, 1.2, (360, 820)), (63.5, 1.7, (360, 960), 0.45)]),  # "nobody will tell you"
    dict(start=64.57, draw=s_blue, dof=2, keys=[
        (64.57, 1.1, (360, 700)), (65.86, 1.6, (360, 640), 0.5),    # "Japanese labor laws"
        (67.28, 1.3, (360, 600), 0.4),                               # "firing someone extremely difficult"
        (69.87, 1.8, (560, 760), 0.5),                               # "nothing stopping companies"
        (71.32, 2.2, (560, 760), 0.4),                               # "miserable"
        (73.31, 1.9, (210, 900), 0.5),                               # "take away your responsibilities"
        (74.58, 1.2, (300, 820), 0.45),                              # "your coworkers"
        (76.02, 2.2, (200, 920), 0.45),                              # "sense of purpose"
        (77.31, 1.7, (560, 760), 0.45)]),                            # "they just wait"
    dict(start=77.82, draw=room_at(77.82, night=1.0), dof=2, keys=[
        (77.82, 1.4, (360, 520)), (78.13, 2.3, (360, 420), 0.3),    # "sooner or later" clock spins
        (79.60, 1.7, (250, 920), 0.5),                               # "getting paid to do nothing"
        (81.30, 0.95, (330, 700), 0.8)]),                            # "becomes unbearable" pull back
]
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

SFX = [
    (1.5, "thud.wav", 0.9), (1.55, "pop.wav", 0.8), (1.6, "sting_soft.wav", 0.6),
    (5.64, "sting_soft.wav", 0.6),
    *[(7.0 + k * 0.5, "step.wav", 0.5) for k in range(4)],
    *[(13.5 + k * 0.5, "tick.wav", 0.7) for k in range(4)],
    (19.0, "sparkle.wav", 0.5),
    (20.4, "pop.wav", 0.5),
    *[(24.3 + k * 0.05, "tick.wav", 0.4) for k in range(10)], (24.85, "bell.wav", 0.4),
    (26.1, "boing.wav", 0.6),
    *[(27.3 + k * 0.35, "coin.wav", 0.5) for k in range(10)],
    (30.65, "sparkle.wav", 0.7),
    (32.9, "murmur.wav", 0.6),
    (34.4, "pop.wav", 0.5),
    (38.2, "sting_soft.wav", 0.5),
    (39.65, "page.wav", 0.8), (40.5, "pop.wav", 0.5),
    *[(47.0 + k * 0.15, "page.wav", 0.5) for k in range(8)], (47.45, "pop.wav", 0.7),
    (49.0, "sparkle.wav", 0.6),
    (53.6, "boing.wav", 0.4),
    (56.8, "page.wav", 0.8), (58.75, "sting.wav", 0.8),
    (65.86, "thud.wav", 0.6), (67.15, "thud.wav", 0.9), (67.2, "pop.wav", 0.7),
    (70.4, "sting_low.wav", 0.9),
    (72.66, "pop.wav", 0.6), (73.0, "pop.wav", 0.6), (73.31, "pop.wav", 0.6), (74.0, "pop.wav", 0.6),
    (74.5, "pop.wav", 0.5), (74.65, "pop.wav", 0.5),
    *[(77.9 + k * 0.06, "tick.wav", 0.4) for k in range(14)],
    (80.6, "sting_low.wav", 0.6),
]

if __name__ == "__main__":
    import json
    import engine
    json.dump([{"time": round(t, 3), "file": f, "volume": v} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    if "--no-lipsync" in sys.argv:
        engine.LIPSYNC = False
    elif len(sys.argv) > 3:
        set_voice(sys.argv[3])
    render(SHOTS, TOTAL, sys.argv[1], grain=5)
