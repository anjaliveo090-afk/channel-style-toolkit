"""Paper Billions style characters, rebuilt from measured reference frames
(V1 0:07, 0:23, 1:01, 1:06, 3:56-5:10 and the user's crops; see style_bible.md section 2).

CONSTRUCTION (units of the head radius R)
- head: circle R, outline INK #200a00, width 0.045 R (+0.6 px)
- body: a capsule / bean under the head, 1.7 R wide, 2.8 R tall, overlapped 0.3 R by the head;
  bottom 0.36 R is a dark shorts band; thin outline; lit side lighter, bottom darker
- arms at rest: curved contour lines INSIDE the body edges; gesturing arms are thin black lines from
  the shoulder (body edge, 25% down) to the hand; holding hands get 3 short finger strokes
- legs: two straight thin lines 1.15 R long, 0.4 R apart, no feet; soft dark ellipse shadow on the floor
- overall ~2.9 heads tall (5.8 R); kids are scaled down with the same proportions
FACE
- skin in 3 tones from one key light, plus the "moon line": a bright crescent inside the outline on the
  key-light side whose inner edge is a thin darker line; a soft darker crescent under the chin
- eyes: vertical dark-brown ovals with a small white highlight; thin arc brows high above; no nose
- the face turns: features slide toward the side the character looks at (look -1..1); glasses keep a
  temple line only toward the far edge of the head
- expressions: neutral happy laugh talk smirk wink shock scared sad worried angry deadpan blush sly
VIEWS (pose): stand, sit, walk, back, back_sit (seen from behind: no face, hair covers the back)
SCENE LIGHT: Char.scene(ambient=(r,g,b), rim="#hex") tints skin/clothes for night or blue scenes.

draw() keeps the signature of reference_examples/animator/style2.py Char2.draw. (x, y) is the point
between the feet (stand/walk/back) or the seat point (sit). s=1 gives R = 40 px.
`arms`: preset name, (preset, amount 0..1), or {"l": (x, y), "r": (x, y)} hand targets (world coords).
"""
import math

import cairo

INK = (0x20 / 255, 0x0a / 255, 0.0)
EYE = (0x3a / 255, 0x24 / 255, 0x14 / 255)


