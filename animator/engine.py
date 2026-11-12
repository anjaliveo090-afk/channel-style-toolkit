"""Small cairo toolkit for reference-style stick-figure shorts (9:16, 30 fps).

Scenes draw in a 720x1280 "world"; each shot has a camera (zoom + centre,
eased over the shot) and shots are joined with cross-dissolves."""
import math
import random
import subprocess

import cairo
import numpy as np

W, H, FPS = 720, 1280, 30
INK = (0.10, 0.09, 0.12)
PI = math.pi
LIPSYNC = True  # False: mouths keep the scene expression instead of following the voice
ENERGY = 2.0  # character motion multiplier (idle sway, head and hand movement)


# ---------- helpers ----------
def hexc(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else (*c, a)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def keyed(t, keys):
    """[(time, value), ...] -> value of the last key at or before t (snappy changes)."""
    v = keys[0][1]
    for k, val in keys:
        if t >= k:
            v = val
    return v


def pop(t):
    """Scale for a bouncy pop-in starting at t=0 (0 before)."""
    if t < 0:
        return 0.0
    return 1 + 0.35 * math.exp(-7 * t) * math.cos(16 * t) - 0.35 * math.exp(-40 * t)


def src(ctx, c):
    ctx.set_source_rgba(*c) if len(c) == 4 else ctx.set_source_rgb(*c)


def fill_stroke(ctx, col, lw=5.0):
    src(ctx, col)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(lw)
    ctx.stroke()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -PI / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
    ctx.arc(x + r, y + h - r, r, PI / 2, PI)
    ctx.arc(x + r, y + r, r, PI, 1.5 * PI)
    ctx.close_path()


def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * PI)
    ctx.restore()


def text(ctx, s, x, y, size, col=(1, 1, 1), outline=True, scale=1.0):
    if scale <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    ctx.move_to(-e.width / 2 - e.x_bearing, -e.height / 2 - e.y_bearing)
    ctx.text_path(s)
    if outline:
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(size * 0.18)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    src(ctx, col)
    ctx.fill()
    ctx.restore()


def label(ctx, s, x, y, size, bg, fg=(1, 1, 1), scale=1.0, tilt=-0.05):
    """Sign / sticker: rounded box with text, pops with `scale`."""
    if scale <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(scale, scale)
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    pw, ph = e.width + size * 0.9, size * 1.5
    rrect(ctx, -pw / 2, -ph / 2, pw, ph, size * 0.3)
    fill_stroke(ctx, bg, size * 0.12)
    ctx.move_to(-e.width / 2 - e.x_bearing, -e.height / 2 - e.y_bearing)
    ctx.text_path(s)
    src(ctx, fg)
    ctx.fill()
    ctx.restore()


