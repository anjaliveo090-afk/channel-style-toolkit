"""Story v2: mom allows only 10 seconds of the block game; you speedrun everything in them.
Rebuilt from scratch on the same voice/SRT as speedrun.py, with the lessons from v1:
- every line happens in a real place (bedroom, desk, obby, boss arena, shop, plaza,
  hatchery, secret room), no empty colour backgrounds;
- the game avatar wears the kid's teal shirt and brown hair, so it is clearly "you";
- camera variety: over-the-shoulder, a dive into the monitor, a drone view down the obby,
  low angles on the boss and the giant toaster, cross-cuts game <-> real life;
- literal game UI: timer HUD, boss health bar, damage numbers, loot chest, rarity banner,
  shopping cart, comment section;
- shots start just before every "Second N" so the timer tick lands inside the shot;
- whole characters inside the Shorts safe zone (safezone.fit, top=250 under the HUD);
- the last frame equals the first frame, so the Short loops."""
import math
import sys

import home as hm
import office as of
import speed as sp
import speed2 as s2
from arcade import hand, red_x
from engine import W, H, clamp, ease, glow, hexc, keyed, label, lerp, pop, render, text
from style2 import Char2, OUT, back_figure

TOTAL = 53.11
C = (W / 2, H / 2)
TEAL, RED = "#4fb3a9", "#e8574a"

KID = Char2(TEAL, hair="bowl", hair_col="#8a4a20", outfit="shirt")
KID_SH = Char2(TEAL, hair="bowl", hair_col="#8a4a20", outfit="shirt", shades=True)
MOM = Char2("#9d7fd6", hair="side", hair_col="#6d381c", outfit="apron")
KID_X, DESK_X = 300, 560


def tint(ctx, rgb, a):
    if a > 0:
        ctx.set_source_rgba(*rgb, a)
        ctx.rectangle(-3000, -5000, 7000, 10000)
        ctx.fill()


def flash(ctx, a):
    tint(ctx, (1, 1, 1), max(0.0, min(1.0, a)))


def mom(ctx, x, y, s, expr, T, finger=False, **kw):
    r = 64 * s
    ctx.new_sub_path()
    ctx.arc(x, y - 4.75 * r, 0.4 * r, 0, 2 * math.pi)
    hm._shade_fill(ctx, hexc("#8a4a20"), hexc("#6d381c"), y - 5.2 * r, y - 4.4 * r, 0.075 * r)
    MOM.draw(ctx, x, y, s, expr, T, **kw)
    if finger:   # one raised finger on the 'show' hand
        hx, hy = x + 1.31 * r, y - 3.18 * r
        ctx.move_to(hx, hy)
        ctx.line_to(hx + 0.02 * r, hy - 0.42 * r)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(0.12 * r)
        ctx.stroke()


def you(ctx, x, y, s, T, **kw):
    """The blocky game avatar: the kid's teal shirt, blue pants, brown hair."""
    hm.avatar(ctx, x, y, s, shirt=TEAL, pants="#2b45a6", hair="curly", t=T, **kw)


def sweat(ctx, x, y, r, T):
    for k, (dx, dy, sc) in enumerate(((0.9, -0.4, 1.0), (1.05, 0.05, 0.7))):
        cx, cy = x + dx * r, y + dy * r + ((T * 2 + k * 0.5) % 1) * 0.3 * r
        d = 0.14 * r * sc
        ctx.move_to(cx, cy - 2 * d)
        ctx.curve_to(cx + d * 1.2, cy - 0.2 * d, cx + d, cy + d, cx, cy + d)
        ctx.curve_to(cx - d, cy + d, cx - d * 1.2, cy - 0.2 * d, cx, cy - 2 * d)
        ctx.set_source_rgb(*hexc("#7fd0ff"))
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(max(2, 0.03 * r))
        ctx.stroke()


def world_screen(play=0.0, spawn=False):
    return lambda c, sx, sy, sw, sh, T: s2.scr_world(c, sx, sy, sw, sh, T, play=play, spawn=spawn)


def room(ctx, T, kid="happy", arms=("hold", "hold"), shades=False, screen=None, night=0.0, door=None,
         watch=None, router=False, kid_on=True):
    """The kid's room: door on the left, desk + monitor on the right, stopwatch on the desk."""
    hm.bedroom(ctx, T, night=0.0)
    if door is not None:
        of.door(ctx, 40, 1000, 170, 380, open_frac=door, col="#b07a4a")
    if router:
        hm.box(ctx, 430, 640, 260, 22, "#b07a4a", "#8a5a33", r=4)
        hm.router(ctx, 560, 628, 0.62, T, on=1.0)
    of.desk(ctx, DESK_X, 960, 330)
    s2.monitor(ctx, DESK_X, 935, 0.9, T, screen or world_screen())
    hm.box(ctx, 480, 936, 160, 16, "#3a3f55", "#262a3a", r=4, lw=3)
    if watch is not None:
        frac, num = watch
        sp.stopwatch(ctx, 418, 922, 30, frac, num, T, num_col="#d63c3c" if num in ("3", "1") else None)
    of.chair(ctx, KID_X, 1180, 1.05, col=RED)
    if kid_on:
        (KID_SH if shades else KID).draw(ctx, KID_X, 1180, 1.1, kid, T, pose="sit", arms=arms, look=0.5)
    tint(ctx, (0.04, 0.05, 0.18), 0.55 * night)
    if night:
        glow(ctx, DESK_X, 820, 380, (0.5, 0.75, 1), 0.3)


# ================================================================ real life: the rule
def s_open(ctx, t, d, T0=0.0, frozen=False):
    T = T0 + (0.0 if frozen else t)
    door = ease((T - 0.15) / 0.4)
    room(ctx, T, kid="happy", door=door, watch=None)
    if door > 0.3:   # mom appears in the doorway behind the kid
        glow(ctx, 125, 800, 220, (1, 0.9, 0.6), 0.45 * door)
        mom(ctx, 125, 1010, 0.95, keyed(T, [(0, "smirk"), (0.43, "cold")]), T, arms=("down", "down"))
        room_front(ctx, T)
    label(ctx, "MOM", 125, 560, 40, hexc("#9d7fd6"), scale=pop(T - 0.43), tilt=0.06)


def room_front(ctx, T):
    """Redraw the kid and his chair in front of mom (she stands in the doorway behind him)."""
    of.chair(ctx, KID_X, 1180, 1.05, col=RED)
    KID.draw(ctx, KID_X, 1180, 1.1, "happy", T, pose="sit", arms=("hold", "hold"), look=0.5)


def s_finger(ctx, t, d):
    T = 0.80 + t
    hm.bedroom(ctx, T)
    mom(ctx, 360, 1280, 1.5, keyed(T, [(0, "cold"), (1.36, "smirk")]), T, arms=("down", "show"), finger=True)
    label(ctx, "ONLY...", 360, 620, 48, hexc("#9d7fd6"), scale=pop(T - 0.8), tilt=-0.05)


def s_timer(ctx, t, d):
    T = 1.51 + t
    hm.bedroom(ctx, T)
    mom(ctx, 520, 1300, 1.25, "smirk", T, arms=("down", "show"))
    sc = pop(T - 1.53)
    if sc > 0.02:
        ctx.save()
        ctx.translate(320, 620)
        ctx.scale(sc, sc)
        ctx.translate(-320, -620)
        sp.stopwatch(ctx, 320, 620, 170, 1.0, "10", T)
        ctx.restore()
    label(ctx, "SECONDS", 320, 860, 44, hexc("#e8574a"), scale=pop(T - 1.81), tilt=-0.04)


