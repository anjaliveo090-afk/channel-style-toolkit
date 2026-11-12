"""Spear & shield, fast cut: 36 shots, a new literal visual every ~1.5 s (2-4 words),
something always moving. Same medieval style as spear_shield.py (2D characters on
the 3D terrace plate, painted 2D sets)."""
import math
import random
import sys

import cairo

import medieval as md
import spear_shield as base
from engine import moon, stars, sun, W, H, clamp, ease, ellipse, glow, hexc, keyed, label, lerp, lerpc, pop, render, rrect, text
from spear_shield import KR, KT, SM, MSG_R, MSG_T, spear_h, tint, terrace_base, shadows
from style3 import Char3, OUT, draw_item3, shield as draw_shield

TOTAL = 52.85
C = (W / 2, H / 2)
SOLD_R = Char3("#d9534a", outfit="tunic", helmet=True, legs=2.0, torso=1.8)
SOLD_T = Char3("#3aa6a0", outfit="tunic", helmet=True, legs=2.0, torso=1.8)


# ---------------------------------------------------------------- small helpers
def push(t0, t1, z0, z1, c0, c1):
    """Camera that moves from (z0, c0) to (z1, c1) across the whole shot."""
    return [(t0, z0, c0), (t1, z1, c1, max(0.2, t1 - t0))]


def bag(ctx, x, y, s=1.0):
    draw_item3(ctx, "moneybag", x, y, 64 * s * 0.9, 0)


def bubble(ctx, x, y, w, h, tx, ty, sc=1.0):
    if sc <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.translate(-x, -y)
    ctx.move_to(x - 30, y + h / 2 - 4)
    ctx.line_to(tx, ty)
    ctx.line_to(x + 10, y + h / 2 - 4)
    ctx.close_path()
    rrect(ctx, x - w / 2, y - h / 2, w, h, h * 0.35)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def shatter(ctx, x, y, T, t_hit, s=1.0, kind="rock", seed=1):
    """An object that breaks into flying pieces at t_hit."""
    rnd = random.Random(seed)
    col = hexc("#9aa0aa") if kind == "rock" else hexc("#c9785a")
    if T < t_hit:
        if kind == "rock":
            pts = [(-90, 40), (-70, -50), (-10, -90), (60, -70), (95, 0), (70, 60), (-20, 75)]
            ctx.move_to(x + pts[0][0] * s, y + pts[0][1] * s)
            for px, py in pts[1:]:
                ctx.line_to(x + px * s, y + py * s)
            ctx.close_path()
            md.shade(ctx, lerpc(col, (1, 1, 1), 0.2), col, y - 90 * s, y + 75 * s, 4)
        else:
            for row in range(5):
                for k in range(3):
                    bx = x - 100 * s + k * 66 * s + (row % 2) * 33 * s
                    rrect(ctx, bx, y - 110 * s + row * 44 * s, 64 * s, 42 * s, 4)
                    md.shade(ctx, lerpc(col, (1, 1, 1), 0.15), col, 0, 1, 3)
        return
    k = T - t_hit
    for i in range(12):
        vx, vy = rnd.uniform(-420, 520) * s, rnd.uniform(-650, -150) * s
        px, py = x + vx * k, y + vy * k + 1400 * s * k * k
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(k * rnd.uniform(-9, 9))
        sz = rnd.uniform(14, 34) * s
        ctx.move_to(-sz, -sz * 0.6)
        ctx.line_to(sz * 0.8, -sz)
        ctx.line_to(sz, sz * 0.5)
        ctx.line_to(-sz * 0.4, sz)
        ctx.close_path()
        md.shade(ctx, col, lerpc(col, (0, 0, 0), 0.2), -sz, sz, 3)
        ctx.restore()
    glow(ctx, x, y, 200 * s, (1, 0.9, 0.6), max(0, 0.7 - k * 1.5))
    for i in range(6):
        ctx.new_sub_path()
        ctx.arc(x + math.cos(i) * 60 * s * (1 + k * 2), y + math.sin(i * 1.3) * 30 * s, 40 * s * (1 + k), 0, 2 * math.pi)
    ctx.set_source_rgba(0.85, 0.82, 0.78, max(0, 0.6 - k))
    ctx.fill()


