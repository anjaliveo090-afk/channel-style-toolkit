"""Explaining devices measured on the references (visual_grammar.md sections 13-14).
Each function draws on a cairo context; `k` is seconds since the device started (animations follow the
measured timings). Concept -> device table: visual_grammar.md section 13.
"""
import math

import cairo

from sets import _fill_line, _slanted_font, glow
from style import INK, _rrect, hexc

GREEN_BOX, GREEN_TXT = "#123a24", "#b8ff6a"


def _ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def _pop(k, dur=0.15):
    """measured pop-in: scale 0 -> 1.1 -> 1.0 in ~0.15 s"""
    if k <= 0:
        return 0.0
    if k < dur:
        return 1.1 * _ease_out(k / dur)
    return 1.0 + 0.1 * math.exp(-(k - dur) * 25)


def _txt(ctx, s, x, y, size, col, center=True, stroke=None):
    _slanted_font(ctx, size)
    e = ctx.text_extents(s)
    ctx.move_to(x - (e.x_advance / 2 if center else 0), y)
    if stroke:
        ctx.text_path(s)
        ctx.set_source_rgb(*hexc(stroke))
        ctx.set_line_width(size * 0.14)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc(col))
        ctx.fill()
    else:
        ctx.set_source_rgb(*hexc(col))
        ctx.show_text(s)


def counter_value(target, k, dur=1.0):
    """digits step slowly, then faster, ending on the round number (measured on '$1 -> $8 BILLION')"""
    p = min(1.0, max(0.0, k / dur))
    return target * p ** 2.6


def counter_box(ctx, x, y, k, target, fmt="${:,.0f}", sub=None, dur=1.0, w=260, h=86):
    """Dark-green rounded box with a glowing number that rolls up to `target`; optional small caption."""
    s = _pop(k)
    if s <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    _rrect(ctx, -w / 2, -h / 2, w, h, 12)
    _fill_line(ctx, hexc(GREEN_BOX), 3)
    v = counter_value(target, k, dur)
    _txt(ctx, fmt.format(v), 0, 12 if not sub else 4, 44, GREEN_TXT)
    if sub:
        _txt(ctx, sub, 0, 32, 16, "#d8f5c0")
    ctx.restore()


def pie_plate(ctx, x, y, k, pct, label=None, empty_at=None, r=110):
    """A pie on a plate, a slice of `pct` % with a yellow price tag; after `empty_at` s the plate is empty."""
    s = _pop(k)
    if s <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s * 0.45)
    ctx.arc(0, 0, r * 1.25, 0, 2 * math.pi)
    _fill_line(ctx, hexc("#f6f2e8"), 4)
    empty = empty_at is not None and k >= empty_at
    if not empty:
        a0 = -math.pi / 2
        ctx.move_to(0, 0)
        ctx.arc(0, 0, r, a0, a0 + 2 * math.pi * pct / 100)
        ctx.close_path()
        _fill_line(ctx, hexc("#3fa34d"), 4)
    else:
        for j in range(5):
            ctx.arc(-40 + j * 20, 10 * math.sin(j), 4, 0, 2 * math.pi)
            ctx.set_source_rgb(*hexc("#7a5a3a"))
            ctx.fill()
    ctx.restore()
    tag = "0%" if empty else (label or f"{pct}%")
    ctx.save()
    ctx.translate(x + r * 0.55, y - r * 0.55)
    ctx.rotate(-0.12)
    _rrect(ctx, -46, -24, 92, 48, 6)
    _fill_line(ctx, hexc("#f2d23a"), 3)
    _txt(ctx, tag, 0, 12, 30, "#200a00")
    ctx.restore()