def s_ots(ctx, t, d):
    T = 2.32 + t
    s2.wall_and_desk(ctx, y_desk=1060)
    s2.monitor(ctx, 440, 1050, 2.0, T, world_screen(play=pop(T - 2.4)))
    k = ease((T - 2.6) / 0.35)
    hm.cursor(ctx, lerp(640, 560, k), lerp(980, 700, k), 1.3, click=1.0 if 2.95 < T < 3.1 else 0.0)
    back_figure(ctx, 170, 1080, 150, "#8a4a20", TEAL)
    label(ctx, "PLAY!", 470, 430, 56, hexc("#4fd16a"), scale=pop(T - 2.52), tilt=-0.05)


def s_set(ctx, t, d):
    T = 3.22 + t
    s2.wall_and_desk(ctx, y_desk=760)
    frac = 1.0 - 0.1 * clamp((T - 3.73) / 0.55)
    sp.stopwatch(ctx, 360, 580, 170, frac, "10", T)
    k = ease((T - 3.22) / 0.24) if T < 3.6 else 1 - ease((T - 3.6) / 0.4)
    s2.hand_up(ctx, 360, lerp(-260, 152, k), 1.0, ang=math.pi, sleeve="#9d7fd6", point=True)
    label(ctx, "JUST 10!", 360, 900, 56, hexc("#e8574a"), scale=pop(T - 3.46), tilt=-0.05)


def s_bed(ctx, t, d):
    T = 4.27 + t
    hm.bedroom(ctx, T, night=0.45)
    hm.bed(ctx, 590, 1150, 1.0, blanket="#4f8bff")
    walk = ease((T - 4.4) / 0.8)
    KID.draw(ctx, lerp(330, 450, walk), 1250, 1.1, "sad", T, pose="walk" if 0 < walk < 1 else "stand",
             walk_phase=T * 2, look=0.5)
    mom(ctx, 150, 1250, 1.15, "cold", T, arms=("down", "point"))
    label(ctx, "BED!", 600, 820, 60, hexc("#4f8bff"), scale=pop(T - 4.91), tilt=0.05)


def s_shock(ctx, t, d):
    T = 5.23 + t
    hm.bedroom(ctx, T)
    tint(ctx, (0.9, 0.2, 0.15), 0.18)
    sp.speed_lines(ctx, T, 360, 900, a=0.45, r0=230)
    KID.draw(ctx, 360, 1240, 1.55, "shock", T, arms=("up", "up"), bob=1.6)
    label(ctx, "10 SECONDS?!", 360, 640, 52, hexc("#ffd84a"), fg=OUT, scale=pop(T - 5.75), tilt=-0.06)


def s_loading(ctx, t, d):
    T = 6.46 + t
    frac = 0.03 + 0.01 * clamp((T - 6.46) / 1.0)
    room(ctx, T, kid="sad", arms=("down", "down"),
         screen=lambda c, sx, sy, sw, sh, TT: s2.scr_loading(c, sx, sy, sw, sh, TT, frac), watch=(1.0, "10"))
    red_x(ctx, DESK_X, 812, 110, (T - 6.9) / 0.25)
    label(ctx, "IMPOSSIBLE!", 420, 600, 50, hexc("#e8323a"), scale=pop(T - 6.68), tilt=0.05)


def s_shades(ctx, t, d):
    T = 7.47 + t
    hm.bedroom(ctx, T)
    glow(ctx, 360, 900, 420, (1, 0.85, 0.5), 0.35)
    on = T >= 8.15
    (KID_SH if on else KID).draw(ctx, 360, 1240, 1.5, keyed(T, [(0, "sad"), (7.85, "smirk")]), T,
                                  arms=("hip", "hip"), bob=0.8)
    r = 64 * 1.5
    ey = 1240 - 3.71 * r + 0.21 * r
    if not on:   # the shades slide down onto his face
        y = lerp(300, ey, ease((T - 7.85) / 0.3))
        for side in (-1, 1):
            hm.rrect(ctx, 360 + side * 0.27 * r - 0.2 * r, y - 0.12 * r, 0.4 * r, 0.25 * r, 0.08 * r)
            ctx.set_source_rgb(0.08, 0.08, 0.12)
            ctx.fill()
        ctx.rectangle(360 - 0.1 * r, y - 0.04 * r, 0.2 * r, 0.05 * r)
        ctx.fill()
    elif T < 8.6:
        text(ctx, "✦", 360 + 0.5 * r, ey - 0.3 * r, 60 * pop(T - 8.15), (1, 1, 1), outline=True)
    label(ctx, "NOT IF...", 360, 640, 50, hexc("#4f8bff"), scale=pop(T - 7.85), tilt=-0.05)


def s_typing(ctx, t, d):
    T = 8.39 + t
    s2.wall_and_desk(ctx, y_desk=520)
    s2.keyboard(ctx, 360, 760, 1.15, T, mash=1.0)
    j = math.sin(T * 55) * 14
    s2.hand_up(ctx, 220 + j, 1010 - abs(j), 1.0, ang=0.3)
    s2.hand_up(ctx, 500 - j, 1010 - abs(math.cos(T * 47) * 14), 1.0, ang=-0.3)
    for k in range(5):   # sparks flying off the keys
        ph = (T * 3 + k / 5) % 1
        text(ctx, "✦", 160 + k * 100, 700 - ph * 220, 40 * (1 - ph), (1, 0.95, 0.5), outline=False)
    label(ctx, "SPEEDRUNNER", 360, 440, 56, hexc("#ffd84a"), fg=OUT, scale=pop(T - 8.88), tilt=-0.05)


def s_dive(ctx, t, d):
    T = 9.40 + t
    room(ctx, T, kid="grin", shades=True, screen=world_screen(spawn=True), watch=(1.0, "10"))


# ================================================================ game: second 10 - obby
def gate(ctx, x, y, T):
    for dx in (-110, 110):
        hm.box(ctx, x + dx - 22, y - 300, 44, 300, "#e9edf2", "#b9bec7", r=8)
    hm.box(ctx, x - 160, y - 380, 320, 90, "#4fd16a", "#2e9c46", r=14)
    text(ctx, "OBBY", x, y - 334, 56, (1, 1, 1), outline=True)


def s_spawn(ctx, t, d):
    T = 10.22 + t
    hm.game_sky(ctx)
    for i in range(5):   # the obby floating in the distance
        hm.block(ctx, 380 + i * 110, 620 - i * 40, 80, 30)
    hm.baseplate(ctx, 1000)
    gate(ctx, 590, 1000, T)
    hm.ellipse(ctx, 200, 1000, 110, 26)
    ctx.set_source_rgba(0.4, 1, 0.8, 0.7)
    ctx.fill()
    k = clamp((T - 10.22) / 0.35)
    glow(ctx, 200, 900, 260, (0.5, 1, 0.9), 0.7 * (1 - k))
    walk = ease((T - 10.94) / 0.7)
    x = lerp(200, 420, walk)
    if k > 0.05:
        ctx.push_group()
        you(ctx, x, 1000, 1.5, T, expr="grin", walk=T * 2.5 if 0 < walk < 1 else 0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)
    sp.sparkles(ctx, T, 200, 820, spread=120, n=8, seed=4) if T < 10.7 else None
    label(ctx, "GO!", 300, 560, 56, hexc("#4fd16a"), fg=OUT, scale=pop(T - 10.94), tilt=-0.05)


def s_hundred(ctx, t, d):
    T = 11.67 + t
    s2.course_persp(ctx, T)
    you(ctx, 360, 1196, 1.0, T, expr="grin")
    label(ctx, "100 STAGES", 360, 560, 56, hexc("#4f8bff"), scale=pop(T - 11.7), tilt=-0.04)


