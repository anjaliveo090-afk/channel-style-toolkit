"""Story: gambling is illegal in Japan, yet there's a pachinko arcade on every corner.
Office/Japan style (style2 characters, office.py + arcade.py sets), rules from
visual_grammar.md (literal visual per phrase, new framing every ~1.6 s) and
sound_design.md (~1 SFX per second on visual events, no camera whoosh)."""
import math
import sys

import arcade as ar
import office as of
from engine import W, H, clamp, ease, glow, hexc, keyed, label, lerp, pop, render, text
from job_room import _bulb
from style2 import Char2, OUT

TOTAL = 55.30
C = (W / 2, H / 2)

YOU = Char2("#4fb3a9", hair="bowl", hair_col="#3a2a24", outfit="shirt")
MAN = Char2("#3a3550", hair="cap", hat_col="#1b1b25", outfit="suit", tie="#e8574a", shades=True)
POLICE = [Char2("#2f4a9a", hair="cap", hat_col="#1f2f6a", outfit="suit", tie="#1f2f6a", mustache=m)
          for m in ("#3a2a24", None)]
CLERK = Char2("#e8a0bf", hair="side", hair_col="#2d2328", outfit="apron")
OLD = Char2("#9d7fd6", hair="bald", hair_col="#9a9aa4", outfit="shirt", glasses=True)
CUST = [Char2(c, hair="bowl", hair_col=h, outfit="shirt") for c, h in (
    ("#e57373", "#2d2328"), ("#f2b84b", "#6d381c"), ("#88b3fb", "#2d2328"), ("#7cc08a", "#4a3a30"))]


def tint(ctx, rgb, a):
    if a > 0:
        ctx.set_source_rgba(*rgb, a)
        ctx.rectangle(-3000, -5000, 7000, 10000)
        ctx.fill()


def hold_pos(x, y, s, side=1):
    """World position of a standing Char2's hand in the 'hold' pose."""
    r = 64 * s
    return x + side * 0.25 * r, y - 1.78 * r


