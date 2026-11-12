"""Story: what if your mom became the owner of the block game (7 days of mom rules).
Office/home style (style2 characters, office.py + home.py sets), literal visual per phrase
(visual_grammar.md 10-11), ~1 SFX per second on visual events (sound_design.md)."""
import math
import sys

import home as hm
import office as of
from arcade import check, red_x
from engine import W, H, clamp, ease, glow, hexc, keyed, label, lerp, pop, render, text
from job_room import _bulb
from style2 import Char2, OUT

TOTAL = 50.36
C = (W / 2, H / 2)

MOM = Char2("#9d7fd6", hair="side", hair_col="#6d381c", outfit="apron")
KID = Char2("#4fb3a9", hair="bowl", hair_col="#8a4a20", outfit="shirt")
FRIENDS = [("#f2b84b", "#2b45a6", None), ("#4fb3a9", "#3a3f55", None), ("#e57373", "#2b45a6", None)]


def tint(ctx, rgb, a):
    if a > 0:
        ctx.set_source_rgba(*rgb, a)
        ctx.rectangle(-3000, -5000, 7000, 10000)
        ctx.fill()


def mom(ctx, x, y, s, expr, T, **kw):
    """Mom = style2 character with a hair bun drawn behind the head."""
    r = 64 * s
    ctx.new_sub_path()
    ctx.arc(x, y - 4.75 * r, 0.4 * r, 0, 2 * math.pi)
    hm._shade_fill(ctx, hexc("#8a4a20"), hexc("#6d381c"), y - 5.2 * r, y - 4.4 * r, 0.075 * r)
    MOM.draw(ctx, x, y, s, expr, T, **kw)


def show_hand(x, y, s, side=1):
    r = 64 * s
    return x + side * 1.31 * r, y - 3.18 * r