def s_jump(ctx, t, d):
    T = 12.75 + t
    pl = sp.course(ctx, T, n=16)
    p = clamp((T - 12.95) / 1.2)
    lx, ly = pl[-1][0] + 75, pl[-1][1]
    x = lerp(150, lx, ease(p))
    y = lerp(900, ly, p) - math.sin(math.pi * p) * 800
    for k in range(4):   # launch dust
        a = clamp((T - 12.95) / 0.5)
        if 0 < a < 1:
            ctx.new_sub_path()
            ctx.arc(150 + (k - 1.5) * 50 * (1 + a), 890, 30 * (1 + a), 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - a))
            ctx.fill()
    if p <= 0:
        you(ctx, 150, 900, 1.3, T, expr="grin", jump=-12)   # crouch
    else:
        ctx.save()
        ctx.translate(x, y - 110)
        ctx.rotate(p * 2 * math.pi)
        ctx.translate(-x, -(y - 110))
        for i in range(3, 0, -1):
            ctx.push_group()
            you(ctx, x - i * 70, y + i * 20, 1.3, T, expr="grin")
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(0.35 * (1 - i / 4))
        you(ctx, x, y, 1.3, T, expr="grin")
        ctx.restore()
    label(ctx, "ONE JUMP!", x, y - 380, 48, hexc("#ffd84a"), fg=OUT, scale=pop(T - 13.9), tilt=-0.05)


def s_finish(ctx, t, d):
    T = 14.20 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 980)
    sp.finish(ctx, 450, 980, 1.1, T, confetti=14.2)
    sq = math.exp(-12 * max(0.0, T - 14.2))
    you(ctx, 300, 980, 1.5, T, expr="happy", wave=T > 14.4, jump=max(0.0, math.sin((T - 14.45) * 9)) * 26 * (T > 14.45))
    if sq > 0.1:   # landing dust
        for k in range(5):
            ctx.new_sub_path()
            ctx.arc(300 + (k - 2) * 60, 975, 26 + 30 * (1 - sq), 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.6 * sq)
        ctx.fill()
    label(ctx, "FINISH!", 360, 560, 72, hexc("#4fd16a"), fg=OUT, scale=pop(T - 14.25), tilt=-0.05)


# ================================================================ second 9 - the noob king
def boss_frac(T):
    if T < 17.99:
        return 1.0
    return max(0.0, 1 - (T - 17.99) / 0.26)


def s_rumble(ctx, t, d):
    T = 15.05 + t
    sp.arena(ctx, T, crack=clamp((T - 15.3) / 0.7))
    you(ctx, 300, 1060, 1.5, T, expr="shock")
    sweat(ctx, 300, 1060 - 176 * 1.5, 50, T)
    label(ctx, "BOSS INCOMING!", 380, 600, 46, hexc("#e8323a"), scale=pop(T - 15.91), tilt=-0.05)


def s_king(ctx, t, d):
    T = 16.03 + t
    sp.arena(ctx, T, crack=1.0)
    rise = ease((T - 16.03) / 0.9)
    for k in range(3):   # light beams from the crack
        ctx.move_to(450 + (k - 1) * 40, 1000)
        ctx.line_to(450 + (k - 1) * 260, -300)
        ctx.line_to(450 + (k - 1) * 260 + 120, -300)
        ctx.close_path()
    ctx.set_source_rgba(1, 0.75, 0.35, 0.18 * rise)
    ctx.fill()
    s2.noob_king(ctx, 450, lerp(1560, 1130, rise), 2.0, T)
    you(ctx, 150, 1180, 0.95, T, expr="shock")


def s_boom(ctx, t, d):
    T = 17.16 + t
    sp.arena(ctx, T, crack=1.0)
    k = (T - 17.16) / 0.56
    s2.noob_king(ctx, 520, 1150, 1.8, T, expr="shock")
    sp.starburst(ctx, 380, 820, 190, k * 2)
    you(ctx, lerp(60, 220, ease(k * 4)), 1150, 1.8, T, expr="angry", wave=True)
    flash(ctx, 0.75 - k * 4)
    label(ctx, "BOOM!", 360, 560, 92, hexc("#ff4f5a"), fg=OUT, scale=pop(T - 17.18), tilt=-0.08)


def s_onehit(ctx, t, d):
    T = 17.72 + t
    sp.arena(ctx, T, crack=1.0)
    p = clamp((T - 17.72) / 0.6)
    sp.speed_lines(ctx, T, 420, 800, a=0.35)
    ctx.save()
    kx, ky = lerp(450, 640, ease(p)), 1150 - math.sin(p * math.pi) * 160
    ctx.translate(kx, ky - 200)
    ctx.rotate(p * 1.6)
    ctx.translate(-kx, -(ky - 200))
    s2.noob_king(ctx, kx, ky, 1.6, T, expr="shock")
    ctx.restore()
    s2.damage(ctx, 470, 760, (T - 17.85) / 0.6)
    you(ctx, 200, 1150, 1.6, T, expr="angry", wave=True)
    label(ctx, "ONE HIT!", 360, 560, 64, hexc("#ffd84a"), fg=OUT, scale=pop(T - 17.99), tilt=-0.05)


def s_ko(ctx, t, d):
    T = 18.33 + t
    sp.arena(ctx, T, crack=1.0)
    ctx.save()
    ctx.translate(480, 1150)
    ctx.rotate(-math.pi / 2 + 0.04)
    sp.cape(ctx, 0, 0, 1.4, T)
    hm.avatar(ctx, 0, 0, 1.4, shirt="#2f6bd8", pants="#3fae4a", expr="sad", t=T)
    ctx.restore()
    sp.stars_around(ctx, 290, 1080, 110, T)
    rk = clamp((T - 18.45) / 0.8)   # the crown pops off and rolls away
    ctx.save()
    cx = lerp(250, 620, ease(rk))
    ctx.translate(cx, 1120 - math.sin(rk * math.pi) * 120)
    ctx.rotate(rk * 6)
    hm.crown(ctx, 0, 30, 0.75)
    ctx.restore()
    you(ctx, 190, 1100, 1.4, T, expr="happy", wave=True)
    label(ctx, "K.O.", 360, 600, 110, hexc("#ff4f5a"), fg=OUT, scale=pop(T - 18.76), tilt=-0.08)


# ================================================================ second 8 - loot
def s_drop(ctx, t, d):
    T = 19.42 + t
    sp.arena(ctx, T, crack=1.0)
    tint(ctx, (1, 0.8, 0.3), 0.12)
    fall = clamp((T - 19.75) / 0.52)
    cy = lerp(-200, 1150, fall * fall)
    s2.chest(ctx, 430, cy, 1.15, T)
    landed = T >= 20.27
    if landed:
        k = clamp((T - 20.27) / 0.5)
        for i in range(6):
            ctx.new_sub_path()
            ctx.arc(430 + (i - 2.5) * 70 * (1 + k), 1140, 30 * (1 + k), 0, 2 * math.pi)
        ctx.set_source_rgba(0.85, 0.8, 0.9, 0.7 * (1 - k))
        ctx.fill()
    you(ctx, 160, 1150, 1.4, T, expr="shock" if landed else "happy", jump=20 if 20.27 < T < 20.45 else 0)
    label(ctx, "LOOT DROP!", 400, 600, 52, hexc("#ffd84a"), fg=OUT, scale=pop(T - 20.27), tilt=-0.05)


def s_billion(ctx, t, d):
    T = 20.60 + t
    sp.arena(ctx, T, crack=1.0)
    tint(ctx, (1, 0.8, 0.3), 0.2)
    open_k = ease((T - 20.6) / 0.35)
    s2.chest(ctx, 440, 1150, 1.15, T, open_k=open_k)
    for i in range(16):   # coin fountain
        ph = (T * 1.2 + i / 16) % 1
        a = (i * 0.61) % 1 - 0.5
        hm.robux_coin(ctx, 440 + a * 520 * ph, 1000 - math.sin(ph * math.pi) * 520, 0.55, spin=T * 4 + i)
    n = int(lerp(0, 1_000_000_000, ease((T - 20.6) / 0.79)))
    text(ctx, f"{n:,}", 380, 720, 56, hexc("#ffd84a"), outline=True)
    you(ctx, 170, 1150, 1.4, T, expr="happy", wave=True)
    label(ctx, "1 BILLION R$", 380, 590, 50, hexc("#e8574a"), scale=pop(T - 21.0), tilt=-0.05)


