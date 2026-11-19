"""Blocky online-game places and UI props for the Toby story (Paper Billions look: flat vector, ink outlines,
soft practical light). Everything is original: generic block worlds, no real game's logo, font or UI.
Each place draws a full background in world coordinates and returns {"floor": y}.
"""
import math
import random

import cairo

from places import _grad
from sets import _fill_line, _slanted_font, glow
from style import INK, _rrect, hexc

W, H = 1280, 720


def _ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def _pop(k, dur=0.15):
    if k <= 0:
        return 0.0
    if k < dur:
        return 1.1 * _ease_out(k / dur)
    return 1.0 + 0.1 * math.exp(-(k - dur) * 25)


def _shade(col, f):
    return tuple(min(1.0, max(0.0, c * f)) for c in col)


def block(ctx, x, y, w, h, col, lw=4, top=14):
    """a toy block: front face + a lighter top face (fake 3D) + a few studs"""
    c = hexc(col) if isinstance(col, str) else col
    ctx.move_to(x, y)
    ctx.line_to(x + top, y - top)
    ctx.line_to(x + w + top, y - top)
    ctx.line_to(x + w, y)
    ctx.close_path()
    _fill_line(ctx, _shade(c, 1.25), lw * 0.8)
    ctx.move_to(x + w, y)
    ctx.line_to(x + w + top, y - top)
    ctx.line_to(x + w + top, y + h - top)
    ctx.line_to(x + w, y + h)
    ctx.close_path()
    _fill_line(ctx, _shade(c, 0.7), lw * 0.8)
    ctx.rectangle(x, y, w, h)
    _fill_line(ctx, c, lw)
    ctx.rectangle(x + 4, y + 4, w - 8, min(10, h * 0.25))
    ctx.set_source_rgba(1, 1, 1, 0.18)
    ctx.fill()


def _sky(ctx, t, top="#6fbdf5", bot="#d8f1ff", horizon=560, sun=(1060, 120)):
    ctx.set_source(_grad(ctx, 0, -200, 0, horizon, [(0, top), (1, bot)]))
    ctx.rectangle(-W, -H, 3 * W, H + horizon + 10)
    ctx.fill()
    glow(ctx, sun[0], sun[1], 260, hexc("#fff6c8"), 0.55)
    ctx.arc(sun[0], sun[1], 46, 0, 2 * math.pi)
    ctx.set_source_rgb(*hexc("#fff3b0"))
    ctx.fill()
    for i, (x0, y, s) in enumerate(((100, 90, 1.0), (520, 60, 0.8), (880, 150, 1.1), (1350, 80, 0.9), (-300, 140, 0.9))):
        x = (x0 + t * (6 + 3 * i)) % (3 * W) - W
        cloud(ctx, x, y, s)


