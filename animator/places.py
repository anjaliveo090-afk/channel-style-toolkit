"""Places (backgrounds) in the Paper Billions style, modelled on the reference sets
(style_bible.md section 4). Every function draws a full 1280x720 background in world coordinates and
returns {"floor": y} = the y where standing characters' feet go (or None for close-up props).
Details are original; only the look (flat vector + practical lights + vignette) follows the reference.
"""
import math
import random

import cairo

from sets import _fill_line, _slanted_font, glow, pop_label  # noqa: F401
from style import INK, _rrect, hexc, mix

W, H = 1280, 720


def _grad(ctx, x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, c in stops:
        g.add_color_stop_rgb(o, *hexc(c))
    return g


def _rect(ctx, x, y, w, h, col, lw=0.0):
    ctx.rectangle(x, y, w, h)
    if lw:
        _fill_line(ctx, hexc(col), lw)
    else:
        ctx.set_source_rgb(*hexc(col))
        ctx.fill()


def _text(ctx, s, x, y, size, col="#200a00", center=True):
    _slanted_font(ctx, size)
    e = ctx.text_extents(s)
    ctx.move_to(x - (e.x_advance / 2 if center else 0), y)
    ctx.set_source_rgb(*hexc(col))
    ctx.show_text(s)


def _floor_planks(ctx, y0, col_top, col_bot, gap=46, line="#00000033"):
    ctx.set_source(_grad(ctx, 0, y0, 0, H, [(0, col_top), (1, col_bot)]))
    ctx.rectangle(-W, y0, 3 * W, H)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.set_line_width(2)
    y = y0 + 8
    k = 0
    while y < H + 50:
        ctx.move_to(-W, y)
        ctx.line_to(2 * W, y)
        ctx.stroke()
        k += 1
        y += gap * (0.6 + 0.4 * k / 3)
    _rect(ctx, -W, y0 - 3, 3 * W, 6, "#200a00")


def _vertical_warm(ctx, top, bottom):
    ctx.set_source(_grad(ctx, 0, 0, W, 0, [(0, top), (1, bottom)]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()


# ------------------------------------------------------------------ 1. living room
def living_room(ctx, t, tv_text="BREAKING NEWS", bike=True):
    floor = 560
    _vertical_warm(ctx, "#f1a865", "#d99868")
    # window with a city/fence silhouette at sunset
    ctx.save()
    ctx.rectangle(110, 70, 380, 270)
    ctx.clip()
    ctx.set_source(_grad(ctx, 0, 70, 0, 340, [(0, "#ffb15e"), (1, "#ffd9a0")]))
    ctx.paint()
    for k in range(8):
        x = 110 + k * 50
        ctx.move_to(x, 340)
        ctx.line_to(x, 250 + (k % 3) * 18)
        ctx.line_to(x + 25, 230 + (k % 2) * 20)
        ctx.line_to(x + 50, 250 + (k % 3) * 18)
        ctx.line_to(x + 50, 340)
        ctx.close_path()
        ctx.set_source_rgb(*hexc("#f08a3c"))
        ctx.fill_preserve()
        ctx.set_source_rgba(*INK, 0.6)
        ctx.set_line_width(2)
        ctx.stroke()
    ctx.restore()
    ctx.rectangle(110, 70, 380, 270)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(7)
    ctx.stroke()
    ctx.move_to(300, 70)
    ctx.line_to(300, 340)
    ctx.stroke()
    # wall picture
    _rect(ctx, 590, 130, 70, 56, "#f6efe0", 3)
    for k in (0, 1):
        ctx.arc(612 + k * 24, 158, 9, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(2)
        ctx.stroke()
    # floor lamp
    glow(ctx, 230, 400, 260, hexc("#ffe2a0"), 0.55)
    ctx.move_to(185, 360)
    ctx.line_to(275, 360)
    ctx.line_to(255, 300)
    ctx.line_to(205, 300)
    ctx.close_path()
    _fill_line(ctx, hexc("#fff0b8"), 3)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.move_to(230, 360)
    ctx.line_to(230, floor + 30)
    ctx.stroke()
    ctx.save()
    ctx.translate(230, floor + 32)
    ctx.scale(45, 9)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    _fill_line(ctx, hexc("#b88a4e"), 3)
    # skirting + floor
    _floor_planks(ctx, floor, "#b4723c", "#7a4a24")
    # sofa
    _rrect(ctx, 30, floor - 70, 250, 80, 30)
    _fill_line(ctx, hexc("#7fa06a"), 4)
    _rrect(ctx, 10, floor - 40, 60, 100, 26)
    _fill_line(ctx, hexc("#86a872"), 4)
    _rrect(ctx, 245, floor - 40, 60, 100, 26)
    _fill_line(ctx, hexc("#86a872"), 4)
    _rect(ctx, 60, floor - 10, 190, 60, "#6f9160", 4)
    # tv on a cabinet
    _rect(ctx, 760, floor - 40, 300, 90, "#6b4428", 4)
    _rect(ctx, 790, floor - 250, 250, 180, "#1b1d22", 5)
    ctx.set_source(_grad(ctx, 0, floor - 240, 0, floor - 80, [(0, "#3f6c9a"), (1, "#25476c")]))
    ctx.rectangle(802, floor - 238, 226, 156)
    ctx.fill()
    _rect(ctx, 802, floor - 128, 226, 30, "#c92a2a")
    _text(ctx, tv_text, 915, floor - 106, 20, "#ffffff")
    _rect(ctx, 850, floor - 70, 130, 30, "#3a2a1c")
    if bike:
        ctx.set_source_rgb(*hexc("#2f6b5a"))
        ctx.set_line_width(5)
        for bx in (1100, 1210):
            ctx.arc(bx, floor + 20, 42, 0, 2 * math.pi)
            ctx.stroke()
        ctx.move_to(1100, floor + 20)
        ctx.line_to(1150, floor - 30)
        ctx.line_to(1210, floor + 20)
        ctx.move_to(1150, floor - 30)
        ctx.line_to(1140, floor + 20)
        ctx.line_to(1100, floor + 20)
        ctx.stroke()
    # fridge edge right
    _rect(ctx, 1180, 120, 140, floor - 120, "#f3ece0", 5)
    return {"floor": floor + 120}


# ------------------------------------------------------------------ 2. porch at sunset
def porch_sunset(ctx, t):
    floor = 600
    ctx.set_source(_grad(ctx, 0, 0, 0, floor, [(0, "#7a3a6a"), (0.5, "#d6607a"), (1, "#f2a46a")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    rnd = random.Random(2)
    for _ in range(9):
        x, y, r = rnd.random() * 340, 220 + rnd.random() * 200, 70 + rnd.random() * 60
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgba(0.18, 0.12, 0.22, 0.8)
        ctx.fill()
    # house wall (siding) from x=380
    ctx.set_source(_grad(ctx, 380, 0, W, 0, [(0, "#f4ece0"), (1, "#fff3dc")]))
    ctx.rectangle(380, -40, W, floor + 40)
    ctx.fill()
    ctx.set_source_rgba(0.55, 0.45, 0.35, 0.35)
    ctx.set_line_width(2)
    for y in range(0, floor, 34):
        ctx.move_to(380, y)
        ctx.line_to(W + 40, y)
        ctx.stroke()
    glow(ctx, 1000, 300, 420, hexc("#ffe7a6"), 0.5)
    # window with curtains
    ctx.rectangle(520, 40, 290, 230)
    ctx.set_source(_grad(ctx, 0, 40, 0, 270, [(0, "#ffe68a"), (1, "#ffd25a")]))
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(6)
    ctx.stroke()
    for sd in (0, 1):
        x0 = 524 if sd == 0 else 762
        ctx.move_to(x0, 44)
        ctx.curve_to(x0 + (40 if sd == 0 else -10), 150, x0 + (10 if sd == 0 else 30), 220, x0 + (24 if sd == 0 else 20), 266)
        ctx.line_to(x0 + (0 if sd == 0 else 44), 266)
        ctx.line_to(x0 + (0 if sd == 0 else 44), 44)
        ctx.close_path()
        ctx.set_source_rgb(*hexc("#e4472c"))
        ctx.fill()
    ctx.move_to(665, 40)
    ctx.line_to(665, 270)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(5)
    ctx.stroke()
    # wall lamp, door
    glow(ctx, 985, 130, 140, hexc("#fff2c0"), 0.5)
    ctx.move_to(960, 110)
    ctx.line_to(1010, 110)
    ctx.line_to(1000, 165)
    ctx.line_to(970, 165)
    ctx.close_path()
    _fill_line(ctx, hexc("#fff8e0"), 4)
    _rect(ctx, 1100, 30, 200, floor - 30, "#5a3524", 6)
    for k in range(6):
        _rect(ctx, 1115, 60 + k * 85, 170, 70, "#64402c", 2)
    # porch posts + railing
    for px in (60, 360):
        _rect(ctx, px, -10, 34, floor + 10, "#f6f0e6", 4)
    _rect(ctx, 0, 420, 380, 16, "#f6f0e6", 3)
    for k in range(5):
        _rect(ctx, 30 + k * 70, 436, 12, floor - 436, "#f6f0e6", 2)
    _floor_planks(ctx, floor, "#8a5a36", "#5a3720", gap=30)
    return {"floor": floor + 60}


# ------------------------------------------------------------------ 3. school corridor
def school_corridor(ctx, t, sign=("NO RUNNING", "LIGHTS OUT 9PM", "CHORES LIST")):
    floor = 470
    ctx.set_source(_grad(ctx, 0, 0, 0, floor, [(0, "#cfe0d4"), (1, "#bcd6c4")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    _rect(ctx, -W, floor - 110, 3 * W, 110, "#4e8a6a")
    for x in (240, 800):
        glow(ctx, x + 115, 20, 260, hexc("#ffffff"), 0.5)
        _rrect(ctx, x, 0, 230, 20, 8)
        _fill_line(ctx, hexc("#f4f6f2"), 4)
    # corkboard sign
    _rect(ctx, 395, 60, 450, 265, "#b07a40", 5)
    _rect(ctx, 420, 82, 400, 220, "#f7f5ef", 4)
    for i, s in enumerate(sign):
        _text(ctx, s, 620, 140 + i * 58, 40)
    # lockers
    for side, x0 in ((-1, -20), (1, 920)):
        for k in range(7):
            x = x0 + k * 52
            _rect(ctx, x, 195, 52, floor - 195, "#3e6c99", 3)
            _rect(ctx, x + 10, 245, 32, 20, "#f4f4f0", 2)
            ctx.set_source_rgba(0.1, 0.15, 0.25, 0.6)
            ctx.set_line_width(2)
            for j in range(3):
                ctx.move_to(x + 14, 212 + j * 7)
                ctx.line_to(x + 38, 212 + j * 7)
                ctx.stroke()
    # tiled floor in perspective
    ctx.set_source(_grad(ctx, 0, floor, 0, H, [(0, "#d7d0c2"), (1, "#a9a090")]))
    ctx.rectangle(-W, floor, 3 * W, H)
    ctx.fill()
    ctx.set_source_rgba(0.3, 0.25, 0.2, 0.3)
    ctx.set_line_width(2)
    for k in range(-12, 13):
        ctx.move_to(640 + k * 40, floor)
        ctx.line_to(640 + k * 190, H + 40)
        ctx.stroke()
    y = floor
    for k in range(8):
        y += 14 + k * 9
        ctx.move_to(-W, y)
        ctx.line_to(2 * W, y)
        ctx.stroke()
    _rect(ctx, -W, floor - 2, 3 * W, 4, "#200a00")
    return {"floor": floor + 110}


# ------------------------------------------------------------------ 4. bathroom stalls
def bathroom_stalls(ctx, t):
    floor = 470
    ctx.set_source(_grad(ctx, 0, 0, 0, floor, [(0, "#dfe8de"), (1, "#c8d8c8")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    glow(ctx, 640, 0, 500, hexc("#ffffff"), 0.4)
    for k in range(9):
        x = 60 + k * 132
        _rect(ctx, x, 120, 120, floor - 150, "#5f9a7a", 4)
        _rect(ctx, x + 100, 270, 10, 26, "#c8c8c0", 2)
        _rect(ctx, x - 6, 110, 132, 14, "#4a7c62", 3)
    ctx.set_source(_grad(ctx, 0, floor, 0, H, [(0, "#d6e0d6"), (1, "#a8b8aa")]))
    ctx.rectangle(-W, floor, 3 * W, H)
    ctx.fill()
    ctx.set_source_rgba(0.2, 0.3, 0.25, 0.25)
    ctx.set_line_width(2)
    for k in range(-14, 15):
        ctx.move_to(640 + k * 50, floor)
        ctx.line_to(640 + k * 160, H + 40)
        ctx.stroke()
    for j in range(7):
        y = floor + 12 + j * j * 7
        ctx.move_to(-W, y)
        ctx.line_to(2 * W, y)
        ctx.stroke()
    ctx.arc(700, floor + 120, 16, 0, 2 * math.pi)
    _fill_line(ctx, hexc("#7a7a7a"), 3)
    _rect(ctx, -W, floor - 2, 3 * W, 4, "#200a00")
    return {"floor": floor + 120}


# ------------------------------------------------------------------ 5. diner
def diner(ctx, t, menu="COFFEE · PIE", year="1993"):
    floor = 470
    ctx.set_source(_grad(ctx, 0, 0, 0, floor, [(0, "#fbf3dc"), (1, "#f4e7c4")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    _rect(ctx, -W, 0, 3 * W, 26, "#c8312c")
    for x in (200, 560, 920):
        ctx.move_to(x, 26)
        ctx.line_to(x, 70)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(3)
        ctx.stroke()
        glow(ctx, x, 100, 160, hexc("#ffe2a0"), 0.45)
        ctx.move_to(x - 40, 100)
        ctx.line_to(x + 40, 100)
        ctx.line_to(x + 18, 70)
        ctx.line_to(x - 18, 70)
        ctx.close_path()
        _fill_line(ctx, hexc("#d8382f"), 3)
    # clock + calendar + menu board
    ctx.arc(420, 120, 38, 0, 2 * math.pi)
    _fill_line(ctx, hexc("#ffffff"), 5)
    ctx.move_to(420, 120)
    ctx.line_to(420, 92)
    ctx.move_to(420, 120)
    ctx.line_to(440, 128)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.stroke()
    _rect(ctx, 520, 80, 90, 100, "#ffffff", 4)
    _rect(ctx, 520, 80, 90, 26, "#d8382f")
    _text(ctx, year, 565, 150, 26)
    _rect(ctx, 860, 60, 330, 110, "#2a2a2a", 5)
    _text(ctx, menu, 1025, 128, 40, "#f2d06b")
    # counter
    _rect(ctx, -W, floor - 150, 3 * W, 20, "#d8382f", 3)
    _rect(ctx, -W, floor - 130, 3 * W, 130, "#f4f0e6", 3)
    ctx.set_source_rgb(*hexc("#d8382f"))
    ctx.rectangle(-W, floor - 70, 3 * W, 14)
    ctx.fill()
    for k in range(-2, 12):
        x = k * 120 + 40
        ctx.move_to(x, floor + 20)
        ctx.line_to(x, floor - 20)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.save()
        ctx.translate(x, floor - 26)
        ctx.scale(34, 10)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        _fill_line(ctx, hexc("#d8382f"), 3)
    # checkered floor in one-point perspective (vanishing point above the counter)
    vx, vy = 640, floor - 420
    rows = [floor]
    for r in range(9):
        rows.append(rows[-1] + 18 + r * 9)
    for r in range(len(rows) - 1):
        y0, y1 = rows[r], rows[r + 1]
        for c in range(-16, 17):
            def X(y, cc):
                return vx + (cc * 60) * (y - vy) / (floor - vy)
            ctx.move_to(X(y0, c), y0)
            ctx.line_to(X(y0, c + 1), y0)
            ctx.line_to(X(y1, c + 1), y1)
            ctx.line_to(X(y1, c), y1)
            ctx.close_path()
            ctx.set_source_rgb(*(hexc("#2a2a2a") if (c + r) % 2 else hexc("#f2efe6")))
            ctx.fill()
    _rect(ctx, -W, floor - 2, 3 * W, 4, "#200a00")
    return {"floor": floor + 110}


# ------------------------------------------------------------------ 6. night office (government)
def gov_building(ctx, cx, base, s=1.0, col="#d8deea"):
    """A generic domed government building (not a specific real one)."""
    c = hexc(col)
    ctx.rectangle(cx - 190 * s, base - 70 * s, 380 * s, 70 * s)
    _fill_line(ctx, c, 2.5)
    for k in range(12):
        ctx.rectangle(cx - 175 * s + k * 30 * s, base - 62 * s, 8 * s, 54 * s)
        ctx.set_source_rgba(0.2, 0.25, 0.4, 0.5)
        ctx.fill()
    ctx.rectangle(cx - 70 * s, base - 120 * s, 140 * s, 50 * s)
    _fill_line(ctx, c, 2.5)
    ctx.new_path()
    ctx.arc(cx, base - 120 * s, 62 * s, math.pi, 0)
    ctx.close_path()
    _fill_line(ctx, c, 2.5)
    ctx.rectangle(cx - 5 * s, base - 200 * s, 10 * s, 20 * s)
    _fill_line(ctx, c, 2)


def night_office(ctx, t):
    floor = 520
    ctx.set_source(_grad(ctx, 0, 0, 0, H, [(0, "#1d2c52"), (1, "#0d1530")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    # big window with the domed building under the moon
    ctx.save()
    ctx.rectangle(330, 60, 620, 330)
    ctx.clip()
    ctx.set_source(_grad(ctx, 0, 60, 0, 390, [(0, "#0b1433"), (1, "#24386a")]))
    ctx.paint()
    rnd = random.Random(9)
    for _ in range(50):
        ctx.arc(330 + rnd.random() * 620, 60 + rnd.random() * 200, 1.6, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.fill()
    glow(ctx, 640, 230, 200, hexc("#cfe0ff"), 0.45)
    gov_building(ctx, 640, 390, 1.1)
    ctx.restore()
    ctx.set_source_rgb(*hexc("#0a0f22"))
    ctx.set_line_width(12)
    ctx.rectangle(330, 60, 620, 330)
    ctx.stroke()
    ctx.set_line_width(6)
    for x in (537, 743):
        ctx.move_to(x, 60)
        ctx.line_to(x, 390)
    ctx.stroke()
    # curtain + flag-like stripes (generic)
    _rect(ctx, 250, -10, 70, floor, "#6a1a22")
    # desk with banker's lamp, phone
    _rect(ctx, -40, floor - 40, 1360, 280, "#4a2c1c", 5)
    _rect(ctx, -40, floor - 40, 1360, 30, "#5a3524", 3)
    glow(ctx, 160, floor - 120, 260, hexc("#c8ffb0"), 0.35)
    ctx.move_to(90, floor - 120)
    ctx.curve_to(110, floor - 170, 210, floor - 170, 230, floor - 120)
    ctx.close_path()
    _fill_line(ctx, hexc("#3a9a4a"), 4)
    ctx.move_to(160, floor - 120)
    ctx.line_to(160, floor - 40)
    ctx.set_source_rgb(*hexc("#c8a040"))
    ctx.set_line_width(6)
    ctx.stroke()
    _rrect(ctx, 960, floor - 80, 150, 50, 10)
    _fill_line(ctx, hexc("#c4262c"), 4)
    ctx.arc(1035, floor - 55, 16, 0, 2 * math.pi)
    _fill_line(ctx, hexc("#f2f2f2"), 3)
    return {"floor": floor + 40, "desk": floor - 40}


# ------------------------------------------------------------------ 7. bright tech office
def tech_office(ctx, t, board_lines=()):
    floor = 520
    ctx.set_source(_grad(ctx, 0, 0, 0, floor, [(0, "#fff3cf"), (1, "#f6e4b4")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    for k in range(5):
        x = -20 + k * 210
        ctx.rectangle(x, 30, 190, 300)
        ctx.set_source_rgba(1, 1, 0.92, 0.65)
        ctx.fill()
        ctx.set_source_rgba(0.6, 0.5, 0.3, 0.6)
        ctx.set_line_width(4)
        ctx.rectangle(x, 30, 190, 300)
        ctx.stroke()
    whiteboard(ctx, 620, 70, 560, 320, board_lines, 1.0)
    # plant + cactus
    ctx.move_to(130, floor - 60)
    for k in range(6):
        a = -2.6 + k * 0.4
        ctx.move_to(150, floor - 90)
        ctx.curve_to(150 + math.cos(a) * 60, floor - 150 + math.sin(a) * 40, 150 + math.cos(a) * 120, floor - 200,
                     150 + math.cos(a) * 150, floor - 180 + k * 8)
    ctx.set_source_rgb(*hexc("#3a8a4a"))
    ctx.set_line_width(8)
    ctx.stroke()
    _rect(ctx, 110, floor - 95, 80, 70, "#c66a3a", 4)
    _rect(ctx, -40, floor - 30, 1360, 260, "#f2e6d0", 5)
    _rrect(ctx, 520, floor - 110, 210, 80, 8)
    _fill_line(ctx, hexc("#e8e8ea"), 4)
    ctx.arc(625, floor - 70, 9, 0, 2 * math.pi)
    ctx.set_source_rgb(*hexc("#8bc34a"))
    ctx.fill()
    _rrect(ctx, 880, floor - 90, 34, 60, 12)
    _fill_line(ctx, hexc("#5a9a4a"), 3)
    _rect(ctx, 870, floor - 40, 54, 22, "#c66a3a", 3)
    return {"floor": floor + 60, "desk": floor - 30}


def whiteboard(ctx, x, y, w, h, lines, k, pen_col="#2a4fa0", size=34):
    """Whiteboard with marker writing revealed progressively (k = 0..1 of all characters)."""
    _rect(ctx, x, y, w, h, "#f8f8f4", 5)
    _rect(ctx, x + 40, y + h, w - 80, 12, "#c8c8c0", 3)
    for i, c in enumerate(("#2a4fa0", "#c4262c", "#3a9a4a")):
        _rect(ctx, x + 60 + i * 50, y + h - 6, 34, 10, c)
    total = sum(len(s) for s in lines) or 1
    shown = int(total * max(0.0, min(1.0, k)))
    yy = y + 60
    for s in lines:
        n = min(len(s), shown)
        shown -= n
        _slanted_font(ctx, size)
        ctx.move_to(x + 36, yy)
        ctx.set_source_rgb(*hexc(pen_col))
        ctx.show_text(s[:n])
        yy += size * 1.45


# ------------------------------------------------------------------ 8. dark blue server corridor
def server_corridor(ctx, t, photo=True):
    floor = 540
    ctx.set_source(_grad(ctx, 0, 0, 0, H, [(0, "#16244a"), (1, "#070c1e")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    vx, vy = 640, 330            # vanishing point
    for side in (-1, 1):
        for k in range(10):
            d0, d1 = 1 / (1 + k * 0.45), 1 / (1 + (k + 1) * 0.45)
            x0, x1 = vx + side * 700 * d0, vx + side * 700 * d1
            y0t, y1t = vy - 520 * d0, vy - 520 * d1
            y0b, y1b = vy + 420 * d0, vy + 420 * d1
            ctx.move_to(x0, y0t)
            ctx.line_to(x1, y1t)
            ctx.line_to(x1, y1b)
            ctx.line_to(x0, y0b)
            ctx.close_path()
            shade = 0.12 + 0.06 * (k % 2)
            ctx.set_source_rgb(0.12 + shade * 0.2, 0.2 + shade * 0.3, 0.42 + shade * 0.4)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.02, 0.04, 0.1, 0.9)
            ctx.set_line_width(2)
            ctx.stroke()
            for j in range(4):
                yy = y0t + (y0b - y0t) * (0.2 + j * 0.18)
                ctx.arc(x0 - side * 18 * d0, yy, 3 * d0 + 1, 0, 2 * math.pi)
                on = (int(t * 3) + k + j) % 3 == 0
                ctx.set_source_rgb(*(hexc("#7dff8a") if on else hexc("#2a4a7a")))
                ctx.fill()
    for k in range(5):
        d = 1 / (1 + k * 0.6)
        ctx.rectangle(vx - 220 * d, vy - 500 * d, 440 * d, 10 * d + 2)
        ctx.set_source_rgba(0.85, 0.92, 1, 0.9)
        ctx.fill()
    glow(ctx, vx, vy - 250, 420, hexc("#cfe0ff"), 0.35)
    ctx.move_to(vx - 700, vy + 420)
    ctx.line_to(vx + 700, vy + 420)
    ctx.line_to(vx + 60, vy + 40)
    ctx.line_to(vx - 60, vy + 40)
    ctx.close_path()
    ctx.set_source(_grad(ctx, 0, vy + 40, 0, vy + 420, [(0, "#0e1a36"), (1, "#22345e")]))
    ctx.fill()
    if photo:
        _rect(ctx, vx - 26, vy - 70, 52, 64, "#f2f2ee", 2)
        _rect(ctx, vx - 18, vy - 62, 36, 40, "#8aa0c0")
        ctx.arc(vx, vy - 76, 4, 0, 2 * math.pi)
        ctx.set_source_rgb(*hexc("#d8342a"))
        ctx.fill()
    return {"floor": floor + 120}


# ------------------------------------------------------------------ 9. black void + spotlight
def void_spotlight(ctx, t, cx=640, floor=600, col="#fff4c8", edge="#4dff7a"):
    ctx.set_source_rgb(0.02, 0.02, 0.03)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    g = cairo.LinearGradient(0, -100, 0, floor)
    g.add_color_stop_rgba(0, *hexc(col), 0.0)
    g.add_color_stop_rgba(1, *hexc(col), 0.25)
    ctx.move_to(cx - 60, -100)
    ctx.line_to(cx + 60, -100)
    ctx.line_to(cx + 260, floor)
    ctx.line_to(cx - 260, floor)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.translate(cx, floor)
    ctx.scale(300, 46)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    g = cairo.RadialGradient(cx, floor, 0, cx, floor, 300)
    g.add_color_stop_rgba(0, *hexc(col), 0.55)
    g.add_color_stop_rgba(1, *hexc(col), 0.0)
    ctx.set_source(g)
    ctx.fill()
    if edge:
        ctx.move_to(cx - 560, floor + 90)
        ctx.line_to(cx + 560, floor + 90)
        ctx.set_source_rgba(*hexc(edge), 0.8)
        ctx.set_line_width(6)
        ctx.stroke()
        glow(ctx, cx, floor + 90, 400, hexc(edge), 0.15)
    return {"floor": floor + 10}


# ------------------------------------------------------------------ 10. night city skyline
def night_city(ctx, t, seed=6):
    ctx.set_source(_grad(ctx, 0, 0, 0, H, [(0, "#0a1230"), (0.7, "#2a2a5a"), (1, "#5a3a6a")]))
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    rnd = random.Random(seed)
    for _ in range(80):
        ctx.arc(rnd.random() * W, rnd.random() * 360, 1.4, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.5 + 0.5 * math.sin(t * 2 + _))
        ctx.fill()
    ctx.arc(1100, 110, 46, 0, 2 * math.pi)
    ctx.set_source_rgb(*hexc("#f6f2dc"))
    ctx.fill()
    glow(ctx, 1100, 110, 160, hexc("#f6f2dc"), 0.25)
    for layer, (col, hmin, hmax) in enumerate((("#1b2350", 160, 330), ("#121836", 220, 470))):
        x = -40
        while x < W + 40:
            bw = 60 + rnd.random() * 90
            bh = hmin + rnd.random() * (hmax - hmin)
            ctx.rectangle(x, H - bh, bw, bh)
            _fill_line(ctx, hexc(col), 2)
            for wy in range(int(H - bh + 14), H - 10, 24):
                for wx in range(int(x + 10), int(x + bw - 14), 18):
                    if rnd.random() < 0.45:
                        ctx.rectangle(wx, wy, 8, 11)
                        ctx.set_source_rgba(1, 0.86, 0.5, 0.85)
                        ctx.fill()
            x += bw + 6
    return {"floor": None}


# ------------------------------------------------------------------ 11-13. close-up props
def calendar(ctx, cx, cy, month, year, s=1.0, wall="#1d2c52"):
    """Wall calendar page (V1 4:33): red header with the month, year, grid."""
    w, h = 300 * s, 360 * s
    _rect(ctx, cx - w / 2 + 10, cy - h / 2 + 12, w, h, "#00000055")
    _rect(ctx, cx - w / 2, cy - h / 2, w, h, "#f4f1e8", 4)
    _rect(ctx, cx - w / 2, cy - h / 2, w, 90 * s, "#c8312c", 4)
    _text(ctx, month, cx, cy - h / 2 + 66 * s, 58 * s, "#ffffff")
    _text(ctx, str(year), cx, cy - h / 2 + 140 * s, 40 * s)
    ctx.set_source_rgba(0.3, 0.3, 0.3, 0.6)
    ctx.set_line_width(2)
    for r in range(5):
        for c in range(7):
            ctx.rectangle(cx - w / 2 + 22 * s + c * 37 * s, cy - h / 2 + 170 * s + r * 34 * s, 30 * s, 28 * s)
            ctx.stroke()


def cheque(ctx, cx, cy, payee, amount, s=1.0, k=1.0):
    """Big presentation cheque; the amount writes on with k (0..1)."""
    w, h = 620 * s, 270 * s
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(-0.04)
    _rect(ctx, -w / 2, -h / 2, w, h, "#f8f6ec", 5)
    ctx.rectangle(-w / 2 + 14 * s, -h / 2 + 14 * s, w - 28 * s, h - 28 * s)
    ctx.set_source_rgb(*hexc("#3d8b2f"))
    ctx.set_line_width(3)
    ctx.stroke()
    _text(ctx, f"PAY {payee}", -w / 2 + 40 * s, -h / 2 + 70 * s, 32 * s, center=False)
    txt = amount[:max(0, int(len(amount) * k))]
    _text(ctx, txt, w / 2 - 210 * s, 30 * s, 64 * s, "#2f7a2a")
    ctx.move_to(-w / 2 + 60 * s, h / 2 - 50 * s)
    ctx.curve_to(-w / 2 + 110 * s, h / 2 - 90 * s, -w / 2 + 160 * s, h / 2 - 20 * s, -w / 2 + 220 * s, h / 2 - 60 * s)
    ctx.set_source_rgb(*hexc("#2a3f9a"))
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.restore()


PLACES = {"living_room": living_room, "porch_sunset": porch_sunset, "school_corridor": school_corridor,
          "bathroom_stalls": bathroom_stalls, "diner": diner, "night_office": night_office,
          "tech_office": tech_office, "server_corridor": server_corridor, "void_spotlight": void_spotlight,
          "night_city": night_city}