# ================================================================ second 7 - shop
def s_shopfront(ctx, t, d):
    T = 22.06 + t
    s2.shop_front(ctx, T)
    k = ease((T - 22.06) / 0.85)
    you(ctx, lerp(80, 360, k), 1042, lerp(1.5, 1.25, k), T, expr="grin", walk=T * 3.2 if k < 1 else 0)


def s_cart(ctx, t, d):
    T = 23.09 + t
    sp.shop_wall(ctx, T, bought_at=23.35)
    k = clamp((T - 23.09) / 1.98)
    cx = lerp(250, 560, k)
    arrived = 0
    for i in range(18):   # cards fly off the shelves into the cart
        t0 = 23.35 + i * 0.1
        f = clamp((T - t0) / 0.3)
        if f >= 1:
            arrived += 1
        elif f > 0:
            r, c = divmod(i, 6)
            sx, sy = -120 + 130 + c * 165, 500 + r * 270
            col, g, lab = sp.PASSES[i % len(sp.PASSES)]
            sp.gamepass(ctx, lerp(sx, cx, f), lerp(sy, 1050, f) - math.sin(f * math.pi) * 120, 0.5, col, g, lab)
    s2.cart(ctx, cx, 1240, 1.0, min(15, arrived), T)
    you(ctx, cx - 250, 1240, 1.3, T, expr="grin", walk=T * 3)
    label(ctx, f"PASSES: {arrived}", 360, 430, 46, hexc("#4fd16a"), scale=1.0 if T > 23.4 else pop(T - 23.3), tilt=0)


def s_case(ctx, t, d):
    T = 25.07 + t
    sp.dark_bg(ctx, "#101018", "#1c1f33")
    s2.glass_case(ctx, 360, 1160, 1.05, T)
    sp.sparkles(ctx, T, 360, 800, spread=260, n=12, seed=7)
    label(ctx, "INCLUDING...", 360, 470, 46, hexc("#ffd84a"), fg=OUT, scale=pop(T - 25.07), tilt=-0.05)


def s_morph(ctx, t, d):
    T = 25.96 + t
    s2.town(ctx)
    if T < 26.58:
        ctx.save()
        ctx.translate(360, 1000)
        ctx.scale(math.cos((T - 25.96) * 18), 1)   # spinning
        ctx.translate(-360, -1000)
        you(ctx, 360, 1000, 1.6, T, expr="shock")
        ctx.restore()
        sp.sparkles(ctx, T, 360, 820, spread=200, n=16, seed=9)
    k = clamp((T - 26.58) / 0.79)
    if T >= 26.69:
        s2.toaster_you(ctx, 360, 1020, lerp(0.35, 1.25, ease((T - 26.69) / 0.68)), T, toast=1.0)
    if 26.5 < T < 27.3:   # poof cloud
        for i in range(9):
            a = i * 2 * math.pi / 9
            ctx.new_sub_path()
            ctx.arc(360 + math.cos(a) * 140 * (0.5 + k), 860 + math.sin(a) * 110 * (0.5 + k), 90 * (1 - 0.6 * k), 0,
                    2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.95 * (1 - k))
        ctx.fill()
    label(ctx, "TRANSFORM!", 360, 520, 52, hexc("#9d7fd6"), scale=pop(T - 25.98), tilt=-0.05)


def s_toaster(ctx, t, d):
    T = 27.37 + t
    s2.town(ctx, horizon=1000)
    stomp = abs(math.sin((T - 27.37) * 6))
    s2.toaster_you(ctx, 380, 1160 - stomp * 30, 1.5, T, toast=1.0, mad=True)
    for i in range(4):   # tiny players running away
        x = (i * 190 + (T - 27.37) * (220 if i % 2 else -220)) % 900 - 90
        hm.avatar(ctx, x, 1230, 0.5, shirt=("#e8574a", "#f2b84b", "#9d7fd6", "#4f8bff")[i], expr="shock",
                  t=T + i, walk=T * 4)
    label(ctx, "GIANT TOASTER!", 380, 470, 50, hexc("#e8574a"), scale=pop(T - 27.37), tilt=-0.05)


# ================================================================ second 6 - plaza
def crowd(ctx, T, crowns_t=None, y0=1080):
    cols = ["#e8574a", "#f2b84b", "#9d7fd6", "#4f8bff", "#e57373", "#7cc08a"]
    i = 0
    for r in range(2):
        for c in range(5):
            x = 70 + c * 145 + (r % 2) * 70
            y = y0 + r * 140
            s = 0.8 + r * 0.15
            hm.avatar(ctx, x, y, s, shirt=cols[(i * 2) % len(cols)], pants="#2b45a6", hair=("curly", None)[i % 2],
                      expr="happy", t=T + i * 0.3, wave=(i % 3 == 0), jump=abs(math.sin(T * 5 + i)) * 12)
            if crowns_t is not None:
                k = ease((T - crowns_t - i * 0.06) / 0.35)
                if k > 0:
                    hm.crown(ctx, x, lerp(-100, y - 216 * s, k), 0.4 * s)
            i += 1


def bill_text(c, x, y, w, h, T):
    text(c, "LIKE &", x + w / 2, y + h * 0.36, h * 0.2, hexc("#ffffff"), outline=True)
    text(c, "SUBSCRIBE?", x + w / 2, y + h * 0.66, h * 0.2, hexc("#ffd84a"), outline=True)


def bill_buttons(c, x, y, w, h, T):
    hm.like_button(c, x + w / 2, y + h * 0.3, 1.25, pressed=clamp((T - 29.9) / 0.12))
    hm.subscribe_button(c, x + w / 2, y + h * 0.7, 1.15, pressed=clamp((T - 30.4) / 0.12))
    k = ease((T - 29.76) / 0.14)
    cy = y + h * (0.3 if T < 30.2 else lerp(0.3, 0.7, ease((T - 30.2) / 0.2)))
    hm.cursor(c, lerp(x + w * 0.9, x + w * 0.55, k), cy + 10, 1.3,
              click=1.0 if (29.9 < T < 30.05 or 30.4 < T < 30.55) else 0.0)


def s_plaza(ctx, t, d):
    T = 28.38 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1000)
    s2.billboard(ctx, 360, 330, 560, 330, T, bill_text)
    crowd(ctx, T)
    label(ctx, "EVERYONE", 360, 760, 52, hexc("#4f8bff"), scale=pop(T - 29.29), tilt=0.04)


def s_buttons(ctx, t, d):
    T = 29.76 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1000)
    s2.billboard(ctx, 360, 360, 600, 440, T, bill_buttons)
    crowd(ctx, T, y0=1100)


def s_crowns(ctx, t, d):
    T = 31.02 + t
    hm.game_sky(ctx)
    hm.baseplate(ctx, 1000)
    crowd(ctx, T, crowns_t=31.07, y0=1060)
    k = ease((T - 31.5) / 0.3)
    you(ctx, 360, 1160, 1.5, T, expr="happy", wave=True)
    if k > 0:
        hm.crown(ctx, 360, lerp(-120, 1160 - 216 * 1.5, k), 0.7)
    sp.sparkles(ctx, T, 360, 700, n=12, seed=2)
    label(ctx, "FREE GOLDEN CROWN", 360, 560, 40, hexc("#ffd84a"), fg=OUT, scale=pop(T - 31.79), tilt=-0.05)


# ================================================================ second 5 - hatch
def hatchery(ctx, T):
    sp.dark_bg(ctx, "#1c1f33", "#3a2a60")
    box_floor = (-600, 1150, 2000, 900)
    hm.box(ctx, *box_floor, "#4a3a7a", "#2a1f4a", r=0)
    for k in range(6):
        glow(ctx, -60 + k * 170, 1150, 120, (0.6, 0.5, 1), 0.25)