def bubble(ctx, x, y, w, h, tx, ty, sc):
    if sc <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.translate(-x, -y)
    for i, f in enumerate((0.3, 0.6)):
        ctx.new_sub_path()
        ctx.arc(lerp(tx, x, f), lerp(ty, y + h / 2, f), 10 + 8 * i, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(4)
        ctx.stroke()
    hm.rrect(ctx, x - w / 2, y - h / 2, w, h, h * 0.45)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def zzz(ctx, x, y, T):
    for k in range(3):
        ph = (T * 0.8 + k / 3) % 1
        text(ctx, "Z", x + ph * 60 + k * 8, y - ph * 110, 30 + ph * 26, (1, 1, 1), outline=True)


def kid_at_pc(ctx, T, expr, night=0.0, screen="game", arms=("down", "down"), pc_on=1.0, s=1.1):
    """Bedroom: kid on a chair facing us, the PC on the desk beside him."""
    hm.bedroom(ctx, T, night=0.0)
    of.desk(ctx, 520, 960, 340)
    hm.pc(ctx, 520, 940, 0.9, T, screen=screen, on=pc_on)
    of.chair(ctx, 250, 1180, 1.05, col="#e8574a")
    KID.draw(ctx, 250, 1180, s, expr, T, pose="sit", arms=arms, look=0.5)
    tint(ctx, (0.04, 0.05, 0.18), 0.55 * night)
    if night and pc_on:
        glow(ctx, 520, 800, 380, (0.5, 0.75, 1), 0.35)


# ---------------------------------------------------------------- 0.0 "What if your mom"
def s_hi(ctx, t, d):
    T = t
    hm.bedroom(ctx, T)
    mom(ctx, 360, 1300, 1.5, "happy", T, arms=("down", "wave"))


# ---------------------------------------------------------------- 0.76 "became the owner of the game?"
def s_owner(ctx, t, d):
    T = 0.76 + t
    hm.owner_office(ctx, T)
    of.chair(ctx, 360, 1130, 1.5, col="#2a2e40")
    mom(ctx, 360, 1130, 1.2, keyed(T, [(0, "neutral"), (1.2, "grin")]), T, arms=("down", "down"))
    hm.big_desk(ctx, 1000, plate="OWNER", plate_k=pop(T - 1.19))
    if T > 1.5:   # the crown drops onto her head
        k = ease((T - 1.5) / 0.3)
        hm.crown(ctx, 360, lerp(-100, 1130 - 4.55 * 64 * 1.2, k), 0.8)


# ---------------------------------------------------------------- day cards
def day_shot(n, t_start, t_tear):
    return lambda ctx, t, d: hm.day_card(ctx, t_start + t, n, t_tear)


# ---------------------------------------------------------------- 3.11 "every single server gets shut down"
OFF1 = [3.72 + k * 0.07 for k in range(12)]


def s_servers(ctx, t, d):
    T = 3.11 + t
    hm.server_wall(ctx, T, OFF1)
    if T > 4.24:
        label(ctx, "SHUT DOWN", 360, 200, 52, hexc("#e8323a"), scale=pop(T - 4.24), tilt=-0.05)


# ---------------------------------------------------------------- 4.83 "at exactly 8pm."
def s_clock(ctx, t, d):
    T = 4.83 + t
    hm.bedroom(ctx, T, night=0.6)
    k = ease((T - 4.9) / 0.6)
    of.wall_clock(ctx, 360, 620, 190, lerp(5.5, 8, k), lerp(30, 0, k) if k < 1 else 0)
    if T > 5.51:
        label(ctx, "8:00 PM", 360, 920, 64, hexc("#e8574a"), scale=pop(T - 5.51), tilt=-0.05)


# ---------------------------------------------------------------- 6.27 "Why?"
def s_why(ctx, t, d):
    T = 6.27 + t
    kid_at_pc(ctx, T, "shock", screen="off", pc_on=0.0, arms=("shrug", "shrug"))
    label(ctx, "WHY?!", 250, 470, 56, hexc("#ffd84a"), fg=OUT, scale=pop(T - 6.3), tilt=0.08)


# ---------------------------------------------------------------- 6.76 "Because it's bedtime."
def s_bedtime(ctx, t, d):
    T = 6.76 + t
    hm.bedroom(ctx, T, night=0.5)
    of.wall_clock(ctx, 560, 420, 80, 8, 0)
    hm.bed(ctx, 560, 1150, 1.0, blanket="#4f8bff")
    mom(ctx, 230, 1150, 1.15, keyed(T, [(0, "smirk"), (7.21, "happy")]), T, arms=("down", "point"))
    if T > 7.21:
        label(ctx, "BEDTIME!", 360, 260, 60, hexc("#9d7fd6"), scale=pop(T - 7.21), tilt=-0.06)


# ---------------------------------------------------------------- 7.89 "No excuses."
def s_noexcuse(ctx, t, d):
    T = 7.89 + t
    hm.bedroom(ctx, T, night=0.5)
    mom(ctx, 400, 1420, 1.7, "angry", T, arms=("down", "wag"))
    bubble(ctx, 200, 760, 300, 130, 300, 930, pop(T - 7.9))
    if T > 7.9:
        text(ctx, "5 MORE MIN!", 200, 760, 32, OUT, outline=False, scale=pop(T - 7.9))
    red_x(ctx, 200, 760, 110, (T - 8.16) / 0.25)


# ---------------------------------------------------------------- 8.95 "Go to sleep."
def s_sleep(ctx, t, d):
    T = 8.95 + t
    hm.bedroom(ctx, T, night=1.0, light_on=False)
    hm.bed(ctx, 380, 1150, 1.4, blanket="#4f8bff")
    KID.draw(ctx, 330, 1150 - 110 * 1.4 + 160, 0.85, "neutral", T, shadow=False, bob=0.2) if False else None
    # kid tucked in: only the head on the pillow
    ctx.save()
    ctx.translate(250, 940)
    ctx.rotate(-0.25)
    ctx.translate(-250, -940)
    KID.draw(ctx, 250, 1180, 0.85, "neutral", T, shadow=False, bob=0.1)
    ctx.restore()
    hm.box(ctx, 300, 960, 330, 140, "#4f8bff", "#2f5fd0", r=26)
    zzz(ctx, 300, 760, T)
    if T > 9.18:
        label(ctx, "SLEEP.", 360, 580, 56, hexc("#3a3f55"), scale=pop(T - 9.18), tilt=0.05)


# ---------------------------------------------------------------- 10.56 "she turns every obby into"
def s_obby(ctx, t, d):
    T = 10.56 + t
    plats = hm.obby(ctx, T, homework=0.0)
    # the avatar hops from platform to platform
    ph = (T - 10.56) / 0.6
    i = min(len(plats) - 2, int(ph))
    f = ph - int(ph)
    (x0, y0, w0), (x1, y1, w1) = plats[i], plats[i + 1]
    ax = lerp(x0 + w0 / 2, x1 + w1 / 2, f)
    ay = lerp(y0, y1, f) - math.sin(f * math.pi) * 140
    hm.avatar(ctx, ax, ay, 0.8, shirt="#e8574a", hair="curly", t=T, walk=T * 2)
    if T > 11.44:
        label(ctx, "OBBY", 360, 280, 56, hexc("#5dd06a"), fg=OUT, scale=pop(T - 11.44), tilt=-0.05)


# ---------------------------------------------------------------- 11.79 "a school assignment."
def s_assignment(ctx, t, d):
    T = 11.79 + t
    hw = ease((T - 11.8) / 0.5)
    hm.obby(ctx, T, homework=hw)
    for k in range(10):   # magic sparkles of the transformation
        ph = (T * 1.5 + k / 10) % 1
        glow(ctx, 100 + k * 70, 1000 - ph * 600, 30, (1, 0.95, 0.6), 0.6 * (1 - ph))
    if T > 12.14:
        hm.box(ctx, 110, 220, 500, 150, "#2f5a3a", "#1f3f28", r=10)
        text(ctx, "ASSIGNMENT", 360, 295, 50, (1, 1, 1), outline=False, scale=pop(T - 12.14))


# ---------------------------------------------------------------- 13.07 "Wait, what?"
def s_waitwhat(ctx, t, d):
    T = 13.07 + t
    kid_at_pc(ctx, T, keyed(T, [(0, "neutral"), (13.2, "shock")]), s=1.15)
    label(ctx, "?!", 250, 450, 70, hexc("#e8574a"), scale=pop(T - 13.46), tilt=0.1)


# ---------------------------------------------------------------- 13.92 "You can't even jump unless"
def s_nojump(ctx, t, d):
    T = 13.92 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1000)
    hm.block(ctx, 430, 760, 220, 240)
    k = T - 14.49
    jump = 0.0 if k < 0 else max(0.0, math.sin(min(k, 0.5) / 0.5 * math.pi)) * 90
    hm.avatar(ctx, 250, 1000, 1.1, shirt="#e8574a", hair="curly", expr="shock" if k > 0.25 else "happy", t=T,
              jump=jump)
    # a padlocked bar over the block stops the jump
    if T > 14.25:
        a = clamp((T - 14.25) / 0.2)
        ctx.rectangle(400, 560, 20, 440)
        ctx.set_source_rgba(0.9, 0.2, 0.2, 0.8 * a)
        ctx.fill()
        hm.box(ctx, 360, 600, 100, 80, "#f2b84b", "#d6a23a", r=10)
        ctx.new_sub_path()
        ctx.arc(410, 600, 30, math.pi, 2 * math.pi)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(12)
        ctx.stroke()
    if T > 14.83:
        label(ctx, "LOCKED", 410, 470, 44, hexc("#e8323a"), scale=pop(T - 14.83), tilt=0.05)