def cloud(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_path()
    for dx, dy, r in ((-60, 10, 34), (-20, -12, 44), (30, -4, 40), (70, 12, 30)):
        ctx.new_sub_path()
        ctx.arc(dx, dy, r, 0, 2 * math.pi)
    ctx.rectangle(-90, 10, 180, 32)
    ctx.set_source_rgba(1, 1, 1, 0.92)
    ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ obby: jumps over lava
OBBY_PLATFORMS = [(390, 500, 96, "#e5483c"), (540, 450, 90, "#3b82d6"), (690, 486, 90, "#f2c230"),
                  (845, 430, 90, "#4cb050"), (1000, 470, 96, "#9b59d0"), (1150, 415, 90, "#e5483c"),
                  (1300, 455, 100, "#3b82d6")]


def obby(ctx, t, floor=560):
    _sky(ctx, t, horizon=620)
    # far floating islands
    for x, y in ((180, 330), (760, 300), (1210, 280)):
        block(ctx, x, y, 90, 30, "#8cb7d8", lw=2, top=8)
    # lava
    ctx.set_source(_grad(ctx, 0, 590, 0, 760, [(0, "#ffb02e"), (0.35, "#ff6a1a"), (1, "#b71c0c")]))
    ctx.rectangle(-W, 590, 3 * W, 2 * H)
    ctx.fill()
    glow(ctx, 640, 600, 900, hexc("#ff7a2a"), 0.35)
    for i in range(14):
        ph = (t * 0.8 + i * 0.37) % 1.0
        x = -200 + i * 130 + 30 * math.sin(i * 3.1)
        ctx.arc(x, 640 - 4 * ph, 8 + 10 * ph, math.pi, 2 * math.pi)
        ctx.set_source_rgba(1, 0.85, 0.4, 0.8 * (1 - ph))
        ctx.set_line_width(4)
        ctx.stroke()
    # spawn pad (where people stand)
    block(ctx, -W, floor, W + 320, 260, "#8a9aa8", top=16)
    for i in range(12):
        ctx.rectangle(-W + i * 110, floor + 30, 55, 26)
        ctx.set_source_rgba(1, 1, 1, 0.12)
        ctx.fill()
    _rrect(ctx, 120, floor - 6, 150, 18, 6)
    _fill_line(ctx, hexc("#4cb050"), 3)
    # the jumps
    for i, (x, y, w, col) in enumerate(OBBY_PLATFORMS):
        bob = 4 * math.sin(t * 1.6 + i)
        block(ctx, x, y + bob, w, 36, col, top=12)
    # finish flag
    ctx.move_to(1420, 415)
    ctx.line_to(1420, 250)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(6)
    ctx.stroke()
    for r in range(3):
        for k in range(4):
            ctx.rectangle(1423 + k * 22, 252 + r * 20, 22, 20)
            ctx.set_source_rgb(*((0.1, 0.1, 0.1) if (r + k) % 2 else (0.97, 0.97, 0.97)))
            ctx.fill()
    return {"floor": floor}


def welcome_sign(ctx, x, k, s=1.0, rainbow_t=0.0):
    """giant WELCOME sign dropping down over the first jump (k = s since it started falling)"""
    if k <= 0:
        return
    drop = 1 - _ease_out(k / 0.32)
    bounce = 18 * math.exp(-max(0, k - 0.32) * 9) * math.sin(max(0, k - 0.32) * 26)
    ctx.save()
    ctx.translate(x, 300 - 900 * drop - bounce)
    ctx.scale(s, s)
    for px in (-230, 230):
        ctx.rectangle(px - 16, 40, 32, 600)
        _fill_line(ctx, hexc("#8a5a32"), 5)
    _rrect(ctx, -330, -60, 660, 330, 24)
    _fill_line(ctx, hexc("#fff4d6"), 8)
    _rrect(ctx, -305, -36, 610, 282, 16)
    ctx.set_source_rgb(*hexc("#ffe08a"))
    ctx.fill()
    txt = "WELCOME!!!"
    _slanted_font(ctx, 112)
    ext = ctx.text_extents(txt)
    xx = -ext.x_advance / 2
    cols = ["#e5483c", "#f28b2c", "#f2c230", "#4cb050", "#3b82d6", "#9b59d0"]
    for i, ch in enumerate(txt):
        e = ctx.text_extents(ch)
        ctx.move_to(xx, 60 + 6 * math.sin(rainbow_t * 6 + i))
        ctx.text_path(ch)
        ctx.set_source_rgb(*hexc(cols[i % len(cols)]))
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(3)
        ctx.stroke()
        xx += e.x_advance
    _slanted_font(ctx, 44)
    sub = "EVERYONE!  :)"
    e = ctx.text_extents(sub)
    ctx.move_to(-e.x_advance / 2, 170)
    ctx.set_source_rgb(*hexc("#c8312c"))
    ctx.show_text(sub)
    for i in range(6):          # little stars
        a = rainbow_t * 3 + i
        sx, sy = -300 + i * 120, -70 + 10 * math.sin(a)
        ctx.arc(sx, sy, 7 + 3 * math.sin(a * 2), 0, 2 * math.pi)
        ctx.set_source_rgb(*hexc("#f2c230"))
        ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ race track
def race_track(ctx, t, floor=650):
    _sky(ctx, t, top="#78c2f2", bot="#e6f5ff", horizon=360, sun=(200, 90))
    # grandstand with a block crowd
    block(ctx, -W, 150, 3 * W, 200, "#7d8794", top=0)
    rnd = random.Random(5)
    cols = [hexc(c) for c in ("#e5483c", "#3b82d6", "#f2c230", "#4cb050", "#9b59d0", "#f28b2c")]
    for r in range(4):
        for i in range(70):
            x = -W + i * 56 + (r % 2) * 28
            y = 180 + r * 40 + 3 * math.sin(t * 6 + i + r)
            ctx.rectangle(x, y, 22, 22)
            ctx.set_source_rgb(*rnd.choice(cols))
            ctx.fill()
    for i in range(30):                     # pennant string
        x = -W + i * 130
        ctx.move_to(x, 140)
        ctx.line_to(x + 30, 172)
        ctx.line_to(x + 60, 140)
        ctx.set_source_rgb(*cols[i % len(cols)])
        ctx.fill()
    # curbs and asphalt
    for i in range(80):
        ctx.rectangle(-W + i * 50, 350, 50, 18)
        ctx.set_source_rgb(*((0.85, 0.15, 0.12) if i % 2 else (0.97, 0.97, 0.97)))
        ctx.fill()
    ctx.rectangle(-W, 368, 3 * W, 200)
    ctx.set_source(_grad(ctx, 0, 368, 0, 568, [(0, "#4a4a52"), (1, "#36363c")]))
    ctx.fill()
    for i in range(40):
        ctx.rectangle(-W + i * 120, 462, 60, 8)
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.fill()
    for r in range(10):                      # start line
        for k in range(2):
            ctx.rectangle(150 + k * 20, 368 + r * 20, 20, 20)
            ctx.set_source_rgb(*((0.1, 0.1, 0.1) if (r + k) % 2 else (0.97, 0.97, 0.97)))
            ctx.fill()
    for i in range(80):
        ctx.rectangle(-W + i * 50, 568, 50, 18)
        ctx.set_source_rgb(*((0.85, 0.15, 0.12) if i % 2 else (0.97, 0.97, 0.97)))
        ctx.fill()
    ctx.rectangle(-W, 586, 3 * W, H)
    ctx.set_source(_grad(ctx, 0, 586, 0, 760, [(0, "#58b04e"), (1, "#3b8a3a")]))
    ctx.fill()
    return {"floor": floor, "lane": 548}


def racecar(ctx, x, y, s=1.0, col="#e5483c", num="7", flip=False, speed=0.0):
    """blocky kart, y = bottom of the wheels; speed > 0 adds speed lines behind it"""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    if speed > 0:
        for i in range(4):
            ctx.move_to(-190 - 40 * i, -40 - i * 16)
            ctx.line_to(-190 - 40 * i - 120 * speed, -40 - i * 16)
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.set_line_width(5)
            ctx.stroke()
    c = hexc(col)
    ctx.move_to(-160, -30)
    ctx.line_to(-150, -78)
    ctx.line_to(-40, -84)
    ctx.line_to(-10, -120)
    ctx.line_to(70, -120)
    ctx.line_to(110, -80)
    ctx.line_to(170, -70)
    ctx.line_to(175, -30)
    ctx.close_path()
    _fill_line(ctx, c, 5)
    ctx.rectangle(-5, -114, 68, 32)
    _fill_line(ctx, hexc("#bfe3ff"), 3)
    ctx.rectangle(-185, -100, 24, 50)          # spoiler
    _fill_line(ctx, _shade(c, 0.7), 4)
    ctx.arc(-75, -58, 22, 0, 2 * math.pi)
    _fill_line(ctx, (0.98, 0.98, 0.98), 3)
    ctx.set_source_rgb(*INK)
    ctx.select_font_face("Kalam", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(30)
    e = ctx.text_extents(num)
    ctx.move_to(-75 - e.x_advance / 2, -47)
    ctx.show_text(num)
    for wx in (-105, 115):
        ctx.rectangle(wx - 34, -40, 68, 44)
        _fill_line(ctx, hexc("#222226"), 4)
        ctx.rectangle(wx - 12, -26, 24, 16)
        ctx.set_source_rgb(0.7, 0.7, 0.74)
        ctx.fill()
    ctx.restore()


def pizza(ctx, x, y, r=40, slices=True):
    ctx.arc(x, y, r, 0, 2 * math.pi)
    _fill_line(ctx, hexc("#e8a64a"), 3)
    ctx.arc(x, y, r * 0.82, 0, 2 * math.pi)
    ctx.set_source_rgb(*hexc("#f6d266"))
    ctx.fill()
    for i in range(6):
        a = i * 1.05 + 0.3
        ctx.arc(x + r * 0.5 * math.cos(a), y + r * 0.5 * math.sin(a), r * 0.13, 0, 2 * math.pi)
        ctx.set_source_rgb(*hexc("#c8312c"))
        ctx.fill()
    if slices:
        for i in range(3):
            a = i * math.pi / 3
            ctx.move_to(x - r * 0.82 * math.cos(a), y - r * 0.82 * math.sin(a))
            ctx.line_to(x + r * 0.82 * math.cos(a), y + r * 0.82 * math.sin(a))
        ctx.set_source_rgba(*INK, 0.5)
        ctx.set_line_width(2)
        ctx.stroke()


def pizza_stand(ctx, x, y, t=0.0):
    """free pizza stand on the grass (y = ground)"""
    for px in (-150, 150):
        ctx.rectangle(x + px - 8, y - 300, 16, 300)
        _fill_line(ctx, hexc("#8a5a32"), 4)
    for i in range(8):                        # striped awning
        ctx.move_to(x - 180 + i * 45, y - 300)
        ctx.line_to(x - 180 + (i + 1) * 45, y - 300)
        ctx.line_to(x - 180 + (i + 1) * 45, y - 250)
        ctx.curve_to(x - 180 + (i + 0.5) * 45 + 10, y - 232, x - 180 + (i + 0.5) * 45 - 10, y - 232,
                     x - 180 + i * 45, y - 250)
        ctx.close_path()
        _fill_line(ctx, hexc("#e5483c" if i % 2 else "#fff4d6"), 3)
    _rrect(ctx, x - 140, y - 380, 280, 70, 12)
    _fill_line(ctx, hexc("#fff4d6"), 5)
    _slanted_font(ctx, 46)
    s = "FREE PIZZA!"
    e = ctx.text_extents(s)
    ctx.move_to(x - e.x_advance / 2, y - 330)
    ctx.set_source_rgb(*hexc("#c8312c"))
    ctx.show_text(s)
    block(ctx, x - 170, y - 120, 340, 120, "#f2c230", top=14)
    for i, dx in enumerate((-100, 0, 100)):
        pizza(ctx, x + dx, y - 140, 34)
        if int(t * 3 + i) % 3 == 0:
            ctx.move_to(x + dx - 6, y - 182)
            ctx.curve_to(x + dx + 8, y - 200, x + dx - 10, y - 214, x + dx + 4, y - 232)
            ctx.set_source_rgba(1, 1, 1, 0.6)
            ctx.set_line_width(3)
            ctx.stroke()


# ------------------------------------------------------------------ hide-and-seek park
HIDE_SPOTS = [(250, 590), (560, 570), (880, 590), (1140, 572)]


def bush(ctx, x, y, s=1.0, col="#3f9a4a"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_path()
    for dx, dy, r in ((-70, -40, 50), (-20, -78, 60), (40, -60, 56), (80, -30, 44), (0, -30, 60)):
        ctx.new_sub_path()
        ctx.arc(dx, dy, r, 0, 2 * math.pi)
    _fill_line(ctx, hexc(col), 5)
    for dx, dy in ((-40, -70), (20, -95), (60, -50)):
        ctx.arc(dx, dy, 12, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.16)
        ctx.fill()
    ctx.restore()


def _house(ctx, x, y, col, roof):
    block(ctx, x - 120, y - 200, 240, 200, col, top=18)
    ctx.move_to(x - 140, y - 200)
    ctx.line_to(x, y - 320)
    ctx.line_to(x + 140, y - 200)
    ctx.close_path()
    _fill_line(ctx, hexc(roof), 5)
    ctx.rectangle(x - 30, y - 110, 60, 110)
    _fill_line(ctx, hexc("#7a4a2a"), 4)
    for dx in (-80, 80):
        ctx.rectangle(x + dx - 25, y - 170, 50, 44)
        _fill_line(ctx, hexc("#bfe3ff"), 3)


def party_park(ctx, t, floor=640, night=False):
    _sky(ctx, t, top="#86c8f0", bot="#e2f4ff", horizon=470, sun=(1100, 100))
    _house(ctx, 120, 470, "#f2c230", "#c8312c")
    _house(ctx, 1150, 470, "#3b82d6", "#4a3a8a")
    # tree
    ctx.rectangle(690, 300, 40, 180)
    _fill_line(ctx, hexc("#7a4a2a"), 4)
    for dx, dy, w in ((-60, 240, 160), (-40, 180, 120)):
        block(ctx, 710 + dx, dy, w, 70, "#3f9a4a", top=14)
    # grass
    ctx.rectangle(-W, 470, 3 * W, H)
    ctx.set_source(_grad(ctx, 0, 470, 0, 760, [(0, "#7ccc5c"), (1, "#3f9a3a")]))
    ctx.fill()
    for i in range(60):
        x = -W + i * 64 + (i * 37) % 30
        y = 500 + (i * 53) % 220
        ctx.move_to(x, y)
        ctx.line_to(x + 6, y - 14)
        ctx.line_to(x + 12, y)
        ctx.set_source_rgba(0.2, 0.45, 0.2, 0.5)
        ctx.set_line_width(2)
        ctx.stroke()
    # crates + slide
    block(ctx, 380, 520, 70, 70, "#c08a4a", top=12)
    block(ctx, 980, 515, 60, 60, "#c08a4a", top=10)
    for (x, y) in HIDE_SPOTS:
        bush(ctx, x, y, 0.9)
    return {"floor": floor}


def balloon(ctx, x, y, col, k=1.0, sway=0.0, r=34):
    """one balloon on a string; y = bottom of the string"""
    s = _pop(k)
    if s <= 0:
        return
    bx, by = x + sway, y - 150 * s
    ctx.move_to(x, y)
    ctx.curve_to(x + 12, y - 50 * s, bx - 12, by + 70 * s, bx, by + r * s)
    ctx.set_source_rgba(*INK, 0.7)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.save()
    ctx.translate(bx, by)
    ctx.scale(s, s * 1.15)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    _fill_line(ctx, hexc(col), 3)
    ctx.arc(-r * 0.35, -r * 0.35, r * 0.22, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.fill()
    ctx.restore()


BALLOON_COLS = ["#e5483c", "#3b82d6", "#f2c230", "#4cb050", "#9b59d0", "#f28b2c", "#ff7ab8"]


def balloon_bunch(ctx, x, y, k, n=6, t=0.0, spread=60, seed=0, stagger=0.05):
    rnd = random.Random(seed)
    for i in range(n):
        dx = (rnd.random() - 0.5) * 2 * spread
        dy = -rnd.random() * 60
        balloon(ctx, x + dx * 0.3, y, BALLOON_COLS[(i + seed) % len(BALLOON_COLS)], k - i * stagger,
                sway=dx + 6 * math.sin(t * 2 + i), r=30 + rnd.random() * 10)
        _ = dy


def confetti(ctx, k, x=640, y=300, n=60, seed=2):
    """burst of confetti (k s since the burst)"""
    if k <= 0 or k > 3.0:
        return
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.random() * 2 * math.pi
        v = 300 + rnd.random() * 500
        px = x + math.cos(a) * v * min(k, 0.6) + 40 * math.sin(k * 4 + i)
        py = y + math.sin(a) * v * min(k, 0.6) * 0.7 + 180 * k * k
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(k * 8 + i)
        ctx.rectangle(-7, -4, 14, 8)
        ctx.set_source_rgba(*hexc(BALLOON_COLS[i % len(BALLOON_COLS)]), max(0.0, 1 - k / 3.0))
        ctx.fill()
        ctx.restore()


def megaphone(ctx, x, y, R, ang=-0.25):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.move_to(-0.1 * R, -0.25 * R)
    ctx.line_to(1.1 * R, -0.65 * R)
    ctx.line_to(1.1 * R, 0.65 * R)
    ctx.line_to(-0.1 * R, 0.25 * R)
    ctx.close_path()
    _fill_line(ctx, hexc("#f2f2f2"), 0.06 * R)
    ctx.rectangle(-0.35 * R, -0.25 * R, 0.3 * R, 0.5 * R)
    _fill_line(ctx, hexc("#c8312c"), 0.05 * R)
    ctx.restore()


# ------------------------------------------------------------------ game UI (generic, original)
def _panel(ctx, x, y, w, h, a=0.92):
    _rrect(ctx, x, y, w, h, 22)
    ctx.set_source_rgba(0.08, 0.1, 0.16, a)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.set_line_width(3)
    ctx.stroke()


def _ui_text(ctx, s, x, y, size, col=(1, 1, 1), center=True, bold=True):
    ctx.select_font_face("Kalam", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    ctx.move_to(x - e.x_advance / 2 if center else x, y)
    ctx.set_source_rgb(*col)
    ctx.show_text(s)


def game_menu(ctx, cx, cy, k, glow_k=-1.0, presses=(), t=0.0, s=1.0):
    """pause menu with a big red LEAVE GAME button. k = s since it opened; glow_k = s since the button
    starts glowing; presses = times (relative to t) when the button is pressed."""
    p = _pop(k)
    if p <= 0:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(p * s, p * s)
    _panel(ctx, -280, -230, 560, 460)
    _ui_text(ctx, "GAME MENU", 0, -170, 44)
    for i, lab in enumerate(("Resume", "Settings")):
        _rrect(ctx, -200, -130 + i * 80, 400, 62, 14)
        ctx.set_source_rgba(1, 1, 1, 0.14)
        ctx.fill()
        _ui_text(ctx, lab, 0, -88 + i * 80, 32, (0.85, 0.88, 0.95), bold=False)
    press = any(0 <= t - pt < 0.12 for pt in presses)
    bs = 0.94 if press else 1.0
    ctx.save()
    ctx.translate(0, 110)
    ctx.scale(bs, bs)
    if glow_k > 0:
        glow(ctx, 0, 0, 300, hexc("#ff5a4a"), 0.45 + 0.15 * math.sin(glow_k * 10))
    _rrect(ctx, -230, -48, 460, 96, 20)
    _fill_line(ctx, hexc("#e0352b" if not press else "#b8241c"), 5)
    _rrect(ctx, -222, -42, 444, 30, 14)
    ctx.set_source_rgba(1, 1, 1, 0.22)
    ctx.fill()
    _ui_text(ctx, "LEAVE GAME", 0, 18, 50)
    ctx.restore()
    ctx.restore()


def cursor(ctx, x, y, pressed=False, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (0.9 if pressed else 1.0), s * (0.9 if pressed else 1.0))
    ctx.move_to(0, 0)
    ctx.line_to(0, 62)
    ctx.line_to(16, 48)
    ctx.line_to(28, 74)
    ctx.line_to(40, 68)
    ctx.line_to(28, 43)
    ctx.line_to(48, 42)
    ctx.close_path()
    _fill_line(ctx, (1, 1, 1), 4)
    if pressed:
        for i in range(6):
            a = i * math.pi / 3
            ctx.move_to(14 * math.cos(a), 14 * math.sin(a))
            ctx.line_to(30 * math.cos(a), 30 * math.sin(a))
        ctx.set_source_rgb(*hexc("#f2c230"))
        ctx.set_line_width(4)
        ctx.stroke()
    ctx.restore()


PLAYER_NAMES = ["BlockyBen", "SkyJumper", "LavaLuke", "Pixel_Pam", "SpeedySam", "HideMaster", "CoolCat99",
                "ZoomZoe", "BuilderBo", "NinjaNia", "JumpyJo", "Toby_Welcome"]


def player_list(ctx, x, y, t, leave_times, k_open, s=1.0):
    """server player list; row i slides out at leave_times[i] (None = stays). The counter follows."""
    p = _pop(k_open)
    if p <= 0:
        return
    n_left = sum(1 for lt in leave_times if lt is None or t < lt)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(p * s, p * s)
    _panel(ctx, -230, -300, 460, 600)
    _ui_text(ctx, f"PLAYERS  {n_left}/{len(leave_times)}", 0, -250, 38)
    row = 0
    for i, (name, lt) in enumerate(zip(PLAYER_NAMES, leave_times)):
        if lt is not None and t >= lt + 0.25:
            continue
        q = 0.0 if lt is None or t < lt else _ease_out((t - lt) / 0.25)
        yy = -200 + row * 42
        ctx.save()
        ctx.translate(-q * 420, 0)
        _rrect(ctx, -205, yy - 18, 410, 36, 10)
        is_toby = name.startswith("Toby")
        ctx.set_source_rgba(*(hexc("#f2c230") if is_toby else (1, 1, 1)), 0.22 if is_toby else 0.1)
        ctx.fill()
        ctx.arc(-180, yy, 12, 0, 2 * math.pi)
        ctx.set_source_rgb(*hexc(BALLOON_COLS[i % len(BALLOON_COLS)]))
        ctx.fill()
        _ui_text(ctx, name, -158, yy + 10, 26, (1, 1, 1), center=False, bold=is_toby)
        ctx.restore()
        row += 1
    ctx.restore()


def chat_box(ctx, x, y, t, msgs, w=520):
    """game chat; msgs = [(time, name, text, colour)], newest at the bottom (max 6 lines)"""
    shown = [m for m in msgs if t >= m[0]]
    if not shown:
        return
    shown = shown[-6:]
    _rrect(ctx, x, y, w, 50 + 40 * len(shown), 14)
    ctx.set_source_rgba(0.05, 0.06, 0.1, 0.72)
    ctx.fill()
    _ui_text(ctx, "CHAT", x + 20, y + 34, 24, (0.7, 0.75, 0.85), center=False)
    for i, (tm, name, text, col) in enumerate(shown):
        yy = y + 74 + i * 40
        n = int(max(0, t - tm) * 40)
        ctx.select_font_face("Kalam", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24)
        ctx.move_to(x + 20, yy)
        ctx.set_source_rgb(*hexc(col))
        ctx.show_text(name + ":")
        nx = x + 30 + ctx.text_extents(name + ":").x_advance
        ctx.select_font_face("Kalam", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.move_to(nx, yy)
        ctx.set_source_rgb(1, 1, 1)
        ctx.show_text(text[:n])


def kick_dialog(ctx, cx, cy, k, title="DISCONNECTED", body=("You were kicked", "from this server.")):
    p = _pop(k)
    if p <= 0:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(p, p)
    _rrect(ctx, -300, -170, 600, 340, 22)
    _fill_line(ctx, hexc("#f4f4f6"), 5)
    _rrect(ctx, -300, -170, 600, 80, 22)
    ctx.set_source_rgb(*hexc("#e0352b"))
    ctx.fill()
    _ui_text(ctx, title, 0, -115, 40)
    for i, ln in enumerate(body):
        _ui_text(ctx, ln, 0, -20 + i * 44, 34, (0.15, 0.15, 0.2), bold=False)
    _rrect(ctx, -90, 90, 180, 56, 14)
    _fill_line(ctx, hexc("#3b82d6"), 3)
    _ui_text(ctx, "OK", 0, 130, 32)
    ctx.restore()


def join_toast(ctx, x, y, k, text, col="#4cb050"):
    """small slide-down notification ('Toby_Welcome joined')"""
    if k <= 0 or k > 2.6:
        return
    q = _ease_out(k / 0.25) * (1 - _ease_out((k - 2.3) / 0.3))
    _rrect(ctx, x - 230, y - 80 + 80 * q, 460, 60, 14)
    ctx.set_source_rgba(0.05, 0.06, 0.1, 0.8 * q)
    ctx.fill()
    ctx.arc(x - 200, y - 50 + 80 * q, 10, 0, 2 * math.pi)
    ctx.set_source_rgba(*hexc(col), q)
    ctx.fill()
    ctx.select_font_face("Kalam", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(26)
    ctx.move_to(x - 180, y - 40 + 80 * q)
    ctx.set_source_rgba(1, 1, 1, q)
    ctx.show_text(text)


def monitor(ctx, x, y, draw_screen=None, w=300, h=190, off=False):
    """desk monitor (y = desk top); draw_screen(ctx, x0, y0, w, h) paints the screen"""
    ctx.rectangle(x - 14, y - 50, 28, 50)
    _fill_line(ctx, hexc("#3a3a42"), 3)
    _rrect(ctx, x - w / 2 - 12, y - 50 - h - 24, w + 24, h + 24, 10)
    _fill_line(ctx, hexc("#26262c"), 4)
    x0, y0 = x - w / 2, y - 50 - h - 12
    ctx.rectangle(x0, y0, w, h)
    if off:
        ctx.set_source_rgb(0.05, 0.05, 0.07)
        ctx.fill()
        return
    ctx.set_source_rgb(*hexc("#86c8f0"))
    ctx.fill()
    if draw_screen:
        ctx.save()
        ctx.rectangle(x0, y0, w, h)
        ctx.clip()
        draw_screen(ctx, x0, y0, w, h)
        ctx.restore()
    glow(ctx, x, y0 + h / 2, w, hexc("#bfe3ff"), 0.25)


PLACES_GAME = {"obby": obby, "race_track": race_track, "party_park": party_park}