def s_hatch(ctx, t, d):
    T = 32.29 + t
    hatchery(ctx, T)
    crack = clamp((T - 33.33) / 0.37)
    s2.incubator(ctx, 440, 1160, 1.15, T, crack=crack, glow_k=crack)
    you(ctx, 150, 1160, 1.3, T, expr="shock" if crack > 0 else "happy", wave=True)
    label(ctx, "HATCH!", 400, 560, 60, hexc("#9d7fd6"), scale=pop(T - 33.33), tilt=-0.05)


def s_legend(ctx, t, d):
    T = 33.70 + t
    hatchery(ctx, T)
    sp.burst_bg(ctx, T, "#fff3a8", "#3a2a60", cx=420, cy=900, a=0.14)
    k = clamp((T - 33.7) / 0.5)
    for i in range(6):   # egg shell pieces flying out
        a = i * math.pi / 3 + 0.3
        ctx.save()
        ctx.translate(420 + math.cos(a) * 420 * k, 940 + math.sin(a) * 300 * k + 500 * k * k)
        ctx.rotate(k * 5 + i)
        ctx.move_to(-40, 0)
        ctx.line_to(0, -36)
        ctx.line_to(44, 6)
        ctx.line_to(0, 30)
        ctx.close_path()
        hm._shade_fill(ctx, hexc("#fff6e0"), hexc("#e8c98a"), -36, 30, 4)
        ctx.restore()
    sp.pet(ctx, 420, 1110 - 30 * math.sin(T * 3), 0.95 * pop(T - 33.72), T)
    s2.rarity_banner(ctx, 360, 470, 1.0, "LEGENDARY", T, sc=pop(T - 33.93))
    you(ctx, 140, 1180, 1.2, T, expr="shock" if T < 34.5 else "happy", wave=T > 34.5)
    flash(ctx, 0.9 - (T - 33.7) * 3)


# ================================================================ four, three - cross-cut
def s_four(ctx, t, d):
    T = 36.00 + t
    pl = sp.course(ctx, T, n=8)
    tint(ctx, (0.6, 0.0, 0.05), 0.25 + 0.12 * math.sin(T * 18))
    ctx.save()
    ctx.translate(360, 620)
    sc = 2.6 * (1 + 0.15 * math.exp(-8 * (T - 36.0)))
    ctx.scale(sc, sc)
    ctx.translate(-360, -186)
    sp.hud(ctx, "0:04", bump=0.0, urgent=True)
    ctx.restore()
    you(ctx, 360, 1150, 1.4, T, expr="shock", walk=T * 5)
    sweat(ctx, 360, 1150 - 176 * 1.4, 45, T)


def s_three(ctx, t, d):
    T = 36.68 + t
    room(ctx, T, kid="shock", arms=("up", "up"), shades=True, watch=(0.3, "3"))
    tint(ctx, (0.8, 0.05, 0.1), 0.15)
    sweat(ctx, KID_X, 1180 - 3.71 * 70, 70, T)
    sc = pop(T - 36.7)
    if sc > 0.02:
        ctx.save()
        ctx.translate(470, 560)
        ctx.scale(sc, sc)
        ctx.translate(-470, -560)
        sp.stopwatch(ctx, 470, 560, 150, 0.3, "3", T, num_col="#d63c3c")
        ctx.restore()


# ================================================================ the secret button
def s_crack(ctx, t, d):
    T = 37.24 + t
    s2.secret_wall(ctx, T, crack=clamp((T - 37.24) / 0.35), hole=ease((T - 37.98) / 0.45))
    you(ctx, 170, 1110, 1.4, T, expr="shock")
    flash(ctx, 0.6 - (T - 37.24) * 4)
    label(ctx, "SUDDENLY!", 380, 470, 56, hexc("#ffd84a"), fg=OUT, scale=pop(T - 37.26), tilt=-0.05)
    if T > 37.98:
        label(ctx, "!", 170, 760, 70, hexc("#e8574a"), scale=pop(T - 37.98), tilt=0)


def secret_room(ctx, T):
    sp.dark_bg(ctx, "#0c2414", "#14361f")
    hm.box(ctx, -600, 1120, 2000, 900, "#1f4a2a", "#123018", r=0)
    for k in range(6):
        ph = (T * 0.5 + k / 6) % 1
        glow(ctx, 60 + k * 120, 1100 - ph * 700, 26, (0.6, 1, 0.7), 0.6 * (1 - ph))


def s_secret(ctx, t, d):
    T = 38.47 + t
    secret_room(ctx, T)
    sp.secret_button(ctx, 360, 1080, 1.3, T)
    sp.sparkles(ctx, T, 360, 820, spread=260, n=12, seed=6)
    label(ctx, "SECRET", 360, 470, 64, hexc("#9d7fd6"), fg=OUT, scale=pop(T - 38.47), tilt=-0.06)
    label(ctx, "EXTRA TIME", 360, 600, 50, hexc("#4fd16a"), fg=OUT, scale=pop(T - 38.94), tilt=0.04)


def s_smash(ctx, t, d):
    T = 40.01 + t
    secret_room(ctx, T)
    hit = 40.13
    k = (T - hit) / 0.6
    sp.secret_button(ctx, 360, 1080, 1.3, T, pressed=1.0 if T >= hit else 0.0)
    sp.shockwave(ctx, 360, 960, k, col=(0.6, 1, 0.7))
    sp.starburst(ctx, 360, 930, 170, k * 2, "#c8ffd0", "#4fd16a")
    ay = lerp(560, 920, ease((T - 40.01) / 0.12)) if T < hit else 920 - math.sin(min(1, k * 2) * math.pi) * 60
    you(ctx, 360, ay, 1.3, T, expr="angry", wave=True)
    flash(ctx, 0.6 - max(0.0, T - hit) * 4 if T >= hit else 0)
    label(ctx, "SMASH!", 360, 470, 84, hexc("#4fd16a"), fg=OUT, scale=pop(T - hit), tilt=-0.08)


def s_slowmo(ctx, t, d):
    T = 40.72 + t
    s2.town(ctx, horizon=1000)
    tint(ctx, (0.2, 0.35, 0.8), 0.35)
    slow = (T - 40.72) * 0.08
    for i in range(12):   # coins, toast and confetti frozen in the air
        hm.robux_coin(ctx, 40 + i * 58, 380 + (i * 97) % 420 + math.sin(slow * 6 + i) * 10, 0.55, spin=slow * 3 + i)
    for i, (x, y) in enumerate(((120, 640), (600, 560))):
        ctx.save()
        ctx.translate(x, y + math.sin(slow * 5 + i) * 8)
        ctx.rotate(0.4 + i + slow)
        hm.rrect(ctx, -40, -44, 80, 88, 16)
        hm._shade_fill(ctx, hexc("#f2c685"), hexc("#c98a4a"), -44, 44, 4)
        ctx.restore()
    sp.shockwave(ctx, 360, 760, ((T - 40.72) / 1.6) % 1.0, col=(0.7, 0.85, 1), r_max=600)
    you(ctx, 360, 1000 - 120 - math.sin(slow * 4) * 20, 1.5, T, expr="happy", wave=True)
    label(ctx, "SLOW MOTION", 360, 520, 52, hexc("#4f8bff"), scale=pop(T - 42.08), tilt=-0.05)


# ================================================================ real life: mom vs wi-fi
def s_momwalk(ctx, t, d):
    T = 42.81 + t
    room(ctx, T, kid="grin", shades=True, watch=(0.3, "3"), router=True, night=0.0)
    k = ease((T - 42.81) / 1.3)
    mom(ctx, lerp(110, 250, k), 1300, 1.2, "cold", T, pose="walk" if k < 1 else "stand", walk_phase=T * 0.6,
        arms=("down", "point"), look=0.6, bob=0.3)
    tint(ctx, (0.04, 0.05, 0.18), 0.45)
    glow(ctx, 560, 600, 200, (0.4, 0.7, 1), 0.3)
    label(ctx, "MOM!", 300, 560, 56, hexc("#9d7fd6"), scale=pop(T - 43.38), tilt=-0.05)