# ---------------------------------------------------------------- 15.09 "you've finished your math homework."
def s_math(ctx, t, d):
    T = 15.09 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1000)
    tint(ctx, (0.1, 0.1, 0.2), 0.35)
    sc = pop(T - 15.2)
    if sc > 0:
        ctx.save()
        ctx.translate(360, 640)
        ctx.scale(sc, sc)
        hm.box(ctx, -250, -330, 500, 660, "#ffffff", "#eef1f7", r=14)
        hm.box(ctx, -250, -330, 500, 90, "#4f8bff", "#3a6fe0", r=14)
        text(ctx, "MATH HOMEWORK", 0, -285, 34, (1, 1, 1), outline=False)
        for i, q in enumerate(("7 x 8 = ?", "36 / 4 = ?", "12 + 19 = ?")):
            text(ctx, q, -30, -150 + i * 130, 44, OUT, outline=False)
            hm.box(ctx, 150, -180 + i * 130, 70, 60, "#ffffff", "#eef1f7", r=6, lw=3)
        ctx.restore()
    if T > 15.63:
        hm.avatar(ctx, 520, 1080, 0.8, shirt="#e8574a", hair="curly", expr="sad", t=T)


# ---------------------------------------------------------------- 16.84 "Are you kidding me?"
def s_kidding(ctx, t, d):
    T = 16.84 + t
    kid_at_pc(ctx, T, "angry", arms=("up", "up"), s=1.15)
    tint(ctx, (0.6, 0.1, 0.1), 0.15)
    label(ctx, "ARE YOU KIDDING?!", 360, 330, 40, hexc("#e8574a"), scale=pop(T - 16.9), tilt=-0.05)


# ---------------------------------------------------------------- 18.67 "she tells everyone to like"
def megaphone(ctx, x, y, s=1.0):
    ctx.move_to(x, y - 20 * s)
    ctx.line_to(x + 110 * s, y - 60 * s)
    ctx.line_to(x + 110 * s, y + 60 * s)
    ctx.line_to(x, y + 20 * s)
    ctx.close_path()
    hm._shade_fill(ctx, hexc("#ffffff"), hexc("#d9dce6"), y - 60 * s, y + 60 * s, 4 * s)
    hm.box(ctx, x - 30 * s, y - 22 * s, 34 * s, 44 * s, "#e8574a", "#b83a33", r=6 * s, lw=3 * s)


def s_like(ctx, t, d):
    T = 18.67 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1080)
    for k, (sh, pa, hr) in enumerate(FRIENDS * 2):   # everyone in the server
        hm.avatar(ctx, 40 + k * 130, 1180 + (k % 2) * 40, 0.75, shirt=sh, pants=pa, t=T + k)
    mom(ctx, 200, 1060, 1.1, "grin", T, arms=("down", "show"))
    hx, hy = show_hand(200, 1060, 1.1)
    megaphone(ctx, hx, hy, 0.9)
    for k in range(3):
        ph = (T * 2 + k / 3) % 1
        ctx.new_sub_path()
        ctx.arc(hx + 120, hy, 40 + ph * 100, -0.6, 0.6)
        ctx.set_source_rgba(1, 1, 1, 1 - ph)
        ctx.set_line_width(6)
        ctx.stroke()
    if T > 19.69:
        hm.like_button(ctx, 470, 720, 1.1 * pop(T - 19.69), pressed=clamp((T - 19.9) / 0.15))


# ---------------------------------------------------------------- 20.03 "and subscribe to this video"
def s_subscribe(ctx, t, d):
    T = 20.03 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1080)
    tint(ctx, (0.1, 0.1, 0.2), 0.3)
    hm.like_button(ctx, 360, 420, 1.0, pressed=1.0)
    if T > 20.13:
        hm.subscribe_button(ctx, 360, 640, 1.1 * pop(T - 20.13), pressed=clamp((T - 20.72) / 0.1))
    k = ease((T - 20.3) / 0.4)
    hm.cursor(ctx, lerp(650, 380, k), lerp(1000, 650, k), 1.3, click=1.0 if 20.65 < T < 20.8 else 0.0)