def arrow(ctx, x, y, ang, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.move_to(-120 * s, 0)
    ctx.line_to(0, 0)
    ctx.set_source_rgb(*hexc("#8a5a33"))
    ctx.set_line_width(8 * s)
    ctx.stroke()
    ctx.move_to(22 * s, 0)
    ctx.line_to(-6 * s, -12 * s)
    ctx.line_to(-6 * s, 12 * s)
    ctx.close_path()
    md.shade(ctx, hexc("#e9edf2"), hexc("#a5abb8"), -12, 12, 3)
    for side in (-1, 1):
        ctx.move_to(-120 * s, 0)
        ctx.line_to(-100 * s, side * 14 * s)
        ctx.line_to(-90 * s, 0)
    ctx.set_source_rgb(*hexc("#e8574a"))
    ctx.fill()
    ctx.restore()


def bounce_off(ctx, T, t_hit, tx, ty, kind, s=1.0):
    """Something flies in from the right, hits (tx, ty) at t_hit and bounces back with TING."""
    if T < t_hit - 0.35:
        return
    if T < t_hit:
        p = (T - (t_hit - 0.35)) / 0.35
        x, y, ang = lerp(tx + 520, tx + 40, p), ty - 40 + 40 * p, math.pi
    else:
        k = T - t_hit
        x, y, ang = tx + 40 + 500 * k, ty - 500 * k + 1200 * k * k, math.pi + k * 12
        if k < 0.35:
            label(ctx, "TING!", tx + 80, ty - 120, 40, hexc("#fff4dc"), fg=OUT, scale=pop(k), tilt=0.1)
            glow(ctx, tx + 30, ty, 120, (1, 0.95, 0.6), 0.8 * (1 - k / 0.35))
    if kind == "arrow":
        arrow(ctx, x, y, ang, s)
    elif kind == "hammer":
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(ang)
        draw_item3(ctx, "hammer", 0, 0, 90 * s, 0)
        ctx.restore()
    else:
        ctx.new_sub_path()
        ctx.arc(x, y, 50 * s, 0, 2 * math.pi)
        md.shade(ctx, hexc("#b9bec7"), hexc("#80858f"), y - 50, y + 50, 4)


def field_bg(ctx, T, night=0.0):
    md.sky(ctx, -900, 640, top="#5f88d0", bottom="#a9cdf3")
    for x, y, s in ((150, 230, 1.3), (560, 160, 1.1), (900, 300, 0.9)):
        md.cloud(ctx, x, y, s, T)
    md.castle(ctx, 110, 600, 0.35, md.RED)
    md.castle(ctx, 930, 600, 0.35, md.TEAL)
    md.field_ground(ctx, 600, 525, y_bottom=1700)
    if night:
        tint(ctx, (0.05, 0.08, 0.25), 0.6 * night)


def zzz(ctx, x, y, T):
    for k in range(3):
        ph = (T * 0.8 + k / 3) % 1
        text(ctx, "z", x + ph * 50 + k * 6, y - ph * 90, 26 + ph * 20, (1, 1, 1), outline=True)


def stamp_label(ctx, txt, x, y, T, t0, col="#d63c3c", size=70):
    if T < t0:
        return
    k = T - t0
    sc = 2.4 - 1.4 * ease(min(1, k / 0.12)) if k < 0.12 else pop(k - 0.12) * 0.0 + 1.0
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.15)
    ctx.scale(sc, sc)
    rrect(ctx, -230, -55, 460, 110, 14)
    ctx.set_source_rgba(*hexc(col), 0.9)
    ctx.set_line_width(10)
    ctx.stroke()
    text(ctx, txt, 0, 0, size, hexc(col), outline=False)
    ctx.restore()


# ---------------------------------------------------------------- shots
def s_forge(ctx, t, d):  # "A blacksmith"
    T = t
    terrace_base(ctx, T)
    shadows(ctx, ((380, 960, 160),))
    SM.draw(ctx, 380, 960, 1.45, "smug", T, arms=("down", "hammer"), item="hammer", shadow=False)
    md.anvil(ctx, 300, 1190, 1.25, spark_t=(T * 2.2) % 1)
    spear_h(ctx, 210, 985, 260, 0.6)


def s_handoff(ctx, t, d):  # "sold one king"
    T = 0.75 + t
    terrace_base(ctx, T)
    shadows(ctx, ((170, 1010, 170), (470, 960, 160)))
    given = T > 1.25
    SM.draw(ctx, 470, 960, 1.45, keyed(T, [(0, "smirk"), (1.3, "grin")]), T,
            arms=("show" if not given else "down", "down"), item=None if given else "spear", item_hand=0, shadow=False)
    KR.draw(ctx, 170, 1010, 1.45, keyed(T, [(0, "neutral"), (1.2, "grin")]), T,
            arms=("belly", "spear" if given else "show"), item="spear" if given else None, shadow=False)
    if T > 1.05:  # coin bag tossed to the smith
        k = clamp((T - 1.05) / 0.4)
        bag(ctx, lerp(200, 430, k), lerp(600, 700, k) - 160 * math.sin(k * math.pi), 1.4)


def s_spear(ctx, t, d):  # "a spear"
    T = 1.5 + t
    terrace_base(ctx, T)
    tint(ctx, (0.2, 0.15, 0.25), 0.35)
    spear_h(ctx, -80, 660, 760, 1.4, ang=-0.12)
    gx = lerp(150, 700, (T - 1.5) / 0.45)
    glow(ctx, gx, 660 - (gx + 80) * 0.12, 70, (1, 1, 1), 0.9)


def s_smash(ctx, t, d):  # "that could break through anything"
    T = 1.95 + t
    terrace_base(ctx, T)
    tipx = lerp(-200, 900, (T - 2.0) / 1.5)
    shatter(ctx, 280, 760, T, 2.47, 1.1, "rock", 1)
    shatter(ctx, 520, 740, T, 3.0, 1.1, "wall", 2)
    spear_h(ctx, tipx - 760, 760, 760, 1.2)
    if T > 3.1:
        label(ctx, "ANYTHING!", 380, 430, 56, hexc("#f2c443"), fg=OUT, scale=pop(T - 3.1), tilt=-0.05)


def s_enemy(ctx, t, d):  # "and his greatest enemy"
    T = 3.64 + t
    terrace_base(ctx, T)
    tint(ctx, (0.1, 0.35, 0.4), 0.25)
    KT.draw(ctx, 380, 1060, 1.65, keyed(T, [(0, "neutral"), (3.95, "angry")]), T, arms=("hip", "hip"), shadow=False)


def s_shield(ctx, t, d):  # "a shield"
    T = 4.7 + t
    terrace_base(ctx, T)
    tint(ctx, (0.15, 0.2, 0.3), 0.35)
    k = ease((T - 4.7) / 0.4)
    ctx.save()
    ctx.translate(380, 640)
    ctx.scale(max(0.05, abs(math.cos((1 - k) * 4))), 1)
    draw_shield(ctx, 0, 0, 230 * (0.6 + 0.4 * k))
    ctx.restore()
    glow(ctx, 300, 560, 90, (1, 1, 1), 0.8 * k)


