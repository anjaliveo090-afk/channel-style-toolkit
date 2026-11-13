"""Backgrounds, props and on-screen graphics for the "drawn on paper" money-story style.
All functions draw in world coordinates on a 1280x720 (16:9) canvas unless given other sizes."""
import math
import random

import cairo

from style import INK, hexc, mix

HAND = "Kalam"          # handwritten caps for tags / labels (OFL, assets/fonts)
SCRIPT = "Caveat"       # handwritten script for black text cards (OFL, assets/fonts)


def _rect(ctx, x, y, w, h, col):
    ctx.rectangle(x, y, w, h)
    ctx.set_source_rgb(*col)
    ctx.fill()


def glow(ctx, x, y, r, col, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(0.35, *col, a * 0.45)
    g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


# ------------------------------------------------------------------ restaurant
def restaurant_bg(ctx, t, W=1280, H=720, seed=3):
    """Warm night restaurant: wood panel wall, a tall window onto a night city with bokeh,
    two wall sconces, red velvet curtain edges. Floor line at y = H*0.78."""
    wall_top, wall_bot = hexc("#3a1f17"), hexc("#26130e")
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *wall_top)
    g.add_color_stop_rgb(1, *wall_bot)
    ctx.set_source(g)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.fill()
    # panels
    ctx.set_line_width(3)
    for i in range(-6, 16):
        x = i * 120
        ctx.set_source_rgba(0.08, 0.03, 0.02, 0.55)
        ctx.move_to(x, -H)
        ctx.line_to(x, H * 2)
        ctx.stroke()
        ctx.set_source_rgba(0.75, 0.45, 0.3, 0.08)
        ctx.move_to(x + 4, -H)
        ctx.line_to(x + 4, H * 2)
        ctx.stroke()
    _rect(ctx, -W, H * 0.42, 3 * W, 10, hexc("#1c0d09"))       # dado rail
    _rect(ctx, -W, H * 0.42 + 10, 3 * W, 4, hexc("#6b3b26"))
    # window with night city + bokeh
    wx, wy, ww, wh = W * 0.58, H * 0.05, W * 0.3, H * 0.52
    ctx.rectangle(wx, wy, ww, wh)
    g = cairo.LinearGradient(0, wy, 0, wy + wh)
    g.add_color_stop_rgb(0, *hexc("#0b1a3a"))
    g.add_color_stop_rgb(1, *hexc("#1d2f5c"))
    ctx.set_source(g)
    ctx.fill()
    rnd = random.Random(seed)
    ctx.save()
    ctx.rectangle(wx, wy, ww, wh)
    ctx.clip()
    for _ in range(26):          # far buildings
        bx = wx + rnd.random() * ww
        bh = wh * (0.2 + rnd.random() * 0.5)
        bw = 20 + rnd.random() * 40
        _rect(ctx, bx, wy + wh - bh, bw, bh, hexc("#13224a"))
        for _k in range(8):
            if rnd.random() < 0.6:
                _rect(ctx, bx + 4 + rnd.random() * (bw - 10), wy + wh - bh + 6 + rnd.random() * (bh - 12),
                      4, 5, (1, 0.85, 0.5))
    for _ in range(18):          # bokeh lights
        bx, by = wx + rnd.random() * ww, wy + rnd.random() * wh
        r = 8 + rnd.random() * 18
        tw = 0.5 + 0.5 * math.sin(t * 1.3 + bx)
        ctx.arc(bx, by, r, 0, 2 * math.pi)
        ctx.set_source_rgba(0.75, 0.85, 1.0, 0.12 + 0.12 * tw)
        ctx.fill()
    ctx.restore()
    # window frame + mullions
    ctx.set_source_rgb(*hexc("#1a0c08"))
    ctx.set_line_width(10)
    ctx.rectangle(wx, wy, ww, wh)
    ctx.stroke()
    ctx.set_line_width(6)
    ctx.move_to(wx + ww / 2, wy)
    ctx.line_to(wx + ww / 2, wy + wh)
    ctx.move_to(wx, wy + wh * 0.45)
    ctx.line_to(wx + ww, wy + wh * 0.45)
    ctx.stroke()
    # curtains
    for cx0, sd in ((wx - 40, -1), (wx + ww - 10, 1)):
        g = cairo.LinearGradient(cx0, 0, cx0 + 50, 0)
        g.add_color_stop_rgb(0, *hexc("#7d0f12"))
        g.add_color_stop_rgb(0.5, *hexc("#c1272a"))
        g.add_color_stop_rgb(1, *hexc("#6a0b0e"))
        ctx.set_source(g)
        ctx.rectangle(cx0, -10, 50, H * 0.7)
        ctx.fill()
    # sconces
    for sx in (W * 0.18, W * 0.42):
        sy = H * 0.2
        glow(ctx, sx, sy, 150, (1.0, 0.72, 0.35), 0.35)
        _rect(ctx, sx - 4, sy, 8, 26, hexc("#2b1a10"))
        for d in (-14, 14):
            ctx.move_to(sx + d - 9, sy - 2)
            ctx.line_to(sx + d + 9, sy - 2)
            ctx.line_to(sx + d + 6, sy - 22)
            ctx.line_to(sx + d - 6, sy - 22)
            ctx.close_path()
            ctx.set_source_rgb(1.0, 0.86, 0.55)
            ctx.fill()
    # floor shadow band
    g = cairo.LinearGradient(0, H * 0.7, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.45)
    ctx.set_source(g)
    ctx.rectangle(-W, H * 0.7, 3 * W, H)
    ctx.fill()