# ---------------------------------------------------------------- 21.31 "in the next 3 seconds"
def s_count(ctx, t, d):
    T = 21.31 + t
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.set_source_rgb(*hexc("#1c1f33"))
    ctx.fill()
    n = 3 if T < 21.95 else (2 if T < 22.2 else 1)
    k = clamp((T - 21.4) / 1.0)
    ctx.new_sub_path()
    ctx.arc(360, 640, 230, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (1 - k))
    ctx.set_source_rgb(*hexc("#ffd84a"))
    ctx.set_line_width(30)
    ctx.stroke()
    t_n = {3: 21.73, 2: 21.95, 1: 22.2}[n]
    text(ctx, str(n), 360, 640, 260, (1, 1, 1), outline=True, scale=pop(T - t_n) if T > 21.73 else 0.0)
    if T < 21.73:
        text(ctx, "NEXT...", 360, 640, 70, (1, 1, 1), outline=True)


# ---------------------------------------------------------------- 22.39 "to get free Robux."
def s_free(ctx, t, d):
    T = 22.39 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1080)
    for k, (sh, pa, hr) in enumerate(FRIENDS * 2):
        hm.avatar(ctx, 40 + k * 130, 1180 + (k % 2) * 40, 0.75, shirt=sh, pants=pa, t=T + k, wave=True,
                  jump=abs(math.sin(T * 6 + k)) * 30)
    hm.coin_rain(ctx, T, n=20)
    if T > 22.63:
        label(ctx, "FREE R$!", 360, 420, 70, hexc("#ffd84a"), fg=OUT, scale=pop(T - 22.63), tilt=-0.06)


# ---------------------------------------------------------------- 24.42 "you can only earn Robux if"
def s_earn(ctx, t, d):
    T = 24.42 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1080)
    hm.box(ctx, 150, 980, 420, 40, "#9aa1ad", "#6d7380", r=6)   # stand
    for k in range(7):   # a pile of coins inside a locked glass case
        hm.robux_coin(ctx, 255 + (k % 4) * 70, 920 - (k // 4) * 70, 0.8, spin=T * 2 + k)
    ctx.rectangle(170, 660, 380, 320)
    ctx.set_source_rgba(0.75, 0.9, 1, 0.25)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.move_to(200, 700)
    ctx.line_to(260, 680)
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(8)
    ctx.stroke()
    if T > 25.03:
        hm.box(ctx, 310, 600, 100, 80, "#f2b84b", "#d6a23a", r=10)
        ctx.new_sub_path()
        ctx.arc(360, 600, 30, math.pi, 2 * math.pi)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(12)
        ctx.stroke()
    if T > 25.7:
        label(ctx, "ONLY IF...", 360, 400, 56, hexc("#9d7fd6"), scale=pop(T - 25.7), tilt=-0.04)


# ---------------------------------------------------------------- 25.84 "you've liked, subscribed,"
def s_list(ctx, t, d):
    T = 25.84 + t
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.set_source_rgb(*hexc("#ffe9b0"))
    ctx.fill()
    hm.checklist(ctx, 360, 470, [("LIKED", 25.97), ("SUBSCRIBED", 26.43), ("CLEAN ROOM", 99)], T)


# ---------------------------------------------------------------- 27.09 "and cleaned your bedroom in real life."
def s_clean(ctx, t, d):
    T = 27.09 + t
    mess = 1 - ease((T - 27.4) / 1.0)
    hm.bedroom(ctx, T, messy=mess)
    hm.bed(ctx, 560, 1150, 1.0)
    x = lerp(120, 360, ease((T - 27.3) / 1.2))
    KID.draw(ctx, x, 1180, 1.15, keyed(T, [(0, "sad"), (28.4, "tired")]), T, pose="walk", walk_phase=T * 2,
             arms=("hold", "hold"))
    # broom
    hx, hy = x + 0.25 * 64 * 1.15, 1180 - 1.78 * 64 * 1.15
    ctx.move_to(hx, hy - 60)
    ctx.line_to(hx + 40, hy + 160)
    ctx.set_source_rgb(*hexc("#8a5a33"))
    ctx.set_line_width(10)
    ctx.stroke()
    hm.box(ctx, hx + 10, hy + 150, 70, 50, "#f2b84b", "#d6a23a", r=6)
    if T > 28.13:
        label(ctx, "REAL LIFE", 360, 300, 56, hexc("#4fd16a"), fg=OUT, scale=pop(T - 28.13), tilt=0.05)


# ---------------------------------------------------------------- 28.92 "That's not fair."
def s_unfair(ctx, t, d):
    T = 28.92 + t
    hm.bedroom(ctx, T)
    KID.draw(ctx, 360, 1450, 1.8, "angry", T, arms=("hip", "hip"))
    label(ctx, "NOT FAIR!", 360, 600, 60, hexc("#e8574a"), scale=pop(T - 29.16), tilt=-0.06)


# ---------------------------------------------------------------- 31.01 "she enters Bacon's server"
def friends_row(ctx, T, expr="happy", wave=False):
    for k, (sh, pa, hr) in enumerate(FRIENDS):
        hm.avatar(ctx, 420 + k * 140, 1080, 0.85, shirt=sh, pants=pa, expr=expr, t=T + k, wave=wave)


def s_enter(ctx, t, d):
    T = 31.01 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1080)
    hm.avatar(ctx, 180, 1080, 1.0, shirt="#e8574a", hair="curly", expr="happy" if T < 31.4 else "shock", t=T)
    friends_row(ctx, T)
    k = ease((T - 31.22) / 0.4)
    if T > 31.22:   # mom's avatar drops in from the sky
        glow(ctx, 360, 900, 220, (1, 0.95, 0.7), 0.6 * (1 - k))
        hm.avatar(ctx, 360, lerp(200, 1080, k), 1.0, shirt="#9d7fd6", pants="#3a3f55", hair="bun", mom=True,
                  expr="grin", t=T)
        hm.chat_banner(ctx, 360, 520, "MOM has joined the game", 0.9 * pop(T - 31.3))
    if T > 31.54:
        label(ctx, "BACON", 180, 820, 30, hexc("#e8574a"), scale=pop(T - 31.54), tilt=0)


# ---------------------------------------------------------------- 32.43 "starts greeting all his friends."
def s_greet(ctx, t, d):
    T = 32.43 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1080)
    friends_row(ctx, T, expr="neutral")
    x = lerp(160, 300, ease((T - 32.43) / 1.2))
    hm.avatar(ctx, x, 1080, 1.05, shirt="#9d7fd6", pants="#3a3f55", hair="bun", mom=True, expr="grin", t=T,
              wave=True, walk=T * 1.5)
    for k, tk in enumerate((32.65, 33.08, 33.36)):   # a heart pops over each friend
        if T > tk:
            text(ctx, "♥", 420 + k * 140, 820, 60, hexc("#ff4f8b"), outline=True, scale=pop(T - tk))


