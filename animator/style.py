"""Flat 2D cartoon characters matched to the Paper Billions references (measured on V1 frames
0:07 and 0:23 at 1280x720, see references/notes_v1_part1.md and style_bible.md):

- head: big circle; outline #200a00 about 4% of the head radius; lines of the face about the same weight
- skin in three tones lit by one warm key light: highlight #fdd480, mid #e9a561, shade #b5794e,
  plus a crisp bright crescent (#ffc56a) just inside the outline on the key-light side
- dot / arc eyes, small curved brows, no nose; laugh = big D mouth (#430b0b inside, cream teeth band,
  coral tongue #d34238)
- the face turns toward whoever the character talks to (look = -1..1 shifts the features)
- glasses: thin frames whose temple lines run out to the edge of the head on both sides
- hair: a big solid shape with its own outline and a few strand lines, reaching outside the head
- body: broad sloped shoulders right under the head (no neck), clothing colour, thin outline
- limbs: long curved black lines about as thick as the head outline; 4 splayed stick fingers

Char.draw() keeps the signature of reference_examples/animator/style2.py Char2.draw. (x, y) is the
point between the feet (or the hip point for pose="sit"); s=1 gives a head radius of 40 px.
`arms` may be a preset name, (preset, amount 0..1), or a dict {"r": (x, y), "l": (x, y)} of hand
targets in world coordinates.
"""
import math

import cairo

INK = (0x20 / 255, 0x0a / 255, 0.0)
SKIN_HI, SKIN_MID, SKIN_SH, SKIN_RIM = "#fdd480", "#e9a561", "#b5794e", "#ffc56a"


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


def _clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