def s_bounce(ctx, t, d):  # "that nothing in the world could break"
    T = 5.2 + t
    terrace_base(ctx, T)
    KT.draw(ctx, 330, 1060, 1.5, "smug", T, arms=("hold", "hip"), shadow=False)
    draw_shield(ctx, 330, 760, 190)
    bounce_off(ctx, T, 5.55, 330, 720, "arrow", 1.2)
    bounce_off(ctx, T, 6.0, 330, 780, "hammer", 1.0)
    bounce_off(ctx, T, 6.5, 330, 740, "rock", 1.0)


def s_map(ctx, t, d):  # "The two kingdoms"
    T = 7.0 + t
    ctx.set_source_rgb(*hexc("#5a3f2a"))
    ctx.paint()
    rrect(ctx, 20, 160, 680, 960, 30)
    md.shade(ctx, hexc("#f4e6c4"), hexc("#dcc597"), 160, 1120, 6)
    ctx.move_to(380, 170)
    ctx.curve_to(300, 400, 460, 700, 360, 1110)
    ctx.set_source_rgb(*hexc("#7fb1d4"))
    ctx.set_line_width(22)
    ctx.stroke()
    md.castle(ctx, 190, 640, 1.3, md.RED, haze=0)
    md.castle(ctx, 560, 640, 1.3, md.TEAL, haze=0)
    k = ease((T - 7.2) / 0.4)
    for sgn in (-1, 1):  # crossed swords
        ctx.save()
        ctx.translate(380, 820)
        ctx.rotate(sgn * 0.7 * k)
        ctx.move_to(0, 110)
        ctx.line_to(0, -110)
        ctx.set_source_rgb(*hexc("#b9bec7"))
        ctx.set_line_width(12)
        ctx.stroke()
        ctx.move_to(-30, 80)
        ctx.line_to(30, 80)
        ctx.set_source_rgb(*hexc("#8a5a33"))
        ctx.stroke()
        ctx.restore()


def s_clash(ctx, t, d):  # "had been fighting"
    T = 7.75 + t
    field_bg(ctx, T)
    k = clamp((T - 7.75) / 0.5)
    for i in range(3):
        SOLD_R.draw(ctx, lerp(-60, 230, k) - i * 90, 1080 + i * 25, 1.0, "angry", T + i, pose="walk",
                    walk_phase=T * 3, arms=("down", "up"), look=0.6)
        SOLD_T.draw(ctx, lerp(780, 500, k) + i * 90, 1080 + i * 25, 1.0, "angry", T + i, pose="walk",
                    walk_phase=T * 3, arms=("up", "down"), look=-0.6)
    if T > 8.25:
        for i in range(7):
            ctx.new_sub_path()
            ctx.arc(365 + math.cos(i * 0.9 + T * 3) * 90, 860 + math.sin(i * 1.7) * 60, 70, 0, 2 * math.pi)
        ctx.set_source_rgba(0.9, 0.86, 0.78, 0.9)
        ctx.fill()
        for a in (-0.6, 0.6):
            ctx.save()
            ctx.translate(365, 780)
            ctx.rotate(a + math.sin(T * 30) * 0.1)
            ctx.move_to(0, 90)
            ctx.line_to(0, -90)
            ctx.set_source_rgb(*hexc("#e9edf2"))
            ctx.set_line_width(10)
            ctx.stroke()
            ctx.restore()


def s_years(ctx, t, d):  # "for a hundred years"
    T = 8.55 + t
    terrace_base(ctx, T)
    n = max(1, int(round(lerp(1, 100, ease((T - 8.55) / 0.6)))))
    md.years_sign(ctx, 40, 1080, 1.05, f"{n:03d}")
    for x, col in ((110, "#e8574a"), (330, "#f2c443"), (560, "#ffffff")):
        md.helmet_flower(ctx, x, 1215, 0.95, col)


def s_split(ctx, t, d):  # "and now both rulers believed"
    T = 9.47 + t
    terrace_base(ctx, T)
    ctx.rectangle(-500, -800, 860, 3000)
    ctx.set_source_rgba(0.9, 0.2, 0.15, 0.25)
    ctx.fill()
    ctx.rectangle(360, -800, 900, 3000)
    ctx.set_source_rgba(0.1, 0.6, 0.6, 0.25)
    ctx.fill()
    ctx.move_to(360, -800)
    ctx.line_to(360, 2200)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(10)
    ctx.stroke()
    KR.draw(ctx, 180, 1060, 1.35, "smug", T, arms=("belly", "spear"), item="spear", look=0.3, shadow=False)
    KT.draw(ctx, 540, 1060, 1.35, "smug", T, arms=("hold", "hip"), item="shield", item_hand=0, look=-0.3, shadow=False)
    sc = pop(T - 10.2)
    bubble(ctx, 180, 330, 230, 150, 170, 450, sc)
    bubble(ctx, 540, 330, 230, 150, 550, 450, pop(T - 10.4))
    if sc > 0:
        text(ctx, "I WIN", 180, 330, 40, OUT, outline=False, scale=sc)
    if T > 10.4:
        text(ctx, "I WIN", 540, 330, 40, OUT, outline=False, scale=pop(T - 10.4))


def s_triumph(ctx, t, d):  # "they finally had the weapon to win the war"
    T = 11.14 + t
    terrace_base(ctx, T)
    shadows(ctx, ((190, 1010, 170), (560, 1010, 170)))
    KR.draw(ctx, 190, 1010, 1.45, "grin", T, arms=("belly", "up"), item="spear", bob=1.5, shadow=False)
    KT.draw(ctx, 560, 1010, 1.45, "grin", T, arms=("up", "hip"), item="shield", item_hand=0, bob=1.5, shadow=False)
    rnd = random.Random(3)
    for i in range(30):  # confetti
        x = rnd.uniform(0, 720)
        y = (rnd.uniform(-200, 1200) + (T - 11.14) * rnd.uniform(300, 500)) % 1400 - 200
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(T * 5 + i)
        ctx.rectangle(-8, -4, 16, 8)
        ctx.set_source_rgb(*hexc(rnd.choice(["#e8574a", "#3aa6a0", "#f2c443"])))
        ctx.fill()
        ctx.restore()
    if T > 12.3:
        label(ctx, "VICTORY!", 380, 300, 64, hexc("#f2c443"), fg=OUT, scale=pop(T - 12.35), tilt=-0.05)


