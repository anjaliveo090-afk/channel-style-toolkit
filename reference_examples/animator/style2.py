"""Character style v2, measured from the user's reference sheets (office worker,
apron worker): head = 39% of height, thick dark limbs, dark ball hands, big
rounded dark shoes, tall oval eyes, thick arched brows, jagged fringe with
highlight streaks, collared clothes, soft shading. All sizes are in units of
the head radius r (r = 64 * s px)."""
import math

import cairo

from engine import (PI, ellipse, fill_stroke, hexc, rrect, src, voice_level, _NOW, _VOICE,
                    draw_item)
import engine

OUT = hexc("#201013")
SKIN = hexc("#fef2e8")
SKIN_SHADE = hexc("#f7d9d6")
SHOE = hexc("#3d3241")


def _shade_fill(ctx, top, bottom, y0, y1, lw):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bottom)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(lw)
    ctx.stroke()


def _lighter(c, k=0.18):
    return tuple(min(1, v + (1 - v) * k) for v in c)


def _darker(c, k=0.18):
    return tuple(v * (1 - k) for v in c)


class Char2:
    """Same draw() signature as engine.Char, so stories can swap styles."""

    def __init__(self, body, hair="bowl", hair_col="#2d2328", outfit="shirt", accent=None,
                 mustache=None, tie=None, hat_col="#24202c", lanyard=False, skin=None, glasses=False,
                 shades=False):
        self.body = hexc(body)
        self.hair = hair
        self.hair_col = hexc(hair_col)
        self.outfit = outfit
        self.accent = hexc(accent) if accent else None
        self.mustache = hexc(mustache) if mustache else None
        self.tie = hexc(tie) if tie else None
        self.hat_col = hexc(hat_col)
        self.lanyard = lanyard
        self.skin = hexc(skin) if skin else SKIN
        self.glasses = glasses
        self.shades = shades

    # ------------------------------------------------------------------
    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False,
             arms=("down", "down"), pose="stand", look=0.0, bob=1.0,
             item=None, item_hand=1, walk_phase=0.0, lean=0.0, head_nod=0.0, shadow=True):
        r = 64 * s
        e = engine.ENERGY * bob
        lw = 0.075 * r                 # outline
        limb = 0.105 * r               # arms and legs (reference 0.08-0.09r, a bit bolder at small sizes)
        ctx.save()
        ctx.translate(x, y)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        if shadow:
            g = cairo.RadialGradient(0, 0, 0, 0, 0, r * 1.1)
            g.add_color_stop_rgba(0, 0, 0, 0, 0.28)
            g.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.save()
            ctx.scale(1, 0.22)
            ctx.set_source(g)
            ctx.arc(0, 0, r * 1.1, 0, 2 * PI)
            ctx.fill()
            ctx.restore()

        bounce = -abs(math.sin(t * 2 * PI * 2.0)) * 0.08 * r * e
        hip = -1.4 * r + bounce          # shirt bottom
        top = -2.73 * r + bounce         # shirt top (collar)

        # legs + shoes
        feet = []
        for side in (-1, 1):
            hx = side * 0.215 * r
            if pose == "sit":
                kx, ky = hx + 0.75 * r, hip + 0.05 * r
                fx, fy = hx + 0.8 * r, -0.12 * r
                ctx.move_to(hx, hip)
                ctx.line_to(kx, ky)
                ctx.line_to(fx, fy)
            elif pose == "feetup":
                # leaning back, feet up on the desk in front
                kx, ky = hx + 0.85 * r, hip - 0.2 * r
                fx, fy = hx + 1.55 * r, hip - 0.45 * r
                ctx.move_to(hx, hip)
                ctx.line_to(kx, ky)
                ctx.line_to(fx, fy)
            elif pose == "walk":
                sw = math.sin(walk_phase * 2 * PI + (0 if side < 0 else PI))
                fx, fy = hx + sw * 0.35 * r, -max(0, sw) * 0.15 * r - 0.12 * r
                ctx.move_to(hx, hip)
                ctx.line_to(fx, fy)
            else:
                fx, fy = hx, -0.12 * r
                ctx.move_to(hx, hip)
                ctx.line_to(fx, fy)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(limb)
            ctx.stroke()
            feet.append((side, fx, fy))
        for side, fx, fy in feet:
            ellipse(ctx, fx + side * 0.09 * r, fy + 0.02 * r, 0.21 * r, 0.12 * r)
            _shade_fill(ctx, _lighter(SHOE, 0.15), SHOE, fy - 0.1 * r, fy + 0.14 * r, lw * 0.8)

        # upper body (sway + lean around the hip)
        ctx.save()
        ctx.translate(0, hip)
        ctx.rotate(lean + math.sin(t * 2.7) * 0.03 * e)
        ctx.translate(0, -hip)
        self._torso(ctx, r, top, hip, lw)

        hcx = 0
        hcy = top - 0.98 * r + head_nod + math.sin(t * 4.3) * 0.03 * r * e
        hand_pts = []
        for i, side in enumerate((-1, 1)):
            sx, sy = side * 0.56 * r, top + 0.42 * r
            a = arms[i]
            tbl = {
                "down": (sx + side * 0.04 * r, hip + 0.18 * r),
                "up": (sx + side * 0.35 * r, top - 1.1 * r),
                "point": (sx + side * 1.35 * r, top - 0.1 * r),
                "hold": (side * 0.25 * r, top + 0.95 * r),
                "show": (sx + side * 0.75 * r, top - 0.45 * r),
                "hip": (sx + side * 0.38 * r, top + 0.95 * r),
                "wag": (sx + side * 0.6 * r, top - 0.85 * r + math.sin(t * 14) * 0.12 * r),
                "wave": (sx + side * 0.6 * r + math.sin(t * 11) * 0.2 * r, top - 1.05 * r),
                "write": (side * 0.08 * r + math.sin(t * 22) * 0.07 * r, top + 0.9 * r),
                "salute": (side * 0.95 * r, hcy - 0.55 * r),
                "shrug": (sx + side * 0.7 * r, top - 0.05 * r),
            }
            hx, hy = tbl.get(a, tbl["down"])
            if a not in ("salute", "write"):
                hx += math.sin(t * 3.8 + side) * 0.06 * r * e
                hy += math.cos(t * 3.1 + side) * 0.05 * r * e
            hand_pts.append((side, a, sx, sy, hx, hy))

        # arms behind the head only when raised above it
        def arm(side, a, sx, sy, hx, hy, i):
            mx, my = (sx + hx) / 2, (sy + hy) / 2
            ctx.move_to(sx, sy)
            ctx.curve_to(mx + side * 0.15 * r, my, mx + side * 0.15 * r, my, hx, hy)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(limb)
            ctx.stroke()
            if item and i == item_hand:
                ctx.save()
                ctx.translate(hx, hy)
                ctx.scale(r / 64, r / 64)
                draw_item(ctx, item, 0, 0, t)
                ctx.restore()
            ctx.new_sub_path()
            ctx.arc(hx, hy, 0.085 * r, 0, 2 * PI)
            src(ctx, OUT)
            ctx.fill()

        self._sleeves(ctx, r, top, lw)
        self._head(ctx, hcx, hcy, r, lw, expr, t, talk, look)
        for i, (side, a, sx, sy, hx, hy) in enumerate(hand_pts):
            arm(side, a, sx, sy, hx, hy, i)
        ctx.restore()
        ctx.restore()

    # ------------------------------------------------------------------
    def _torso(self, ctx, r, top, hip, lw):
        w_top, w_bot = 0.5 * r, 0.47 * r
        ctx.move_to(-w_top, top + 0.12 * r)
        ctx.curve_to(-w_top, top, -w_top * 0.6, top - 0.02 * r, 0, top - 0.02 * r)
        ctx.curve_to(w_top * 0.6, top - 0.02 * r, w_top, top, w_top, top + 0.12 * r)
        ctx.line_to(w_bot, hip - 0.08 * r)
        ctx.curve_to(w_bot, hip, w_bot * 0.8, hip + 0.02 * r, 0, hip + 0.02 * r)
        ctx.curve_to(-w_bot * 0.8, hip + 0.02 * r, -w_bot, hip, -w_bot, hip - 0.08 * r)
        ctx.close_path()
        base = self.body
        if self.outfit == "apron":
            base = hexc("#fbece8")
        if self.outfit == "suit":
            base = self.body
        _shade_fill(ctx, _lighter(base, 0.22), _darker(base, 0.1), top, hip, lw)
        if self.outfit in ("shirt", "apron"):
            # placket + buttons
            ctx.move_to(0, top + 0.12 * r)
            ctx.line_to(0, hip - 0.05 * r)
            ctx.set_source_rgba(*OUT, 0.35)
            ctx.set_line_width(lw * 0.5)
            ctx.stroke()
            for k in range(2):
                ctx.new_sub_path()
                ctx.arc(0, top + (0.25 + k * 0.35) * r, 0.035 * r, 0, 2 * PI)
                ctx.set_source_rgba(*OUT, 0.45)
                ctx.set_line_width(lw * 0.4)
                ctx.stroke()
        if self.outfit == "apron":
            col = self.accent or hexc("#3e9a4a")
            rrect(ctx, -0.42 * r, top + 0.35 * r, 0.84 * r, hip - top - 0.33 * r, 0.06 * r)
            _shade_fill(ctx, _lighter(col, 0.12), _darker(col, 0.12), top + 0.35 * r, hip, lw * 0.8)
            for side in (-1, 1):
                ctx.move_to(side * 0.3 * r, top + 0.36 * r)
                ctx.line_to(side * 0.28 * r, top + 0.02 * r)
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(lw * 1.6)
                ctx.stroke()
                ctx.move_to(side * 0.3 * r, top + 0.34 * r)
                ctx.line_to(side * 0.28 * r, top + 0.04 * r)
                src(ctx, col)
                ctx.set_line_width(lw * 0.8)
                ctx.stroke()
            rrect(ctx, -0.25 * r, top + 0.78 * r, 0.5 * r, 0.3 * r, 0.04 * r)
            _shade_fill(ctx, col, _darker(col, 0.15), top + 0.78 * r, top + 1.1 * r, lw * 0.7)
        if self.outfit == "suit":
            ctx.move_to(-0.2 * r, top)
            ctx.line_to(0, top + 0.6 * r)
            ctx.line_to(0.2 * r, top)
            ctx.close_path()
            fill_stroke(ctx, hexc("#f4f1f4"), lw * 0.6)
            for side in (-1, 1):
                ctx.move_to(side * 0.2 * r, top)
                ctx.line_to(side * 0.02 * r, top + 0.62 * r)
                ctx.line_to(side * 0.3 * r, top + 0.25 * r)
                ctx.close_path()
                fill_stroke(ctx, _darker(self.body, 0.15), lw * 0.6)
        if self.tie:
            ctx.move_to(-0.06 * r, top + 0.05 * r)
            ctx.line_to(0.06 * r, top + 0.05 * r)
            ctx.line_to(0.04 * r, top + 0.5 * r)
            ctx.line_to(0, top + 0.58 * r)
            ctx.line_to(-0.04 * r, top + 0.5 * r)
            ctx.close_path()
            fill_stroke(ctx, self.tie, lw * 0.5)
        if self.outfit in ("shirt", "apron"):
            # collar flaps
            cc = hexc("#fbece8") if self.outfit == "apron" else _darker(self.body, 0.12)
            for side in (-1, 1):
                ctx.move_to(side * 0.02 * r, top - 0.0 * r)
                ctx.line_to(side * 0.27 * r, top - 0.04 * r)
                ctx.line_to(side * 0.2 * r, top + 0.2 * r)
                ctx.close_path()
                fill_stroke(ctx, cc, lw * 0.6)
        if self.lanyard:
            ctx.move_to(-0.22 * r, top + 0.02 * r)
            ctx.line_to(0, top + 0.55 * r)
            ctx.line_to(0.22 * r, top + 0.02 * r)
            ctx.set_source_rgb(*hexc("#2b45a6"))
            ctx.set_line_width(0.05 * r)
            ctx.stroke()
            rrect(ctx, -0.13 * r, top + 0.52 * r, 0.26 * r, 0.32 * r, 0.03 * r)
            fill_stroke(ctx, hexc("#f5f1ec"), lw * 0.6)
            ctx.new_sub_path()
            ctx.arc(0, top + 0.63 * r, 0.05 * r, 0, 2 * PI)
            src(ctx, hexc("#9aa0b8"))
            ctx.fill()

    def _sleeves(self, ctx, r, top, lw):
        base = hexc("#fbece8") if self.outfit == "apron" else self.body
        for side in (-1, 1):
            ctx.move_to(side * 0.42 * r, top + 0.02 * r)
            ctx.curve_to(side * 0.56 * r, top, side * 0.66 * r, top + 0.15 * r, side * 0.7 * r, top + 0.4 * r)
            ctx.line_to(side * 0.47 * r, top + 0.5 * r)
            ctx.close_path()
            _shade_fill(ctx, _lighter(base, 0.2), base, top, top + 0.5 * r, lw * 0.8)

    # ------------------------------------------------------------------
    def _head(self, ctx, cx, cy, r, lw, expr, t, talk, look):
        hat_behind = self.hair == "tophat"
        ctx.new_sub_path()
        ctx.arc(cx, cy, r, 0, 2 * PI)
        g = cairo.RadialGradient(cx - 0.25 * r, cy - 0.3 * r, 0.2 * r, cx, cy + 0.2 * r, r * 1.05)
        g.add_color_stop_rgb(0, *self.skin)
        g.add_color_stop_rgb(0.75, *self.skin)
        g.add_color_stop_rgb(1, *SKIN_SHADE)
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(lw * 1.1)
        ctx.stroke()
        self._hair(ctx, cx, cy, r, lw)
        _face(ctx, cx, cy, r, lw, expr, t, talk, look, self)

    def _hair(self, ctx, cx, cy, r, lw):
        h = self.hair
        col = self.hair_col
        if h in ("bowl", "cap", "side"):
            # puffy cap of hair with a jagged fringe
            ctx.move_to(cx - 1.04 * r, cy + 0.12 * r)
            ctx.curve_to(cx - 1.12 * r, cy - 0.85 * r, cx - 0.5 * r, cy - 1.06 * r, cx, cy - 1.05 * r)
            ctx.curve_to(cx + 0.55 * r, cy - 1.06 * r, cx + 1.12 * r, cy - 0.8 * r, cx + 1.04 * r, cy + 0.12 * r)
            # smooth, slightly curved fringe just above the brows
            ctx.line_to(cx + 0.97 * r, cy + 0.0 * r)
            ctx.curve_to(cx + 0.7 * r, cy - 0.16 * r, cx + 0.3 * r, cy - 0.2 * r, cx, cy - 0.2 * r)
            ctx.curve_to(cx - 0.3 * r, cy - 0.2 * r, cx - 0.7 * r, cy - 0.16 * r, cx - 0.97 * r, cy + 0.0 * r)
            ctx.close_path()
            _shade_fill(ctx, _lighter(col, 0.12), _darker(col, 0.1), cy - 1.1 * r, cy, lw * 1.05)
            # strand cuts in the fringe
            for fx in (-0.62, -0.32, 0.0, 0.3, 0.6):
                yb = cy - 0.2 * r + abs(fx) ** 2 * 0.25 * r
                ctx.move_to(cx + fx * r, yb)
                ctx.line_to(cx + (fx + 0.03) * r, yb - 0.16 * r)
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(0.035 * r)
                ctx.stroke()
            # long soft highlight streaks following the dome
            for k, (a0, a1, rr) in enumerate(((1.18, 1.38, 0.86), (1.44, 1.62, 0.9), (1.68, 1.82, 0.84))):
                ctx.new_sub_path()
                ctx.arc(cx, cy - 0.12 * r, rr * r, a0 * PI, a1 * PI)
                ctx.set_source_rgba(*_lighter(col, 0.4), 0.55)
                ctx.set_line_width(0.07 * r)
                ctx.stroke()
            if h == "side":
                ctx.move_to(cx - 0.3 * r, cy - 1.04 * r)
                ctx.curve_to(cx - 0.35 * r, cy - 0.7 * r, cx - 0.45 * r, cy - 0.45 * r, cx - 0.55 * r, cy - 0.15 * r)
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(0.04 * r)
                ctx.stroke()
            if h == "cap":
                ctx.move_to(cx - 1.0 * r, cy - 0.35 * r)
                ctx.curve_to(cx - 1.0 * r, cy - 1.25 * r, cx + 1.0 * r, cy - 1.25 * r, cx + 1.0 * r, cy - 0.35 * r)
                ctx.close_path()
                _shade_fill(ctx, _lighter(self.hat_col, 0.15), self.hat_col, cy - 1.2 * r, cy - 0.3 * r, lw)
                ellipse(ctx, cx + 0.55 * r, cy - 0.35 * r, 0.6 * r, 0.12 * r)
                fill_stroke(ctx, _darker(self.hat_col, 0.1), lw * 0.9)
        elif h == "tophat":
            for side in (-1, 1):
                ellipse(ctx, cx + side * 0.93 * r, cy - 0.12 * r, 0.16 * r, 0.32 * r)
                _shade_fill(ctx, _lighter(col, 0.1), col, cy - 0.45 * r, cy + 0.2 * r, lw * 0.8)
            ellipse(ctx, cx, cy - 0.82 * r, 1.0 * r, 0.2 * r)
            fill_stroke(ctx, self.hat_col, lw)
            rrect(ctx, cx - 0.62 * r, cy - 2.05 * r, 1.24 * r, 1.25 * r, 0.08 * r)
            _shade_fill(ctx, _lighter(self.hat_col, 0.15), self.hat_col, cy - 2.05 * r, cy - 0.8 * r, lw)
            ctx.rectangle(cx - 0.62 * r, cy - 1.08 * r, 1.24 * r, 0.2 * r)
            src(ctx, hexc("#c0392b"))
            ctx.fill()
        elif h == "bald":
            for side in (-1, 1):
                ellipse(ctx, cx + side * 0.94 * r, cy - 0.15 * r, 0.17 * r, 0.34 * r)
                _shade_fill(ctx, _lighter(col, 0.1), col, cy - 0.5 * r, cy + 0.2 * r, lw * 0.8)
            ctx.move_to(cx - 0.35 * r, cy - 0.75 * r)
            ctx.curve_to(cx - 0.2 * r, cy - 0.9 * r, cx + 0.05 * r, cy - 0.9 * r, cx + 0.15 * r, cy - 0.82 * r)
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.set_line_width(0.06 * r)
            ctx.stroke()