def bubble(ctx, x, y, w, h, tx, ty, sc):
    if sc <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.translate(-x, -y)
    for k, (dx, dy, rr) in enumerate(((0.0, 0.0, 1.0),)):
        pass
    for i, f in enumerate((0.25, 0.5)):
        ctx.new_sub_path()
        ctx.arc(lerp(tx, x, f), lerp(ty, y + h / 2, f), 10 + 8 * i, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(4)
        ctx.stroke()
    ar.rrect(ctx, x - w / 2, y - h / 2, w, h, h * 0.45)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def sound_lines(ctx, x, y, T, a=1.0):
    for k in range(3):
        ph = (T * 2 + k / 3) % 1
        for side in (-1, 1):
            ctx.new_sub_path()
            ctx.arc(x, y, 60 + ph * 140, -0.5 + (0 if side > 0 else math.pi), 0.5 + (0 if side > 0 else math.pi))
            ctx.set_source_rgba(1, 1, 1, a * (1 - ph))
            ctx.set_line_width(7)
            ctx.stroke()


def blue_room(ctx):
    of.room(ctx, -400, 1100, 230, 980, wall="#33467f", floor="#283259", ceil="#252a4f")
    of.pendant(ctx, 360, 230)
    glow(ctx, 360, 560, 520, (1, 0.8, 0.45), 0.35)


# ---------------------------------------------------------------- 0.0 "Gambling"
def s_hook(ctx, t, d):
    T = t
    ar.aisle(ctx, T)
    tint(ctx, (0.05, 0.02, 0.1), 0.4)
    ar.machine(ctx, 360, 1000, 1.7, T, seed=3)
    label(ctx, "GAMBLING", 360, 300, 56, hexc("#ff4f8b"), scale=pop(T - 0.1), tilt=-0.06)


# ---------------------------------------------------------------- 0.6 "is against the law in Japan"
def s_law(ctx, t, d):
    T = 0.6 + t
    blue_room(ctx)
    of.law_book(ctx, 360, 700, 1.25)
    ar.machine(ctx, 360, 640, 0.55, T, seed=1)
    ar.red_x(ctx, 360, 530, 120, (T - 1.12) / 0.25)
    if T > 1.47:
        label(ctx, "JAPAN", 360, 330, 54, hexc("#e8323a"), scale=pop(T - 1.47), tilt=0.08)


# ---------------------------------------------------------------- 1.98 "but somehow there's a gambling arcade"
def s_street(ctx, t, d):
    T = 1.98 + t
    on = 1.0 if T > 2.92 else 0.0
    ar.street(ctx, T, neon_on=on)
    YOU.draw(ctx, 300, 1560, 1.25, keyed(T, [(0, "neutral"), (2.95, "shock")]), T, look=0.3,
             arms=("down", "down") if T < 2.95 else ("shrug", "shrug"))


# ---------------------------------------------------------------- 3.82 "on practically every corner"
def s_aerial(ctx, t, d):
    T = 3.82 + t
    ar.city_aerial(ctx, T, [4.0, 4.25, 4.51, 4.66, 4.81, 4.95])


# ---------------------------------------------------------------- 5.29 "Step inside"
def s_enter(ctx, t, d):
    T = 5.29 + t
    ar.street(ctx, T, neon_on=1.0, doors=ease((T - 5.55) / 0.35))
    x = lerp(360, 150, ease((T - 5.29) / 0.85))
    s = lerp(1.6, 1.15, ease((T - 5.29) / 0.85))
    YOU.draw(ctx, x, lerp(1700, 1560, ease((T - 5.29) / 0.85)), s, "happy", T, pose="walk", walk_phase=T * 1.8)


# ---------------------------------------------------------------- 6.15 "and thousands of machines"
def s_aisle(ctx, t, d):
    ar.aisle(ctx, 6.15 + t)


# ---------------------------------------------------------------- 7.39 "are blinking and making noise"
def s_blink(ctx, t, d):
    T = 7.39 + t
    ar.aisle(ctx, T)
    tint(ctx, (0.05, 0.02, 0.1), 0.35)
    flash = 1.0 if int(T * 8) % 2 else 0.0
    for x, s, sd in ((150, 1.0, 1), (570, 1.0, 2), (360, 1.35, 4)):
        ar.machine(ctx, x, 1100 if s > 1 else 960, s, T * (2 if T > 7.45 else 1), seed=sd)
    glow(ctx, 360, 600, 500, (1, 0.5, 0.8), 0.25 * flash)
    if T > 8.07:
        sound_lines(ctx, 360, 520, T)
        label(ctx, "DING DING!", 360, 260, 48, hexc("#ffd84a"), fg=OUT, scale=pop(T - 8.1), tilt=0.06)


# ---------------------------------------------------------------- 8.78 "while customers walk around carrying buckets"
def s_customers(ctx, t, d):
    T = 8.78 + t
    ar.aisle(ctx, T)
    tint(ctx, (0.05, 0.02, 0.1), 0.25)
    for i, (x0, y, s) in enumerate(((-120, 1180, 1.1), (180, 1260, 1.25), (-420, 1230, 1.2), (480, 1170, 1.05))):
        x = x0 + (T - 8.78) * 170
        ch = CUST[i]
        ch.draw(ctx, x, y, s, "happy" if i % 2 else "grin", T + i, pose="walk", walk_phase=T * 1.7 + i * 0.3,
                arms=("hold", "hold"), look=0.5)
        if T > 10.2 or i < 2:
            hx, hy = hold_pos(x, y, s)
            ar.bucket(ctx, hx - 16 * s, hy + 70 * s, 0.65 * s, fill=0.95, seed=i)


# ---------------------------------------------------------------- 10.79 "overflowing with tiny metal balls"
def s_bucket(ctx, t, d):
    T = 10.79 + t
    ar.aisle(ctx, T)
    tint(ctx, (0.05, 0.02, 0.1), 0.45)
    ar.bucket(ctx, 360, 900, 2.0, fill=1.0, overflow=clamp((T - 10.85) / 0.4), T=T, seed=5)
    if T > 11.58:
        k = ease((T - 11.58) / 0.4)
        ar.ball(ctx, 470, 560, 26 + 30 * k)
        if T > 11.94:
            label(ctx, "METAL", 470, 440, 34, hexc("#c9ced8"), fg=OUT, scale=pop(T - 11.95), tilt=-0.05)


# ---------------------------------------------------------------- 13.12 "Police officers pass right by the entrance"
def s_police(ctx, t, d):
    T = 13.12 + t
    ar.street(ctx, T, neon_on=1.0)
    for i, ch in enumerate(POLICE):
        x = lerp(-250, 760, (T - 13.12) / 2.2) - i * 170
        look = -0.7 if 14.1 < T < 15.0 else 0.4
        ch.draw(ctx, x, 1560, 1.2, keyed(T, [(0, "neutral"), (14.2, "happy")]), T + i, pose="walk",
                walk_phase=T * 1.6 + i * 0.4, look=look, arms=("down", "wave") if 14.3 < T < 14.9 and i == 0 else ("down", "down"))


# ---------------------------------------------------------------- 15.33 "yet nobody ever gets arrested"
def s_arrest(ctx, t, d):
    T = 15.33 + t
    ar.street(ctx, T, neon_on=1.0)
    tint(ctx, (0.05, 0.02, 0.15), 0.3)
    POLICE[0].draw(ctx, 360, 1350, 1.6, keyed(T, [(0, "smirk"), (15.5, "happy")]), T, arms=("down", "show"))
    hx, hy = 360 + 1.31 * 64 * 1.6, 1350 - 3.18 * 64 * 1.6
    ar.handcuffs(ctx, hx, hy, 0.9, swing=math.sin(T * 6) * 0.4)
    ar.red_x(ctx, hx, hy + 60, 110, (T - 16.41) / 0.25)


# ---------------------------------------------------------------- 16.98 "So you decide to play"
def s_play(ctx, t, d):
    T = 16.98 + t
    ar.aisle(ctx, T)
    tint(ctx, (0.05, 0.02, 0.1), 0.3)
    ar.machine(ctx, 470, 1060, 1.35, T, seed=6)
    of.chair(ctx, 260, 1160, 1.0, col="#d6404a")
    YOU.draw(ctx, 230, 1160, 1.0, keyed(T, [(0, "neutral"), (17.37, "smirk"), (17.78, "grin")]), T,
             pose="sit", arms=("down", "point") if T > 17.75 else ("down", "down"), look=0.6)


# ---------------------------------------------------------------- 18.18 "win a whole bucket"
def s_win(ctx, t, d):
    T = 18.18 + t
    ar.aisle(ctx, T)
    tint(ctx, (0.05, 0.02, 0.1), 0.3)
    ar.machine(ctx, 360, 860, 1.4, T * 3, seed=7)
    text(ctx, "777", 360, 860 - 420 * 1.4 + 170 * 1.4, 44, hexc("#ffd84a"), outline=True, scale=pop(T - 18.2))
    fill = clamp((T - 18.25) / 0.6)
    for k in range(10):   # balls pouring out of the tray into the bucket
        ph = (T * 2.5 + k / 10) % 1
        ar.ball(ctx, 330 + math.sin(k) * 25, 760 + ph * 220, 9)
    ar.bucket(ctx, 360, 1200, 1.6, fill=fill, overflow=clamp((T - 18.8) / 0.3), T=T, seed=8)
    if T > 18.53:
        label(ctx, "WIN!", 360, 280, 70, hexc("#ffd84a"), fg=OUT, scale=pop(T - 18.53), tilt=-0.08)
    if T > 18.5:
        of.coins(ctx, T, -100, 820, -200, 1300, n=14)


# ---------------------------------------------------------------- 19.19 "head to the counter expecting your money"
def s_tocounter(ctx, t, d):
    T = 19.19 + t
    ar.shelves(ctx, T)
    ar.counter(ctx, 880)
    CLERK.draw(ctx, 560, 900, 0.95, "happy", T, arms=("down", "down"))
    x = lerp(-80, 240, ease((T - 19.19) / 1.0))
    YOU.draw(ctx, x, 1400, 1.45, "grin", T, pose="walk" if T < 20.2 else "stand", walk_phase=T * 1.8,
             arms=("hold", "hold"), look=0.6)
    hx, hy = hold_pos(x, 1400, 1.45)
    ar.bucket(ctx, hx - 23, hy + 100, 1.0, fill=1.0, seed=9)
    sc = pop(T - 20.08)
    bubble(ctx, 300, 520, 300, 170, x + 60, 1400 - 4.2 * 64 * 1.45, sc)
    if sc > 0:
        for k in range(3):
            ar.yen_note(ctx, 300 + (k - 1) * 50, 520 + (k - 1) * 10, 0.75 * sc, rot=(k - 1) * 0.25)


# ---------------------------------------------------------------- 21.05 "But there's a problem."
def s_problem(ctx, t, d):
    T = 21.05 + t
    ar.shelves(ctx, T)
    ar.counter(ctx, 880)
    tint(ctx, (0.15, 0.15, 0.3), 0.45 * ease((T - 21.1) / 0.2))
    YOU.draw(ctx, 360, 1300, 1.7, keyed(T, [(0, "grin"), (21.4, "shock")]), T, arms=("hold", "hold"))
    hx, hy = hold_pos(360, 1300, 1.7)
    ar.bucket(ctx, hx - 27, hy + 120, 1.15, fill=1.0, seed=9)
    if T > 21.41:
        label(ctx, "?!", 520, 380, 70, hexc("#e8323a"), scale=pop(T - 21.41), tilt=0.1)


# ---------------------------------------------------------------- 22.05 "They won't give you even one yen."
def s_noyen(ctx, t, d):
    T = 22.05 + t
    ar.shelves(ctx, T)
    ar.counter(ctx, 980)
    CLERK.draw(ctx, 360, 1000, 1.3, keyed(T, [(0, "smirk"), (22.4, "happy")]), T,
               arms=("down", "wag") if T > 22.17 else ("down", "down"))
    if T > 22.96:
        k = ease((T - 22.96) / 0.3)
        x, y = 360, 360
        glow(ctx, x, y, 120, (1, 0.9, 0.6), 0.4 * k)
        ctx.new_sub_path()
        ctx.arc(x, y, 60 * k, 0, 2 * math.pi)
        ar._shade_fill(ctx, hexc("#e9edf2"), hexc("#b9bec7"), y - 60, y + 60, 4)
        text(ctx, "¥1", x, y, 40 * k, hexc("#6d7380"), outline=False)
        ar.red_x(ctx, x, y, 90, (T - 23.28) / 0.25)


# ---------------------------------------------------------------- 24.09 "Instead, you can choose" + items
ITEMS = [(25.25, ar.candy, 170), (25.78, ar.chocolate, 360), (26.38, ar.shampoo, 550)]


def s_counter(ctx, t, d, T0):
    T = T0 + t
    ar.shelves(ctx, T)
    ar.counter(ctx, 880)
    CLERK.draw(ctx, 600, 900, 0.95, "happy", T, arms=("down", "show") if T > 24.7 else ("down", "down"))
    for t0, fn, x in ITEMS:
        if T > t0:
            sc = pop(T - t0)
            ctx.save()
            ctx.translate(x, 840)
            ctx.scale(sc, sc)
            fn(ctx, 0, 0, 0.9)
            ctx.restore()
    if T > 27.2:
        for k in range(4):
            ar.token(ctx, 120 + k * 55, 935, 0.6 * pop(T - 27.2 - k * 0.06), rot=k * 0.3)
    YOU.draw(ctx, 140, 1270, 1.1, keyed(T, [(0, "happy"), (25.3, "neutral"), (26.4, "worried")]), T,
             look=0.6, arms=("hold", "hold"))
    hx, hy = hold_pos(140, 1270, 1.1)
    ar.bucket(ctx, hx - 18, hy + 80, 0.75, fill=1.0, seed=9)


# ---------------------------------------------------------------- 27.2 "these strange little plastic tokens"
def s_tokens(ctx, t, d):
    T = 27.2 + t
    ar.counter(ctx, 600, col="#d9b07a")
    ctx.rectangle(-800, -800, 2400, 1400)
    ctx.set_source_rgb(*hexc("#fff1d6"))
    ctx.fill()
    ar.counter(ctx, 600, col="#d9b07a")
    ar.box(ctx, 140, 610, 440, 160, "#2b2f45", "#1b1e30", r=20)
    for k in range(5):
        ar.token(ctx, 220 + k * 70, 680 + (k % 2) * 25, 1.0 * pop(T - 27.3 - k * 0.08), rot=-0.3 + k * 0.17,
                 shine=clamp((T - 28.43) / 0.3) * (1 if k == 2 else 0.3))
    if T > 27.33:
        label(ctx, "???", 360, 400, 50, hexc("#9d7fd6"), scale=pop(T - 27.35), tilt=-0.05)
    if T > 28.0:
        label(ctx, "PLASTIC", 360, 900, 36, hexc("#ffd84a"), fg=OUT, scale=pop(T - 28.0), tilt=0.04)


# ---------------------------------------------------------------- 29.06 "Then you notice the man ahead of you"
def s_notice(ctx, t, d):
    T = 29.06 + t
    ar.shelves(ctx, T)
    ar.counter(ctx, 880)
    CLERK.draw(ctx, 600, 900, 0.95, "neutral", T)
    MAN.draw(ctx, 420, 1230, 1.1, "smirk", T, look=0.5, arms=("down", "down"))
    YOU.draw(ctx, 110, 1300, 1.15, keyed(T, [(0, "neutral"), (29.45, "worried")]), T, look=0.7, arms=("hold", "hold"))
    hx, hy = hold_pos(110, 1300, 1.15)
    ar.bucket(ctx, hx - 18, hy + 80, 0.8, fill=1.0, seed=9)
    if T > 29.43:
        label(ctx, "!", 160, 870, 50, hexc("#ffd84a"), fg=OUT, scale=pop(T - 29.43), tilt=0)


# ---------------------------------------------------------------- 30.54 "grabs the tokens and walks straight outside"
def s_grab(ctx, t, d):
    T = 30.54 + t
    ar.shelves(ctx, T, x1=1500)
    ar.counter(ctx, 880, x1=900)
    of.door(ctx, 1000, 1300, 200, 380, open_frac=clamp((T - 31.9) / 0.3))
    CLERK.draw(ctx, 600, 900, 0.95, "neutral", T)
    walking = T > 31.52
    x = 420 if not walking else lerp(420, 1150, ease((T - 31.52) / 1.0))
    MAN.draw(ctx, x, 1230, 1.1, "grin" if T > 30.6 else "smirk", T, pose="walk" if walking else "stand",
             walk_phase=T * 1.8, look=0.6, arms=("hold", "down") if T > 30.54 else ("down", "down"))
    if T > 30.54:
        hx, hy = hold_pos(x, 1230, 1.1, -1)
        for k in range(3):
            ar.token(ctx, hx + k * 8, hy - k * 12, 0.5, rot=k * 0.4)
    if T > 32.21:
        label(ctx, "EXIT", 1100, 870, 30, hexc("#4fd16a"), scale=1.0, tilt=0)


# ---------------------------------------------------------------- 32.86 "Curious, you follow him around the corner"
def s_follow(ctx, t, d):
    T = 32.86 + t
    ar.alley(ctx, T)
    MAN.draw(ctx, lerp(440, 600, (T - 32.86) / 2.0), 1180, 0.95, "smirk", T, pose="walk", walk_phase=T * 1.6, look=0.4)
    # the corner of a building in the foreground; YOU peeks around it
    peek = ease((T - 33.5) / 0.4)
    YOU.draw(ctx, lerp(-110, 110, peek), 1300, 1.3, keyed(T, [(0, "worried"), (33.6, "smirk")]), T, look=0.7,
             lean=0.2 * peek)
    ar.box(ctx, -600, -900, 560, 2600, "#3e3450", "#2a2238", r=0)
    if T > 32.95:
        for k in range(3):
            label(ctx, "?", 220 + k * 60, 520 - k * 40, 40 - k * 4, hexc("#ffd84a"), fg=OUT, scale=pop(T - 32.95 - k * 0.1), tilt=0.1)


# ---------------------------------------------------------------- 34.86 "a tiny window hidden in a wall"
def s_window(ctx, t, d):
    T = 34.86 + t
    ar.alley(ctx, T)
    ar.hatch(ctx, 360, 700, 1.0)
    if T > 35.6:
        label(ctx, "TINY", 520, 560, 34, hexc("#ffd84a"), fg=OUT, scale=pop(T - 35.6), tilt=0.1)


# ---------------------------------------------------------------- 36.71 "without a single sign."
def s_nosign(ctx, t, d):
    T = 36.71 + t
    ar.alley(ctx, T)
    ar.hatch(ctx, 360, 760, 1.0)
    ar.box(ctx, 180, 380, 360, 150, "#d9d6e4", "#b9b6c8", r=10)   # the empty sign board
    text(ctx, "?", 360, 455, 80, hexc("#9a96ad"), outline=False, scale=pop(T - 37.0))
    ar.red_x(ctx, 360, 455, 60, (T - 37.38) / 0.25, w=16)


# ---------------------------------------------------------------- 37.73 "Here's the trick."
def s_trick(ctx, t, d):
    T = 37.73 + t
    ar.alley(ctx, T, lamp=1.3)
    YOU.draw(ctx, 360, 1450, 1.9, keyed(T, [(0, "neutral"), (38.45, "smirk")]), T, arms=("down", "point"))
    _bulb(ctx, 360, 560, T - 38.5)


# ---------------------------------------------------------------- 39.05 "That window technically belongs to a completely different business"
def s_diagram(ctx, t, d):
    T = 39.05 + t
    blue_room(ctx)
    ctx.rectangle(-800, 1000, 2400, 800)
    ctx.set_source_rgb(*hexc("#283259"))
    ctx.fill()
    # big arcade building (left) and the tiny shop (right)
    ar.box(ctx, 20, 460, 420, 540, "#5e3f6e", "#3e2a4e", r=8)
    ar.neon_text(ctx, "ARCADE", 230, 540, 44, "#ff4f8b", 1.0, T)
    ar.machine(ctx, 150, 980, 0.55, T, seed=2)
    ar.machine(ctx, 310, 980, 0.55, T, seed=3)
    s_in = pop(T - 40.2)
    ar.box(ctx, 480, 760, 220, 240, "#4f5a7a", "#3a4462", r=8)
    ar.hatch(ctx, 590, 870, 0.5)
    # dashed property line between them, drawn on "belongs"
    k = clamp((T - 40.22) / 0.5)
    for i in range(int(14 * k)):
        ctx.rectangle(458, 380 + i * 50, 8, 30)
    ctx.set_source_rgb(*hexc("#ffd84a"))
    ctx.fill()
    if T > 41.38:
        label(ctx, "DIFFERENT", 590, 640, 30, hexc("#4fe3ff"), fg=OUT, scale=pop(T - 41.38), tilt=0.06)
        label(ctx, "COMPANY", 590, 700, 30, hexc("#4fe3ff"), fg=OUT, scale=pop(T - 41.5), tilt=0.06)
    if T > 39.7:
        label(ctx, "OWNER A", 230, 410, 28, hexc("#ff8fc0"), fg=OUT, scale=pop(T - 39.7), tilt=-0.05)
    if T > 40.81:
        label(ctx, "OWNER B", 590, 580, 28, hexc("#88b3fb"), fg=OUT, scale=pop(T - 40.81), tilt=-0.05)


# ---------------------------------------------------------------- 42.34 "one that just happens to purchase those exact tokens"
def s_buys(ctx, t, d):
    T = 42.34 + t
    ar.alley(ctx, T)
    ar.box(ctx, 130, 430, 460, 420, "#ffcf7a", "#f0a85a", r=6)   # inside the window, close
    glow(ctx, 360, 640, 360, (1, 0.85, 0.5), 0.5)
    OLD.draw(ctx, 360, 960, 1.05, keyed(T, [(0, "neutral"), (42.99, "smirk"), (44.1, "happy")]), T,
             look=(-0.6 if 42.99 < T < 43.48 else 0.0), arms=("down", "show") if T > 43.48 else ("down", "down"))
    ar.box(ctx, 90, 850, 540, 60, "#8a8f9a", "#5a5f6a", r=6)
    ar.box(ctx, 60, 380, 600, 60, "#3a3346", "#2a2436", r=4)
    if 42.99 < T < 43.48:
        text(ctx, "♪", 520, 520, 46, (1, 1, 1), outline=True)
    if T > 43.48:
        label(ctx, "WE BUY", 360, 300, 44, hexc("#4fd16a"), fg=OUT, scale=pop(T - 43.48), tilt=-0.05)
    if T > 44.09:
        hx, hy = 360 + 1.31 * 64 * 1.05, 960 - 3.18 * 64 * 1.05
        ar.token(ctx, hx, hy - 20, 1.1, shine=clamp((T - 44.5) / 0.3))


# ---------------------------------------------------------------- 45.12 "So the arcade isn't paying out cash"
def s_notcash(ctx, t, d):
    T = 45.12 + t
    ar.shelves(ctx, T)
    ar.counter(ctx, 880)
    CLERK.draw(ctx, 360, 900, 1.0, keyed(T, [(0, "neutral"), (45.9, "smirk")]), T, arms=("down", "down"))
    if T > 46.03:
        ar.cash_stack(ctx, 360, 520, 1.1 * pop(T - 46.03))
        ar.red_x(ctx, 360, 470, 110, (T - 46.47) / 0.25)


# ---------------------------------------------------------------- 47.02 "it's simply handing out prizes"
def s_prizes(ctx, t, d):
    T = 47.02 + t
    ar.shelves(ctx, T)
    ar.counter(ctx, 880)
    CLERK.draw(ctx, 470, 900, 1.0, "happy", T, arms=("down", "point") if T > 47.54 else ("down", "down"))
    YOU.draw(ctx, 170, 1270, 1.1, "neutral", T, look=0.6, arms=("down", "show") if T > 47.9 else ("down", "down"))
    if T > 47.54:
        k = ease((T - 47.54) / 0.4)
        ar.shampoo(ctx, lerp(560, 330, k), lerp(820, 780, k), 0.8)
    ar.check(ctx, 360, 380, 70, (T - 48.0) / 0.3)
    if T > 48.0:
        label(ctx, "PRIZES", 360, 260, 40, hexc("#ffd84a"), fg=OUT, scale=pop(T - 48.0), tilt=-0.04)


# ---------------------------------------------------------------- 48.62 "and the other shop, it's just buying them"
def s_buying(ctx, t, d):
    T = 48.62 + t
    ar.alley(ctx, T)
    ar.hatch(ctx, 360, 640, 1.2, open_k=0.9)
    # token goes in, cash comes out
    k1 = clamp((T - 49.5) / 0.5)
    ar.token(ctx, lerp(150, 330, ease(k1)), 620, 0.9)
    if T > 50.05:
        k2 = ease((T - 50.05) / 0.45)
        ar.yen_note(ctx, lerp(380, 560, k2), 760, 0.8, rot=-0.1)
    ar.check(ctx, 360, 360, 60, (T - 50.48) / 0.3)
    if T > 48.9:
        label(ctx, "OTHER SHOP", 360, 250, 38, hexc("#88b3fb"), fg=OUT, scale=pop(T - 48.9), tilt=0.04)


# ---------------------------------------------------------------- 51.15 "The man pushes his tokens through the window"
def s_push(ctx, t, d):
    T = 51.15 + t
    ar.alley(ctx, T)
    ar.hatch(ctx, 480, 640, 1.5, open_k=0.85)
    k = ease((T - 51.48) / 0.8)
    hx = lerp(-120, 330, k)
    for i in range(4):
        ar.token(ctx, hx + 70 + i * 22, 735 - i * 6, 0.75, rot=0.1 * i)
    ar.hand(ctx, hx, 760, 1.2, flip=1, col="#fce7d6")


# ---------------------------------------------------------------- 53.12 "and a hand pushes back a stack of cash."
def s_cash(ctx, t, d):
    T = 53.12 + t
    ar.alley(ctx, T)
    ar.hatch(ctx, 480, 640, 1.5, open_k=0.85)
    k = ease((T - 53.5) / 0.6)
    hx = lerp(820, 560, k)
    ar.cash_stack(ctx, hx - 130, 760, 0.9, n=int(3 + 7 * clamp((T - 54.2) / 0.4)))
    ar.hand(ctx, hx, 760, 1.2, flip=-1, col="#e9c9a8")
    if T > 54.23:
        MAN.draw(ctx, 150, 1350, 1.4, "grin", T, arms=("down", "up"))
        of.coins(ctx, T, -100, 820, -200, 1300, n=10)


S = []


def shot(start, draw, keys, **kw):
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def push(t0, t1, z0, z1, c0, c1):
    return [(t0, z0, c0), (t1, z1, c1, max(0.2, t1 - t0))]


shot(0.0, s_hook, push(0.0, 0.6, 1.0, 1.3, (360, 640), (360, 600)), dof=2)
shot(0.6, s_law, [(0.6, 1.0, (360, 640)), (1.12, 1.5, (360, 560), 0.3), (1.47, 1.2, (360, 500), 0.3)])
shot(1.98, s_street, [(1.98, 0.85, (300, 1250)), (2.92, 1.0, (140, 1100), 0.45), (3.4, 1.2, (160, 1080), 0.4)])
shot(3.82, s_aerial, push(3.82, 5.29, 1.6, 0.8, (500, 500), (450, 550)))
shot(5.29, s_enter, push(5.29, 6.15, 0.9, 1.5, (250, 1150), (130, 1300)))
shot(6.15, s_aisle, push(6.15, 7.39, 1.0, 2.1, (360, 700), (360, 580)), dof=2)
shot(7.39, s_blink, [(7.39, 1.0, (360, 800)), (7.45, 1.5, (360, 700), 0.3), (8.07, 1.15, (360, 640), 0.4)], shake=(0.68, 6))
shot(8.78, s_customers, push(8.78, 10.79, 1.2, 1.4, (120, 900), (420, 900)), dof=2)
shot(10.79, s_bucket, [(10.79, 1.0, (360, 760)), (11.58, 1.6, (440, 620), 0.4), (12.22, 1.8, (460, 580), 0.6)], dof=3)
shot(13.12, s_police, [(13.12, 0.85, (300, 1050)), (13.91, 1.15, (420, 1150), 0.5), (14.8, 0.9, (300, 1000), 0.5)])
shot(15.33, s_arrest, [(15.33, 1.0, (360, 880)), (15.51, 1.25, (420, 820), 0.3), (16.41, 1.3, (430, 800), 0.35)], dof=2)
shot(16.98, s_play, push(16.98, 18.18, 1.0, 1.4, (360, 780), (310, 760)), dof=2)
shot(18.18, s_win, [(18.18, 1.0, (360, 760)), (18.53, 1.15, (360, 720), 0.3), (18.77, 1.3, (360, 900), 0.4)],
     shake=(0.35, 8))
shot(19.19, s_tocounter, push(19.19, 21.05, 1.2, 1.05, (200, 1000), (280, 860)))
shot(21.05, s_problem, [(21.05, 1.0, (360, 820)), (21.41, 1.4, (380, 700), 0.2)], shake=(0.36, 10))
shot(22.05, s_noyen, [(22.05, 1.1, (360, 760)), (22.96, 1.3, (360, 560), 0.35)])
shot(24.09, lambda ctx, t, d: s_counter(ctx, t, d, 24.09),
     [(24.09, 0.95, (360, 820)), (25.25, 1.6, (200, 820), 0.35), (25.78, 1.6, (360, 820), 0.3),
      (26.38, 1.6, (540, 820), 0.3), (27.08, 1.05, (360, 860), 0.25)])
shot(27.2, s_tokens, push(27.2, 29.06, 1.1, 1.6, (360, 700), (360, 680)), dof=3)
shot(29.06, s_notice, [(29.06, 1.0, (260, 860)), (29.82, 1.5, (420, 760), 0.45)], dof=2)
shot(30.54, s_grab, [(30.54, 1.3, (420, 780)), (31.65, 1.0, (700, 860), 0.6), (32.21, 1.0, (950, 860), 0.5)], dof=2)
shot(32.86, s_follow, [(32.86, 1.0, (360, 860)), (33.63, 1.3, (220, 920), 0.4), (34.42, 1.3, (500, 860), 0.4)])
shot(34.86, s_window, push(34.86, 36.71, 0.9, 1.8, (360, 640), (360, 700)), dof=2)
shot(36.71, s_nosign, push(36.71, 37.73, 1.3, 1.7, (360, 560), (360, 480)), dof=2)
shot(37.73, s_trick, [(37.73, 1.0, (360, 860)), (38.43, 1.2, (360, 840), 0.3)])
shot(39.05, s_diagram, [(39.05, 0.95, (360, 700)), (39.7, 1.3, (230, 620), 0.4), (40.81, 1.4, (580, 760), 0.45),
                        (41.78, 1.2, (450, 700), 0.4)])
shot(42.34, s_buys, [(42.34, 1.0, (360, 700)), (43.48, 1.3, (360, 560), 0.35), (44.51, 1.5, (440, 600), 0.4)])
shot(45.12, s_notcash, [(45.12, 1.0, (360, 760)), (46.03, 1.35, (360, 560), 0.35)], dof=2)
shot(47.02, s_prizes, [(47.02, 1.0, (360, 800)), (47.54, 1.3, (420, 760), 0.35), (48.0, 1.15, (360, 600), 0.3)], dof=2)
shot(48.62, s_buying, [(48.62, 0.95, (360, 600)), (49.5, 1.35, (300, 640), 0.4), (50.05, 1.35, (480, 700), 0.4)], dof=2)
shot(51.15, s_push, push(51.15, 53.12, 1.0, 1.45, (360, 700), (420, 720)), dof=2)
shot(53.12, s_cash, [(53.12, 1.4, (520, 740)), (53.92, 1.6, (450, 720), 0.4), (54.23, 1.0, (360, 760), 0.5)], dof=2)
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ~1 SFX per second on visual events (sound_design.md); no camera whoosh
SFX = [
    (0.1, "pop.wav", 0.7), (0.3, "tick.wav", 0.5), (1.12, "thud.wav", 1.0), (1.47, "pop.wav", 0.8),
    (2.92, "tick.wav", 0.7), (2.95, "sparkle.wav", 0.8), (3.0, "pop.wav", 0.5),
    *[(t0, "tick.wav", 0.6) for t0 in (4.0, 4.25, 4.51, 4.66, 4.81, 4.95)],
    (5.55, "page.wav", 0.6), *[(5.4 + k * 0.28, "step.wav", 0.5) for k in range(3)],
    (6.4, "murmur.wav", 0.5), (6.97, "sparkle.wav", 0.5),
    *[(7.45 + k * 0.25, "tick.wav", 0.5) for k in range(4)], (8.1, "bell.wav", 0.7), (8.42, "bell.wav", 0.6),
    *[(8.9 + k * 0.32, "step.wav", 0.5) for k in range(6)], (10.39, "pop.wav", 0.6),
    *[(10.9 + k * 0.12, "tick.wav", 0.5) for k in range(6)], (11.6, "pop.wav", 0.7), (11.95, "coin.wav", 0.7),
    *[(13.2 + k * 0.36, "step.wav", 0.6) for k in range(6)], (14.3, "pop.wav", 0.5),
    (15.5, "boing.wav", 0.5), (15.9, "tick.wav", 0.5), (16.41, "thud.wav", 0.9),
    (17.4, "tick.wav", 0.6), (17.78, "pop.wav", 0.7),
    (18.2, "bell.wav", 0.8), *[(18.25 + k * 0.08, "coin.wav", 0.4) for k in range(8)], (18.53, "sparkle.wav", 0.8),
    *[(19.25 + k * 0.3, "step.wav", 0.5) for k in range(3)], (20.08, "pop.wav", 0.7), (20.63, "coin.wav", 0.6),
    (21.1, "sting_low.wav", 0.8), (21.41, "boing.wav", 0.6),
    (22.2, "tick.wav", 0.6), (22.5, "tick.wav", 0.6), (22.96, "coin.wav", 0.7), (23.28, "thud.wav", 0.9),
    (24.7, "pop.wav", 0.5), (25.25, "pop.wav", 0.8), (25.78, "pop.wav", 0.8), (26.38, "pop.wav", 0.8),
    *[(27.3 + k * 0.08, "tick.wav", 0.5) for k in range(5)], (27.35, "boing.wav", 0.4), (28.0, "pop.wav", 0.6),
    (28.43, "sparkle.wav", 0.7),
    (29.43, "pop.wav", 0.7), (29.82, "tick.wav", 0.5), (30.6, "coin.wav", 0.6),
    *[(31.55 + k * 0.3, "step.wav", 0.5) for k in range(3)], (31.95, "page.wav", 0.6), (32.21, "pop.wav", 0.5),
    (32.95, "pop.wav", 0.4), (33.05, "pop.wav", 0.4), (33.15, "pop.wav", 0.4),
    *[(33.7 + k * 0.4, "step.wav", 0.4) for k in range(3)],
    (35.6, "pop.wav", 0.7), (36.0, "tick.wav", 0.5), (37.0, "pop.wav", 0.5), (37.38, "thud.wav", 0.8),
    (38.5, "bell.wav", 0.8),
    (39.7, "pop.wav", 0.6), (40.22, "tick.wav", 0.6), (40.81, "pop.wav", 0.6), (41.38, "pop.wav", 0.7),
    (41.5, "pop.wav", 0.6), (42.99, "boing.wav", 0.4), (43.48, "pop.wav", 0.8), (44.1, "coin.wav", 0.6),
    (44.5, "sparkle.wav", 0.6),
    (46.03, "coin.wav", 0.6), (46.47, "thud.wav", 0.9), (47.6, "tick.wav", 0.6), (48.0, "bell.wav", 0.7),
    (48.9, "pop.wav", 0.6), (49.6, "tick.wav", 0.6), (50.05, "coin.wav", 0.7), (50.48, "bell.wav", 0.6),
    (51.5, "tick.wav", 0.5), (51.9, "tick.wav", 0.5), (52.35, "tick.wav", 0.6), (52.6, "page.wav", 0.5),
    (53.6, "page.wav", 0.6), *[(54.2 + k * 0.08, "page.wav", 0.4) for k in range(5)], (54.67, "sting.wav", 0.9),
    (54.7, "coin.wav", 0.6),
]

if __name__ == "__main__":
    import json
    import engine
    engine.LIPSYNC = False
    json.dump([{"time": round(t, 3), "file": f, "volume": v} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    kw = {}
    if len(sys.argv) > 4:
        kw["frames"] = (int(sys.argv[3]), int(sys.argv[4]))
    render(SHOTS, TOTAL, sys.argv[1], grain=4, xfade=0.2, **kw)