def hexc(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


def mul(a, b):
    return tuple(a[i] * b[i] for i in range(3))


SKIN = {"hi": "#fdd480", "mid": "#e9a561", "sh": "#b5794e", "rim": "#ffd98a"}
SKIN_LIGHT = {"hi": "#fde2b0", "mid": "#efc08f", "sh": "#c48e67", "rim": "#fff0c8"}
SKIN_DARK = {"hi": "#c98a5a", "mid": "#9a6340", "sh": "#6e4329", "rim": "#e0a46a"}


class Char:
    def __init__(self, body="#e07a4f", hair="bowl", hair_col="#1d1716", skin=None, glasses=None,
                 collar="shirt", tie=None, earrings=None, pants="#3a2f30", light=(-1.0, -0.2), pin=None,
                 build=1.0, creases=False, mustache=None, zipper=False, lapels=False, blush=False):
        self.body = hexc(body)
        self.hair = hair
        self.hair_col = hexc(hair_col)
        sk = dict(SKIN)
        sk.update(skin or {})
        self.sk = {k: hexc(v) for k, v in sk.items()}
        self.glasses = glasses
        self.collar = collar
        self.tie = hexc(tie) if tie else None
        self.earrings = hexc(earrings) if earrings else None
        self.pants = hexc(pants)
        self.pin = hexc(pin) if pin else None
        self.build = build
        self.creases = creases
        self.mustache = hexc(mustache) if mustache else None
        self.zipper = zipper
        self.lapels = lapels
        self.blush_always = blush
        n = math.hypot(*light) or 1
        self.light = (light[0] / n, light[1] / n)
        self.ambient = (1.0, 1.0, 1.0)
        self.rim = None

    def scene(self, ambient=(1, 1, 1), rim=None, light=None):
        """Tint for the scene light, e.g. night blue: ambient=(0.55,0.62,0.85), rim="#bcd4ff"."""
        self.ambient = ambient
        self.rim = hexc(rim) if rim else None
        if light:
            n = math.hypot(*light) or 1
            self.light = (light[0] / n, light[1] / n)
        return self

    def _c(self, col):
        return mul(col, self.ambient)

    # ------------------------------------------------------------------ public
    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False, arms="rest", pose="stand",
             look=0.0, bob=0.0, item=None, item_hand="r", walk_phase=None, lean=0.0, shadow=True):
        R = 40 * s
        lw = 0.045 * R + 0.6
        limb = 0.05 * R + 0.6
        back = pose in ("back", "back_sit")
        sit = pose in ("sit", "back_sit")
        breathe = math.sin(t * 2.2) * 0.008 * R
        bw, bh = 1.7 * R * self.build, 2.8 * R
        legs = 0.0 if sit else 1.15 * R
        if pose == "walk" and walk_phase is None:
            walk_phase = t * 9
        hop = abs(math.sin(walk_phase)) * 0.06 * R if walk_phase is not None else 0
        base = y - legs - hop
        top = base - bh + breathe
        hx = x + lean * 0.5 * R
        hy = top + 0.3 * R - R + bob * R

        if shadow and not sit:
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(1, 0.18)
            g = cairo.RadialGradient(0, 0, 0, 0, 0, 1.35 * R)
            g.add_color_stop_rgba(0, 0, 0, 0, 0.42)
            g.add_color_stop_rgba(0.7, 0, 0, 0, 0.25)
            g.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.set_source(g)
            ctx.arc(0, 0, 1.35 * R, 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()
        if not sit:
            for sd in (-1, 1):
                fx = x + sd * 0.2 * R
                kx = fx
                if walk_phase is not None:
                    sw = math.sin(walk_phase + (0 if sd < 0 else math.pi)) * 0.4 * R
                    fx += sw
                    kx += sw * 0.4
                _line(ctx, [(x + sd * 0.2 * R, base - 0.05 * R), (kx, base + legs * 0.5), (fx, y)], limb)
        if self.hair == "long" and not back:
            self._long_hair_back(ctx, hx, hy, R, lw)
        hands = self._body(ctx, hx, top, base, bw, bh, R, lw, limb, arms, item, item_hand, t, back)
        if back:
            self._head_back(ctx, hx, hy, R, lw, look)
        else:
            self._head(ctx, hx, hy, R, lw, expr, t, talk, look)
        self._last = (hx, top, base, bw, bh, R, lw, limb, arms, item, item_hand, t, back)
        return {"head": (hx, hy, R), "hands": hands, "top": top, "base": base}

    def draw_arms_over(self, ctx, only=("l", "r")):
        """Re-draw gesturing arms of the last draw() on top of props (hands resting ON a table)."""
        hx, top, base, bw, bh, R, lw, limb, arms, item, item_hand, t, back = self._last
        self._arms(ctx, hx, top, bw, bh, R, lw, limb, arms, item, item_hand, t, only, rest=False)

    # ------------------------------------------------------------------ body
    def _body_path(self, ctx, x, top, base, bw):
        h = base - top
        ctx.new_path()
        ctx.move_to(x, top)
        ctx.curve_to(x + bw * 0.3, top, x + bw * 0.44, top + h * 0.18, x + bw * 0.48, top + h * 0.45)
        ctx.curve_to(x + bw * 0.53, top + h * 0.78, x + bw * 0.48, base, x, base)
        ctx.curve_to(x - bw * 0.48, base, x - bw * 0.53, top + h * 0.78, x - bw * 0.48, top + h * 0.45)
        ctx.curve_to(x - bw * 0.44, top + h * 0.18, x - bw * 0.3, top, x, top)
        ctx.close_path()

    def _body(self, ctx, x, top, base, bw, bh, R, lw, limb, arms, item, item_hand, t, back):
        h = base - top
        body = self._c(self.body)
        lx = self.light[0]
        self._body_path(ctx, x, top, base, bw)
        ctx.save()
        ctx.clip_preserve()
        g = cairo.LinearGradient(x + lx * bw * 0.5, top, x - lx * bw * 0.5, base)
        g.add_color_stop_rgb(0, *mix(body, (1, 0.9, 0.7), 0.12))
        g.add_color_stop_rgb(0.6, *body)
        g.add_color_stop_rgb(1, *mix(body, (0, 0, 0), 0.3))
        ctx.set_source(g)
        ctx.fill()
        ctx.rectangle(x - bw, base - 0.36 * R, 2 * bw, R)
        ctx.set_source_rgb(*self._c(self.pants))
        ctx.fill()
        ctx.move_to(x - bw, base - 0.36 * R)
        ctx.line_to(x + bw, base - 0.36 * R)
        ctx.set_source_rgba(*INK, 0.5)
        ctx.set_line_width(lw * 0.4)
        ctx.stroke()
        ctx.set_line_width(R * 0.12)
        ctx.set_source_rgba(*(self.rim or self.sk["rim"]), 0.22)
        sd = 1 if lx > 0 else -1
        ctx.move_to(x + sd * bw * 0.48, top + h * 0.2)
        ctx.curve_to(x + sd * bw * 0.53, top + h * 0.5, x + sd * bw * 0.5, top + h * 0.75, x + sd * bw * 0.42, base - 0.4 * R)
        ctx.stroke()
        if not back:
            self._clothes_front(ctx, x, top, base, bw, R, lw)
        ctx.restore()
        self._body_path(ctx, x, top, base, bw)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw * 0.8)
        ctx.stroke()
        return self._arms(ctx, x, top, bw, bh, R, lw, limb, arms, item, item_hand, t)

    def _clothes_front(self, ctx, x, top, base, bw, R, lw):
        h = base - top
        white = self._c((0.97, 0.95, 0.9))
        if self.collar == "shirt":
            c0 = top + 0.26 * R
            ctx.new_path()
            ctx.move_to(x - 0.36 * R, c0)
            ctx.line_to(x - 0.03 * R, c0 + 0.32 * R)
            ctx.line_to(x + 0.03 * R, c0 + 0.32 * R)
            ctx.line_to(x + 0.36 * R, c0)
            ctx.line_to(x + 0.16 * R, c0 + 0.08 * R)
            ctx.line_to(x, c0 + 0.2 * R)
            ctx.line_to(x - 0.16 * R, c0 + 0.08 * R)
            ctx.close_path()
            ctx.set_source_rgb(*white)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 0.45)
            ctx.stroke()
        elif self.collar == "round":
            ctx.new_path()
            ctx.save()
            ctx.translate(x, top + 0.3 * R)
            ctx.scale(0.4 * R, 0.16 * R)
            ctx.arc(0, 0, 1, 0, math.pi)
            ctx.restore()
            ctx.set_source_rgb(*white)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 0.45)
            ctx.stroke()
        elif self.collar == "turtleneck":
            ctx.rectangle(x - 0.35 * R, top + 0.05 * R, 0.7 * R, 0.18 * R)
            ctx.set_source_rgb(*mix(self._c(self.body), (0, 0, 0), 0.15))
            ctx.fill()
        if self.lapels:
            ctx.set_source_rgba(*INK, 0.55)
            ctx.set_line_width(lw * 0.45)
            for sd in (-1, 1):
                ctx.move_to(x + sd * 0.32 * R, top + 0.14 * R)
                ctx.line_to(x + sd * 0.06 * R, top + h * 0.45)
                ctx.line_to(x + sd * 0.38 * R, top + h * 0.3)
                ctx.stroke()
        if self.tie:
            ctx.new_path()
            ctx.move_to(x, top + 0.24 * R)
            ctx.line_to(x - 0.08 * R, top + h * 0.42)
            ctx.line_to(x, top + h * 0.5)
            ctx.line_to(x + 0.08 * R, top + h * 0.42)
            ctx.close_path()
            ctx.set_source_rgb(*self._c(self.tie))
            ctx.fill()
        if self.zipper or (self.collar == "shirt" and not self.tie):
            ctx.move_to(x, top + 0.58 * R)
            ctx.line_to(x, base - 0.4 * R)
            ctx.set_source_rgba(*INK, 0.5)
            ctx.set_line_width(lw * 0.35)
            ctx.stroke()
        if self.pin:
            ctx.arc(x + 0.42 * R, top + h * 0.48, 0.08 * R, 0, 2 * math.pi)
            ctx.set_source_rgb(*self._c(self.pin))
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 0.3)
            ctx.stroke()

    def _arms(self, ctx, x, top, bw, bh, R, lw, limb, arms, item, item_hand, t, only=("l", "r"), rest=True):
        presets = {
            "rest": {}, "down": {},
            "hold": {"l": (-0.25, 1.15), "r": (0.25, 1.15)},
            "raise_r": {"r": (1.1, -0.7)}, "raise_l": {"l": (-1.1, -0.7)},
            "wave": {"r": (1.05, -1.0)},
            "point_r": {"r": (2.2, 0.15)}, "point_l": {"l": (-2.2, 0.15)},
            "shrug": {"l": (-1.15, -0.2), "r": (1.15, -0.2)},
            "present_r": {"r": (1.35, 0.55)}, "present_l": {"l": (-1.35, 0.55)},
            "hips": {"l": (-0.85, 0.95), "r": (0.85, 0.95)},
            "chin": {"r": (0.15, -0.35)},
            "cheer": {"l": (-0.9, -1.4), "r": (0.9, -1.4)},
        }
        amount = 1.0
        targets = {}
        sh_y = top + 0.25 * bh
        if isinstance(arms, dict):
            targets = dict(arms)
        else:
            if isinstance(arms, tuple):
                arms, amount = arms
            for k, (ox, oy) in presets.get(arms, {}).items():
                rx, ry = (-0.55 if k == "l" else 0.55), 1.15
                targets[k] = (x + (rx + (ox - rx) * amount) * R, sh_y + (ry + (oy - ry) * amount) * R)
        hands = {}
        for sd, key in ((-1, "l"), (1, "r")):
            if key not in only:
                continue
            sx = x + sd * bw * 0.46
            if key not in targets:
                if rest:
                    ctx.new_path()
                    ctx.move_to(x + sd * bw * 0.36, sh_y - 0.05 * R)
                    ctx.curve_to(x + sd * bw * 0.44, sh_y + 0.5 * R, x + sd * bw * 0.44, sh_y + 0.95 * R,
                                 x + sd * bw * 0.32, sh_y + 1.25 * R)
                    ctx.set_source_rgb(*INK)
                    ctx.set_line_width(lw * 0.8)
                    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                    ctx.stroke()
                hands[key] = (x + sd * bw * 0.32, sh_y + 1.25 * R)
                continue
            hxp, hyp = targets[key]
            dx, dy = hxp - sx, hyp - sh_y
            mx = sx + dx * 0.5 + sd * 0.1 * R
            my = sh_y + dy * 0.5 + abs(dx) * 0.08
            _line(ctx, [(sx, sh_y), (mx, my), (hxp, hyp)], limb)
            hands[key] = (hxp, hyp)
            if item and key == item_hand:
                draw_item(ctx, item, hxp, hyp, R, t)
            ang = math.atan2(hyp - my, hxp - mx)
            for k in (-0.6, 0, 0.6):
                a = ang + k
                _line(ctx, [(hxp, hyp), (hxp + math.cos(a) * 0.14 * R, hyp + math.sin(a) * 0.14 * R)], limb * 0.8)
        return hands

    # ------------------------------------------------------------------ head
    def _skin(self, col):
        # skin keeps its warmth under coloured scene light (half-strength tint), clothes take it fully
        return mix(col, mul(col, self.ambient), 0.5)

    def _skin_fill(self, ctx, cx, cy, R):
        lx, ly = self.light
        sk = {k: self._skin(v) for k, v in self.sk.items()}
        g = cairo.LinearGradient(cx + lx * R, cy + ly * R, cx - lx * R, cy - ly * R)
        g.add_color_stop_rgb(0, *sk["hi"])
        g.add_color_stop_rgb(0.4, *sk["mid"])
        g.add_color_stop_rgb(1, *sk["sh"])
        ctx.set_source(g)
        ctx.paint()
        g = cairo.RadialGradient(cx + lx * 0.25 * R, cy - 0.45 * R, 0, cx + lx * 0.25 * R, cy - 0.45 * R, 0.8 * R)
        g.add_color_stop_rgba(0, *sk["hi"], 0.5)
        g.add_color_stop_rgba(1, *sk["hi"], 0)
        ctx.set_source(g)
        ctx.paint()
        g = cairo.LinearGradient(0, cy + 0.55 * R, 0, cy + R)
        g.add_color_stop_rgba(0, *sk["sh"], 0)
        g.add_color_stop_rgba(1, *sk["sh"], 0.55)
        ctx.set_source(g)
        ctx.paint()

    def _moon(self, ctx, cx, cy, R, lw):
        """The bright crescent on the key-light side and its thin inner edge line."""
        lx, ly = self.light
        rim = self.rim or self._skin(self.sk["rim"])
        ox, oy = -lx * 0.13 * R, -ly * 0.13 * R
        ctx.new_path()
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.new_sub_path()
        ctx.arc(cx + ox, cy + oy, R * 0.985, 0, 2 * math.pi)
        g = cairo.LinearGradient(cx + lx * R, cy + ly * R, cx, cy)
        g.add_color_stop_rgba(0, *rim, 0.95)
        g.add_color_stop_rgba(1, *rim, 0.55)
        ctx.set_source(g)
        ctx.fill()
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        a = math.atan2(ly, lx)
        ctx.new_path()
        ctx.arc(cx + ox, cy + oy, R * 0.985, a - 1.25, a + 1.25)
        ctx.set_source_rgba(*mix(self._c(self.sk["sh"]), (0, 0, 0), 0.25), 0.55)
        ctx.set_line_width(max(0.8, lw * 0.3))
        ctx.stroke()

    def _head(self, ctx, cx, cy, R, lw, expr, t, talk, look):
        if self.hair == "bob":
            self._hair_back(ctx, cx, cy, R, lw, look)
        ctx.save()
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.clip()
        self._skin_fill(ctx, cx, cy, R)
        self._moon(ctx, cx, cy, R, lw)
        ctx.restore()
        if self.earrings:
            for sd in (-1, 1):
                ex = cx + sd * R * (0.97 - 0.25 * max(0, sd * look))
                ctx.arc(ex, cy + R * 0.32, R * 0.06, 0, 2 * math.pi)
                ctx.set_source_rgb(*self._c(self.earrings))
                ctx.fill()
        ctx.new_path()
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw)
        ctx.stroke()
        fx = cx + look * 0.38 * R
        self._temples(ctx, fx, cx, cy, R, lw, look)
        draw_face(ctx, fx, cy, R, lw, expr, t, talk, self, look)
        self._glasses(ctx, fx, cy, R, lw, look)
        self._hair_front(ctx, cx, cy, R, lw, look)

    def _head_back(self, ctx, cx, cy, R, lw, look):
        ctx.save()
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.clip()
        self._skin_fill(ctx, cx, cy, R)
        ctx.restore()
        col = self._c(self.hair_col)
        if self.hair != "bald":
            ctx.save()
            ctx.arc(cx, cy, R + lw, 0, 2 * math.pi)
            ctx.clip()
            ctx.new_path()
            low = 0.25 if self.hair in ("bob", "long", "bun") else 0.05
            ctx.move_to(cx - 1.2 * R, cy - 1.2 * R)
            ctx.line_to(cx + 1.2 * R, cy - 1.2 * R)
            ctx.line_to(cx + 1.2 * R, cy + low * R)
            for k in range(7):
                xx = cx + R - (k + 0.5) * (2 * R / 7)
                ctx.line_to(xx, cy + (low + (0.12 if k % 2 == 0 else 0)) * R)
            ctx.line_to(cx - 1.2 * R, cy + low * R)
            ctx.close_path()
            ctx.set_source_rgb(*col)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 0.6)
            ctx.stroke()
            ctx.restore()
            if self.hair == "bun":
                ctx.new_path()
                ctx.arc(cx, cy - 1.05 * R, 0.32 * R, 0, 2 * math.pi)
                _fill_ink(ctx, col, lw * 0.8)
            if self.hair == "long":
                ctx.new_path()
                ctx.rectangle(cx - 0.95 * R, cy, 1.9 * R, 1.6 * R)
                _fill_ink(ctx, col, lw * 0.8)
        ctx.new_path()
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw)
        ctx.stroke()

    def _hair_back(self, ctx, cx, cy, R, lw, look):
        ctx.new_path()
        ctx.move_to(cx - 1.12 * R, cy + 0.8 * R)
        ctx.curve_to(cx - 1.32 * R, cy - 1.4 * R, cx + 1.32 * R, cy - 1.4 * R, cx + 1.12 * R, cy + 0.8 * R)
        ctx.close_path()
        _fill_ink(ctx, self._c(self.hair_col), lw * 0.8)

    def _long_hair_back(self, ctx, cx, cy, R, lw):
        ctx.new_path()
        ctx.move_to(cx - 1.05 * R, cy)
        ctx.curve_to(cx - 1.25 * R, cy - 1.3 * R, cx + 1.25 * R, cy - 1.3 * R, cx + 1.05 * R, cy)
        ctx.line_to(cx + 1.0 * R, cy + 2.2 * R)
        ctx.line_to(cx - 1.0 * R, cy + 2.2 * R)
        ctx.close_path()
        _fill_ink(ctx, self._c(self.hair_col), lw * 0.8)

    def _hair_front(self, ctx, cx, cy, R, lw, look):
        h = self.hair
        col = self._c(self.hair_col)
        if h == "none":
            return
        if h == "bald":
            for sd in (-1, 1):
                ctx.new_path()
                ctx.move_to(cx + sd * 1.03 * R, cy + 0.1 * R)
                ctx.curve_to(cx + sd * 1.15 * R, cy - 0.25 * R, cx + sd * 1.08 * R, cy - 0.5 * R, cx + sd * 0.86 * R, cy - 0.6 * R)
                ctx.curve_to(cx + sd * 0.92 * R, cy - 0.3 * R, cx + sd * 0.9 * R, cy - 0.05 * R, cx + sd * 1.03 * R, cy + 0.1 * R)
                ctx.close_path()
                _fill_ink(ctx, col, lw * 0.7)
            return
        side = 0.08 if h in ("bowl", "bun", "bob", "long") else -0.2
        fr = cx + look * 0.25 * R
        ctx.new_path()
        ctx.move_to(cx - 1.08 * R, cy + side * R)
        ctx.curve_to(cx - 1.18 * R, cy - 1.3 * R, cx + 1.18 * R, cy - 1.3 * R, cx + 1.08 * R, cy + side * R)
        if h == "spiky":
            for k in range(6):
                xx = cx + R - (k + 0.5) * (2 * R / 6)
                ctx.line_to(xx + 0.1 * R, cy - 0.35 * R)
                ctx.line_to(xx - 0.05 * R, cy - 0.6 * R)
        elif h == "side":
            ctx.curve_to(cx + 0.9 * R, cy - 0.5 * R, fr + 0.4 * R, cy - 0.45 * R, fr - 0.2 * R, cy - 0.62 * R)
            ctx.curve_to(fr - 0.5 * R, cy - 0.7 * R, cx - 0.9 * R, cy - 0.45 * R, cx - 1.08 * R, cy + side * R)
        else:
            ctx.curve_to(cx + 0.95 * R, cy - 0.38 * R, fr + 0.5 * R, cy - 0.5 * R, fr, cy - 0.5 * R)
            ctx.curve_to(fr - 0.5 * R, cy - 0.5 * R, cx - 0.95 * R, cy - 0.38 * R, cx - 1.08 * R, cy + side * R)
        ctx.close_path()
        _fill_ink(ctx, col, lw * 0.75)
        if h == "curly":
            for k in range(9):
                a = math.pi + 0.1 + k * (math.pi - 0.2) / 8
                ctx.new_path()
                ctx.arc(cx + math.cos(a) * 0.98 * R, cy + math.sin(a) * 0.98 * R, 0.2 * R, 0, 2 * math.pi)
                _fill_ink(ctx, col, lw * 0.6)
        if h == "bun":
            ctx.new_path()
            ctx.arc(cx + look * 0.1 * R, cy - 1.18 * R, 0.3 * R, 0, 2 * math.pi)
            _fill_ink(ctx, col, lw * 0.75)

    def _temples(self, ctx, fx, cx, cy, R, lw, look):
        if not self.glasses:
            return
        ey = cy - 0.04 * R
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(max(1.0, lw * 0.4))
        for sd in (-1, 1):
            if look * sd > 0.15:
                continue
            ex = fx + sd * 0.42 * R
            edge = cx + sd * R * 0.99
            if (edge - ex) * sd > 0:
                ctx.move_to(ex, ey)
                ctx.line_to(edge, ey - 0.04 * R)
                ctx.stroke()

    def _glasses(self, ctx, fx, cy, R, lw, look):
        g = self.glasses
        if not g:
            return
        ey = cy - 0.04 * R
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(max(1.0, lw * 0.4))
        for sd in (-1, 1):
            ex = fx + sd * 0.25 * R
            squash = 1 - 0.35 * max(0, -sd * look)
            ctx.new_path()
            if g == "round":
                ctx.save()
                ctx.translate(ex, ey)
                ctx.scale(squash, 1)
                ctx.arc(0, 0, 0.16 * R, 0, 2 * math.pi)
                ctx.restore()
            else:
                _rrect(ctx, ex - 0.17 * R * squash, ey - 0.11 * R, 0.34 * R * squash, 0.22 * R, 0.04 * R)
            if g == "shades":
                ctx.set_source_rgb(0.03, 0.02, 0.02)
                ctx.fill_preserve()
                ctx.set_source_rgb(*INK)
            ctx.stroke()
        ctx.move_to(fx - 0.09 * R, ey - 0.02 * R)
        ctx.line_to(fx + 0.09 * R, ey - 0.02 * R)
        ctx.stroke()