def _face(ctx, cx, cy, r, lw, expr, t, talk, look, ch):
    lx = look * r * 0.18
    ey = cy + 0.21 * r
    ex0 = 0.22 * r
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    def line(x1, y1, x2, y2, w):
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(w)
        ctx.stroke()

    def brow(side, lift=0.0, tilt=0.0):
        bx = cx + side * 0.25 * r + lx
        by = ey - 0.23 * r - lift * r
        ctx.move_to(bx - 0.12 * r, by + side * tilt * r + 0.02 * r)
        ctx.curve_to(bx - 0.05 * r, by - 0.035 * r, bx + 0.05 * r, by - 0.035 * r,
                     bx + 0.12 * r, by - side * tilt * r + 0.02 * r)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(0.062 * r)
        ctx.stroke()

    def oval(x, y, rx, ry, col=OUT):
        ellipse(ctx, x, y, rx, ry)
        src(ctx, col)
        ctx.fill()

    for side in (-1, 1):
        ex = cx + side * ex0 + lx
        if expr in ("happy", "grin", "laugh"):
            ctx.new_sub_path()
            ctx.arc(ex, ey + 0.04 * r, 0.075 * r, PI + 0.25, 2 * PI - 0.25)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(0.05 * r)
            ctx.stroke()
            brow(side, 0.05)
        elif expr == "shock":
            ellipse(ctx, ex, ey, 0.13 * r, 0.16 * r)
            fill_stroke(ctx, (1, 1, 1), 0.04 * r)
            oval(ex, ey, 0.04 * r, 0.055 * r)
            brow(side, 0.12)
        elif expr in ("smirk", "cold"):
            ctx.save()
            ctx.rectangle(ex - 0.1 * r, ey - 0.02 * r, 0.2 * r, 0.2 * r)
            ctx.clip()
            oval(ex, ey, 0.062 * r, 0.107 * r)
            ctx.restore()
            line(ex - 0.08 * r, ey - 0.02 * r, ex + 0.08 * r, ey - 0.02 * r, 0.04 * r)
            if expr == "smirk":
                brow(side, 0.08 if side > 0 else -0.02)
            else:
                brow(side, -0.03)
        else:
            oval(ex, ey, 0.066 * r, 0.112 * r)
            if expr == "angry":
                brow(side, -0.02, tilt=-0.07)
            elif expr in ("sad", "worried", "forced"):
                brow(side, 0.02, tilt=0.07)
            else:
                brow(side)

    if ch is not None and ch.glasses:
        for side in (-1, 1):
            ellipse(ctx, cx + side * ex0 + lx, ey, 0.15 * r, 0.15 * r)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(0.035 * r)
            ctx.stroke()

    if ch is not None and ch.shades:
        for side in (-1, 1):
            rrect(ctx, cx + side * ex0 + lx - 0.17 * r, ey - 0.12 * r, 0.34 * r, 0.22 * r, 0.08 * r)
            fill_stroke(ctx, hexc("#1c1a24"), 0.035 * r)
        line(cx - 0.06 * r + lx, ey - 0.05 * r, cx + 0.06 * r + lx, ey - 0.05 * r, 0.035 * r)

    my = cy + 0.56 * r + (0.05 * r if ch is not None and ch.mustache else 0)
    mx = cx + lx * 1.1
    mouth = expr
    speaking = engine.LIPSYNC and (talk or _NOW["speaker"] is ch)
    level = 0.0
    if speaking and _VOICE["env"] is not None:
        level = voice_level()
        if level > 0 and expr not in ("laugh", "shock"):
            mouth = "open"
    elif engine.LIPSYNC and talk and int(t * 9) % 2 == 0 and expr not in ("laugh", "shock", "grin"):
        mouth, level = "open", 0.55

    red = hexc("#7a2430")
    if mouth == "open" and expr == "grin":
        ctx.new_sub_path()
        ctx.arc(mx, my - 0.06 * r, (0.17 + 0.08 * level) * r, 0, PI)
        ctx.close_path()
        fill_stroke(ctx, red, 0.04 * r)
        rrect(ctx, mx - 0.15 * r, my - 0.06 * r, 0.3 * r, 0.07 * r, 0.02 * r)
        src(ctx, (1, 1, 1))
        ctx.fill()
    elif mouth == "open":
        ellipse(ctx, mx, my + 0.02 * r, (0.08 + 0.05 * level) * r, (0.04 + 0.08 * level) * r)
        fill_stroke(ctx, red, 0.04 * r)
    elif mouth in ("neutral", "determined", "cold"):
        line(mx - 0.12 * r, my, mx + 0.12 * r, my, 0.045 * r)
    elif mouth == "smirk":
        ctx.move_to(mx - 0.12 * r, my + 0.01 * r)
        ctx.curve_to(mx, my + 0.03 * r, mx + 0.08 * r, my, mx + 0.15 * r, my - 0.06 * r)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(0.045 * r)
        ctx.stroke()
    elif mouth == "shock":
        ellipse(ctx, mx, my + 0.03 * r, 0.06 * r, 0.09 * r)
        fill_stroke(ctx, red, 0.04 * r)
    elif mouth == "happy":
        ctx.new_sub_path()
        ctx.arc(mx, my - 0.08 * r, 0.14 * r, 0.35, PI - 0.35)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(0.045 * r)
        ctx.stroke()
    elif mouth in ("grin", "forced"):
        rrect(ctx, mx - 0.3 * r, my - 0.1 * r, 0.6 * r, 0.22 * r, 0.07 * r)
        fill_stroke(ctx, (1, 1, 1), 0.04 * r)
        for k in range(1, 6):
            xx = mx - 0.3 * r + k * 0.1 * r
            line(xx, my - 0.1 * r, xx, my + 0.12 * r, 0.018 * r)
        line(mx - 0.3 * r, my + 0.01 * r, mx + 0.3 * r, my + 0.01 * r, 0.018 * r)
    elif mouth == "laugh":
        ctx.new_sub_path()
        ctx.arc(mx, my - 0.05 * r, 0.22 * r, 0, PI)
        ctx.close_path()
        fill_stroke(ctx, red, 0.04 * r)
        for side in (-1, 1):
            k = (t * 2.5) % 1
            ellipse(ctx, cx + side * 0.45 * r, ey + 0.1 * r + k * 0.35 * r, 0.04 * r, 0.065 * r)
            fill_stroke(ctx, hexc("#7fd3ff"), 0.02 * r)
    elif mouth in ("angry", "sad", "worried"):
        ctx.new_sub_path()
        ctx.arc(mx, my + 0.12 * r, 0.13 * r, PI + 0.55, 2 * PI - 0.55)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(0.045 * r)
        ctx.stroke()

    if ch is not None and ch.mustache:
        for side in (-1, 1):
            ellipse(ctx, cx + side * 0.13 * r + lx, cy + 0.47 * r, 0.16 * r, 0.07 * r)
            fill_stroke(ctx, ch.mustache, 0.03 * r)