def s_reach(ctx, t, d):
    T = 44.18 + t
    s2.wall_and_desk(ctx, y_desk=1200)
    hm.box(ctx, 100, 700, 560, 30, "#b07a4a", "#8a5a33", r=4)
    hm.router(ctx, 330, 688, 1.25, T, on=1.0)
    tint(ctx, (0.04, 0.05, 0.18), 0.4)
    k = ease((T - 44.18) / 1.25)
    hand(ctx, lerp(-260, 470, k), 1000, 1.5, flip=1, col="#fce7d6")
    label(ctx, "WI-FI!", 360, 430, 70, hexc("#e8323a"), scale=pop(T - 44.73), tilt=0.06)


def s_enter(ctx, t, d):
    T = 45.43 + t
    s2.wall_and_desk(ctx, y_desk=520)
    hit = 45.6
    s2.keyboard(ctx, 330, 760, 1.15, T, enter_k=1.0 if T >= hit else 0.0)
    ex, ey = 330 + 231 * 1.15, 760 - 30
    k = ease((T - 45.43) / (hit - 45.43))
    s2.hand_up(ctx, ex + 10, lerp(1400, ey + 205, k), 1.0, ang=-0.12, point=True)
    if T >= hit:
        glow(ctx, ex, ey, 220, (0.5, 1, 0.6), 0.8 * math.exp(-4 * (T - hit)))
        sp.shockwave(ctx, ex, ey, (T - hit) / 0.5, col=(0.6, 1, 0.7), r_max=300)
    label(ctx, "TOO LATE!", 360, 430, 80, hexc("#e8323a"), fg=OUT, scale=pop(T - 45.73), tilt=-0.06)


def trophy(ctx, x, y, s):
    hm.box(ctx, x - 70 * s, y + 70 * s, 140 * s, 40 * s, "#8a5a33", "#6b4422", r=8 * s, lw=4 * s)
    hm.box(ctx, x - 16 * s, y + 20 * s, 32 * s, 55 * s, "#ffd84a", "#d6a23a", r=6 * s, lw=4 * s)
    ctx.move_to(x - 80 * s, y - 110 * s)
    ctx.line_to(x + 80 * s, y - 110 * s)
    ctx.curve_to(x + 80 * s, y, x + 30 * s, y + 25 * s, x, y + 25 * s)
    ctx.curve_to(x - 30 * s, y + 25 * s, x - 80 * s, y, x - 80 * s, y - 110 * s)
    ctx.close_path()
    hm._shade_fill(ctx, hexc("#ffe27a"), hexc("#d6a23a"), y - 110 * s, y + 25 * s, 5 * s)
    text(ctx, "★", x, y - 50 * s, 60 * s, (1, 1, 1), outline=True)


def s_trophy(ctx, t, d):
    T = 46.06 + t
    hm.bedroom(ctx, T)
    glow(ctx, 360, 900, 440, (1, 0.85, 0.4), 0.4)
    KID_SH.draw(ctx, 290, 1260, 1.45, "grin", T, arms=("down", "point"), bob=0.7)
    r = 64 * 1.45
    trophy(ctx, 290 + 1.91 * r + 10, 1260 - 2.83 * r - 60, 0.85)
    sp.sparkles(ctx, T, 360, 900, spread=280, n=14)
    label(ctx, "SPEEDRUNNER", 360, 620, 54, hexc("#ffd84a"), fg=OUT, scale=pop(T - 46.62), tilt=-0.05)


def s_plus(ctx, t, d):
    T = 47.19 + t
    s2.wall_and_desk(ctx, y_desk=820)
    k = clamp((T - 47.51) / 0.25)
    hit = T >= 47.51
    sp.stopwatch(ctx, 360, 600, 180 * (1 + 0.15 * math.exp(-8 * max(0, T - 47.51))), 0.3 + 0.7 * k,
                 "13" if hit else "3", T, ring="#4fd16a" if hit else "#e8574a",
                 num_col="#2e9c46" if hit else "#d63c3c")
    if not hit:   # "+10" flies into the stopwatch
        f = ease((T - 47.19) / 0.32)
        text(ctx, "+10", lerp(640, 420, f), lerp(260, 520, f), 90, hexc("#4fd16a"), outline=True)
    hand(ctx, -40, 1080, 1.4, flip=1, col="#fce7d6")   # mom's hand, frozen
    label(ctx, "+10 SECONDS!", 360, 940, 60, hexc("#4fd16a"), fg=OUT, scale=pop(T - 47.51), tilt=-0.05)


def s_momshock(ctx, t, d):
    T = 48.38 + t
    room(ctx, T, kid="grin", shades=True, watch=(1.0, "13"), router=True)
    mom(ctx, 120, 1300, 1.2, "shock", T, arms=("up", "up"), bob=1.5)
    tint(ctx, (0.04, 0.05, 0.18), 0.25)
    label(ctx, "?!", 200, 560, 90, hexc("#e8323a"), scale=pop(T - 48.4), tilt=0.1)


def s_what(ctx, t, d):
    T = 49.01 + t
    hm.bedroom(ctx, T)
    tint(ctx, (0.9, 0.2, 0.15), 0.15)
    mom(ctx, 360, 1260, 1.55, keyed(T, [(0, "shock"), (49.3, "angry")]), T, arms=("hip", "hip"), bob=2.0)
    r = 64 * 1.55
    hx, hy = 360 + 0.6 * r, 1260 - 3.9 * r
    for k in range(3):   # anger twitch marks
        a = -0.8 + k * 0.5
        ctx.move_to(hx + math.cos(a) * 0.5 * r, hy + math.sin(a) * 0.5 * r)
        ctx.line_to(hx + math.cos(a) * 0.8 * r, hy + math.sin(a) * 0.8 * r)
    ctx.set_source_rgb(*hexc("#e8323a"))
    ctx.set_line_width(8)
    ctx.stroke()
    label(ctx, "WHAT?!", 360, 600, 76, hexc("#e8323a"), fg=OUT, scale=pop(T - 49.05), tilt=-0.05)


def s_again(ctx, t, d):
    T = 49.62 + t
    room(ctx, T, kid="grin", shades=True, watch=(1.0, "13"))
    mom(ctx, 590, 1300, 1.15, "angry", T, arms=("up", "up"), bob=2.0)
    for k in range(3):   # steam
        ph = (T * 1.5 + k / 3) % 1
        ctx.new_sub_path()
        ctx.arc(560 + k * 40, 760 - ph * 160, 18 + ph * 20, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - ph))
        ctx.fill()
    label(ctx, "NOT AGAIN!", 360, 560, 64, hexc("#e8323a"), fg=OUT, scale=pop(T - 49.89), tilt=-0.05)


def s_comments(ctx, t, d):
    T = 50.51 + t
    sp.burst_bg(ctx, T, "#dfe9ff", "#4f8bff")
    sp.loop_arrow(ctx, 360, 760, 330, T)
    s2.phone_comments(ctx, 360, 790, 0.92, T, 50.51, typed=(T - 50.89) / 0.45)
    label(ctx, "COMMENT \"LOOP\"", 360, 300, 48, hexc("#e8574a"), scale=pop(T - 50.89), tilt=-0.04)


def s_end(ctx, t, d):
    s_open(ctx, t, d, T0=0.0, frozen=True)   # exactly the first frame: the Short loops


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def push(t0, t1, z0, z1, c0, c1, amp=1.9):
    """Camera move across a shot; amp exaggerates zoom and travel (v1 measured too calm)."""
    z1 = z0 + (z1 - z0) * amp
    c1 = (c1[0] + (c1[0] - c0[0]) * (amp - 1), c1[1] + (c1[1] - c0[1]) * (amp - 1))
    return [(t0, z0, c0), (t1, z1, c1, max(0.2, t1 - t0))]