# ---------------------------------------------------------------- 33.94 "Hello, sweetie, in giant capital letters."
def s_sweetie(ctx, t, d):
    T = 33.94 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1080)
    friends_row(ctx, T, expr="shock")
    hm.avatar(ctx, 160, 1080, 1.0, shirt="#9d7fd6", pants="#3a3f55", hair="bun", mom=True, expr="grin", t=T,
              wave=True)
    size = lerp(44, 90, ease((T - 35.07) / 0.6)) if T > 35.07 else 44
    sc = pop(T - 33.95)
    if sc > 0:
        text(ctx, "HELLO", 360, 420, size, hexc("#ff4f8b"), outline=True, scale=sc)
        text(ctx, "SWEETIE!!!", 360, 420 + size * 1.2, size, hexc("#ff4f8b"), outline=True, scale=pop(T - 34.32))


# ---------------------------------------------------------------- 36.38 "Mom, stop embarrassing me."
def s_embarrass(ctx, t, d):
    T = 36.38 + t
    kid_at_pc(ctx, T, keyed(T, [(0, "shock"), (36.9, "angry")]), arms=("up", "up"), s=1.15)
    glow(ctx, 250, 1180 - 3.71 * 64 * 1.15, 120, (1, 0.25, 0.2), 0.45)   # red face
    for k, tk in enumerate((36.9, 37.2, 37.5)):
        if T > tk:
            text(ctx, "LOL", 470 + (k % 2) * 90, 560 + k * 60, 34, hexc("#ffd84a"), outline=True, scale=pop(T - tk))
    if T > 36.88:
        label(ctx, "MOM, STOP!", 300, 330, 54, hexc("#e8574a"), scale=pop(T - 36.88), tilt=-0.05)


# ---------------------------------------------------------------- 38.80 "Bacon refuses to log off after bedtime,"
def s_refuse(ctx, t, d):
    T = 38.80 + t
    kid_at_pc(ctx, T, keyed(T, [(0, "smirk"), (39.97, "grin")]), night=1.0, arms=("hold", "hold"))
    of.wall_clock(ctx, 360, 380, 75, 10, 30)
    sc = pop(T - 39.4)
    if sc > 0:
        ctx.save()
        ctx.translate(500, 700)
        ctx.scale(sc * 0.75, sc * 0.75)
        hm.dialog(ctx, 0, 0, "LOG OFF?", pick=1 if T > 39.97 else None)
        ctx.restore()
        if T > 39.97:
            hm.cursor(ctx, 570, 720, 0.9, click=1.0 if T < 40.15 else 0.0)