def s_march(ctx, t, d):  # "So their armies marched"
    T = 12.9 + t
    md.sky(ctx, -900, 500)
    ctx.rectangle(-2000, 500, 5000, 3000)
    md.shade(ctx, hexc("#d9b07a"), hexc("#b4844f"), 500, 1300, 0)
    for k in range(9):
        x = (k * 120 + T * 280) % 1200 - 250
        ph = T * 3.2 + k * 0.4
        col = hexc("#d9534a") if k % 2 else hexc("#c9403a")
        rrect(ctx, x - 55, 330, 110, 260, 40)
        md.shade(ctx, col, lerpc(col, (0, 0, 0), 0.2), 330, 590, 5)
        for side in (-1, 1):
            sw = math.sin(ph * 2 * math.pi + (0 if side < 0 else math.pi))
            fx = x + side * 28 + sw * 70
            fy = 1060 - max(0, sw) * 60
            ctx.move_to(x + side * 28, 580)
            ctx.line_to(fx, fy)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(26)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
            ellipse(ctx, fx + 30, fy + 10, 60, 28)
            ctx.set_source_rgb(*OUT)
            ctx.fill()
            if sw < -0.9:
                glow(ctx, fx, fy + 30, 70, (0.9, 0.8, 0.6), 0.6)


def s_aerial(ctx, t, d):  # "onto the same battlefield"
    md.river_aerial(ctx, 14.5 + t, bridge_y=900)


def field_kings(ctx, T, kr_expr, kt_expr, kr_arms=("belly", "up"), kt_arms=("up", "hip"), xr=260, xt=790, sweat=False):
    field_bg(ctx, T)
    md.army_rows(ctx, 330, 615, -150, 900, rows=16, side=md.RED, s_near=0.55, t=T)
    md.army_rows(ctx, 720, 615, 1200, 900, rows=16, side=md.TEAL, s_near=0.55, t=T)
    KR.draw(ctx, xr, 1060, 1.3, kr_expr, T, arms=kr_arms, item="spear", look=0.5, sweat=sweat, shake=0.6 if sweat else 0)
    KT.draw(ctx, xt, 1060, 1.3, kt_expr, T, arms=kt_arms, item="shield", item_hand=0, look=-0.5, sweat=sweat,
            shake=0.6 if sweat else 0)


def s_kr_field(ctx, t, d):  # "one king holding the spear"
    T = 15.9 + t
    field_kings(ctx, T, "smug", "neutral", kr_arms=("belly", "up"), kt_arms=("hold", "hip"))
    md.flowers_foreground(ctx, 1350, T, x0=-300, x1=1100)


def s_kt_field(ctx, t, d):  # "and the other carrying the shield"
    T = 17.38 + t
    field_kings(ctx, T, "neutral", "smug", kr_arms=("belly", "spear"), kt_arms=("up", "hip"))
    md.flowers_foreground(ctx, 1350, T, x0=-300, x1=1100)


def s_strange(ctx, t, d):  # "But then something strange happened"
    T = 18.85 + t
    field_kings(ctx, T, "worried", "worried", kr_arms=("belly", "spear"), kt_arms=("hold", "hip"))
    rnd = random.Random(5)
    for i in range(10):
        x, y = rnd.uniform(-100, 1100), rnd.uniform(560, 760)
        label(ctx, "?", x, y, 34, hexc("#fff4dc"), fg=OUT, scale=pop(T - 19.2 - i * 0.07), tilt=0)


def s_nobody(ctx, t, d):  # "Nobody attacked."
    T = 20.6 + t
    field_bg(ctx, T)
    blink = "happy" if int(T * 4) % 3 == 0 else "neutral"
    SOLD_T.draw(ctx, 380, 1250, 2.1, blink, T, arms=("down", "down"), bob=0.2)
    x = lerp(-150, 870, (T - 20.6) / 1.1)
    ctx.save()
    ctx.translate(x, 1180)
    ctx.rotate(T * 8)
    for k in range(7):
        ctx.new_sub_path()
        ctx.arc(0, 0, 25 + k * 9, k, k + 4.6)
    ctx.set_source_rgb(*hexc("#a8865a"))
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def s_week(ctx, t, d):  # "An entire week passed"
    T = 21.7 + t
    p = (T - 21.7) / 1.3
    a = p * 2 * math.pi * 3.5
    day = math.sin(a)
    md.sky(ctx, -900, 640, top="#5f88d0" if day > 0 else "#1d2457", bottom="#a9cdf3" if day > 0 else "#4a3a7a")
    sx, sy = 360 + math.cos(a) * 380, 640 - abs(math.sin(a)) * 480
    if day > 0:
        sun(ctx, sx, sy, 50, (1, 0.85, 0.5))
    else:
        moon(ctx, sx, sy, 40)
    md.field_ground(ctx, 600, 525, y_bottom=1700)
    if day < 0:
        tint(ctx, (0.05, 0.08, 0.25), 0.45)
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    i = min(6, int(p * 7))
    label(ctx, days[i], 380, 900, 80, hexc("#fff4dc"), fg=OUT, scale=1.0, tilt=0)