shot(0.0, s_open, [(0.0, 1.0, (380, 800)), (0.43, 1.2, (230, 820), 0.4)], dof=2)
shot(0.80, s_finger, push(0.80, 1.51, 1.05, 1.2, (360, 900), (380, 880)), dof=2)
shot(1.51, s_timer, push(1.51, 2.32, 1.05, 1.2, (360, 820), (340, 780)), shake=(0.03, 6),
     keep=[(130, 380, 510, 890)])
shot(2.32, s_ots, push(2.32, 3.22, 1.0, 1.15, (380, 820), (440, 780)), dof=1)
shot(3.22, s_set, push(3.22, 4.27, 1.0, 1.15, (360, 680), (360, 640)), shake=(0.24, 7))
shot(4.27, s_bed, [(4.27, 1.1, (230, 880)), (4.91, 1.05, (470, 900), 0.5)], dof=2)
shot(5.23, s_shock, push(5.23, 6.46, 1.0, 1.2, (360, 940), (360, 920)), shake=(0.52, 10))
shot(6.46, s_loading, [(6.46, 1.0, (430, 860)), (6.68, 1.15, (470, 840), 0.3)], dof=2)
shot(7.47, s_shades, [(7.47, 1.05, (360, 940)), (8.3, 1.2, (360, 920), 0.4)], dof=2)
shot(8.39, s_typing, push(8.39, 9.40, 1.0, 1.15, (360, 760), (360, 720)), shake=(0.0, 4))
shot(9.40, s_dive, [(9.40, 1.0, (430, 860)), (9.86, 1.5, (560, 820), 0.4), (10.22, 4.3, (560, 811), 0.36)])
shot(10.22, s_spawn, [(10.22, 1.0, (300, 840)), (10.94, 1.05, (330, 840), 0.4), (11.6, 1.15, (470, 820), 0.6)])
shot(11.67, s_hundred, [(11.67, 1.3, (360, 1060)), (12.4, 0.95, (360, 700), 0.6)])
shot(12.75, s_jump, [(12.75, 1.05, (220, 820)), (13.55, 0.8, (1450, 560), 0.7), (14.15, 1.0, (2845, 780), 0.55)])
shot(14.20, s_finish, push(14.20, 15.05, 1.0, 1.15, (380, 840), (380, 820)), shake=(0.0, 8))
shot(15.05, s_rumble, push(15.05, 16.03, 1.0, 1.1, (360, 880), (360, 900)), shake=(0.39, 10), dof=2)
shot(16.03, s_king, [(16.03, 1.0, (420, 960)), (16.61, 0.95, (420, 860), 0.5)], shake=(0.2, 8))
shot(17.16, s_boom, push(17.16, 17.72, 1.1, 1.2, (380, 860), (390, 850)), shake=(0.0, 18))
shot(17.72, s_onehit, push(17.72, 18.33, 1.0, 1.1, (380, 880), (450, 880)), shake=(0.27, 9))
shot(18.33, s_ko, push(18.33, 19.42, 1.0, 1.15, (380, 900), (380, 880)), shake=(0.43, 7))
shot(19.42, s_drop, push(19.42, 20.60, 1.0, 1.1, (360, 880), (380, 900)), shake=(0.85, 12))
shot(20.60, s_billion, push(20.60, 22.06, 1.0, 1.15, (380, 880), (380, 860)))
shot(22.06, s_shopfront, push(22.06, 23.09, 1.0, 1.15, (360, 820), (380, 860)), keep=[(120, 400, 600, 530)])
shot(23.09, s_cart, [(23.09, 1.0, (330, 840)), (25.0, 1.0, (520, 840), 1.8)])
shot(25.07, s_case, push(25.07, 25.96, 1.0, 1.3, (360, 860), (360, 820)), dof=1)
shot(25.96, s_morph, push(25.96, 27.37, 1.0, 1.1, (360, 860), (360, 820)), shake=(0.62, 12))
shot(27.37, s_toaster, push(27.37, 28.38, 1.15, 1.0, (380, 900), (380, 860)), shake=(0.0, 6),
     keep=[(120, 760, 640, 1200)])
shot(28.38, s_plaza, [(28.38, 1.0, (360, 980)), (29.29, 0.95, (360, 800), 0.5)], keep=[(62, 312, 658, 680)])
shot(29.76, s_buttons, push(29.76, 31.02, 1.05, 1.15, (360, 680), (360, 660)), keep=[(42, 342, 678, 818)])
shot(31.02, s_crowns, push(31.02, 32.29, 1.0, 1.15, (360, 900), (360, 880)))
shot(32.29, s_hatch, push(32.29, 33.70, 1.0, 1.15, (360, 900), (400, 880)), shake=(1.04, 8),
     keep=[(190, 820, 690, 1240)])
shot(33.70, s_legend, push(33.70, 36.00, 1.0, 1.15, (360, 880), (380, 840)), keep=[(190, 410, 630, 1130)])
shot(36.00, s_four, push(36.00, 36.68, 1.0, 1.1, C, C), shake=(0.0, 9))
shot(36.68, s_three, push(36.68, 37.24, 1.05, 1.15, (420, 760), (440, 740)), shake=(0.02, 9),
     keep=[(300, 340, 640, 760)])
shot(37.24, s_crack, push(37.24, 38.47, 1.0, 1.15, (330, 860), (400, 840)), shake=(0.0, 9))
shot(38.47, s_secret, push(38.47, 40.01, 1.0, 1.3, (360, 860), (360, 880)), keep=[(110, 880, 610, 1160)])
shot(40.01, s_smash, push(40.01, 40.72, 1.2, 1.05, (360, 900), (360, 860)), shake=(0.12, 16),
     keep=[(110, 880, 610, 1160)])
shot(40.72, s_slowmo, push(40.72, 42.81, 1.0, 1.12, (360, 820), (360, 800)))
shot(42.81, s_momwalk, push(42.81, 44.18, 1.0, 1.15, (330, 860), (380, 860)), dof=2)
shot(44.18, s_reach, push(44.18, 45.43, 1.0, 1.12, (380, 760), (420, 780), amp=1.0), shake=(0.55, 5),
     keep=[(100, 360, 660, 1060)])
shot(45.43, s_enter, push(45.43, 46.06, 1.0, 1.15, (380, 760), (430, 760)), shake=(0.17, 12))
shot(46.06, s_trophy, push(46.06, 47.19, 1.0, 1.15, (360, 940), (360, 920)), dof=2)
shot(47.19, s_plus, push(47.19, 48.38, 1.0, 1.15, (360, 700), (360, 680)), shake=(0.32, 9),
     keep=[(160, 330, 560, 820)])
shot(48.38, s_momshock, push(48.38, 49.01, 1.0, 1.15, (330, 880), (300, 860)), shake=(0.02, 8))
shot(49.01, s_what, push(49.01, 49.62, 1.05, 1.2, (360, 940), (360, 920)), shake=(0.04, 10))
shot(49.62, s_again, push(49.62, 50.51, 1.0, 1.1, (430, 880), (460, 880)))
shot(50.51, s_comments, push(50.51, 52.20, 1.0, 1.08, (360, 740), (360, 760)), keep=[(130, 330, 590, 1200)])
shot(52.20, s_end, [(52.20, 1.15, (330, 820)), (TOTAL, 1.0, (380, 800), 0.91)], dof=2)
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- overlays: timer HUD + boss bar
HUD = [(10.22, "0:10", False), (15.44, "0:09", False), (19.83, "0:08", False), (22.47, "0:07", False),
       (28.77, "0:06", False), (32.71, "0:05", False), (36.00, "0:04", True), (36.68, "0:03", True)]
GAME = {s_spawn, s_hundred, s_jump, s_finish, s_rumble, s_king, s_boom, s_onehit, s_ko, s_drop, s_billion,
        s_shopfront, s_cart, s_case, s_morph, s_toaster, s_plaza, s_buttons, s_crowns, s_hatch, s_legend,
        s_crack, s_secret, s_smash, s_slowmo}