# ---------- characters ----------
class Char:
    """Big round head, bean body, stick limbs, thick outlines, flat colours."""

    def __init__(self, body, hair="bowl", hair_col="#5a3a22", skin="#f6dcc0",
                 mustache=None, tie=None, hat_col="#1f1f28", glasses=False):
        self.body = hexc(body)
        self.hair = hair
        self.hair_col = hexc(hair_col)
        self.skin = hexc(skin)
        self.mustache = hexc(mustache) if mustache else None
        self.tie = hexc(tie) if tie else None
        self.hat_col = hexc(hat_col)
        self.glasses = glasses

    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False,
             arms=("down", "down"), pose="stand", look=0.0, bob=1.0,
             item=None, item_hand=1, walk_phase=0.0, lean=0.0, head_nod=0.0):
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(s, s)
        lw = 6.0
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        e = ENERGY * bob
        dy = -abs(math.sin(t * 2 * PI * 2.0)) * 7 * e
        hip_y = -85 + dy

        # legs
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw)
        feet = []
        for side in (-1, 1):
            hx = side * 16
            if pose == "sit":
                kx, ky, fx, fy = hx + 48, hip_y + 4, hx + 52, 0
                ctx.move_to(hx, hip_y)
                ctx.line_to(kx, ky)
                ctx.line_to(fx, fy)
            elif pose == "walk":
                sw = math.sin(walk_phase * 2 * PI + (0 if side < 0 else PI))
                fx, fy = hx + sw * 22, -max(0, sw) * 10
                ctx.move_to(hx, hip_y)
                ctx.line_to(fx, fy)
            else:
                fx, fy = hx * 1.1, 0
                ctx.move_to(hx, hip_y)
                ctx.line_to(fx, fy)
            ctx.stroke()
            feet.append((fx, fy))
        for fx, fy in feet:
            ellipse(ctx, fx + 6, fy - 2, 14, 7)
            fill_stroke(ctx, (0.25, 0.17, 0.12), 3)

        # upper body (leans around the hip)
        ctx.save()
        ctx.translate(0, hip_y)
        ctx.rotate(lean + math.sin(t * 2.7) * 0.06 * e)
        rrect(ctx, -37, -105, 74, 112, 34)
        fill_stroke(ctx, self.body, 5)
        if self.tie:
            ctx.move_to(-7, -100)
            ctx.line_to(7, -100)
            ctx.line_to(4, -55)
            ctx.line_to(0, -48)
            ctx.line_to(-4, -55)
            ctx.close_path()
            fill_stroke(ctx, self.tie, 2.5)

        hcx, hcy = 0, -105 - 52 + head_nod + math.sin(t * 4.3) * 3 * e
        r = 64
        # head
        ctx.new_sub_path()
        ctx.arc(hcx, hcy, r, 0, 2 * PI)
        fill_stroke(ctx, self.skin, 5.5)
        self._hair(ctx, hcx, hcy, r)
        draw_face(ctx, hcx, hcy, r, expr, t, talk, look, self)
        for i, side in enumerate((-1, 1)):
            sx, sy = side * 30, -88
            a = arms[i]
            if a == "down":
                hx, hy = sx + side * 16, sy + 74
            elif a == "up":
                hx, hy = sx + side * 34, sy - 88
            elif a == "point":
                hx, hy = sx + side * 98, sy - 30
            elif a == "hold":
                hx, hy = side * 20, sy + 46
            elif a == "show":
                hx, hy = sx + side * 60, sy - 40
            elif a == "hip":
                hx, hy = sx + side * 30, sy + 44
            elif a == "wag":
                hx, hy = sx + side * 52, sy - 70 + math.sin(t * 14) * 9
            elif a == "wave":
                hx, hy = sx + side * 55 + math.sin(t * 11) * 14, sy - 84
            elif a == "write":
                hx, hy = side * 6 + math.sin(t * 22) * 5, sy + 38
            elif a == "salute":
                hx, hy = side * 34, hcy - 34
            elif a == "shrug":
                hx, hy = sx + side * 50, sy - 6
            else:
                hx, hy = sx + side * 16, sy + 74
            if a not in ("salute", "write"):
                hx += math.sin(t * 3.8 + side) * 6 * e
                hy += math.cos(t * 3.1 + side) * 5 * e
            mx, my = (sx + hx) / 2, (sy + hy) / 2
            ctx.move_to(sx, sy)
            ctx.curve_to(mx + side * 14, my, mx + side * 14, my, hx, hy)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw)
            ctx.stroke()
            if item and i == item_hand:
                draw_item(ctx, item, hx, hy, t)
            ctx.new_sub_path()
            ctx.arc(hx, hy, 9, 0, 2 * PI)
            fill_stroke(ctx, self.skin, 3.5)

        ctx.restore()
        ctx.restore()

    def _hair(self, ctx, cx, cy, r):
        h = self.hair
        if h in ("bowl", "side"):
            ctx.new_sub_path()
            ctx.arc(cx, cy, r + 1.5, PI + 0.28, 2 * PI - 0.28)
            ctx.close_path()
            fill_stroke(ctx, self.hair_col, 5)
            if h == "side":
                ctx.move_to(cx - r * 0.25, cy - r * 0.98)
                ctx.line_to(cx - r * 0.35, cy - r * 0.35)
                ctx.set_line_width(3)
                ctx.stroke()
        elif h == "cap":
            ctx.new_sub_path()
            ctx.arc(cx, cy, r + 3, PI + 0.42, 2 * PI - 0.42)
            ctx.close_path()
            fill_stroke(ctx, self.hair_col, 5)
            ellipse(ctx, cx + r * 0.55, cy - r * 0.42, r * 0.45, r * 0.12)
            fill_stroke(ctx, self.hair_col, 4)
        elif h == "tophat":
            ellipse(ctx, cx, cy - r * 0.86, r * 0.95, r * 0.18)
            fill_stroke(ctx, self.hat_col, 4.5)
            rrect(ctx, cx - r * 0.58, cy - r * 2.0, r * 1.16, r * 1.15, 6)
            fill_stroke(ctx, self.hat_col, 4.5)
            ctx.rectangle(cx - r * 0.58, cy - r * 1.08, r * 1.16, r * 0.2)
            src(ctx, hexc("#b8322a"))
            ctx.fill()
            for side in (-1, 1):
                ellipse(ctx, cx + side * r * 0.9, cy - r * 0.15, r * 0.14, r * 0.3)
                fill_stroke(ctx, self.hair_col, 3)
        elif h == "bald":
            for side in (-1, 1):
                ellipse(ctx, cx + side * r * 0.92, cy - r * 0.2, r * 0.16, r * 0.32)
                fill_stroke(ctx, self.hair_col, 3)


# ---------- lip-sync from the voiceover ----------
_VOICE = {"env": None}
_NOW = {"t": 0.0, "speaker": None}