# ---------------------------------------------------------------- 41.28 "so she disconnects the Wi-Fi"
def s_unplug(ctx, t, d):
    T = 41.28 + t
    hm.bedroom(ctx, T, night=0.7)
    hm.box(ctx, 160, 760, 400, 30, "#b07a4a", "#8a5a33", r=4)   # shelf
    pull = ease((T - 41.59) / 0.35)
    hm.router(ctx, 340, 700, 1.0, T, on=1.0 if T < 41.75 else 0.0, plug_out=pull)
    mom(ctx, 590, 1000, 1.05, keyed(T, [(0, "smirk"), (41.59, "cold")]), T, arms=("down", "point"))
    if T > 42.22:
        hm.wifi_icon(ctx, 340, 470, 0.9, crossed=(T - 42.22) / 0.3)


# ---------------------------------------------------------------- 42.68 "for the entire server."
OFF2 = [42.9 + k * 0.03 for k in range(12)]


def s_allserver(ctx, t, d):
    T = 42.68 + t
    hm.server_wall(ctx, T, OFF2, label_txt="NO WI-FI")
    if T > 43.37:
        label(ctx, "DISCONNECTED", 360, 200, 48, hexc("#e8323a"), scale=pop(T - 43.37), tilt=0.04)


# ---------------------------------------------------------------- 45.11 "she finally releases her very own game."
def s_release(ctx, t, d):
    T = 45.11 + t
    ctx.rectangle(-3000, -3000, 7000, 7000)
    ctx.set_source_rgb(*hexc("#2a1f3d"))
    ctx.fill()
    glow(ctx, 360, 700, 520, (1, 0.85, 0.5), 0.5)   # spotlight
    open_k = ease((T - 45.72) / 0.6)
    # the game box revealed behind sliding curtains
    hm.box(ctx, 200, 380, 320, 420, "#4f3a8a", "#2f2260", r=16)
    text(ctx, "MOM'S", 360, 470, 44, hexc("#ffd84a"), outline=True)
    text(ctx, "GAME", 360, 530, 44, hexc("#ffd84a"), outline=True)
    hm.avatar(ctx, 360, 760, 0.9, shirt="#9d7fd6", pants="#3a3f55", hair="bun", mom=True, expr="grin", t=T)
    for side in (-1, 1):
        x0 = 360 + side * (0 + open_k * 420)
        hm.box(ctx, x0 - 360 if side < 0 else x0, -200, 360, 1500, "#c63d33", "#8a1f22", r=0)
    mom(ctx, 600, 1300, 1.2, "grin", T, arms=("down", "show"))
    if T > 45.9:
        rnd = __import__("random").Random(3)
        for i in range(30):
            x = rnd.uniform(0, 720)
            y = (rnd.uniform(-200, 1200) + (T - 45.9) * rnd.uniform(300, 500)) % 1400 - 200
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(T * 5 + i)
            ctx.rectangle(-8, -4, 16, 8)
            ctx.set_source_rgb(*hexc(rnd.choice(["#e8574a", "#4fb3a9", "#f2b84b", "#9d7fd6"])))
            ctx.fill()
            ctx.restore()
    if T > 46.92:
        label(ctx, "NEW GAME!", 360, 260, 56, hexc("#ffd84a"), fg=OUT, scale=pop(T - 46.92), tilt=-0.05)


# ---------------------------------------------------------------- 47.80 "And guess what it's called?"
def s_guess(ctx, t, d):
    T = 47.80 + t
    kid_at_pc(ctx, T, "worried", arms=("down", "down"), s=1.15)
    for k in range(3):
        label(ctx, "?", 200 + k * 70, 480 - k * 40, 44, hexc("#ffd84a"), fg=OUT, scale=pop(T - 47.98 - k * 0.12),
              tilt=0.1)


# ---------------------------------------------------------------- 48.96 "Go to Bed Simulator."
def s_title(ctx, t, d):
    T = 48.96 + t
    hm.game_sky(ctx, night=1.0)
    hm.baseplate(ctx, 1080, col="#3f6a4a")
    ctx.new_sub_path()
    ctx.arc(560, 200, 50, 0, 2 * math.pi)
    ctx.set_source_rgb(0.97, 0.95, 0.85)
    ctx.fill()
    glow(ctx, 560, 200, 180, (0.8, 0.85, 1), 0.4)
    for k, x in enumerate((140, 360, 580)):   # rows of beds, everyone asleep
        hm.bed(ctx, x, 1180, 0.55, blanket=("#e8574a", "#4f8bff", "#f2b84b")[k])
        hm.avatar(ctx, x - 50, 1120, 0.45, shirt="#e8574a", hair="curly" if k == 1 else None, expr="sleep", t=T)
        zzz(ctx, x, 1000, T + k)
    words = [("GO TO", 48.96, 380), ("BED", 49.28, 490), ("SIMULATOR", 49.57, 600)]
    for w, tw, y in words:
        if T > tw:
            text(ctx, w, 360, y, 70 if w != "BED" else 110, hexc("#ffd84a"), outline=True, scale=pop(T - tw))


S = []


def shot(start, draw, keys, **kw):
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def push(t0, t1, z0, z1, c0, c1):
    return [(t0, z0, c0), (t1, z1, c1, max(0.2, t1 - t0))]