class Char:
    """hair: 'swept' (big side-swept), 'bob', 'bun', 'short', 'curly', 'bald', 'none'.
    glasses: None, 'rect', 'round', 'shades'. collar: None, 'shirt', 'lapel', 'round'.
    light: direction the key light comes FROM, e.g. (1, 0.3) = from the right and a bit below."""

    def __init__(self, body="#1a1412", hair="short", hair_col="#2b2422", skin=None,
                 glasses=None, collar="lapel", tie=None, earrings=None, light=(1.0, 0.2), pin=None, build=1.0):
        self.body = hexc(body)
        self.hair = hair
        self.hair_col = hexc(hair_col)
        sk = skin or {}
        self.sk_hi = hexc(sk.get("hi", SKIN_HI))
        self.sk_mid = hexc(sk.get("mid", SKIN_MID))
        self.sk_sh = hexc(sk.get("sh", SKIN_SH))
        self.sk_rim = hexc(sk.get("rim", SKIN_RIM))
        self.glasses = glasses
        self.collar = collar
        self.tie = hexc(tie) if tie else None
        self.earrings = hexc(earrings) if earrings else None
        self.pin = hexc(pin) if pin else None
        self.build = build
        n = math.hypot(*light) or 1
        self.light = (light[0] / n, light[1] / n)

    # ------------------------------------------------------------------ public
    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False, arms="down", pose="stand",
             look=0.0, bob=0.0, item=None, item_hand="r", walk_phase=None, lean=0.0, shadow=True):
        R = 40 * s
        lw = 0.04 * R + 0.6
        limb = 0.042 * R + 0.6
        sway = math.sin(t * 2.0) * 0.01 * R + bob * R
        legs_h = 0.0 if pose == "sit" else 1.15 * R
        torso_h, torso_w = 1.75 * R, 1.75 * R * self.build
        hip_y = y - legs_h
        top_y = hip_y - torso_h
        hx = x + lean * R * 0.5
        head_cy = top_y - 0.82 * R + sway

        if shadow and pose != "sit":
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(1, 0.2)
            g = cairo.RadialGradient(0, 0, 0, 0, 0, 1.4 * R)
            g.add_color_stop_rgba(0, 0, 0, 0, 0.3)
            g.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.set_source(g)
            ctx.arc(0, 0, 1.4 * R, 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()

        if pose != "sit":
            for side in (-1, 1):
                fx = x + side * 0.3 * R
                kx = fx
                if walk_phase is not None:
                    sw = math.sin(walk_phase + (0 if side < 0 else math.pi)) * 0.35 * R
                    fx += sw
                    kx += sw * 0.5
                _curve(ctx, [(x + side * 0.3 * R, hip_y - 0.1 * R), (kx, y - 0.55 * R), (fx, y)], limb)
                _curve(ctx, [(fx, y), (fx + side * 0.2 * R, y)], limb)

        self._hair_back(ctx, hx, head_cy, R, lw, look)
        self._torso(ctx, hx, hip_y, torso_w, torso_h, lw)
        hands = self._arms(ctx, hx, top_y, torso_w, R, limb, arms, item, item_hand, t)
        self._last_arms = (hx, top_y, torso_w, R, limb, arms, item, item_hand, t)
        self._head(ctx, hx, head_cy, R, lw, expr, t, talk, look)
        return {"head": (hx, head_cy, R), "hands": hands}

    def draw_arms_over(self, ctx, only=("l", "r")):
        """Re-draw the arms of the last draw() on top of props (hands resting ON a table)."""
        hx, top_y, w, R, limb, arms, item, item_hand, t = self._last_arms
        if isinstance(arms, dict):
            arms = {k: v for k, v in arms.items() if k in only}
            if not arms:
                return
        self._arms(ctx, hx, top_y, w, R, limb, arms, item, item_hand, t, only=only)

    # ----------------------------------------------------------------- pieces
    def _torso(self, ctx, x, hip_y, w, h, lw):
        top = hip_y - h
        ctx.new_path()
        ctx.move_to(x - w * 0.52, hip_y + h * 0.05)
        ctx.curve_to(x - w * 0.56, top + h * 0.45, x - w * 0.5, top + h * 0.08, x - w * 0.18, top)
        ctx.line_to(x + w * 0.18, top)
        ctx.curve_to(x + w * 0.5, top + h * 0.08, x + w * 0.56, top + h * 0.45, x + w * 0.52, hip_y + h * 0.05)
        ctx.close_path()
        lx = self.light[0]
        g = cairo.LinearGradient(x + lx * w * 0.6, top, x - lx * w * 0.6, hip_y)
        g.add_color_stop_rgb(0, *mix(self.body, (1, 0.85, 0.6), 0.14))
        g.add_color_stop_rgb(1, *mix(self.body, (0, 0, 0), 0.25))
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw * 0.85)
        ctx.stroke()
        if self.collar == "lapel":
            ctx.set_source_rgb(*mix(self.body, (0, 0, 0), 0.5))
            ctx.set_line_width(lw * 0.5)
            for sd in (-1, 1):
                ctx.move_to(x + sd * w * 0.2, top + h * 0.02)
                ctx.line_to(x + sd * w * 0.08, top + h * 0.42)
                ctx.line_to(x + sd * w * 0.3, top + h * 0.3)
                ctx.stroke()
        elif self.collar == "shirt":
            ctx.new_path()
            ctx.move_to(x - w * 0.24, top + h * 0.0)
            ctx.line_to(x, top + h * 0.2)
            ctx.line_to(x + w * 0.24, top + h * 0.0)
            ctx.line_to(x + w * 0.12, top + h * 0.12)
            ctx.line_to(x, top + h * 0.08)
            ctx.line_to(x - w * 0.12, top + h * 0.12)
            ctx.close_path()
            ctx.set_source_rgb(0.97, 0.94, 0.88)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 0.5)
            ctx.stroke()
        elif self.collar == "round":
            ctx.new_path()
            ctx.save()
            ctx.translate(x, top + h * 0.02)
            ctx.scale(w * 0.3, h * 0.12)
            ctx.arc(0, 0, 1, 0, math.pi)
            ctx.restore()
            ctx.set_source_rgb(0.97, 0.95, 0.9)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 0.5)
            ctx.stroke()
        if self.tie:
            ctx.new_path()
            ctx.move_to(x, top + h * 0.12)
            ctx.line_to(x - w * 0.05, top + h * 0.45)
            ctx.line_to(x, top + h * 0.55)
            ctx.line_to(x + w * 0.05, top + h * 0.45)
            ctx.close_path()
            ctx.set_source_rgb(*self.tie)
            ctx.fill()
        if self.pin:
            ctx.save()
            ctx.translate(x + w * 0.22, top + h * 0.48)
            ctx.scale(w * 0.05, w * 0.04)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgb(*self.pin)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 0.3)
            ctx.stroke()

    def _arms(self, ctx, x, top_y, w, R, limb, arms, item, item_hand, t, only=("l", "r")):
        presets = {
            "down": {"l": (-0.62, 1.5), "r": (0.62, 1.5)},
            "hold": {"l": (-0.45, 1.2), "r": (0.45, 1.2)},
            "raise_r": {"r": (1.2, -0.6)}, "raise_l": {"l": (-1.2, -0.6)},
            "toast": {"r": (1.05, -0.35)},
            "point_r": {"r": (1.9, 0.2)}, "point_l": {"l": (-1.9, 0.2)},
            "shrug": {"l": (-1.15, -0.05), "r": (1.15, -0.05)},
            "chin": {"r": (0.2, -0.45)},
            "table": {"l": (-0.8, 1.6), "r": (0.8, 1.6)},
        }
        amount = 1.0
        targets = {}
        sh_y = top_y + 0.32 * R
        base = presets["down"]
        if isinstance(arms, dict):
            targets = dict(arms)
        else:
            if isinstance(arms, tuple):
                arms, amount = arms
            p = presets.get(arms, {})
            for k in ("l", "r"):
                bx, by = base[k]
                px, py = p.get(k, base[k])
                tx, ty = bx + (px - bx) * amount, by + (py - by) * amount
                targets[k] = (x + tx * w, sh_y + ty * R)
        hands = {}
        for side, key in ((-1, "l"), (1, "r")):
            if key not in only:
                continue
            sx = x + side * w * 0.44
            hxp, hyp = targets.get(key, (x + base[key][0] * w, sh_y + base[key][1] * R))
            # elbow bends outward and down for a soft curve
            dx, dy = hxp - sx, hyp - sh_y
            mx, my = sx + dx * 0.5 + side * abs(dy) * 0.18 + side * 0.12 * R, sh_y + dy * 0.5 + abs(dx) * 0.12
            _curve(ctx, [(sx, sh_y), (mx, my), (hxp, hyp)], limb)
            hands[key] = (hxp, hyp)
            ang = math.atan2(hyp - my, hxp - mx)
            if item and key == item_hand:
                draw_item(ctx, item, hxp, hyp, R, t)
            _fingers(ctx, hxp, hyp, ang, R, limb)
        return hands

    def _head(self, ctx, cx, cy, R, lw, expr, t, talk, look):
        lx, ly = self.light
        ctx.save()
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.clip()
        # three tones: shade on the side away from the light, mid, highlight toward the light/top
        g = cairo.LinearGradient(cx + lx * R, cy + ly * R, cx - lx * R, cy - ly * R)
        g.add_color_stop_rgb(0, *self.sk_hi)
        g.add_color_stop_rgb(0.35, *self.sk_mid)
        g.add_color_stop_rgb(0.85, *self.sk_sh)
        g.add_color_stop_rgb(1, *mix(self.sk_sh, (0.2, 0.08, 0.02), 0.25))
        ctx.set_source(g)
        ctx.paint()
        g = cairo.RadialGradient(cx - 0.1 * R, cy - 0.55 * R, 0, cx - 0.1 * R, cy - 0.55 * R, 0.9 * R)
        g.add_color_stop_rgba(0, *self.sk_hi, 0.55)
        g.add_color_stop_rgba(1, *self.sk_hi, 0)
        ctx.set_source(g)
        ctx.paint()
        # crisp rim crescent: head circle minus the same circle nudged away from the light
        ctx.new_path()
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.new_sub_path()
        ctx.arc(cx - lx * 0.09 * R, cy - ly * 0.09 * R, R * 0.995, 0, 2 * math.pi)
        ctx.set_source_rgba(*self.sk_rim, 0.95)
        ctx.fill()
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        ctx.restore()
        if self.earrings:
            for sd in (-1, 1):
                ctx.arc(cx + sd * R * 0.97, cy + R * 0.35, R * 0.06, 0, 2 * math.pi)
                ctx.set_source_rgb(*self.earrings)
                ctx.fill()
        ctx.new_path()
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw)
        ctx.stroke()
        fx = cx + look * R * 0.3
        self._glasses(ctx, fx, cy, R, lw, cx)
        draw_face(ctx, fx, cy, R, lw, expr, t, talk)
        self._glasses(ctx, fx, cy, R, lw, cx, frames_only=True)
        self._hair_front(ctx, cx, cy, R, lw, look)

    # hair: back part (behind head) and front part (over the head)
    def _hair_back(self, ctx, cx, cy, R, lw, look):
        if self.hair == "bob":
            ctx.new_path()
            ctx.move_to(cx - 1.15 * R, cy + 0.95 * R)
            ctx.curve_to(cx - 1.35 * R, cy - 1.45 * R, cx + 1.35 * R, cy - 1.45 * R, cx + 1.15 * R, cy + 0.95 * R)
            ctx.close_path()
            _fill_line(ctx, self.hair_col, lw * 0.9)

    def _hair_front(self, ctx, cx, cy, R, lw, look):
        h, col = self.hair, self.hair_col
        strand = mix(col, (0, 0, 0), 0.35)
        if h == "swept":
            # big side-swept cap: covers the top, spills past the outline on the far side
            sd = -1 if look >= 0 else 1
            ctx.new_path()
            ctx.move_to(cx + sd * 1.12 * R, cy + 0.1 * R)
            ctx.line_to(cx + sd * 1.0 * R, cy - 0.05 * R)
            ctx.line_to(cx + sd * 1.18 * R, cy - 0.2 * R)
            ctx.line_to(cx + sd * 1.0 * R, cy - 0.35 * R)
            ctx.curve_to(cx + sd * 1.1 * R, cy - 1.2 * R, cx - sd * 0.6 * R, cy - 1.35 * R,
                         cx - sd * 1.05 * R, cy - 0.55 * R)
            ctx.curve_to(cx - sd * 0.6 * R, cy - 0.5 * R, cx - sd * 0.2 * R, cy - 0.85 * R, cx + sd * 0.1 * R, cy - 0.62 * R)
            ctx.curve_to(cx + sd * 0.5 * R, cy - 0.45 * R, cx + sd * 0.75 * R, cy - 0.3 * R, cx + sd * 0.8 * R, cy + 0.1 * R)
            ctx.close_path()
            _fill_line(ctx, col, lw * 0.9)
            ctx.set_source_rgba(*strand, 0.75)
            ctx.set_line_width(lw * 0.35)
            for k in range(4):
                a0 = cx + sd * (0.75 - k * 0.38) * R
                ctx.move_to(a0, cy - 1.05 * R + k * 0.06 * R)
                ctx.curve_to(a0 - sd * 0.1 * R, cy - 0.9 * R, a0 - sd * 0.25 * R, cy - 0.8 * R, a0 - sd * 0.35 * R, cy - 0.72 * R)
                ctx.stroke()
        elif h in ("bob", "short", "bun"):
            ctx.new_path()
            ctx.move_to(cx - 1.08 * R, cy + (0.1 if h == "bob" else -0.25) * R)
            ctx.curve_to(cx - 1.15 * R, cy - 1.25 * R, cx + 1.15 * R, cy - 1.25 * R, cx + 1.08 * R, cy + (0.1 if h == "bob" else -0.25) * R)
            ctx.curve_to(cx + 0.9 * R, cy - 0.45 * R, cx + 0.5 * R, cy - 0.62 * R, cx + 0.1 * R, cy - 0.6 * R)
            ctx.curve_to(cx - 0.35 * R, cy - 0.58 * R, cx - 0.85 * R, cy - 0.45 * R, cx - 1.08 * R, cy + (0.1 if h == "bob" else -0.25) * R)
            ctx.close_path()
            _fill_line(ctx, col, lw * 0.9)
            if h == "bun":
                ctx.new_path()
                ctx.arc(cx + 0.15 * R, cy - 1.15 * R, 0.32 * R, 0, 2 * math.pi)
                _fill_line(ctx, col, lw * 0.9)
            ctx.set_source_rgba(*mix(col, (1, 1, 1), 0.25), 0.5)
            ctx.set_line_width(lw * 0.35)
            for k in range(3):
                a0 = cx - 0.5 * R + k * 0.35 * R
                ctx.move_to(a0, cy - 0.98 * R)
                ctx.curve_to(a0 + 0.08 * R, cy - 0.85 * R, a0 + 0.1 * R, cy - 0.75 * R, a0 + 0.06 * R, cy - 0.66 * R)
                ctx.stroke()
        elif h == "curly":
            for k in range(10):
                a = math.pi + 0.05 + k * (math.pi - 0.1) / 9
                ctx.new_path()
                ctx.arc(cx + math.cos(a) * 0.98 * R, cy + math.sin(a) * 0.98 * R, 0.24 * R, 0, 2 * math.pi)
                _fill_line(ctx, col, lw * 0.7)
        elif h == "bald":
            for sd in (-1, 1):
                ctx.new_path()
                ctx.move_to(cx + sd * 1.04 * R, cy + 0.15 * R)
                ctx.curve_to(cx + sd * 1.18 * R, cy - 0.2 * R, cx + sd * 1.12 * R, cy - 0.5 * R, cx + sd * 0.86 * R, cy - 0.62 * R)
                ctx.curve_to(cx + sd * 0.92 * R, cy - 0.3 * R, cx + sd * 0.9 * R, cy - 0.05 * R, cx + sd * 1.04 * R, cy + 0.15 * R)
                ctx.close_path()
                _fill_line(ctx, col, lw * 0.8)

    def _glasses(self, ctx, fx, cy, R, lw, cx, frames_only=False):
        g = self.glasses
        if not g:
            return
        ey = cy - 0.12 * R
        w = lw * 0.85
        ctx.set_line_width(w)
        ctx.set_source_rgb(*INK)
        if not frames_only:
            # temples run out to the head edge on both sides
            for sd in (-1, 1):
                ex = fx + sd * 0.33 * R + sd * 0.17 * R
                edge = cx + sd * math.sqrt(max(0, R * R - (ey - cy) ** 2)) * 1.02
                ctx.move_to(ex, ey - 0.03 * R)
                ctx.line_to(edge, ey - 0.06 * R)
                ctx.stroke()
            return
        for sd in (-1, 1):
            ex = fx + sd * 0.33 * R
            if g == "round":
                ctx.new_path()
                ctx.arc(ex, ey, 0.17 * R, 0, 2 * math.pi)
            else:
                _rrect(ctx, ex - 0.17 * R, ey - 0.11 * R, 0.34 * R, 0.22 * R, 0.04 * R)
            if g == "shades":
                ctx.set_source_rgb(0.03, 0.02, 0.02)
                ctx.fill_preserve()
                ctx.set_source_rgb(*INK)
            ctx.stroke()
            if g == "shades":
                ctx.set_source_rgba(1, 1, 1, 0.5)
                ctx.rectangle(ex - 0.11 * R, ey - 0.06 * R, 0.06 * R, 0.03 * R)
                ctx.fill()
                ctx.set_source_rgb(*INK)
        ctx.move_to(fx - 0.16 * R, ey - 0.03 * R)
        ctx.curve_to(fx - 0.05 * R, ey - 0.08 * R, fx + 0.05 * R, ey - 0.08 * R, fx + 0.16 * R, ey - 0.03 * R)
        ctx.stroke()