def s_bored(ctx, t, d):  # "with 10,000 soldiers standing around"
    T = 23.0 + t
    field_bg(ctx, T)
    md.army_rows(ctx, 330, 615, -150, 900, rows=12, side=md.RED, s_near=0.45, t=T)
    SOLD_R.draw(ctx, 140, 1150, 1.25, "laugh", T, arms=("up", "up"), bob=0.4)   # yawning
    SOLD_T.draw(ctx, 380, 1150, 1.25, "tired", T, arms=("down", "down"), bob=0.1, lean=0.15)
    zzz(ctx, 420, 760, T)
    SOLD_R.draw(ctx, 610, 1150, 1.25, "happy", T, arms=("down", "show"), bob=0.4)
    for k in range(5):  # the flower he picked
        a = k * 2 * math.pi / 5
        ctx.new_sub_path()
        ctx.arc(700 + math.cos(a) * 12, 790 + math.sin(a) * 12, 11, 0, 2 * math.pi)
    ctx.set_source_rgb(*hexc("#e8574a"))
    ctx.fill()
    label(ctx, "10,000 SOLDIERS", 380, 330, 50, hexc("#f2c443"), fg=OUT, scale=pop(T - 23.15), tilt=-0.04)


def s_metal(ctx, t, d):  # "watching two pieces of metal"
    T = 25.3 + t
    field_bg(ctx, T)
    for x in (280, 470):  # wooden stands
        for dx in (-50, 50):
            ctx.move_to(x, 760)
            ctx.line_to(x + dx, 1000)
        ctx.set_source_rgb(*hexc("#8a5a33"))
        ctx.set_line_width(10)
        ctx.stroke()
    ctx.move_to(280, 1000)
    ctx.line_to(280, 470)
    ctx.set_source_rgb(*hexc("#b07a3a"))
    ctx.set_line_width(14)
    ctx.stroke()
    spear_h(ctx, 280, 470, 1, 1.4, ang=-math.pi / 2)
    draw_shield(ctx, 470, 700, 120)
    glow(ctx, 380, 620, 260, (1, 0.95, 0.7), 0.3 + 0.2 * math.sin(T * 6))
    for k in range(7):  # helmets of soldiers staring, in the foreground
        x = -20 + k * 120
        ctx.new_sub_path()
        ctx.arc(x, 1260, 75, math.pi, 2 * math.pi)
        ctx.close_path()
        md.shade(ctx, hexc("#d9dde3"), hexc("#9aa1ad"), 1180, 1260, 5)
        ellipse(ctx, x, 1290, 75, 45)
        md.shade(ctx, hexc("#fcf6ef"), hexc("#e2dcd6"), 1250, 1330, 5)


def s_moon(ctx, t, d):  # "One night"
    T = 26.85 + t
    md.sky(ctx, -900, 900, top="#0e1638", bottom="#3b2c66")
    stars(ctx, 3, 120, 0.9, T, 900)
    moon(ctx, 470, lerp(760, 470, ease((T - 26.85) / 0.6)), 60)
    for x, roof in ((190, md.RED), (560, md.TEAL)):
        md.castle(ctx, x, 1000, 1.0, roof, haze=0)
    tint(ctx, (0.04, 0.05, 0.18), 0.45)
    ctx.rectangle(-2000, 1000, 5000, 2000)
    ctx.set_source_rgb(*hexc("#1b1833"))
    ctx.fill()


def tent(ctx, x, y, col):
    ctx.move_to(x - 170, y)
    ctx.line_to(x, y - 330)
    ctx.line_to(x + 170, y)
    ctx.close_path()
    md.shade(ctx, col, lerpc(col, (0, 0, 0), 0.3), y - 330, y, 5)
    ctx.move_to(x, y - 330)
    ctx.line_to(x - 40, y)
    ctx.line_to(x + 40, y)
    ctx.close_path()
    ctx.set_source_rgb(*hexc("#2a1d2e"))
    ctx.fill()


def s_tents(ctx, t, d):  # "both kings secretly sent messengers"
    T = 27.45 + t
    md.sky(ctx, -900, 900, top="#0e1638", bottom="#3b2c66")
    stars(ctx, 4, 100, 0.8, T, 700)
    ctx.rectangle(-2000, 900, 5000, 2000)
    ctx.set_source_rgb(*hexc("#2a2a45"))
    ctx.fill()
    tent(ctx, 190, 980, md.RED)
    tent(ctx, 560, 980, md.TEAL)
    run = clamp((T - 28.6) / 0.7)
    KR.draw(ctx, 120, 1120, 0.95, "smirk", T, arms=("belly", "show"), look=0.6)
    KT.draw(ctx, 630, 1120, 0.95, "smirk", T, arms=("show", "hip"), look=-0.6)
    MSG_R.draw(ctx, lerp(250, 400, run), 1130, 0.9, "worried", T, pose="walk" if run > 0 else "stand",
               walk_phase=T * 3, look=-0.6 if run == 0 else 0.6)
    MSG_T.draw(ctx, lerp(500, 330, run), 1130, 0.9, "worried", T, pose="walk" if run > 0 else "stand",
               walk_phase=T * 3, look=0.6 if run == 0 else -0.6)
    glow(ctx, 380, 1000, 400, (1, 0.7, 0.35), 0.2)
    if 27.9 < T < 28.6:
        text(ctx, "psst...", 220, 760, 34, (1, 1, 1), outline=True)
        text(ctx, "psst...", 530, 760, 34, (1, 1, 1), outline=True)


def forge_night(ctx, T, smith_expr, msg_x=(200, 560), msg_expr="worried", msg_arms=("hold", "hold"), sweat=False):
    terrace_base(ctx, T, night=1.0)
    glow(ctx, 380, 760, 300, (1, 0.7, 0.35), 0.45)
    md.anvil(ctx, 380, 1180, 1.2)
    SM.draw(ctx, 380, 960, 1.45, smith_expr, T, arms=("hip", "hip") if smith_expr in ("smirk", "grin") else ("down", "down"),
            bob=0.6, shadow=False)
    for ch, x, lk in ((MSG_R, msg_x[0], 0.6), (MSG_T, msg_x[1], -0.6)):
        ch.draw(ctx, x, 1060, 1.15, msg_expr, T, arms=msg_arms, look=lk, sweat=sweat, shake=0.7 if sweat else 0)