shot(0.0, s_hi, push(0.0, 0.76, 1.2, 1.45, (360, 900), (360, 880)), dof=2)
shot(0.76, s_owner, [(0.76, 1.0, (360, 700)), (1.19, 1.3, (360, 900), 0.3), (1.62, 1.2, (360, 760), 0.3)])
shot(1.99, day_shot(1, 1.99, 2.37), push(1.99, 3.11, 1.0, 1.2, C, (360, 620)))
shot(3.11, s_servers, push(3.11, 4.83, 1.25, 0.95, (360, 560), (360, 640)), shake=(1.13, 8))
shot(4.83, s_clock, push(4.83, 6.27, 1.0, 1.35, (360, 680), (360, 720)))
shot(6.27, s_why, push(6.27, 6.76, 1.15, 1.35, (300, 780), (270, 740)), shake=(0.03, 6))
shot(6.76, s_bedtime, [(6.76, 0.95, (380, 760)), (7.21, 1.05, (360, 720), 0.35)])
shot(7.89, s_noexcuse, push(7.89, 8.95, 1.0, 1.1, (340, 800), (320, 820)), dof=2, shake=(0.27, 7),
     keep=[(40, 680, 360, 840)])
shot(8.95, s_sleep, push(8.95, 9.74, 1.1, 1.35, (360, 820), (320, 820)))
shot(9.74, day_shot(2, 9.74, 9.94), push(9.74, 10.56, 1.0, 1.2, C, (360, 620)))
shot(10.56, s_obby, [(10.56, 0.9, (380, 780)), (11.44, 1.1, (480, 680), 0.4)])
shot(11.79, s_assignment, [(11.79, 1.1, (420, 760)), (12.14, 1.0, (360, 560), 0.35)])
shot(13.07, s_waitwhat, push(13.07, 13.92, 1.2, 1.5, (330, 800), (270, 760)), shake=(0.39, 8))
shot(13.92, s_nojump, [(13.92, 1.0, (360, 820)), (14.49, 1.25, (330, 760), 0.35), (14.83, 1.3, (380, 640), 0.3)])
shot(15.09, s_math, push(15.09, 16.84, 1.05, 1.2, C, (360, 600)), keep=[(110, 310, 610, 970)])
shot(16.84, s_kidding, push(16.84, 17.81, 1.15, 1.4, (330, 800), (300, 700)), shake=(0.1, 9))
shot(17.81, day_shot(3, 17.81, 18.18), push(17.81, 18.67, 1.0, 1.2, C, (360, 620)))
shot(18.67, s_like, [(18.67, 1.0, (330, 780)), (19.69, 1.2, (440, 760), 0.4)], keep=[(330, 650, 610, 790)])
shot(20.03, s_subscribe, push(20.03, 21.31, 1.0, 1.25, (360, 600), (360, 620)))
shot(21.31, s_count, push(21.31, 22.39, 1.0, 1.3, C, C), shake=(0.42, 6))
shot(22.39, s_free, push(22.39, 23.3, 1.0, 1.25, (360, 700), (360, 520)))
shot(23.3, day_shot(4, 23.3, 23.95), push(23.3, 24.42, 1.0, 1.2, C, (360, 620)))
shot(24.42, s_earn, [(24.42, 1.0, (360, 760)), (25.03, 1.3, (360, 760), 0.35), (25.7, 1.15, (360, 600), 0.3)])
shot(25.84, s_list, [(25.84, 1.1, (360, 620)), (26.43, 1.3, (330, 700), 0.3), (26.9, 1.2, (330, 800), 0.3)])
shot(27.09, s_clean, push(27.09, 28.92, 1.0, 1.1, (300, 860), (360, 820)))
shot(28.92, s_unfair, push(28.92, 30.18, 1.1, 1.25, (360, 920), (360, 900)), shake=(0.24, 7))
shot(30.18, day_shot(5, 30.18, 30.53), push(30.18, 31.01, 1.0, 1.2, C, (360, 620)))
shot(31.01, s_enter, [(31.01, 1.0, (330, 820)), (31.22, 1.05, (340, 700), 0.3), (31.87, 1.2, (300, 820), 0.4)])
shot(32.43, s_greet, push(32.43, 33.94, 1.1, 1.3, (360, 860), (420, 820)))
shot(33.94, s_sweetie, [(33.94, 1.0, (360, 620)), (35.07, 0.9, (360, 640), 0.5)], shake=(1.13, 8),
     keep=[(20, 360, 700, 600)])
shot(36.38, s_embarrass, push(36.38, 38.14, 1.15, 1.35, (330, 760), (300, 700)))
shot(38.14, day_shot(6, 38.14, 38.51), push(38.14, 38.8, 1.0, 1.2, C, (360, 620)))
shot(38.80, s_refuse, [(38.80, 1.0, (380, 760)), (39.4, 1.25, (480, 760), 0.35), (40.34, 1.2, (330, 800), 0.4)],
     keep=[(330, 610, 680, 790)])
shot(41.28, s_unplug, [(41.28, 1.0, (420, 760)), (41.59, 1.35, (420, 800), 0.3), (42.22, 1.15, (380, 760), 0.3)],
     shake=(0.35, 7), keep=[(190, 360, 560, 780)])