BOSS = {s_king, s_boom, s_onehit, s_ko}


def make_overlay(T0, boss):
    def ov(ctx, t, d):
        T = T0 + t
        cur = None
        for ts, txt, urg in HUD:
            if T >= ts:
                cur = (ts, txt, urg)
        if cur:
            sp.hud(ctx, cur[1], bump=math.exp(-9 * (T - cur[0])), urgent=cur[2])
        if boss and T >= 16.61:
            a = clamp((T - 16.61) / 0.2) * (1 - clamp((T - 18.9) / 0.4))
            shake = max(0.0, 1 - (T - 17.16) / 0.4) if T >= 17.16 else 0.0
            s2.boss_bar(ctx, boss_frac(T), a=a, shake=shake)
    return ov


for s in SHOTS:
    if s["draw"] in GAME:
        s["overlay"] = make_overlay(s["start"], s["draw"] in BOSS)
        s["top"] = 330 if s["draw"] in BOSS else 250

# ---------------------------------------------------------------- SFX (~1 per second, on visual events)
SFX = [
    (0.2, "tick.wav", 0.5), (0.43, "pop.wav", 0.7), (0.85, "pop.wav", 0.6), (1.55, "pop.wav", 0.8),
    (1.65, "tick.wav", 0.5), (1.95, "tick.wav", 0.5), (2.45, "pop.wav", 0.6), (2.95, "tick.wav", 0.9),
    (3.46, "thud.wav", 0.6), (3.5, "bell.wav", 0.5), (3.8, "tick.wav", 0.5), (4.05, "tick.wav", 0.5),
    (4.6, "step.wav", 0.5), (4.91, "pop.wav", 0.7), (5.75, "thud.wav", 0.9), (5.8, "boing.wav", 0.5),
    (6.68, "sting_low.wav", 0.6), (6.9, "thud.wav", 0.7), (7.85, "pop.wav", 0.6), (8.15, "sparkle.wav", 0.8),
    (8.2, "tick.wav", 0.6), *[(8.45 + k * 0.08, "tick.wav", 0.25) for k in range(10)], (8.88, "pop.wav", 0.8),
    (9.6, "sparkle.wav", 0.6), (10.22, "bell.wav", 0.6), (10.25, "tick.wav", 0.9),
    *[(10.98 + k * 0.2, "step.wav", 0.5) for k in range(3)], (11.0, "pop.wav", 0.6), (11.7, "pop.wav", 0.7),
    (12.2, "tick.wav", 0.4), (12.95, "boing.wav", 0.8), (13.9, "pop.wav", 0.7), (14.2, "thud.wav", 0.8),
    (14.25, "bell.wav", 0.8), (14.3, "sparkle.wav", 0.6), (15.3, "thud.wav", 0.6), (15.44, "tick.wav", 0.9),
    (15.6, "thud.wav", 0.6), (15.91, "pop.wav", 0.6), (16.2, "murmur.wav", 0.5), (16.61, "sting.wav", 0.8),
    (17.16, "thud.wav", 1.0), (17.2, "pop.wav", 0.8), (17.85, "pop.wav", 0.6), (17.99, "pop.wav", 0.8),
    (18.1, "tick.wav", 0.6), (18.4, "thud.wav", 0.8), (18.76, "pop.wav", 0.8), (19.0, "coin.wav", 0.4),
    (19.83, "tick.wav", 0.9), (20.27, "thud.wav", 1.0), (20.3, "pop.wav", 0.6), (20.65, "sparkle.wav", 0.8),
    *[(20.7 + k * 0.1, "coin.wav", 0.45) for k in range(6)], (21.0, "pop.wav", 0.8), (21.4, "bell.wav", 0.6),
    *[(22.1 + k * 0.2, "step.wav", 0.5) for k in range(4)], (22.47, "tick.wav", 0.9), (22.95, "page.wav", 0.6),
    (23.3, "pop.wav", 0.6), *[(23.4 + k * 0.2, "pop.wav", 0.3) for k in range(9)], (25.07, "sparkle.wav", 0.6),
    (25.6, "bell.wav", 0.5), (25.98, "pop.wav", 0.7), (26.2, "sparkle.wav", 0.5), (26.58, "thud.wav", 0.9),
    (26.62, "boing.wav", 0.8), (27.37, "pop.wav", 0.8), (27.5, "thud.wav", 0.6), (27.9, "thud.wav", 0.5),
    (28.77, "tick.wav", 0.9), (28.9, "murmur.wav", 0.5), (29.29, "pop.wav", 0.7), (29.9, "tick.wav", 0.9),
    (30.4, "tick.wav", 0.9), (30.45, "bell.wav", 0.5), *[(31.1 + k * 0.12, "pop.wav", 0.35) for k in range(5)],
    (31.79, "sparkle.wav", 0.8), (32.71, "tick.wav", 0.9), (33.33, "pop.wav", 0.7), (33.45, "tick.wav", 0.5),
    (33.58, "tick.wav", 0.5), (33.70, "thud.wav", 0.8), (33.72, "sparkle.wav", 0.9), (33.93, "bell.wav", 0.8),
    (34.53, "pop.wav", 0.6), (35.37, "pop.wav", 0.5), (36.0, "tick.wav", 1.0), (36.05, "thud.wav", 0.8),
    (36.3, "tick.wav", 0.6), (36.68, "tick.wav", 1.0), (36.72, "thud.wav", 0.9), (37.0, "tick.wav", 0.6),
    (37.24, "sting.wav", 0.8), (37.3, "thud.wav", 0.5), (37.98, "pop.wav", 0.7), (38.47, "pop.wav", 0.8),
    (38.6, "sparkle.wav", 0.6), (38.94, "pop.wav", 0.7), (39.68, "bell.wav", 0.5), (40.13, "thud.wav", 1.0),
    (40.15, "sparkle.wav", 0.8), (40.72, "sting_low.wav", 0.6), (41.4, "tick.wav", 0.3), (42.08, "pop.wav", 0.6),
    (42.9, "step.wav", 0.5), (43.38, "pop.wav", 0.6), (43.6, "step.wav", 0.5), (44.3, "murmur.wav", 0.4),
    (44.73, "sting.wav", 0.8), (45.6, "tick.wav", 1.0), (45.62, "thud.wav", 0.9), (45.73, "pop.wav", 0.8),
    (46.62, "sparkle.wav", 0.8), (46.65, "bell.wav", 0.6), (47.25, "pop.wav", 0.6), (47.51, "bell.wav", 0.9),
    (47.55, "coin.wav", 0.6), (48.4, "boing.wav", 0.7), (49.05, "thud.wav", 0.8), (49.3, "tick.wav", 0.5),
    (49.89, "pop.wav", 0.8), (50.2, "boing.wav", 0.4), (50.6, "pop.wav", 0.5), (50.89, "pop.wav", 0.8),
    *[(51.0 + k * 0.11, "tick.wav", 0.4) for k in range(4)], (51.6, "pop.wav", 0.5), (52.2, "sparkle.wav", 0.4),
]

if __name__ == "__main__":
    import json
    import engine
    import safezone
    engine.LIPSYNC = False
    json.dump([{"time": round(t, 3), "file": f, "volume": v} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    kw = {}
    if len(sys.argv) > 4:
        kw["frames"] = (int(sys.argv[3]), int(sys.argv[4]))
    safezone.fit(SHOTS, sys.modules[__name__])
    # seamless loop: the last framing equals the (fitted) first framing
    z0, c0 = SHOTS[0]["keys"][0][1], SHOTS[0]["keys"][0][2]
    SHOTS[-1]["keys"][-1] = (TOTAL, z0, c0, 0.91)
    render(SHOTS, TOTAL, sys.argv[1], grain=4, xfade=0.18, fade_out=0.0, fade_in=0.0, **kw)