def back_figure(ctx, x, y, r, hair_col, body_col, outfit_col=None):
    """Over-the-shoulder foreground: back of a head and shoulders, seen from behind."""
    hair_col, body_col = hexc(hair_col), hexc(body_col)
    lw = 0.075 * r
    ctx.save()
    ctx.translate(x, y)
    ctx.move_to(-1.0 * r, 2.2 * r)
    ctx.curve_to(-1.0 * r, 1.1 * r, -0.7 * r, 0.85 * r, 0, 0.85 * r)
    ctx.curve_to(0.7 * r, 0.85 * r, 1.0 * r, 1.1 * r, 1.0 * r, 2.2 * r)
    ctx.close_path()
    _shade_fill(ctx, _lighter(body_col, 0.15), _darker(body_col, 0.15), 0.85 * r, 2.2 * r, lw)
    ctx.new_sub_path()
    ctx.arc(0, 0, r, 0, 2 * PI)
    _shade_fill(ctx, _lighter(hair_col, 0.15), _darker(hair_col, 0.1), -r, r, lw * 1.1)
    for k, (a0, a1) in enumerate(((1.2, 1.45), (1.5, 1.75))):
        ctx.new_sub_path()
        ctx.arc(0, 0, 0.82 * r, a0 * PI, a1 * PI)
        ctx.set_source_rgba(*_lighter(hair_col, 0.4), 0.5)
        ctx.set_line_width(0.07 * r)
        ctx.stroke()
    ctx.restore()