shot(42.68, s_allserver, push(42.68, 44.18, 1.2, 0.95, (360, 640), (360, 640)))
shot(44.18, day_shot(7, 44.18, 44.63), push(44.18, 45.11, 1.0, 1.25, C, (360, 620)))
shot(45.11, s_release, [(45.11, 1.0, (420, 760)), (45.72, 1.15, (360, 600), 0.5), (46.92, 1.1, (400, 600), 0.4)],
     keep=[(190, 220, 530, 800)])
shot(47.80, s_guess, push(47.80, 48.96, 1.15, 1.4, (330, 780), (280, 720)))
shot(48.96, s_title, push(48.96, TOTAL, 1.25, 1.0, (360, 520), (360, 700)), keep=[(60, 330, 660, 1190)])
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ~1 SFX per second on visual events (sound_design.md); no camera whoosh
SFX = [
    (0.1, "pop.wav", 0.6), (0.5, "boing.wav", 0.4), (1.19, "pop.wav", 0.8), (1.6, "sparkle.wav", 0.8),
    (1.75, "thud.wav", 0.6),
    *[(t0, "page.wav", 0.8) for t0 in (2.37, 9.94, 18.18, 23.95, 30.53, 38.51, 44.63)],
    *[(t0, "tick.wav", 0.5) for t0 in OFF1[::2]], (4.24, "thud.wav", 1.0), (4.3, "sting_low.wav", 0.6),
    *[(4.95 + k * 0.1, "tick.wav", 0.5) for k in range(6)], (5.51, "bell.wav", 0.8),
    (6.3, "boing.wav", 0.7), (7.21, "pop.wav", 0.7), (7.3, "sparkle.wav", 0.4),
    (7.9, "pop.wav", 0.6), (8.16, "thud.wav", 0.9), (9.0, "tick.wav", 0.7), (9.18, "pop.wav", 0.5),
    *[(10.6 + k * 0.6, "boing.wav", 0.35) for k in range(2)], (11.44, "pop.wav", 0.6),
    (11.85, "sparkle.wav", 0.8), (12.14, "page.wav", 0.7), (13.2, "boing.wav", 0.6), (13.46, "pop.wav", 0.7),
    (14.25, "tick.wav", 0.6), (14.55, "thud.wav", 0.8), (14.83, "pop.wav", 0.6),
    (15.2, "page.wav", 0.8), (15.63, "pop.wav", 0.5), (16.9, "sting_low.wav", 0.6), (17.0, "pop.wav", 0.7),
    (19.0, "murmur.wav", 0.5), (19.69, "pop.wav", 0.8), (19.9, "tick.wav", 0.7),
    (20.13, "pop.wav", 0.8), (20.7, "tick.wav", 0.8), (20.75, "bell.wav", 0.5),
    (21.73, "tick.wav", 0.9), (21.95, "tick.wav", 0.9), (22.2, "tick.wav", 0.9),
    *[(22.45 + k * 0.1, "coin.wav", 0.4) for k in range(8)], (22.63, "sparkle.wav", 0.8),
    (25.03, "thud.wav", 0.7), (25.7, "pop.wav", 0.6), (25.97, "tick.wav", 0.8), (26.0, "pop.wav", 0.5),
    (26.43, "tick.wav", 0.8), (26.46, "pop.wav", 0.5),
    *[(27.4 + k * 0.25, "step.wav", 0.5) for k in range(5)], (28.13, "pop.wav", 0.7),
    (29.16, "sting_low.wav", 0.6), (29.2, "pop.wav", 0.6),
    (31.25, "sparkle.wav", 0.8), (31.62, "thud.wav", 0.7), (31.54, "pop.wav", 0.5),
    (32.65, "pop.wav", 0.6), (33.08, "pop.wav", 0.6), (33.36, "pop.wav", 0.6),
    (33.95, "pop.wav", 0.8), (34.32, "pop.wav", 0.8), (35.07, "boing.wav", 0.7), (35.5, "thud.wav", 0.6),
    (36.4, "sting_soft.wav", 0.6), (36.9, "pop.wav", 0.4), (37.2, "pop.wav", 0.4), (37.5, "pop.wav", 0.4),
    (39.4, "pop.wav", 0.7), (39.97, "tick.wav", 0.8), (40.7, "tick.wav", 0.5),
    (41.59, "thud.wav", 0.9), (41.75, "sting_low.wav", 0.7), (42.22, "pop.wav", 0.7),
    *[(t0, "tick.wav", 0.4) for t0 in OFF2[::3]], (43.37, "thud.wav", 0.8),
    (45.3, "page.wav", 0.6), (45.72, "sparkle.wav", 0.9), (45.9, "bell.wav", 0.7), (46.92, "pop.wav", 0.7),
    (47.98, "pop.wav", 0.5), (48.1, "pop.wav", 0.5), (48.22, "pop.wav", 0.5),
    (48.96, "pop.wav", 0.8), (49.28, "thud.wav", 0.9), (49.57, "pop.wav", 0.8), (49.6, "sting.wav", 0.9),
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
    import safezone
    safezone.fit(SHOTS, sys.modules[__name__])   # characters + key props inside the Shorts safe zone
    render(SHOTS, TOTAL, sys.argv[1], grain=4, xfade=0.2, **kw)