# ---------------------------------------------------------------------- helpers
def _curve(ctx, pts, w, col=INK):
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


def _fingers(ctx, hx, hy, ang, R, limb):
    for k in (-0.75, -0.25, 0.25, 0.75):
        a = ang + k * 0.9
        L = 0.2 * R * (1 - abs(k) * 0.25)
        _curve(ctx, [(hx, hy), (hx + math.cos(a) * L, hy + math.sin(a) * L)], limb * 0.85)


def _fill_line(ctx, col, w):
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


# ---------------------------------------------------------------------- face
EXPRESSIONS = ("neutral", "happy", "laugh", "smirk", "shock", "sad", "deadpan", "angry", "worried", "sly")


def draw_face(ctx, cx, cy, R, lw, expr, t, talk):
    w = lw * 0.9
    ey = cy - 0.12 * R
    ex = 0.33 * R
    my = cy + 0.38 * R

    def stroke():
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(w)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()

    def brow(sd, lift=0.0, tilt=0.0):
        x0, y0 = cx + sd * ex, ey - (0.33 + lift) * R
        ctx.new_path()
        ctx.move_to(x0 - 0.13 * R, y0 + 0.03 * R + sd * tilt * R)
        ctx.curve_to(x0 - 0.05 * R, y0 - 0.04 * R, x0 + 0.05 * R, y0 - 0.04 * R, x0 + 0.13 * R, y0 + 0.03 * R - sd * tilt * R)
        stroke()

    def dot(x0, y0, r=0.055):
        ctx.new_path()
        ctx.arc(x0, y0, r * R, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.fill()

    blink = (t % 3.9) < 0.08
    if expr in ("happy", "laugh"):
        for sd in (-1, 1):
            ctx.new_path()
            ctx.arc(cx + sd * ex, ey + 0.05 * R, 0.1 * R, math.pi * 1.12, math.pi * 1.88)
            stroke()
            # little crease lines at the outer corners (seen on laughs)
            if expr == "laugh":
                for k in (-1, 1):
                    ctx.new_path()
                    ctx.move_to(cx + sd * (ex + 0.2 * R), ey + k * 0.03 * R)
                    ctx.line_to(cx + sd * (ex + 0.28 * R), ey + k * 0.06 * R)
                    ctx.set_source_rgba(*INK, 0.35)
                    ctx.set_line_width(w * 0.5)
                    ctx.stroke()
            brow(sd, 0.04)
    elif expr == "shock":
        for sd in (-1, 1):
            ctx.new_path()
            ctx.arc(cx + sd * ex, ey, 0.11 * R, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill_preserve()
            stroke()
            dot(cx + sd * ex, ey, 0.04)
            brow(sd, 0.12)
    elif blink:
        for sd in (-1, 1):
            ctx.new_path()
            ctx.move_to(cx + sd * ex - 0.06 * R, ey)
            ctx.line_to(cx + sd * ex + 0.06 * R, ey)
            stroke()
    else:
        for sd in (-1, 1):
            dot(cx + sd * ex, ey)
        if expr in ("smirk", "sly"):
            brow(-1, 0.05, 0.05)
            brow(1, -0.03, -0.02)
        elif expr == "angry":
            brow(-1, -0.03, 0.08)
            brow(1, -0.03, 0.08)
        elif expr in ("sad", "worried"):
            brow(-1, 0.05, -0.07)
            brow(1, 0.05, -0.07)
        else:
            brow(-1)
            brow(1)

    if expr == "laugh" or (talk and expr in ("happy", "neutral", "smirk")):
        k = 1.0 if expr == "laugh" else 0.45 + 0.4 * abs(math.sin(t * 11))
        k *= 0.92 + 0.08 * math.sin(t * 17)
        mw, mh = 0.33 * R, 0.42 * R * k
        top = my - 0.05 * R
        ctx.new_path()
        ctx.move_to(cx - mw, top)
        ctx.curve_to(cx - mw * 0.95, top + mh * 1.25, cx + mw * 0.95, top + mh * 1.25, cx + mw, top)
        ctx.close_path()
        ctx.set_source_rgb(0x43 / 255, 0x0b / 255, 0x0b / 255)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        ctx.rectangle(cx - mw, top - 0.02 * R, 2 * mw, 0.13 * R)
        ctx.set_source_rgb(0xe8 / 255, 0xd8 / 255, 0xb4 / 255)
        ctx.fill()
        ctx.new_path()
        ctx.arc(cx + 0.02 * R, top + mh * 0.95, mw * 0.5, 0, 2 * math.pi)
        ctx.set_source_rgb(0xd3 / 255, 0x42 / 255, 0x38 / 255)
        ctx.fill()
        ctx.restore()
        ctx.new_path()
        ctx.move_to(cx - mw, top)
        ctx.curve_to(cx - mw * 0.95, top + mh * 1.25, cx + mw * 0.95, top + mh * 1.25, cx + mw, top)
        ctx.close_path()
        stroke()
    elif expr == "shock":
        ctx.new_path()
        ctx.save()
        ctx.translate(cx, my + 0.05 * R)
        ctx.scale(0.12 * R, 0.17 * R)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0x43 / 255, 0x0b / 255, 0x0b / 255)
        ctx.fill_preserve()
        stroke()
    else:
        ctx.new_path()
        if expr == "happy":
            ctx.move_to(cx - 0.17 * R, my - 0.02 * R)
            ctx.curve_to(cx - 0.07 * R, my + 0.09 * R, cx + 0.07 * R, my + 0.09 * R, cx + 0.17 * R, my - 0.02 * R)
        elif expr in ("smirk", "sly"):
            ctx.move_to(cx - 0.15 * R, my + 0.02 * R)
            ctx.curve_to(cx - 0.02 * R, my + 0.08 * R, cx + 0.1 * R, my + 0.04 * R, cx + 0.18 * R, my - 0.05 * R)
        elif expr in ("sad", "worried"):
            ctx.move_to(cx - 0.14 * R, my + 0.05 * R)
            ctx.curve_to(cx - 0.05 * R, my - 0.04 * R, cx + 0.05 * R, my - 0.04 * R, cx + 0.14 * R, my + 0.05 * R)
        elif expr == "angry":
            ctx.move_to(cx - 0.14 * R, my + 0.02 * R)
            ctx.line_to(cx + 0.14 * R, my - 0.02 * R)
        elif expr in ("deadpan", "neutral"):
            ctx.move_to(cx - 0.08 * R, my)
            ctx.line_to(cx + 0.08 * R, my)
        stroke()
    if expr in ("shock", "worried"):
        sx, sy = cx + 0.8 * R, cy - 0.45 * R + (t * 25 % 10) * 0.012 * R
        ctx.new_path()
        ctx.move_to(sx, sy - 0.15 * R)
        ctx.curve_to(sx + 0.1 * R, sy, sx + 0.08 * R, sy + 0.1 * R, sx, sy + 0.1 * R)
        ctx.curve_to(sx - 0.08 * R, sy + 0.1 * R, sx - 0.1 * R, sy, sx, sy - 0.15 * R)
        ctx.set_source_rgb(0.62, 0.86, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(w * 0.7)
        ctx.stroke()


# ---------------------------------------------------------------------- items
def draw_item(ctx, item, x, y, R, t):
    lw = 0.035 * R + 0.5
    if item == "wine":
        # held by the base (as in the reference): stem rises from the hand, bowl on top
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
        ctx.set_source_rgba(1, 1, 1, 0.65)
        ctx.set_line_width(lw * 1.4)
        ctx.move_to(-bw * 0.62, top + bh * 0.12)
        ctx.curve_to(-bw * 0.75, top + bh * 0.4, -bw * 0.7, top + bh * 0.6, -bw * 0.5, top + bh * 0.8)
        ctx.stroke()
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
        _rrect(ctx, -0.22 * R, -0.4 * R, 0.44 * R, 0.8 * R, 0.06 * R)
        ctx.set_source_rgb(0.1, 0.1, 0.12)
        ctx.fill()
        ctx.rectangle(-0.17 * R, -0.33 * R, 0.34 * R, 0.62 * R)
        ctx.set_source_rgb(0.55, 0.85, 1.0)
        ctx.fill()
        ctx.restore()