def set_voice(path):
    """Load the voiceover loudness (30 values per second) to drive mouths."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    hop = 16000 // FPS
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    _VOICE["env"] = np.clip(rms / (np.percentile(rms, 95) + 1e-6), 0, 1)


def voice_level():
    env = _VOICE["env"]
    if env is None:
        return 0.0
    i = int(_NOW["t"] * FPS)
    v = float(env[i]) if 0 <= i < len(env) else 0.0
    return 0.0 if v < 0.45 else (0.55 if v < 0.8 else 1.0)  # snap to 3 mouth sizes, closed between syllables


def draw_face(ctx, cx, cy, r, expr, t, talk, look, ch=None):
    lx = look * r * 0.2
    ey = cy + 0.08 * r
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgb(*INK)

    def dot(x, y, rr=0.08):
        ctx.new_sub_path()
        ctx.arc(x, y, r * rr, 0, 2 * PI)
        ctx.set_source_rgb(*INK)
        ctx.fill()

    def line(x1, y1, x2, y2, w=4.5):
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(w)
        ctx.stroke()

    for side in (-1, 1):
        ex = cx + side * 0.33 * r + lx
        if expr in ("happy", "grin", "laugh"):
            ctx.new_sub_path()
            ctx.arc(ex, ey + r * 0.05, r * 0.13, PI + 0.2, 2 * PI - 0.2)
            ctx.set_line_width(5)
            ctx.stroke()
        elif expr == "shock":
            ctx.new_sub_path()
            ctx.arc(ex, ey, r * 0.21, 0, 2 * PI)
            fill_stroke(ctx, (1, 1, 1), 4)
            dot(ex + lx * 0.3, ey, 0.055)
            line(ex - r * 0.16, ey - r * 0.42, ex + r * 0.16, ey - r * 0.46)
        elif expr in ("smirk", "cold"):
            line(ex - r * 0.14, ey - r * 0.02, ex + r * 0.14, ey - r * 0.02, 5)
            ctx.save()
            ctx.rectangle(ex - r * 0.2, ey - r * 0.02, r * 0.4, r * 0.3)
            ctx.clip()
            dot(ex, ey + r * 0.0, 0.085)
            ctx.restore()
            if expr == "smirk" and side == 1:
                line(ex - r * 0.14, ey - r * 0.36, ex + r * 0.14, ey - r * 0.42)
            elif expr == "cold":
                line(ex - r * 0.15, ey - r * 0.22 - side * r * 0.0, ex + r * 0.15, ey - r * 0.22)
        else:
            dot(ex, ey)
            if expr == "angry":
                line(ex - side * r * 0.17, ey - r * 0.32, ex + side * r * 0.12, ey - r * 0.2)
            elif expr == "sad":
                line(ex - side * r * 0.17, ey - r * 0.2, ex + side * r * 0.12, ey - r * 0.32)
            elif expr == "determined":
                line(ex - r * 0.14, ey - r * 0.22, ex + r * 0.14, ey - r * 0.22)
            elif expr == "worried":
                line(ex - side * r * 0.17, ey - r * 0.26, ex + side * r * 0.12, ey - r * 0.36)

    if ch is not None and ch.glasses:
        for side in (-1, 1):
            ctx.new_sub_path()
            ctx.arc(cx + side * 0.33 * r + lx, ey, r * 0.2, 0, 2 * PI)
            ctx.set_line_width(3.5)
            ctx.stroke()

    my = cy + 0.47 * r
    mx = cx + lx * 1.2
    mouth = expr
    level = 0.0
    speaking = talk or (ch is not None and _NOW["speaker"] is ch)
    if speaking and _VOICE["env"] is not None:
        level = voice_level()
        if level > 0 and expr not in ("laugh", "shock"):
            mouth = "open"
    elif talk and expr in ("neutral", "determined", "worried", "smirk", "sad", "happy"):
        if int(t * 9) % 2 == 0:
            mouth = "talk"
    if ch is not None and ch.mustache:
        my += r * 0.06
    if mouth == "talk":
        ellipse(ctx, mx, my, r * 0.11, r * 0.08)
        fill_stroke(ctx, hexc("#6b1f24"), 3.5)
    elif mouth == "open" and expr == "grin":
        # the reference boss: teeth grin opens into a laugh shape while talking
        ctx.new_sub_path()
        ctx.arc(mx, my - r * 0.08, r * (0.2 + 0.12 * level), 0, PI)
        ctx.close_path()
        fill_stroke(ctx, hexc("#7a1f28"), 4)
        rrect(ctx, mx - r * 0.18, my - r * 0.08, r * 0.36, r * 0.08, 2)
        src(ctx, (1, 1, 1))
        ctx.fill()
    elif mouth == "open":
        ellipse(ctx, mx, my + r * 0.02, r * (0.1 + 0.06 * level), r * (0.05 + 0.1 * level))
        fill_stroke(ctx, hexc("#6b1f24"), 3.5)
    elif mouth in ("neutral", "determined"):
        line(mx - r * 0.13, my, mx + r * 0.13, my)
    elif mouth == "smirk":
        ctx.move_to(mx - r * 0.14, my + r * 0.02)
        ctx.curve_to(mx, my + r * 0.04, mx + r * 0.1, my, mx + r * 0.18, my - r * 0.07)
        ctx.set_line_width(4.5)
        ctx.stroke()
    elif mouth == "shock":
        ellipse(ctx, mx, my + r * 0.04, r * 0.08, r * 0.11)
        fill_stroke(ctx, hexc("#6b1f24"), 3.5)
    elif mouth == "happy":
        ctx.new_sub_path()
        ctx.arc(mx, my - r * 0.1, r * 0.17, 0.3, PI - 0.3)
        ctx.set_line_width(4.5)
        ctx.stroke()
    elif mouth == "grin":
        rrect(ctx, mx - r * 0.36, my - r * 0.12, r * 0.72, r * 0.26, r * 0.08)
        fill_stroke(ctx, (1, 1, 1), 4)
        for k in range(1, 6):
            xx = mx - r * 0.36 + k * r * 0.12
            line(xx, my - r * 0.12, xx, my + r * 0.14, 2)
        line(mx - r * 0.36, my + r * 0.01, mx + r * 0.36, my + r * 0.01, 2)
    elif mouth == "laugh":
        ctx.new_sub_path()
        ctx.arc(mx, my - r * 0.05, r * 0.24, 0, PI)
        ctx.close_path()
        fill_stroke(ctx, hexc("#7a1f28"), 4)
        for side in (-1, 1):
            k = (t * 2.5) % 1
            ellipse(ctx, cx + side * r * 0.55, ey + r * 0.1 + k * r * 0.4, r * 0.05, r * 0.08)
            fill_stroke(ctx, hexc("#7fd3ff"), 2)
    elif mouth in ("angry", "sad"):
        ctx.new_sub_path()
        ctx.arc(mx, my + r * 0.12, r * 0.15, PI + 0.5, 2 * PI - 0.5)
        ctx.set_line_width(4.5)
        ctx.stroke()
    elif mouth == "worried":
        ctx.move_to(mx - r * 0.14, my)
        for k in range(1, 5):
            ctx.line_to(mx - r * 0.14 + k * r * 0.07, my + (r * 0.04 if k % 2 else -r * 0.02))
        ctx.set_line_width(4)
        ctx.stroke()
    elif mouth == "cold":
        ctx.move_to(mx - r * 0.18, my)
        ctx.curve_to(mx - r * 0.05, my + r * 0.05, mx + r * 0.05, my + r * 0.05, mx + r * 0.18, my - r * 0.02)
        ctx.set_line_width(4)
        ctx.stroke()

    if ch is not None and ch.mustache:
        for side in (-1, 1):
            ellipse(ctx, cx + side * r * 0.14 + lx, cy + r * 0.38, r * 0.17, r * 0.08)
            fill_stroke(ctx, ch.mustache, 3)


def draw_item(ctx, item, x, y, t):
    if item == "watch":
        ctx.move_to(x, y)
        ctx.curve_to(x - 10, y + 30, x - 30, y + 30, x - 34, y + 10)
        ctx.set_source_rgb(*hexc("#e0b84a"))
        ctx.set_line_width(2.5)
        ctx.stroke()
        clock_face(ctx, x, y - 22, 20, 6, 0, rim="#d9a92e", lw=3)
    elif item == "notebook":
        rrect(ctx, x - 26, y - 34, 50, 62, 4)
        fill_stroke(ctx, (0.98, 0.96, 0.88), 3)
        for k in range(5):
            ctx.move_to(x - 18, y - 22 + k * 10)
            ctx.line_to(x + 16, y - 22 + k * 10)
        ctx.set_source_rgba(0.3, 0.4, 0.7, 0.6)
        ctx.set_line_width(1.5)
        ctx.stroke()
    elif item == "sandwich":
        draw_sandwich(ctx, x, y - 12)
    elif item == "suitcase":
        rrect(ctx, x - 34, y + 8, 68, 48, 8)
        fill_stroke(ctx, hexc("#8a5a33"), 3.5)
        ctx.move_to(x - 10, y + 8)
        ctx.line_to(x - 10, y)
        ctx.line_to(x + 10, y)
        ctx.line_to(x + 10, y + 8)
        ctx.set_line_width(3)
        ctx.stroke()


def draw_sandwich(ctx, x, y, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    for k, col in enumerate(("#e9c27a", "#d9776d", "#7cc35a", "#e9c27a")):
        ctx.move_to(-28, 10 - k * 7)
        ctx.line_to(28, 10 - k * 7)
        ctx.line_to(0, -22 - k * 7)
        ctx.close_path()
        fill_stroke(ctx, hexc(col), 3)
    ctx.restore()



# ---------- parallax ----------
_CAM = {"z": 1.0, "c": (W / 2, H / 2), "z0": 1.0, "c0": (W / 2, H / 2), "strength": 1.0}


def _parallax(fn, default):
    """Draw a layer with depth k: k<1 is farther (moves less with the camera),
    k>1 is foreground (moves more). Gives the flat 2D sets a 3D-like camera."""
    def wrapper(ctx, *a, depth=None, **kw):
        k = depth if depth is not None else default(a, kw)
        k = 1 - (1 - k) * _CAM["strength"]
        if abs(k - 1) < 1e-3:
            return fn(ctx, *a, **kw)
        z, (cx, cy), z0, (x0, y0) = _CAM["z"], _CAM["c"], _CAM["z0"], _CAM["c0"]
        zk = z0 + (z - z0) * k
        ckx, cky = x0 + (cx - x0) * k, y0 + (cy - y0) * k
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(zk / z, zk / z)
        ctx.translate(-ckx, -cky)
        fn(ctx, *a, **kw)
        ctx.restore()
    wrapper.__name__ = fn.__name__
    return wrapper

# ---------- props & backgrounds ----------
def clock_face(ctx, cx, cy, r, h, m, rim="#3a2c26", face="#fbf3dc", lw=None, glow=0.0, eyes=None):
    lw = lw or max(3, r * 0.06)
    if glow > 0:
        g = cairo.RadialGradient(cx, cy, r * 0.5, cx, cy, r * 2.2)
        g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.55 * glow)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g)
        ctx.arc(cx, cy, r * 2.2, 0, 2 * PI)
        ctx.fill()
    ctx.new_sub_path()
    ctx.arc(cx, cy, r * 1.1, 0, 2 * PI)
    fill_stroke(ctx, hexc(rim), lw)
    ctx.new_sub_path()
    ctx.arc(cx, cy, r, 0, 2 * PI)
    fill_stroke(ctx, hexc(face), lw * 0.7)
    ctx.set_source_rgb(*INK)
    for k in range(12):
        a = k * PI / 6
        r1 = r * (0.78 if k % 3 == 0 else 0.86)
        ctx.move_to(cx + math.sin(a) * r1, cy - math.cos(a) * r1)
        ctx.line_to(cx + math.sin(a) * r * 0.93, cy - math.cos(a) * r * 0.93)
        ctx.set_line_width(lw * (0.9 if k % 3 == 0 else 0.5))
        ctx.stroke()
    if eyes:
        draw_face(ctx, cx, cy - r * 0.15, r * 0.75, eyes, 0, False, 0)
    ha = ((h % 12) + m / 60) * PI / 6
    ma = m * PI / 30
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for ang, ln, w in ((ha, 0.5, 1.4), (ma, 0.78, 0.9)):
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.sin(ang) * r * ln, cy - math.cos(ang) * r * ln)
        ctx.set_line_width(lw * w)
        ctx.set_source_rgb(*INK)
        ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(cx, cy, lw * 0.9, 0, 2 * PI)
    ctx.fill()


def sky(ctx, top, bottom, y0=-400, y1=H + 200):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bottom)
    ctx.set_source(g)
    ctx.rectangle(-3000, -5000, W + 6000, H + 10000)
    ctx.fill()


def stars(ctx, seed, n, alpha, t=0.0, ymax=700):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(-200, W + 200), rnd.uniform(-300, ymax)
        a = alpha * (0.5 + 0.5 * math.sin(t * 3 + x))
        ctx.set_source_rgba(1, 1, 0.9, a)
        ctx.arc(x, y, rnd.uniform(1, 2.6), 0, 2 * PI)
        ctx.fill()


def glow(ctx, x, y, r, col, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * PI)
    ctx.fill()


def disc(ctx, x, y, r, col):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * PI)
    src(ctx, col)
    ctx.fill()


def hills(ctx, base, col, seed, amp=60, x0=-600, x1=W + 600):
    rnd = random.Random(seed)
    ctx.move_to(x0, H + 800)
    x = x0
    ctx.line_to(x, base)
    while x < x1:
        nx = x + rnd.uniform(120, 260)
        ctx.curve_to(x + 40, base - rnd.uniform(0, amp), nx - 40, base - rnd.uniform(0, amp), nx, base)
        x = nx
    ctx.line_to(x1, H + 800)
    ctx.close_path()
    src(ctx, col)
    ctx.fill()


def houses(ctx, base, seed, s, wall, roof, win, lit=0.0, x0=-500, x1=W + 500, outline=3.0):
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        w = rnd.uniform(80, 140) * s
        h = rnd.uniform(110, 230) * s
        rh = rnd.uniform(40, 80) * s
        wc = lerpc(wall, (1, 1, 1), rnd.uniform(-0.08, 0.12))
        ctx.rectangle(x, base - h, w, h + 900)
        fill_stroke(ctx, wc, outline)
        ctx.move_to(x - 6 * s, base - h)
        ctx.line_to(x + w / 2, base - h - rh)
        ctx.line_to(x + w + 6 * s, base - h)
        ctx.close_path()
        fill_stroke(ctx, roof, outline)
        for row in range(int(h / (55 * s))):
            for col in range(max(1, int(w / (45 * s)))):
                wx = x + 14 * s + col * 45 * s
                wy = base - h + 22 * s + row * 55 * s
                if wx + 20 * s > x + w:
                    continue
                on = rnd.random() < 0.55
                c = lerpc(win, (1.0, 0.82, 0.45), lit if on else 0)
                ctx.rectangle(wx, wy, 20 * s, 26 * s)
                fill_stroke(ctx, c, outline * 0.6)
                if on and lit > 0:
                    glow(ctx, wx + 10 * s, wy + 13 * s, 40 * s, (1, 0.8, 0.4), 0.25 * lit)
        x += w + rnd.uniform(-4, 10) * s


def bricks(ctx, x, y, w, h, base, mortar, size=34):
    ctx.rectangle(x, y, w, h)
    src(ctx, base)
    ctx.fill()
    ctx.set_source_rgba(*mortar, 0.55)
    ctx.set_line_width(2)
    row = 0
    yy = y
    while yy < y + h:
        ctx.move_to(x, yy)
        ctx.line_to(x + w, yy)
        off = (size if row % 2 else 0)
        xx = x + off
        while xx < x + w:
            ctx.move_to(xx, yy)
            ctx.line_to(xx, min(yy + size * 0.5, y + h))
            xx += size * 2
        yy += size * 0.5
        row += 1
    ctx.stroke()


def tower(ctx, cx, base, s, h, m, lit=0.0, bell=0.0, clock_eyes=None, glow_a=0.0):
    tw = 170 * s
    top = base - 760 * s
    ctx.rectangle(cx - tw / 2, top, tw, 760 * s + 900)
    fill_stroke(ctx, hexc("#9c5b44"), 4)
    bricks(ctx, cx - tw / 2 + 3, top + 3, tw - 6, 760 * s, hexc("#9c5b44"), hexc("#5e3226"), 22 * s)
    ctx.rectangle(cx - tw / 2, top, tw, 760 * s + 900)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.stroke()
    # belfry
    bw = tw * 1.12
    by = top - 170 * s
    ctx.rectangle(cx - bw / 2, by, bw, 170 * s)
    fill_stroke(ctx, hexc("#b46c50"), 4)
    rrect(ctx, cx - bw * 0.3, by + 25 * s, bw * 0.6, 140 * s, bw * 0.3)
    fill_stroke(ctx, hexc("#2a1d2e"), 3)
    ctx.save()
    ctx.translate(cx, by + 40 * s)
    ctx.rotate(bell)
    ctx.move_to(-38 * s, 95 * s)
    ctx.curve_to(-34 * s, 20 * s, -24 * s, 0, 0, 0)
    ctx.curve_to(24 * s, 0, 34 * s, 20 * s, 38 * s, 95 * s)
    ctx.close_path()
    fill_stroke(ctx, hexc("#e2b23c"), 3.5)
    ctx.restore()
    # spire
    ctx.move_to(cx - bw / 2 - 14 * s, by)
    ctx.line_to(cx, by - 230 * s)
    ctx.line_to(cx + bw / 2 + 14 * s, by)
    ctx.close_path()
    fill_stroke(ctx, hexc("#3f4e74"), 4)
    clock_face(ctx, cx, top + 120 * s, 66 * s, h, m, glow=glow_a, eyes=clock_eyes)
    for k in range(3):
        wy = top + 260 * s + k * 150 * s
        rrect(ctx, cx - 18 * s, wy, 36 * s, 70 * s, 18 * s)
        fill_stroke(ctx, lerpc(hexc("#2c2235"), (1, 0.82, 0.45), lit), 3)


def mill(ctx, x, base, s, t, lit=0.0, gate=True):
    w, h = 460 * s, 330 * s
    for k, sx in enumerate((x + 60 * s, x + w - 110 * s)):
        ctx.rectangle(sx, base - h - 260 * s, 50 * s, 300 * s)
        fill_stroke(ctx, hexc("#7d4636"), 4)
        for p in range(6):
            ph = (t * 0.6 + p / 6 + k * 0.3) % 1
            px = sx + 25 * s + math.sin(ph * 5 + k) * 18 * s + ph * 60 * s
            py = base - h - 270 * s - ph * 300 * s
            ctx.set_source_rgba(0.85, 0.85, 0.88, 0.55 * (1 - ph))
            ctx.arc(px, py, (22 + ph * 50) * s, 0, 2 * PI)
            ctx.fill()
    ctx.rectangle(x, base - h, w, h + 900)
    fill_stroke(ctx, hexc("#a2563f"), 4)
    bricks(ctx, x + 3, base - h + 3, w - 6, h, hexc("#a2563f"), hexc("#5e3226"), 24 * s)
    ctx.rectangle(x, base - h, w, h + 900)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.stroke()
    n = 5
    for k in range(n):
        ctx.move_to(x + k * w / n, base - h)
        ctx.line_to(x + k * w / n + w / n * 0.5, base - h - 60 * s)
        ctx.line_to(x + (k + 1) * w / n, base - h)
    ctx.close_path()
    fill_stroke(ctx, hexc("#4b3a4f"), 4)
    for row in range(2):
        for k in range(6):
            wx = x + 26 * s + k * 72 * s
            wy = base - h + 40 * s + row * 110 * s
            rrect(ctx, wx, wy, 40 * s, 60 * s, 18 * s)
            fill_stroke(ctx, lerpc(hexc("#2d2a3b"), (1, 0.8, 0.45), lit), 3)
    if gate:
        rrect(ctx, x + w / 2 - 55 * s, base - 120 * s, 110 * s, 140 * s, 50 * s)
        fill_stroke(ctx, hexc("#3b2a22"), 4)


def cobbles(ctx, y0, top_col, bot_col, y1=H + 400):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top_col)
    g.add_color_stop_rgb(1, *bot_col)
    ctx.set_source(g)
    ctx.rectangle(-600, y0, W + 1200, y1 - y0 + 600)
    ctx.fill()
    rnd = random.Random(7)
    y = y0 + 10
    row = 0
    while y < y1:
        sz = 10 + (y - y0) * 0.05
        x = -600 + (sz if row % 2 else 0)
        while x < W + 600:
            ellipse(ctx, x, y, sz * 1.5, sz * 0.5)
            ctx.set_source_rgba(0, 0, 0, 0.12 + rnd.random() * 0.06)
            ctx.fill()
            x += sz * 3.4
        y += sz * 1.3
        row += 1


def shafts(ctx, t, col=(1, 0.9, 0.6), a=0.18, x=-100):
    for k in range(3):
        sx = x + k * 170 + math.sin(t * 1.4 + k) * 22
        g = cairo.LinearGradient(sx, 0, sx + 500, H)
        g.add_color_stop_rgba(0, *col, a)
        g.add_color_stop_rgba(1, *col, 0)
        ctx.set_source(g)
        ctx.move_to(sx, -200)
        ctx.line_to(sx + 90, -200)
        ctx.line_to(sx + 640, H + 200)
        ctx.line_to(sx + 360, H + 200)
        ctx.close_path()
        ctx.fill()


def bokeh(ctx, seed, n, t, col, a=0.25):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(-100, W + 100) + math.sin(t * 0.4 + rnd.random() * 6) * 20
        y = (rnd.uniform(0, H) - t * rnd.uniform(15, 50)) % (H + 200) - 100
        r = rnd.uniform(6, 26)
        glow(ctx, x, y, r, col, a * rnd.uniform(0.4, 1))


def sun(ctx, x, y, r, col):
    glow(ctx, x, y, r * 4, col, 0.45)
    disc(ctx, x, y, r, (*col, 1))


def moon(ctx, x, y, r):
    glow(ctx, x, y, r * 3.5, (0.8, 0.85, 1), 0.3)
    disc(ctx, x, y, r, (0.97, 0.95, 0.85, 1))


def hourglass(ctx, cx, cy, s, fill_top):
    w, h = 120 * s, 170 * s
    for sign in (-1, 1):
        ctx.rectangle(cx - w * 0.75, cy + sign * h - (12 * s if sign > 0 else 0) - (0 if sign > 0 else 0), w * 1.5, 14 * s)
        fill_stroke(ctx, hexc("#7a4a2a"), 4)
    ctx.move_to(cx - w * 0.6, cy - h + 14 * s)
    ctx.line_to(cx + w * 0.6, cy - h + 14 * s)
    ctx.line_to(cx + 8 * s, cy)
    ctx.line_to(cx + w * 0.6, cy + h - 12 * s)
    ctx.line_to(cx - w * 0.6, cy + h - 12 * s)
    ctx.line_to(cx - 8 * s, cy)
    ctx.close_path()
    fill_stroke(ctx, (0.85, 0.93, 1.0, 0.35), 4)
    sand = hexc("#f0c45a")
    ft = clamp(fill_top)
    ty = cy - (h - 14 * s) * ft
    ctx.move_to(cx - w * 0.6 * ft, ty)
    ctx.line_to(cx + w * 0.6 * ft, ty)
    ctx.line_to(cx + 6 * s, cy - 2)
    ctx.line_to(cx - 6 * s, cy - 2)
    ctx.close_path()
    src(ctx, sand)
    ctx.fill()
    fb = 1 - ft
    by = cy + h - 12 * s
    ctx.move_to(cx - w * 0.6, by)
    ctx.line_to(cx + w * 0.6, by)
    ctx.line_to(cx, by - (h - 12 * s) * 0.75 * fb)
    ctx.close_path()
    ctx.fill()
    ctx.rectangle(cx - 2.5 * s, cy, 5 * s, h - 14 * s)
    ctx.fill()


# depth of each background helper (scaled sets: smaller scale = farther away)
sky = _parallax(sky, lambda a, kw: 0.15)
stars = _parallax(stars, lambda a, kw: 0.2)
sun = _parallax(sun, lambda a, kw: 0.25)
moon = _parallax(moon, lambda a, kw: 0.25)
hills = _parallax(hills, lambda a, kw: 0.45)
houses = _parallax(houses, lambda a, kw: min(1.0, a[2] * 0.9))
tower = _parallax(tower, lambda a, kw: min(1.0, a[2]))
mill = _parallax(mill, lambda a, kw: min(1.0, a[2]))
bokeh = _parallax(bokeh, lambda a, kw: 1.35)


# ---------- render ----------
def _vignette(ctx, k):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, k)
    ctx.set_source(g)
    ctx.paint()


def key_camera(keys, T):
    """Camera from keyframes [(time, zoom, (cx, cy)), ...] in absolute seconds.
    The camera *arrives* at each framing on its key time (the key word), moving
    with an ease-in-out over the preceding ~0.55 s, and keeps a slow push while
    it holds. Long moves dip the zoom mid-way like a drone pull-back."""
    def drift(k, since):
        # between moves the camera keeps creeping in and sideways (it never fully stops)
        z, c = k[1], k[2]
        since = max(0.0, since)
        return z * (1 + 0.07 * since), (c[0] + 14 * since, c[1] - 10 * since)
    if T <= keys[0][0]:
        return keys[0][1], keys[0][2]
    for i in range(1, len(keys)):
        t1 = keys[i][0]
        t0 = keys[i - 1][0]
        m = keys[i][3] if len(keys[i]) > 3 else min(0.55, 0.75 * (t1 - t0))
        if T < t1 - m:
            return drift(keys[i - 1], T - t0)
        if T < t1:
            za, ca = drift(keys[i - 1], t1 - m - t0)
            zb, cb = keys[i][1], keys[i][2]
            x = (T - (t1 - m)) / m
            p = 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2   # cubic ease in-out
            dist = math.hypot(cb[0] - ca[0], cb[1] - ca[1])
            bump = 0.22 if dist > 350 else 0.0
            z = math.exp(lerp(math.log(za), math.log(zb), p)) * (1 - bump * math.sin(PI * p))
            return z, (lerp(ca[0], cb[0], p), lerp(ca[1], cb[1], p))
    return drift(keys[-1], T - keys[-1][0])


def _motion_blur(surf, dx, dy):
    """Directional blur for fast camera moves (screen px per frame)."""
    import cv2
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    lx, ly = int(min(abs(dx) * 0.9, 41)), int(min(abs(dy) * 0.9, 41))
    if lx < 5 and ly < 5:
        return
    b = a
    if lx >= 5:
        b = cv2.blur(b, (lx, 1))
    if ly >= 5:
        b = cv2.blur(b, (1, ly))
    a[:] = b
    surf.mark_dirty()


def _draw_shot(shot, t, surf, rng_noise):
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    d = shot["end"] - shot["start"]
    # ease=False: reference-style move that starts fast and settles (ease-out)
    p = ease(t / d) if shot.get("ease", True) else 1 - (1 - clamp(t / d)) ** 1.3
    keys = shot.get("keys")
    if keys:
        T = shot["start"] + t
        z, (cx, cy) = key_camera(keys, T)
        zp, (px, py) = key_camera(keys, T - 1 / FPS)
        z0, c0 = keys[0][1], keys[0][2]
        shot["_vel"] = ((cx - px) * z, (cy - py) * z + (z - zp) * H * 0.5)
    else:
        z0, z1, c0, c1 = shot.get("cam", (1.0, 1.06, (W / 2, H / 2), (W / 2, H / 2)))
        z = lerp(z0, z1, p)
        cx, cy = lerp(c0[0], c1[0], p), lerp(c0[1], c1[1], p)
    for bt, mult in shot.get("beats", ()):
        # punch-in cut inside a long shot: closer framing on the focus
        if t >= bt:
            z *= mult
            fx, fy = shot.get("focus", (cx, cy))
            cx, cy = lerp(cx, fx, 0.6), lerp(cy, fy, 0.6)
    shake = shot.get("shake")
    if shake:
        st, amp = shake
        if t >= st:
            k = math.exp(-(t - st) * 6) * amp
            cx += math.sin(t * 70) * k
            cy += math.cos(t * 53) * k
    ctx.save()
    ctx.translate(W / 2, H / 2)
    if shot.get("dutch"):
        ctx.rotate(shot["dutch"])
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)
    # keyframed shots travel far, so soften parallax to keep objects where the keys expect them
    _CAM.update(z=z, c=(cx, cy), z0=z0, c0=c0, strength=0.3 if keys else 1.0)
    _NOW.update(t=shot["start"] + t, speaker=shot.get("speaker"))
    shot["draw"](ctx, t, d)
    ctx.restore()
    if shot.get("overlay"):
        shot["overlay"](ctx, t, d)
    _vignette(ctx, shot.get("vignette", 0.45))
    surf.flush()
    if shot.get("dof", 0) and keys:
        _dof(surf, (W / 2, H * 0.47), shot["dof"])
    elif shot.get("dof", 0) and "focus" in shot:
        fx, fy = shot["focus"]
        _dof(surf, ((fx - cx) * z + W / 2, (fy - cy) * z + H / 2), shot["dof"])
    if keys and shot.get("blur", True):
        _motion_blur(surf, *shot["_vel"])
    if shot.get("sepia"):
        a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
        g = a[:, :, :3].astype(np.float32).mean(axis=2, keepdims=True)
        tone = np.array([0.62, 0.82, 1.0], np.float32)  # B, G, R
        a[:, :, :3] = np.clip(g * tone * 1.05 + 10, 0, 255).astype(np.uint8)
        surf.mark_dirty()


def _dof(surf, focus, strength):
    """Depth of field: sharp around the focus point, blurred toward the edges."""
    import cv2
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    blur = cv2.GaussianBlur(a, (0, 0), strength)
    ys, xs = np.ogrid[0:H, 0:W]
    d = np.sqrt(((xs - focus[0]) / (W * 0.42)) ** 2 + ((ys - focus[1]) / (H * 0.3)) ** 2)
    m = np.clip(d - 0.6, 0, 1)[..., None].astype(np.float32)
    a[:] = (a * (1 - m) + blur * m).astype(np.uint8)
    surf.mark_dirty()


def render(shots, total, out_path, xfade=0.22, grain=9, fade_out=0.6, frames=None, fade_in=0.25):
    surf_a = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    surf_b = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    rs = np.random.default_rng(3)
    noise = [rs.integers(-grain, grain + 1, (H, W, 1), dtype=np.int16) for _ in range(6)]
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
           "-pix_fmt", "bgr0", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(round(total * FPS))
    # frames=(first, last) renders only that part, for patching a finished video
    for f in range(*(frames or (0, nframes))):
        T = f / FPS
        i = max(k for k, s in enumerate(shots) if s["start"] <= T or k == 0)
        _draw_shot(shots[i], T - shots[i]["start"], surf_a, noise)
        if i + 1 < len(shots):
            nxt = shots[i + 1]
            w0 = nxt["start"] - xfade
            if T >= w0:
                _draw_shot(nxt, T - nxt["start"], surf_b, noise)
                ctx = cairo.Context(surf_a)
                ctx.set_source_surface(surf_b, 0, 0)
                ctx.paint_with_alpha(ease((T - w0) / xfade))
        ctx = cairo.Context(surf_a)
        if T > total - fade_out:
            ctx.set_source_rgba(0, 0, 0, clamp((T - (total - fade_out)) / fade_out))
            ctx.paint()
        if T < fade_in:   # fade_in=0 for Shorts that loop (first frame must match the last)
            ctx.set_source_rgba(0, 0, 0, 1 - T / fade_in)
            ctx.paint()
        surf_a.flush()
        a = np.ndarray((H, W, 4), np.uint8, surf_a.get_data())
        n = noise[f % len(noise)]
        a[:, :, :3] = np.clip(a[:, :, :3].astype(np.int16) + n, 0, 255).astype(np.uint8)
        proc.stdin.write(a.tobytes())
        if f % 150 == 0:
            print(f"frame {f}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()


def ref_camera(shots, rate=0.4, cap=2.0, drift=(18, -45), beat=1.25, travel_px=(100, 150)):
    """Apply the measured reference camera (visual_grammar.md): about 0.18x zoom per
    second at a near-constant speed, push-ins drifting up and sideways, pull-outs
    covering a similar distance. A push ends centred on the shot's `focus` (a face or
    object) when given; `cap` limits the zoom for busy frames. hold=True keeps the
    shot's own camera."""
    for s in shots:
        if s.get("hold") or s.get("keys"):
            continue
        dur = s["end"] - s["start"]
        travel = min(s.get("cap", cap), 1 + rate * dur)
        z0, z1, c0, c1 = s.get("cam", (1.0, 1.06, (W / 2, H / 2), (W / 2, H / 2)))
        if z1 >= z0:
            z1 = max(z1, z0 * travel)
            c1 = s["focus"] if "focus" in s else (c1[0] + drift[0], c1[1] + drift[1])
            # the reference camera also travels sideways and up while it zooms
            c0 = (c1[0] - travel_px[0], c1[1] + travel_px[1])
        else:
            z0 = max(z0, z1 * travel)
            if "focus" in s:
                c0 = s["focus"]
                c1 = (c1[0], s["focus"][1] + 0.05 * H / z1)
        s["cam"] = (z0, z1, c0, c1)
        s["ease"] = False
        # long push-ins get a punch-in cut halfway so a new frame comes every ~2 s
        if z1 > z0 and dur > 2.4 and "focus" in s and "cap" not in s:
            s["beats"] = [(dur * 0.52, beat)]