def balance_scale(ctx, x, y, k, left_draw, right_draw, tilt=0.18, label=None, s=1.0):
    """Gold balance scale (V1 5:00 'a new car per chip'): enters with a pop, then tilts toward `tilt`
    (+ = right side heavier). left_draw/right_draw(ctx, cx, cy) draw the objects on the pans."""
    p = _pop(k)
    if p <= 0:
        return
    ang = tilt * _ease_out((k - 0.2) / 0.6)
    gold = hexc("#c9a032")
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(p * s, p * s)
    ctx.rectangle(-70, 230, 140, 26)
    _fill_line(ctx, gold, 3)
    ctx.rectangle(-8, -10, 16, 240)
    _fill_line(ctx, gold, 3)
    ctx.save()
    ctx.rotate(ang)
    ctx.rectangle(-260, -14, 520, 12)
    _fill_line(ctx, gold, 3)
    ctx.restore()
    ctx.arc(0, -8, 12, 0, 2 * math.pi)
    _fill_line(ctx, gold, 3)
    for sd, drawer in ((-1, left_draw), (1, right_draw)):
        px = sd * 250 * math.cos(ang)
        py = sd * 250 * math.sin(ang)
        ctx.set_source_rgba(*INK, 0.7)
        ctx.set_line_width(2)
        for dx in (-50, 50):
            ctx.move_to(px, py)
            ctx.line_to(px + dx, py + 110)
            ctx.stroke()
        ctx.save()
        ctx.translate(px, py + 110)
        ctx.scale(1, 0.25)
        ctx.arc(0, 0, 70, 0, math.pi)
        ctx.restore()
        _fill_line(ctx, gold, 3)
        drawer(ctx, px, py + 100)
    if label:
        ctx.rectangle(-110, 236, 220, 18)
        ctx.set_source_rgb(*hexc("#2a2a2a"))
        ctx.fill()
        _txt(ctx, label, 0, 251, 16, "#f2d23a")
    ctx.restore()


def stamp(ctx, x, y, k, text="BLOCKED", col="#d0302a", angle=-0.18, size=64):
    """Rubber stamp slams down: starts big and transparent, lands in ~0.12 s (pair with a thud)."""
    if k <= 0:
        return
    p = min(1.0, k / 0.12)
    sc = 1.8 - 0.8 * p
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(sc, sc)
    _slanted_font(ctx, size)
    e = ctx.text_extents(text)
    w, h = e.x_advance + 40, size * 1.25
    ctx.set_source_rgba(*hexc(col), 0.9 * p)
    ctx.set_line_width(7)
    _rrect(ctx, -w / 2, -h / 2, w, h, 10)
    ctx.stroke()
    ctx.move_to(-e.x_advance / 2, size * 0.35)
    ctx.show_text(text)
    ctx.restore()


def strike(ctx, x0, y, x1, k, dur=0.3, col="#d0302a", w=6):
    """Hand-drawn strike-through growing left -> right."""
    p = _ease_out(k / dur)
    if p <= 0:
        return
    ctx.move_to(x0, y + 3)
    ctx.curve_to(x0 + (x1 - x0) * 0.3, y - 4, x0 + (x1 - x0) * 0.6, y + 5, x0 + (x1 - x0) * p, y - 2)
    ctx.set_source_rgb(*hexc(col))
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def marker_circle(ctx, x, y, rx, ry, k, dur=0.5, col="#d8342a", hand=True):
    """A hand with a red marker draws an ellipse around (x, y) (V1 0:18)."""
    p = _ease_out(k / dur)
    if p <= 0:
        return
    a0 = -2.4
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, a0, a0 + 2 * math.pi * 1.08 * p)
    ctx.restore()
    ctx.set_source_rgb(*hexc(col))
    ctx.set_line_width(7)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    if hand and p < 1:
        a = a0 + 2 * math.pi * 1.08 * p
        hx, hy = x + rx * math.cos(a), y + ry * math.sin(a)
        ctx.move_to(hx, hy)
        ctx.line_to(hx + 260, hy + 160)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(26)
        ctx.stroke()
        ctx.move_to(hx, hy)
        ctx.line_to(hx + 40, hy + 25)
        ctx.set_source_rgb(*hexc(col))
        ctx.set_line_width(14)
        ctx.stroke()


def checkbox_form(ctx, x, y, k, rows, ticked, tick_at=0.3, title="ENROLMENT FORM"):
    """Paper form with checkboxes; row `ticked` gets a tick at tick_at s (V1 1:16 'REFORM PROGRAM')."""
    s = _pop(k)
    if s <= 0:
        return
    w, h = 420, 120 + 56 * len(rows)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rectangle(-w / 2, -h / 2, w, h)
    _fill_line(ctx, hexc("#fbf8ef"), 4)
    _txt(ctx, title, 0, -h / 2 + 52, 30, "#200a00")
    for i, r in enumerate(rows):
        yy = -h / 2 + 100 + i * 56
        ctx.rectangle(-w / 2 + 34, yy, 30, 30)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(3)
        ctx.stroke()
        _txt(ctx, r, -w / 2 + 84, yy + 25, 28, "#c8312c" if i == ticked else "#200a00", center=False)
        if i == ticked and k > tick_at:
            p = _ease_out((k - tick_at) / 0.15)
            ctx.move_to(-w / 2 + 38, yy + 14)
            ctx.line_to(-w / 2 + 38 + 10 * min(1, p * 2), yy + 14 + 12 * min(1, p * 2))
            if p > 0.5:
                ctx.line_to(-w / 2 + 48 + 26 * (p - 0.5) * 2, yy + 26 - 34 * (p - 0.5) * 2)
            ctx.set_source_rgb(*hexc("#c8312c"))
            ctx.set_line_width(6)
            ctx.stroke()
    ctx.restore()