# ---------------------------------------------------------------------- face
EXPRESSIONS = ("neutral", "happy", "joy", "laugh", "talk", "smirk", "wink", "shock", "scared", "sad", "worried",
               "angry", "deadpan", "blush", "sly")


def draw_face(ctx, cx, cy, R, lw, expr, t, talk, ch=None, look=0.0):
    w = max(1.0, lw * 0.55)
    ey = cy - 0.02 * R
    ex = 0.21 * R
    my = cy + 0.32 * R
    if expr == "talk":
        talk, expr = True, "neutral"

    def stroke(width=None):
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(width or w)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()

    def eye(x0, scale=1.0):
        ctx.new_path()
        ctx.save()
        ctx.translate(x0, ey)
        ctx.scale(0.055 * R * scale, 0.085 * R * scale)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(*EYE)
        ctx.fill()
        ctx.arc(x0 + 0.018 * R, ey - 0.035 * R, 0.018 * R * scale, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()

    def closed(x0):
        ctx.new_path()
        ctx.arc(x0, ey + 0.04 * R, 0.08 * R, math.pi * 1.15, math.pi * 1.85)
        stroke()

    def brow(sd, lift=0.0, tilt=0.0):
        x0, y0 = cx + sd * ex, ey - (0.24 + lift) * R
        ctx.new_path()
        ctx.move_to(x0 - 0.1 * R, y0 + 0.025 * R + sd * tilt * R)
        ctx.curve_to(x0 - 0.04 * R, y0 - 0.03 * R, x0 + 0.04 * R, y0 - 0.03 * R, x0 + 0.1 * R, y0 + 0.025 * R - sd * tilt * R)
        stroke()

    def creases():
        for sd in (-1, 1):
            for k in (-1, 0, 1):
                ctx.new_path()
                x0 = cx + sd * (ex + 0.13 * R)
                ctx.move_to(x0, ey + k * 0.035 * R)
                ctx.line_to(x0 + sd * 0.07 * R, ey + k * 0.05 * R)
                ctx.set_source_rgba(*INK, 0.35)
                ctx.set_line_width(w * 0.6)
                ctx.stroke()

    def blush():
        for sd in (-1, 1):
            for k in range(3):
                x0 = cx + sd * (ex + 0.02 * R) + (k - 1) * 0.045 * R
                ctx.new_path()
                ctx.move_to(x0 - 0.02 * R, ey + 0.17 * R)
                ctx.line_to(x0 + 0.02 * R, ey + 0.11 * R)
                ctx.set_source_rgba(0.93, 0.35, 0.45, 0.8)
                ctx.set_line_width(w * 0.8)
                ctx.stroke()

    blink = (t % 4.1) < 0.09
    if expr in ("joy", "laugh"):
        closed(cx - ex)
        closed(cx + ex)
        brow(-1, 0.03)
        brow(1, 0.03)
        if expr == "laugh":
            creases()
    elif expr == "wink":
        eye(cx - ex)
        closed(cx + ex)
        brow(-1, 0.05)
        brow(1, -0.02)
        creases()
    elif expr in ("shock", "scared"):
        for sd in (-1, 1):
            ctx.new_path()
            ctx.arc(cx + sd * ex, ey, 0.1 * R, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill_preserve()
            stroke()
            ctx.arc(cx + sd * ex, ey, 0.035 * R, 0, 2 * math.pi)
            ctx.set_source_rgb(*EYE)
            ctx.fill()
            brow(sd, 0.1, -0.03 if expr == "scared" else 0)
    elif blink:
        for sd in (-1, 1):
            ctx.new_path()
            ctx.move_to(cx + sd * ex - 0.05 * R, ey)
            ctx.line_to(cx + sd * ex + 0.05 * R, ey)
            stroke()
    else:
        eye(cx - ex)
        eye(cx + ex)
        if expr in ("smirk", "sly"):
            brow(-1, 0.07, 0.03)
            brow(1, -0.03, -0.02)
            if expr == "sly":
                for sd in (-1, 1):
                    ctx.new_path()
                    ctx.move_to(cx + sd * ex - 0.07 * R, ey - 0.03 * R)
                    ctx.line_to(cx + sd * ex + 0.07 * R, ey - 0.03 * R)
                    stroke(w * 1.2)
        elif expr == "angry":
            brow(-1, -0.04, 0.06)
            brow(1, -0.04, 0.06)
        elif expr in ("sad", "worried"):
            brow(-1, 0.04, -0.05)
            brow(1, 0.04, -0.05)
        else:
            brow(-1)
            brow(1)
    if ch is not None and ch.creases and expr not in ("laugh", "wink"):
        creases()
    if expr == "blush" or (ch is not None and ch.blush_always):
        blush()

    if expr == "laugh":
        mw, mh = 0.24 * R, 0.3 * R * (0.92 + 0.08 * math.sin(t * 17))
        top = my - 0.04 * R
        ctx.new_path()
        ctx.move_to(cx - mw, top)
        ctx.curve_to(cx - mw * 0.95, top + mh * 1.25, cx + mw * 0.95, top + mh * 1.25, cx + mw, top)
        ctx.close_path()
        ctx.set_source_rgb(0x43 / 255, 0x0b / 255, 0x0b / 255)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        ctx.rectangle(cx - mw, top - 0.02 * R, 2 * mw, 0.1 * R)
        ctx.set_source_rgb(0xec / 255, 0xe0 / 255, 0xc0 / 255)
        ctx.fill()
        ctx.new_path()
        ctx.arc(cx, top + mh * 0.95, mw * 0.5, 0, 2 * math.pi)
        ctx.set_source_rgb(0xd3 / 255, 0x42 / 255, 0x38 / 255)
        ctx.fill()
        ctx.restore()
        ctx.new_path()
        ctx.move_to(cx - mw, top)
        ctx.curve_to(cx - mw * 0.95, top + mh * 1.25, cx + mw * 0.95, top + mh * 1.25, cx + mw, top)
        ctx.close_path()
        stroke()
    elif expr in ("shock", "scared"):
        ctx.new_path()
        ctx.save()
        ctx.translate(cx, my + 0.03 * R)
        ctx.scale(0.08 * R, 0.11 * R)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0x43 / 255, 0x0b / 255, 0x0b / 255)
        ctx.fill_preserve()
        stroke()
    elif talk:
        k = 0.25 + 0.75 * abs(math.sin(t * 9.0)) * (0.6 + 0.4 * math.sin(t * 3.1))
        ctx.new_path()
        ctx.save()
        ctx.translate(cx, my)
        ctx.scale(0.09 * R, 0.075 * R * k + 0.01 * R)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0x43 / 255, 0x0b / 255, 0x0b / 255)
        ctx.fill_preserve()
        stroke(w * 0.8)
    else:
        ctx.new_path()
        if expr in ("happy", "joy", "neutral", "blush", "wink"):
            wdt = 0.12 if expr == "neutral" else 0.16
            ctx.move_to(cx - wdt * R, my - 0.02 * R)
            ctx.curve_to(cx - 0.05 * R, my + 0.06 * R, cx + 0.05 * R, my + 0.06 * R, cx + wdt * R, my - 0.02 * R)
        elif expr in ("smirk", "sly"):
            ctx.move_to(cx - 0.11 * R, my + 0.01 * R)
            ctx.curve_to(cx - 0.02 * R, my + 0.05 * R, cx + 0.07 * R, my + 0.03 * R, cx + 0.14 * R, my - 0.05 * R)
        elif expr in ("sad", "worried"):
            ctx.move_to(cx - 0.1 * R, my + 0.04 * R)
            ctx.curve_to(cx - 0.04 * R, my - 0.03 * R, cx + 0.04 * R, my - 0.03 * R, cx + 0.1 * R, my + 0.04 * R)
        elif expr == "angry":
            ctx.move_to(cx - 0.1 * R, my + 0.02 * R)
            ctx.line_to(cx + 0.1 * R, my - 0.01 * R)
        else:
            ctx.move_to(cx - 0.07 * R, my)
            ctx.line_to(cx + 0.07 * R, my)
        stroke()
    if ch is not None and ch.mustache:
        ctx.new_path()
        ctx.move_to(cx - 0.12 * R, my - 0.05 * R)
        ctx.curve_to(cx - 0.05 * R, my - 0.12 * R, cx + 0.05 * R, my - 0.12 * R, cx + 0.12 * R, my - 0.05 * R)
        ctx.curve_to(cx + 0.04 * R, my - 0.07 * R, cx - 0.04 * R, my - 0.07 * R, cx - 0.12 * R, my - 0.05 * R)
        ctx.set_source_rgb(*ch.mustache)
        ctx.fill()
    if expr in ("shock", "worried", "scared"):
        sx, sy = cx + 0.62 * R, cy - 0.42 * R + (t * 25 % 10) * 0.012 * R
        ctx.new_path()
        ctx.move_to(sx, sy - 0.14 * R)
        ctx.curve_to(sx + 0.09 * R, sy, sx + 0.07 * R, sy + 0.09 * R, sx, sy + 0.09 * R)
        ctx.curve_to(sx - 0.07 * R, sy + 0.09 * R, sx - 0.09 * R, sy, sx, sy - 0.14 * R)
        ctx.set_source_rgb(0.62, 0.86, 1.0)
        ctx.fill_preserve()
        stroke(w * 0.7)