def s_arrive(ctx, t, d):  # "to the blacksmith"
    T = 29.35 + t
    k = ease((T - 29.35) / 0.35)
    forge_night(ctx, T, "tired" if T < 29.75 else "shock", msg_x=(lerp(-150, 200, k), lerp(900, 560, k)))
    if T < 29.75:
        zzz(ctx, 440, 480, T)


def s_question(ctx, t, d):  # "asking exactly the same question"
    T = 30.2 + t
    forge_night(ctx, T, "worried", msg_expr="laugh", msg_arms=("up", "up"))
    bubble(ctx, 200, 640, 200, 110, 210, 740, pop(T - 30.4))
    bubble(ctx, 560, 640, 200, 110, 550, 740, pop(T - 30.45))
    if T > 30.4:
        text(ctx, "WHICH?", 200, 640, 36, OUT, outline=False, scale=pop(T - 30.4))
        text(ctx, "WHICH?", 560, 640, 36, OUT, outline=False, scale=pop(T - 30.45))


def s_which(ctx, t, d):  # "which weapon actually works?"
    T = 32.1 + t
    forge_night(ctx, T, "worried")
    sc = pop(T - 32.15)
    bubble(ctx, 380, 380, 520, 260, 400, 520, sc)
    if sc > 0:
        ctx.save()
        ctx.translate(380, 380)
        ctx.scale(sc, sc)
        spear_h(ctx, -230, 0, 180, 0.8)
        text(ctx, "VS", 0, 0, 50, hexc("#d63c3c"), outline=False)
        draw_shield(ctx, 150, 0, 70)
        ctx.restore()
        label(ctx, "?", 380, 210, 70, hexc("#f2c443"), fg=OUT, scale=pop(T - 32.6), tilt=0)


def s_reply(ctx, t, d):  # "And the blacksmith gave them both the same reply"
    T = 33.7 + t
    forge_night(ctx, T, keyed(T, [(0, "neutral"), (34.4, "smirk")]))


def s_findout(ctx, t, d):  # "fight and you'll find out."
    T = 36.1 + t
    forge_night(ctx, T, "grin", msg_expr="shock", sweat=True)
    label(ctx, "FIGHT AND FIND OUT", 380, 330, 40, hexc("#e8574a"), scale=pop(T - 36.15), tilt=0.04)


def blue_bg(ctx):
    g = cairo.LinearGradient(0, -400, 0, 1700)
    g.add_color_stop_rgb(0, *hexc("#1c2550"))
    g.add_color_stop_rgb(1, *hexc("#3b2f6b"))
    ctx.set_source(g)
    ctx.paint()
    glow(ctx, 380, 600, 520, (1, 0.8, 0.45), 0.25)


def s_pierce(ctx, t, d):  # "a spear that can pierce absolutely anything"
    T = 37.4 + t
    blue_bg(ctx)
    tipx = lerp(-100, 900, clamp((T - 38.0) / 1.7))
    for i, (x, kind) in enumerate(((200, "rock"), (400, "wall"), (600, "rock"))):
        shatter(ctx, x, 640, T, 38.0 + (x + 100) / 1000 * 1.7, 0.9, kind, i + 3)
    spear_h(ctx, tipx - 700, 640, 700, 1.1, glow_a=0.5)


def s_never(ctx, t, d):  # "and a shield that can never be pierced"
    T = 40.15 + t
    blue_bg(ctx)
    glow(ctx, 330, 640, 300, (0.6, 0.95, 1.0), 0.45)
    draw_shield(ctx, 330, 640, 200)
    bounce_off(ctx, T, 40.6, 330, 600, "arrow", 1.2)
    bounce_off(ctx, T, 41.0, 330, 680, "arrow", 1.2)
    bounce_off(ctx, T, 41.4, 330, 620, "arrow", 1.2)


def s_clash_paradox(ctx, t, d):  # "cannot both be real."
    T = 41.8 + t
    blue_bg(ctx)
    hit = ease((T - 41.85) / 0.35)
    spear_h(ctx, lerp(-400, -60, hit), 640, 520, 1.0)
    draw_shield(ctx, 560, 640, 150)
    if T > 42.2:
        k = T - 42.2
        for a in range(12):
            ang = a * math.pi / 6
            ln = 220 * min(1, k * 5)
            ctx.move_to(470 + math.cos(ang) * 30, 640 + math.sin(ang) * 30)
            ctx.line_to(470 + math.cos(ang) * ln, 640 + math.sin(ang) * ln)
        ctx.set_source_rgba(1, 0.9, 0.5, max(0, 1 - k))
        ctx.set_line_width(8)
        ctx.stroke()
        for a in range(6):  # cracks
            ang = a * 1.1
            ctx.move_to(560, 640)
            ctx.line_to(560 + math.cos(ang) * 140, 640 + math.sin(ang) * 140)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(4)
        ctx.stroke()
        label(ctx, "?!", 380, 380, 120, hexc("#f2c443"), fg=OUT, scale=pop(k - 0.1), tilt=0.06)