def sticky_label(ctx, x, k, text, y_end=40, w=300, h=56):
    """Yellow label slides down from the top edge and settles (~0.2 s) (V1 4:40 'A YEAR LATER')."""
    if k <= 0:
        return
    p = _ease_out(k / 0.2)
    y = -h + (y_end + h) * p + 4 * math.exp(-k * 18) * math.sin(k * 40)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.02)
    ctx.rectangle(-w / 2, 0, w, h)
    _fill_line(ctx, hexc("#f7e04a"), 3)
    _txt(ctx, text, 0, h * 0.68, h * 0.55, "#200a00")
    ctx.restore()


def route_arc(ctx, x0, y0, x1, y1, k, dur=0.9, dotted=True, label0=None, label1=None, plane=False):
    """Dotted travel line drawn from A to B over a map (V1 0:58 plane arc, 4:35 Santa Clara -> Washington)."""
    p = _ease_out(k / dur)
    if p <= 0:
        return
    mx, my = (x0 + x1) / 2, min(y0, y1) - abs(x1 - x0) * 0.25
    pts = []
    for i in range(61):
        tt = i / 60 * p
        pts.append(((1 - tt) ** 2 * x0 + 2 * (1 - tt) * tt * mx + tt * tt * x1,
                    (1 - tt) ** 2 * y0 + 2 * (1 - tt) * tt * my + tt * tt * y1))
    ctx.move_to(*pts[0])
    for q in pts[1:]:
        ctx.line_to(*q)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(5)
    if dotted:
        ctx.set_dash([4, 10])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.set_dash([])
    if plane:
        px, py = pts[-1]
        ctx.save()
        ctx.translate(px, py)
        ctx.move_to(-18, 0)
        ctx.line_to(18, 0)
        ctx.move_to(0, -12)
        ctx.line_to(4, 12)
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.restore()
    for (lx, ly, lb) in ((x0, y0, label0), (x1, y1, label1)):
        if lb:
            _rrect(ctx, lx - 70, ly + 14, 140, 32, 6)
            _fill_line(ctx, hexc("#1d2340"), 2)
            _txt(ctx, lb, lx, ly + 38, 20, "#ffffff")