# ---------------------------------------------------------------------- helpers
def _line(ctx, pts, w, col=INK):
    ctx.new_path()
    ctx.set_source_rgb(*col)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    if len(pts) == 3:
        (x0, y0), (mx, my), (x1, y1) = pts
        ctx.curve_to(x0 + (mx - x0) * 0.66, y0 + (my - y0) * 0.66, x1 + (mx - x1) * 0.66, y1 + (my - y1) * 0.66, x1, y1)
    else:
        for p in pts[1:]:
            ctx.line_to(*p)
    ctx.stroke()


def _fill_ink(ctx, col, w):
    ctx.set_source_rgb(*col)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(w)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def _rrect(ctx, x, y, w, h, r):
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


# ---------------------------------------------------------------------- items
def draw_item(ctx, item, x, y, R, t):
    lw = 0.035 * R + 0.5
    if item == "wine":
        bw, bh, stem = 0.36 * R, 0.75 * R, 0.75 * R
        ctx.save()
        ctx.translate(x, y)
        ctx.save()
        ctx.scale(bw * 0.95, bw * 0.2)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.95, 0.92, 0.85)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw * 0.7)
        ctx.stroke()
        ctx.set_source_rgb(0.95, 0.92, 0.85)
        ctx.set_line_width(lw * 1.5)
        ctx.move_to(0, 0)
        ctx.line_to(0, -stem)
        ctx.stroke()
        top = -stem - bh
        ctx.new_path()
        ctx.move_to(-bw, top)
        ctx.curve_to(-bw * 1.05, -stem + bh * 0.05, bw * 1.05, -stem + bh * 0.05, bw, top)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.new_path()
        ctx.move_to(-bw * 0.98, top + bh * 0.35)
        ctx.curve_to(-bw, -stem + bh * 0.02, bw, -stem + bh * 0.02, bw * 0.98, top + bh * 0.35)
        ctx.close_path()
        ctx.set_source_rgb(0x93 / 255, 0x2a / 255, 0x27 / 255)
        ctx.fill()
        ctx.restore()
    elif item == "fork":
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-0.55)
        ctx.set_source_rgb(0.92, 0.9, 0.86)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_width(lw * 2.2)
        ctx.move_to(0, 0.1 * R)
        ctx.line_to(0, -1.2 * R)
        ctx.stroke()
        ctx.set_line_width(lw * 1.6)
        for k in (-1, 0, 1):
            ctx.move_to(k * 0.09 * R, -1.15 * R)
            ctx.line_to(k * 0.09 * R, -1.55 * R)
            ctx.stroke()
        ctx.restore()
    elif item == "phone":
        ctx.save()
        ctx.translate(x, y - 0.3 * R)
        _rrect(ctx, -0.2 * R, -0.36 * R, 0.4 * R, 0.72 * R, 0.06 * R)
        ctx.set_source_rgb(0.1, 0.1, 0.12)
        ctx.fill()
        ctx.rectangle(-0.15 * R, -0.3 * R, 0.3 * R, 0.56 * R)
        ctx.set_source_rgb(0.55, 0.85, 1.0)
        ctx.fill()
        ctx.restore()
    elif item == "paper":
        ctx.save()
        ctx.translate(x, y - 0.5 * R)
        ctx.rotate(-0.08)
        ctx.rectangle(-0.45 * R, -0.6 * R, 0.9 * R, 1.2 * R)
        _fill_ink(ctx, (0.98, 0.97, 0.94), lw)
        ctx.set_source_rgba(*INK, 0.4)
        ctx.set_line_width(lw * 0.6)
        for k in range(4):
            ctx.move_to(-0.3 * R, -0.35 * R + k * 0.22 * R)
            ctx.line_to(0.3 * R, -0.35 * R + k * 0.22 * R)
            ctx.stroke()
        ctx.restore()
    elif item == "key":
        ctx.save()
        ctx.translate(x, y - 0.4 * R)
        g = cairo.RadialGradient(0, 0, 0, 0, 0, 0.9 * R)
        g.add_color_stop_rgba(0, 1, 0.85, 0.3, 0.6)
        g.add_color_stop_rgba(1, 1, 0.85, 0.3, 0)
        ctx.set_source(g)
        ctx.arc(0, 0, 0.9 * R, 0, 2 * math.pi)
        ctx.fill()
        ctx.arc(0, -0.25 * R, 0.18 * R, 0, 2 * math.pi)
        ctx.set_source_rgb(0.98, 0.78, 0.2)
        ctx.set_line_width(0.09 * R)
        ctx.stroke()
        ctx.move_to(0, -0.07 * R)
        ctx.line_to(0, 0.55 * R)
        ctx.move_to(0, 0.4 * R)
        ctx.line_to(0.15 * R, 0.4 * R)
        ctx.move_to(0, 0.52 * R)
        ctx.line_to(0.12 * R, 0.52 * R)
        ctx.stroke()
        ctx.restore()