def booth(ctx, x, y, w, h):
    """Red velvet booth back seen behind a seated character."""
    ctx.new_path()
    ctx.move_to(x, y + h)
    ctx.line_to(x, y + 30)
    ctx.curve_to(x, y, x + 30, y, x + 30, y)
    ctx.line_to(x + w - 30, y)
    ctx.curve_to(x + w, y, x + w, y + 30, x + w, y + 30)
    ctx.line_to(x + w, y + h)
    ctx.close_path()
    g = cairo.LinearGradient(x, 0, x + w, 0)
    g.add_color_stop_rgb(0, *hexc("#6e0d10"))
    g.add_color_stop_rgb(0.5, *hexc("#b3242a"))
    g.add_color_stop_rgb(1, *hexc("#6e0d10"))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hexc("#c99a3c"))
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.set_source_rgba(0, 0, 0, 0.25)
    for k in range(1, 4):
        ctx.move_to(x + w * k / 4, y + 12)
        ctx.line_to(x + w * k / 4, y + h)
        ctx.set_line_width(3)
        ctx.stroke()


def table(ctx, cx, top, w, t, candle=True, plates=True):
    """Round table with a white cloth seen from the front; a candle in the middle."""
    h = 220
    ctx.new_path()
    ctx.save()
    ctx.translate(cx, top)
    ctx.scale(w / 2, 34)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*hexc("#f4ead2"))
    ctx.fill()
    ctx.rectangle(cx - w / 2, top, w, h)
    g = cairo.LinearGradient(0, top, 0, top + h)
    g.add_color_stop_rgb(0, *hexc("#efe2c3"))
    g.add_color_stop_rgb(1, *hexc("#b89e78"))
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(0.45, 0.33, 0.2, 0.35)
    ctx.set_line_width(2.5)
    for k in (-0.3, 0.05, 0.35):
        ctx.move_to(cx + k * w, top + 30)
        ctx.curve_to(cx + k * w + 6, top + 90, cx + k * w - 4, top + 150, cx + k * w + 4, top + h)
        ctx.stroke()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(3)
    ctx.save()
    ctx.translate(cx, top)
    ctx.scale(w / 2, 34)
    ctx.arc(0, 0, 1, 0, math.pi)
    ctx.restore()
    ctx.stroke()
    if plates:
        for px in (cx - w * 0.28, cx + w * 0.28):
            ctx.save()
            ctx.translate(px, top + 4)
            ctx.scale(70, 15)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(2)
            ctx.stroke()
            ctx.save()
            ctx.translate(px, top + 1)
            ctx.scale(30, 9)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgb(*hexc("#8a3a1e"))
            ctx.fill()
    if candle:
        candle_at(ctx, cx, top - 4, t)


def candle_at(ctx, x, y, t, s=1.0):
    fl = 1 + 0.06 * math.sin(t * 17) + 0.04 * math.sin(t * 29)
    glow(ctx, x, y - 60 * s, 260 * s * fl, (1.0, 0.75, 0.38), 0.55)
    ctx.rectangle(x - 12 * s, y - 52 * s, 24 * s, 52 * s)
    ctx.set_source_rgb(*hexc("#f7f0dc"))
    ctx.fill()
    ctx.save()
    ctx.translate(x, y - 66 * s)
    ctx.scale(7 * s, 14 * s * fl)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(1, 0.92, 0.55)
    ctx.fill()


# ------------------------------------------------------------------ graphics (screen space)
def name_tag(ctx, text, x, y, k, accent="#e8a33d", size=30):
    """Lower-third name tag: dark box, coloured accent bar, handwritten caps. k = 0..1 slide-in."""
    if k <= 0:
        return
    ctx.save()
    ctx.select_font_face(HAND, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ext = ctx.text_extents(text)
    w, h = ext.x_advance + 44, size * 1.55
    off = (1 - k) ** 3 * -60
    ctx.translate(x + off, y)
    ctx.rectangle(0, 0, w, h)
    ctx.set_source_rgba(0.06, 0.05, 0.05, 0.82 * k)
    ctx.fill()
    ctx.rectangle(0, 0, 6, h)
    ctx.set_source_rgba(*hexc(accent), k)
    ctx.fill()
    ctx.move_to(22, h * 0.72)
    ctx.set_source_rgba(1, 1, 1, k)
    ctx.show_text(text)
    ctx.restore()


def pop_label(ctx, text, x, y, k, col="#e23b2e", size=64, angle=-0.06):
    """Handwritten label that pops in with overshoot (k = time since start in s)."""
    if k <= 0:
        return
    sc = 1 + 0.35 * math.exp(-k * 9) * math.cos(k * 22) if k < 0.6 else 1
    sc *= min(1, k / 0.08)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(sc, sc)
    ctx.select_font_face(HAND, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ext = ctx.text_extents(text)
    ctx.move_to(-ext.x_advance / 2, ext.height / 2)
    ctx.text_path(text)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(0.08, 0.05, 0.05)
    ctx.set_line_width(size * 0.16)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc(col))
    ctx.fill()
    ctx.restore()


def text_card(ctx, text, t, W=1280, H=720, cps=24.0, size=46, align="center"):
    """Black screen, white handwritten script typed on letter by letter. Returns letters shown."""
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    n = max(0, min(len(text), int(t * cps)))
    ctx.select_font_face(SCRIPT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    full = ctx.text_extents(text)
    x = (W - full.x_advance) / 2 if align == "center" else W * 0.08
    ctx.move_to(x, H * 0.5 + size * 0.3)
    ctx.set_source_rgb(0.97, 0.97, 0.97)
    ctx.show_text(text[:n])
    return n