def live_tv(ctx, t, W=1280, H=720):
    """TV interview set background (V1 5:10): blue backdrop with light streaks, a desk, a LIVE bug."""
    g = cairo.LinearGradient(0, 0, W, H)
    g.add_color_stop_rgb(0, *hexc("#1a3f8a"))
    g.add_color_stop_rgb(1, *hexc("#0b1d4a"))
    ctx.set_source(g)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    for i in range(7):
        ctx.move_to(100 + i * 160, -20)
        ctx.line_to(220 + i * 160, -20)
        ctx.line_to(20 + i * 160 + 300, H)
        ctx.line_to(-80 + i * 160 + 300, H)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.05)
        ctx.fill()
    ctx.rectangle(160, 470, 900, 260)
    _fill_line(ctx, hexc("#e9e6df"), 5)
    ctx.rectangle(160, 470, 900, 14)
    ctx.set_source_rgb(*hexc("#c8312c"))
    ctx.fill()
    _rrect(ctx, W - 170, 30, 120, 40, 6)
    ctx.set_source_rgb(*hexc("#d0302a"))
    ctx.fill()
    if int(t * 2) % 2 == 0:
        ctx.arc(W - 150, 50, 7, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    _txt(ctx, "LIVE", W - 100, 60, 26, "#ffffff")
    return {"floor": 560}


def camera_flash(img, k, dur=0.08):
    """White flash over the whole frame for a camera shot (polaroids, V1 0:17). img: float BGR array."""
    if 0 <= k < dur:
        a = 0.6 * (1 - k / dur)
        return img * (1 - a) + a
    return img


def glow_label(ctx, x, y, k, text, size=44):
    """Yellow-green glowing money label floating over an object (V1 0:27 '$ BILLIONS')."""
    s = _pop(k)
    if s <= 0:
        return
    glow(ctx, x, y - size * 0.3, size * 2.5, hexc("#b8ff6a"), 0.35)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    _txt(ctx, text, 0, 0, size, "#c8ff4a", stroke="#0b2410")
    ctx.restore()


# ------------------------------------------------------------------ added after the every-frame pass (visual_grammar 15)
def marker_hand(ctx, x, y, t, col="#2a4fa0"):
    """A hand holding a marker, tip at (x, y), wiggling while it writes (V1 4:52)."""
    wob = math.sin(t * 40) * 3
    ctx.save()
    ctx.translate(x + wob, y + abs(wob) * 0.5)
    ctx.rotate(-0.6)
    _rrect(ctx, -10, 0, 20, 120, 8)
    _fill_line(ctx, hexc("#f4f1ea"), 3)
    ctx.rectangle(-10, 0, 20, 18)
    ctx.set_source_rgb(*hexc(col))
    ctx.fill()
    ctx.move_to(-5, 0)
    ctx.line_to(0, -14)
    ctx.line_to(5, 0)
    ctx.close_path()
    ctx.fill()
    ctx.arc(0, 120, 30, 0, 2 * math.pi)
    _fill_line(ctx, hexc("#e9a561"), 3)
    ctx.move_to(0, 140)
    ctx.line_to(30, 420)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(46)
    ctx.stroke()
    ctx.restore()


def whiteboard_live(ctx, x, y, w, h, lines, k, cps=14.0, pen_col="#2a4fa0", size=48, extra=None):
    """Whiteboard where the words are written AS THEY ARE SAID by a visible marker hand.
    k = seconds since writing started. Returns True while still writing."""
    ctx.rectangle(x, y, w, h)
    _fill_line(ctx, hexc("#f8f8f4"), 5)
    ctx.rectangle(x + 40, y + h, w - 80, 12)
    _fill_line(ctx, hexc("#c8c8c0"), 3)
    n = int(max(0.0, k) * cps)
    yy = y + 30 + size
    cur = None
    for s in lines:
        m = min(len(s), n)
        n -= m
        _slanted_font(ctx, size)
        ctx.move_to(x + 36, yy)
        ctx.set_source_rgb(*hexc(pen_col))
        ctx.show_text(s[:m])
        if 0 < m <= len(s) and (n == 0):
            e = ctx.text_extents(s[:m])
            cur = (x + 36 + e.x_advance, yy - size * 0.2)
        yy += size * 1.45
    if extra:
        extra(ctx)
    if cur and k > 0:
        marker_hand(ctx, cur[0], cur[1], k, pen_col)
        return True
    return False


def arrow_down(ctx, x, y, k, length=160, col="#d0302a"):
    """Red arrow drawn downward (a fall)."""
    p = _ease_out(k / 0.35)
    if p <= 0:
        return
    ctx.move_to(x, y)
    ctx.line_to(x + 20, y + length * p)
    ctx.set_source_rgb(*hexc(col))
    ctx.set_line_width(10)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    if p > 0.9:
        tx, ty = x + 20, y + length
        ctx.move_to(tx - 28, ty - 30)
        ctx.line_to(tx, ty)
        ctx.line_to(tx + 26, ty - 34)
        ctx.stroke()


def cash_tower(ctx, x, base, k, n_max=14, build=1.2, collapse_at=None, brick=(120, 30)):
    """Green cash bricks stack one by one (k s since start, all stacked by `build` s). After `collapse_at`
    s the bricks fall and scatter (the money disappears)."""
    bw, bh = brick
    n = min(n_max, int(max(0.0, k) / build * n_max) + (1 if k > 0 else 0))
    for i in range(n):
        bx, by, rot = x - bw / 2 + (i % 2) * 6 - 3, base - (i + 1) * bh, 0.0
        if collapse_at is not None and k > collapse_at:
            tt = k - collapse_at - i * 0.015
            if tt > 0:
                sd = -1 if i % 2 else 1
                bx += sd * (60 + i * 9) * tt * 3
                by += 900 * tt * tt
                rot = sd * tt * 4
        ctx.save()
        ctx.translate(bx + bw / 2, by + bh / 2)
        ctx.rotate(rot)
        _rrect(ctx, -bw / 2, -bh / 2, bw, bh, 4)
        _fill_line(ctx, hexc("#3f9a4a"), 3)
        ctx.rectangle(-bw * 0.12, -bh / 2, bw * 0.24, bh)
        ctx.set_source_rgb(*hexc("#e8e2c8"))
        ctx.fill()
        ctx.restore()


def slide_in(k, dur=0.25, dist=400):
    """Offset for a prop sliding in from the side and settling (returns px still to travel)."""
    return dist * (1 - _ease_out(k / dur))