def s_iron(ctx, t, d):  # "So the blacksmith had made them both from ordinary iron"
    T = 43.1 + t
    terrace_base(ctx, T)
    for k in range(9):  # scrap pile
        ctx.save()
        ctx.translate(110 + (k % 3) * 30, 1080 - (k // 3) * 22)
        ctx.rotate(-0.3 + k * 0.17)
        ctx.rectangle(-80, -8, 160, 16)
        ctx.set_source_rgb(*hexc("#7d6a5a" if k % 2 else "#8a8f99"))
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.restore()
    label(ctx, "SCRAP", 140, 960, 34, hexc("#c9ced8"), fg=OUT, scale=pop(T - 43.3), tilt=-0.05)
    SM.draw(ctx, 420, 980, 1.45, keyed(T, [(0, "smirk"), (45.4, "smug")]), T,
            arms=("down", "show"), shadow=False)
    md.anvil(ctx, 420, 1200, 1.2)
    painted = clamp((T - 44.3) / 1.0)
    spear_h(ctx, 330, 960, 260, 0.7)
    ctx.save()
    ctx.rectangle(330, 900, 300 * painted, 120)
    ctx.clip()
    glow(ctx, 470, 960, 120, (1, 0.85, 0.3), 0.6)
    ctx.restore()
    if 44.3 < T < 45.4:  # paintbrush
        bx = 330 + 260 * painted
        ctx.move_to(bx, 940)
        ctx.line_to(bx + 60, 860)
        ctx.set_source_rgb(*hexc("#8a5a33"))
        ctx.set_line_width(10)
        ctx.stroke()
        ctx.rectangle(bx - 10, 930, 20, 22)
        ctx.set_source_rgb(*hexc("#f2c443"))
        ctx.fill()
    if T > 45.04:
        label(ctx, "ORDINARY IRON", 380, 380, 50, hexc("#c9ced8"), fg=OUT, scale=pop(T - 45.05), tilt=-0.05)


def s_nobody_first(ctx, t, d):  # "knowing neither king would risk being the first to test them"
    T = 46.0 + t
    kr_arms = ("belly", "point") if 46.5 < T < 47.4 else ("belly", "spear")
    kt_arms = ("point", "hip") if 47.2 < T < 48.1 else ("hold", "hip")
    expr = "grin" if T > 48.2 else "worried"
    field_kings(ctx, T, expr, expr, kr_arms=kr_arms, kt_arms=kt_arms, xr=250, xt=520, sweat=True)
    if 46.6 < T < 47.4:
        bubble(ctx, 210, 470, 210, 100, 230, 560, pop(T - 46.6))
        text(ctx, "YOU FIRST", 210, 470, 32, OUT, outline=False, scale=pop(T - 46.6))
    if 47.3 < T < 48.2:
        bubble(ctx, 560, 470, 210, 100, 540, 560, pop(T - 47.3))
        text(ctx, "NO, YOU!", 560, 470, 32, OUT, outline=False, scale=pop(T - 47.3))


def s_over(ctx, t, d):  # "And just like that, he ended a hundred years of war"
    T = 48.95 + t
    terrace_base(ctx, T)
    md.years_sign(ctx, 40, 1080, 1.05, "100")
    for x, col in ((110, "#e8574a"), (330, "#f2c443"), (560, "#ffffff")):
        md.helmet_flower(ctx, x, 1215, 0.95, col)
    stamp_label(ctx, "WAR OVER", 230, 720, T, 50.06)


def s_rich(ctx, t, d):  # "without a single battle."
    T = 51.45 + t
    terrace_base(ctx, T)
    rnd = random.Random(8)
    for i in range(60):  # pile of gold coins
        x = 380 + rnd.gauss(0, 120)
        y = 1150 - abs(rnd.gauss(0, 1)) * 60 - max(0, 160 - abs(x - 380)) * 1.2
        ctx.new_sub_path()
        ellipse(ctx, x, y, 26, 12)
        md.shade(ctx, hexc("#ffe08a"), hexc("#d6a23a"), y - 12, y + 12, 2)
    SM.draw(ctx, 380, 980, 1.35, "smug", T, arms=("bags", "bags"), bob=0.8, shadow=False)
    for k in range(5):
        ph = (T * 1.5 + k / 5) % 1
        glow(ctx, 260 + k * 60, 1050 - ph * 200, 30, (1, 0.95, 0.6), 0.8 * (1 - ph))


S = []


def shot(start, draw, keys, **kw):
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


shot(0.0, s_forge, push(0.0, 0.75, 1.5, 1.85, (360, 780), (360, 760)), dof=2)
shot(0.75, s_handoff, push(0.75, 1.5, 1.2, 1.4, (300, 720), (320, 700)), dof=2)
shot(1.5, s_spear, push(1.5, 1.95, 1.0, 1.2, C, (420, 620)))
shot(1.95, s_smash, push(1.95, 3.64, 1.0, 1.15, (380, 700), (420, 660)), shake=(0.52, 9))
shot(3.64, s_enemy, push(3.64, 4.7, 1.2, 1.9, (380, 700), (380, 560)), dutch=0.06, dof=3)
shot(4.7, s_shield, push(4.7, 5.2, 1.0, 1.2, C, C))
shot(5.2, s_bounce, push(5.2, 7.0, 1.0, 1.15, (380, 760), (380, 720)), shake=(0.35, 6))
shot(7.0, s_map, push(7.0, 7.75, 1.25, 1.0, (380, 700), C))
shot(7.75, s_clash, push(7.75, 8.55, 1.0, 1.4, (380, 800), (370, 820)), shake=(0.5, 8))
shot(8.55, s_years, push(8.55, 9.47, 1.6, 1.25, (290, 690), (330, 820)), dof=2)
shot(9.47, s_split, push(9.47, 11.14, 1.0, 1.1, C, (360, 660)))
shot(11.14, s_triumph, push(11.14, 12.9, 1.0, 1.25, (380, 760), (380, 640)), dof=2)
shot(12.9, s_march, push(12.9, 14.5, 1.0, 1.1, C, (360, 700)))
shot(14.5, s_aerial, push(14.5, 15.9, 0.95, 1.35, (360, 520), (360, 760)))
shot(15.9, s_kr_field, push(15.9, 17.38, 1.1, 1.7, (420, 700), (280, 620)), dof=2)
shot(17.38, s_kt_field, push(17.38, 18.85, 1.1, 1.7, (640, 700), (770, 620)), dof=2)
shot(18.85, s_strange, push(18.85, 20.6, 1.2, 0.85, (525, 700), (525, 640)))
shot(20.6, s_nobody, push(20.6, 21.7, 1.0, 1.2, (380, 760), (380, 700)), dof=2)
shot(21.7, s_week, push(21.7, 23.0, 1.0, 1.0, C, C), blur=False)
shot(23.0, s_bored, push(23.0, 25.3, 1.25, 1.25, (220, 760), (560, 760)), dof=2)
shot(25.3, s_metal, push(25.3, 26.85, 1.0, 1.45, (380, 760), (380, 620)), dof=2)
shot(26.85, s_moon, push(26.85, 27.45, 1.0, 1.1, C, (420, 600)))
shot(27.45, s_tents, push(27.45, 29.35, 1.0, 1.15, (380, 800), (380, 820)))
shot(29.35, s_arrive, push(29.35, 30.2, 1.0, 1.2, (380, 760), (380, 640)), dof=2)
shot(30.2, s_question, [(30.2, 1.2, (380, 700)), (30.63, 1.8, (200, 680), 0.35),
                        (31.26, 1.8, (560, 680), 0.35), (32.0, 1.15, (380, 700), 0.3)], dof=2)
shot(32.1, s_which, push(32.1, 33.7, 1.1, 1.35, (380, 560), (380, 460)), dof=2)
shot(33.7, s_reply, push(33.7, 36.1, 1.2, 2.2, (380, 700), (380, 540)), dof=3)
shot(36.1, s_findout, push(36.1, 37.4, 1.1, 1.3, (380, 640), (380, 600)), shake=(0.1, 6), dof=2)
shot(37.4, s_pierce, push(37.4, 40.15, 1.0, 1.15, C, (420, 640)), shake=(0.9, 7))
shot(40.15, s_never, push(40.15, 41.8, 1.0, 1.2, (380, 640), (360, 640)), shake=(0.45, 6))
shot(41.8, s_clash_paradox, push(41.8, 43.1, 1.0, 1.25, C, (470, 620)), shake=(0.4, 14))
shot(43.1, s_iron, [(43.1, 1.4, (200, 960)), (44.3, 1.6, (440, 860), 0.5), (45.04, 1.1, (380, 640), 0.4)], dof=2)
shot(46.0, s_nobody_first, [(46.0, 1.1, (380, 700)), (46.65, 1.7, (230, 560), 0.4),
                            (47.35, 1.7, (540, 560), 0.4), (48.3, 1.2, (385, 640), 0.4)], dof=2)
shot(48.95, s_over, push(48.95, 51.45, 1.0, 1.3, (360, 760), (300, 760)), shake=(1.11, 10), dof=2)
shot(51.45, s_rich, push(51.45, 52.85, 1.6, 1.0, (380, 700), (380, 760)), dof=2)
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

SFX = [
    *[(k * 0.45, "tick.wav", 0.8) for k in range(2)], (0.25, "sparkle.wav", 0.4),
    (1.15, "coin.wav", 0.8), (1.5, "sparkle.wav", 0.8),
    (2.47, "thud.wav", 1.0), (3.0, "thud.wav", 1.0), (3.1, "pop.wav", 0.6),
    (3.95, "sting_soft.wav", 0.7), (4.75, "sparkle.wav", 0.8),
    (5.55, "coin.wav", 0.9), (6.0, "coin.wav", 0.9), (6.5, "coin.wav", 0.9),
    (7.2, "page.wav", 0.8), (8.25, "thud.wav", 0.8), (8.3, "murmur.wav", 0.5),
    *[(8.6 + k * 0.06, "tick.wav", 0.4) for k in range(10)],
    (10.2, "pop.wav", 0.6), (10.4, "pop.wav", 0.6), (12.35, "sparkle.wav", 0.8), (12.35, "bell.wav", 0.5),
    *[(12.95 + k * 0.32, "step.wav", 0.8) for k in range(5)],
    (16.0, "sparkle.wav", 0.5), (17.5, "sparkle.wav", 0.5),
    *[(19.2 + k * 0.07, "pop.wav", 0.25) for k in range(10)],
    (20.7, "boing.wav", 0.4), *[(21.75 + k * 0.18, "tick.wav", 0.6) for k in range(7)],
    (23.15, "pop.wav", 0.7), (25.4, "sting_soft.wav", 0.5),
    (26.9, "bell.wav", 0.3), *[(28.6 + k * 0.2, "step.wav", 0.5) for k in range(4)],
    (29.75, "boing.wav", 0.6), (30.4, "pop.wav", 0.6), (32.15, "pop.wav", 0.7), (32.6, "pop.wav", 0.6),
    (34.4, "sparkle.wav", 0.4), (36.15, "sting.wav", 0.8),
    (38.2, "thud.wav", 0.9), (38.88, "thud.wav", 0.9), (39.56, "thud.wav", 0.9),
    (40.6, "coin.wav", 0.9), (41.0, "coin.wav", 0.9), (41.4, "coin.wav", 0.9),
    (42.2, "thud.wav", 1.0), (42.25, "sting_low.wav", 0.7),
    (43.3, "pop.wav", 0.5), (44.4, "sparkle.wav", 0.6), (45.05, "pop.wav", 0.7),
    (46.6, "pop.wav", 0.6), (47.3, "pop.wav", 0.6), (48.2, "boing.wav", 0.5),
    (50.06, "thud.wav", 1.0), (50.1, "bell.wav", 0.6),
    *[(51.5 + k * 0.25, "coin.wav", 0.6) for k in range(5)],
]

if __name__ == "__main__":
    import json
    import engine
    engine.LIPSYNC = False
    json.dump([{"time": round(t, 3), "file": f, "volume": v} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    render(SHOTS, TOTAL, sys.argv[1], grain=4, xfade=0.15)
