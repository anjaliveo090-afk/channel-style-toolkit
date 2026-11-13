"""Flat 2D "drawn on paper" cartoon characters (style measured on the Paper Billions references,
see references/notes_v1_part1.md): big round head with a thick dark outline and a warm rim light,
dot eyes, no nose, a small egg-shaped torso in the clothing colour, thin black stick arms and legs.

Char.draw() keeps the same signature as reference_examples/animator/style2.py Char2.draw, so story
templates work unchanged. (x, y) is the point between the feet; s=1 gives a head radius of 40 px.
"""
import math

import cairo

INK = (0.13, 0.10, 0.09)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


def _clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def _ease(x):
    x = _clamp(x)
    return x * x * (3 - 2 * x)


class Char:
    """hair: 'bald' (side tufts), 'short', 'bun', 'bob', 'spiky', 'curly', 'none'.
    glasses: None, 'round', 'rect', 'shades'. body: clothing colour. collar: None, 'shirt', 'lapel'."""

    def __init__(self, body="#5b7a5a", hair="short", hair_col="#2b2422", skin="#f2c79a",
                 glasses=None, collar="shirt", tie=None, earrings=None, light=(-0.6, -0.8)):
        self.body = hexc(body)
        self.hair = hair
        self.hair_col = hexc(hair_col)
        self.skin = hexc(skin)
        self.glasses = glasses
        self.collar = collar
        self.tie = hexc(tie) if tie else None
        self.earrings = hexc(earrings) if earrings else None
        self.light = light          # direction the key light comes FROM (x, y), normalised-ish

    # ------------------------------------------------------------------ public
    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False, arms="down", pose="stand",
             look=0.0, bob=0.0, item=None, item_hand="r", walk_phase=None, lean=0.0, shadow=True):
        R = 40 * s
        lw = max(1.6, 0.075 * R)          # head outline
        limb = max(1.2, 0.055 * R)        # stick limbs
        sway = math.sin(t * 2.1) * 0.012 * R + bob * R
        legs_h = 0.0 if pose == "sit" else 1.25 * R
        torso_h, torso_w = 2.05 * R, 1.6 * R
        hip_y = y - legs_h
        # torso is an egg from hip_y up; head sits on top, overlapping the shoulders a little
        top_y = hip_y - torso_h
        head_cy = top_y - 0.62 * R + sway
        hx = x + lean * R * 0.6

        if shadow and pose != "sit":
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(1, 0.22)
            g = cairo.RadialGradient(0, 0, 0, 0, 0, 1.3 * R)
            g.add_color_stop_rgba(0, 0, 0, 0, 0.28)
            g.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.set_source(g)
            ctx.arc(0, 0, 1.3 * R, 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()

        # legs
        if pose != "sit":
            ph = walk_phase if walk_phase is not None else None
            for side in (-1, 1):
                fx = x + side * 0.28 * R
                kx = fx
                if ph is not None:
                    sw = math.sin(ph + (0 if side < 0 else math.pi)) * 0.35 * R
                    fx += sw
                    kx += sw * 0.5
                self._line(ctx, [(x + side * 0.28 * R, hip_y - 0.15 * R), (kx, y - 0.6 * R), (fx, y)], limb)
                self._line(ctx, [(fx, y), (fx + side * 0.22 * R, y)], limb)

        # arms behind torso are drawn after the torso (stick arms sit on top in the references)
        self._torso(ctx, hx, hip_y, torso_w, torso_h, lw)

        hands = self._arms(ctx, hx, top_y, torso_w, R, limb, arms, t)
        if item:
            hxp, hyp = hands["r" if item_hand == "r" else "l"]
            draw_item(ctx, item, hxp, hyp, R, t)
            # fingers over the item
            self._fingers(ctx, hxp, hyp, R, limb, 1 if item_hand == "r" else -1)

        self._head(ctx, hx, head_cy, R, lw, expr, t, talk, look)
        return {"head": (hx, head_cy, R), "hands": hands}

    # ----------------------------------------------------------------- pieces
    def _line(self, ctx, pts, w, col=INK):
        ctx.set_source_rgb(*col)
        ctx.set_line_width(w)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.move_to(*pts[0])
        if len(pts) == 3:
            ctx.curve_to(pts[1][0], pts[1][1], pts[1][0], pts[1][1], pts[2][0], pts[2][1])
        else:
            for p in pts[1:]:
                ctx.line_to(*p)
        ctx.stroke()

    def _torso(self, ctx, x, hip_y, w, h, lw):
        top = hip_y - h
        ctx.new_path()
        ctx.move_to(x - w * 0.5, hip_y)
        ctx.curve_to(x - w * 0.62, hip_y - h * 0.55, x - w * 0.42, top, x, top)
        ctx.curve_to(x + w * 0.42, top, x + w * 0.62, hip_y - h * 0.55, x + w * 0.5, hip_y)
        ctx.curve_to(x + w * 0.2, hip_y + h * 0.06, x - w * 0.2, hip_y + h * 0.06, x - w * 0.5, hip_y)
        ctx.close_path()
        g = cairo.LinearGradient(x + self.light[0] * w * 0.5, top, x - self.light[0] * w * 0.5, hip_y)
        g.add_color_stop_rgb(0, *mix(self.body, (1, 0.95, 0.85), 0.12))
        g.add_color_stop_rgb(1, *mix(self.body, (0, 0, 0), 0.22))
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw * 0.55)
        ctx.stroke()
        # collar
        if self.collar == "shirt":
            ctx.move_to(x - w * 0.22, top + h * 0.06)
            ctx.line_to(x, top + h * 0.2)
            ctx.line_to(x + w * 0.22, top + h * 0.06)
            ctx.set_source_rgb(0.96, 0.94, 0.9)
            ctx.set_line_width(lw * 0.9)
            ctx.stroke()
        elif self.collar == "lapel":
            ctx.set_source_rgb(*mix(self.body, (0, 0, 0), 0.35))
            ctx.set_line_width(lw * 0.45)
            for sd in (-1, 1):
                ctx.move_to(x + sd * w * 0.18, top + h * 0.04)
                ctx.line_to(x + sd * w * 0.05, top + h * 0.42)
                ctx.stroke()
            ctx.set_source_rgb(0.96, 0.94, 0.9)
            ctx.move_to(x - w * 0.12, top + h * 0.03)
            ctx.line_to(x, top + h * 0.18)
            ctx.line_to(x + w * 0.12, top + h * 0.03)
            ctx.close_path()
            ctx.fill()
        if self.tie:
            ctx.set_source_rgb(*self.tie)
            ctx.move_to(x, top + h * 0.16)
            ctx.line_to(x - w * 0.05, top + h * 0.45)
            ctx.line_to(x, top + h * 0.52)
            ctx.line_to(x + w * 0.05, top + h * 0.45)
            ctx.close_path()
            ctx.fill()

    def _arms(self, ctx, x, top_y, w, R, limb, arms, t):
        amount = 1.0
        if isinstance(arms, tuple):
            arms, amount = arms
        sh_y = top_y + 0.35 * R
        hands = {}
        for side, key in ((-1, "l"), (1, "r")):
            sx = x + side * w * 0.42
            down = (x + side * w * 0.62, sh_y + 1.45 * R)
            pose = down
            if arms == "hold":                       # both hands forward at the table
                pose = (x + side * w * 0.38, sh_y + 1.05 * R)
            elif arms in ("raise_r", "toast") and key == "r":
                pose = (x + w * 0.95, sh_y - 0.55 * R)
            elif arms == "raise_l" and key == "l":
                pose = (x - w * 0.95, sh_y - 0.55 * R)
            elif arms == "point_r" and key == "r":
                pose = (x + w * 1.35, sh_y + 0.1 * R)
            elif arms == "shrug":
                pose = (x + side * w * 1.0, sh_y - 0.1 * R)
            elif arms == "chin" and key == "r":
                pose = (x + w * 0.15, sh_y - 0.5 * R)
            hxp = down[0] + (pose[0] - down[0]) * amount
            hyp = down[1] + (pose[1] - down[1]) * amount
            mid = ((sx + hxp) / 2 + side * 0.18 * R, (sh_y + hyp) / 2 + 0.1 * R)
            self._line(ctx, [(sx, sh_y), mid, (hxp, hyp)], limb)
            hands[key] = (hxp, hyp)
            self._fingers(ctx, hxp, hyp, R, limb, side)
        return hands

    def _fingers(self, ctx, hx, hy, R, limb, side):
        for k in (-0.7, 0.0, 0.7):
            a = -math.pi / 2 + side * (0.9 + k * 0.5)
            self._line(ctx, [(hx, hy), (hx + math.cos(a) * 0.16 * R, hy - math.sin(a) * 0.16 * R)], limb * 0.75)

    def _head(self, ctx, cx, cy, R, lw, expr, t, talk, look):
        lx, ly = self.light
        # skin with soft directional shading
        g = cairo.RadialGradient(cx + lx * R * 0.35, cy + ly * R * 0.35, R * 0.1, cx, cy, R * 1.05)
        g.add_color_stop_rgb(0, *mix(self.skin, (1, 0.97, 0.88), 0.25))
        g.add_color_stop_rgb(0.75, *self.skin)
        g.add_color_stop_rgb(1, *mix(self.skin, (0.45, 0.2, 0.12), 0.35))
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        # warm rim light arc just inside the outline on the lit side
        ang = math.atan2(ly, lx)
        ctx.set_line_width(R * 0.07)
        ctx.set_source_rgba(1, 0.93, 0.7, 0.75)
        ctx.arc(cx, cy, R - R * 0.07, ang - 0.9, ang + 0.9)
        ctx.stroke()
        if self.earrings:
            for sd in (-1, 1):
                ctx.arc(cx + sd * R * 0.98, cy + R * 0.32, R * 0.07, 0, 2 * math.pi)
                ctx.set_source_rgb(*self.earrings)
                ctx.fill()
        self._hair(ctx, cx, cy, R, lw, back=True)
        # outline
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw)
        ctx.stroke()
        self._hair(ctx, cx, cy, R, lw, back=False)
        draw_face(ctx, cx + look * R * 0.25, cy, R, lw, expr, t, talk)
        self._glasses(ctx, cx + look * R * 0.25, cy, R, lw, expr)

    def _hair(self, ctx, cx, cy, R, lw, back):
        col, h = self.hair_col, self.hair
        dark = mix(col, (0, 0, 0), 0.3)
        if back:
            if h == "bob":
                ctx.new_path()
                ctx.move_to(cx - R * 1.12, cy + R * 0.75)
                ctx.curve_to(cx - R * 1.3, cy - R * 1.2, cx + R * 1.3, cy - R * 1.2, cx + R * 1.12, cy + R * 0.75)
                ctx.line_to(cx + R * 0.7, cy + R * 0.75)
                ctx.line_to(cx - R * 0.7, cy + R * 0.75)
                ctx.close_path()
                ctx.set_source_rgb(*col)
                ctx.fill_preserve()
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(lw * 0.7)
                ctx.stroke()
            return
        ctx.set_line_width(lw * 0.7)
        if h in ("short", "bob", "bun", "spiky", "curly"):
            # cap over the top of the head, cut by a fringe line
            ctx.save()
            ctx.arc(cx, cy, R + lw * 0.5, 0, 2 * math.pi)
            ctx.clip()
            ctx.new_path()
            fr = 0.05 if h != "bob" else -0.05
            ctx.move_to(cx - R * 1.2, cy - R * fr)
            ctx.curve_to(cx - R * 0.6, cy - R * 0.75, cx + R * 0.1, cy - R * 0.25, cx + R * 0.45, cy - R * 0.62)
            ctx.curve_to(cx + R * 0.8, cy - R * 0.4, cx + R * 1.0, cy - R * 0.2, cx + R * 1.2, cy + R * 0.0)
            ctx.line_to(cx + R * 1.2, cy - R * 1.3)
            ctx.line_to(cx - R * 1.2, cy - R * 1.3)
            ctx.close_path()
            ctx.set_source_rgb(*col)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.stroke()          # stroked inside the head clip: only the fringe line shows
            ctx.restore()
            # strands
            ctx.set_source_rgba(*dark, 0.8)
            ctx.set_line_width(lw * 0.35)
            for k in range(4):
                a = -2.4 + k * 0.35
                ctx.move_to(cx + math.cos(a) * R * 0.95, cy + math.sin(a) * R * 0.95)
                ctx.line_to(cx + math.cos(a + 0.5) * R * 0.55, cy + math.sin(a + 0.5) * R * 0.62)
                ctx.stroke()
            if h == "bun":
                ctx.arc(cx + R * 0.1, cy - R * 1.12, R * 0.3, 0, 2 * math.pi)
                ctx.set_source_rgb(*col)
                ctx.fill_preserve()
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(lw * 0.7)
                ctx.stroke()
            if h == "spiky":
                for k in range(5):
                    a = -2.6 + k * 0.3
                    ctx.move_to(cx + math.cos(a) * R * 0.98, cy + math.sin(a) * R * 0.98)
                    ctx.line_to(cx + math.cos(a + 0.12) * R * 1.22, cy + math.sin(a + 0.12) * R * 1.22)
                    ctx.line_to(cx + math.cos(a + 0.26) * R * 0.98, cy + math.sin(a + 0.26) * R * 0.98)
                ctx.set_source_rgb(*col)
                ctx.fill()
            if h == "curly":
                for k in range(9):
                    a = -2.9 + k * 0.36
                    ctx.arc(cx + math.cos(a) * R * 0.98, cy + math.sin(a) * R * 0.98, R * 0.2, 0, 2 * math.pi)
                    ctx.set_source_rgb(*col)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(*INK)
                    ctx.set_line_width(lw * 0.5)
                    ctx.stroke()
        elif h == "bald":
            for sd in (-1, 1):
                ctx.new_path()
                a0 = math.pi + 0.15 if sd < 0 else -0.15
                ctx.arc(cx, cy, R, *(sorted((a0, a0 - sd * 0.75))))
                ctx.set_line_width(R * 0.16)
                ctx.set_source_rgb(*col)
                ctx.stroke()
            ctx.set_line_width(lw * 0.35)
            ctx.set_source_rgba(*mix(self.skin, (0.5, 0.25, 0.1), 0.4), 0.7)
            ctx.arc(cx - R * 0.25, cy - R * 0.62, R * 0.12, math.pi, 1.9 * math.pi)
            ctx.stroke()

    def _glasses(self, ctx, cx, cy, R, lw, expr):
        g = self.glasses
        if not g:
            return
        ey = cy - R * 0.05
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw * 0.42)
        for sd in (-1, 1):
            ex = cx + sd * R * 0.36
            if g == "round":
                ctx.arc(ex, ey, R * 0.22, 0, 2 * math.pi)
            else:
                ctx.rectangle(ex - R * 0.25, ey - R * 0.14, R * 0.5, R * 0.28)
            if g == "shades":
                ctx.fill()
            else:
                ctx.stroke()
            # temple line to the edge of the head
            ctx.move_to(ex + sd * R * 0.25, ey - R * 0.05)
            ctx.line_to(cx + sd * R * 0.97, ey - R * 0.1)
            ctx.stroke()
        ctx.move_to(cx - R * 0.12, ey - R * 0.04)
        ctx.line_to(cx + R * 0.12, ey - R * 0.04)
        ctx.stroke()
        if g == "shades":
            ctx.set_source_rgba(1, 1, 1, 0.35)
            for sd in (-1, 1):
                ctx.rectangle(cx + sd * R * 0.36 - R * 0.16, ey - R * 0.09, R * 0.1, R * 0.05)
                ctx.fill()


# ---------------------------------------------------------------------- face
EXPRESSIONS = ("neutral", "happy", "laugh", "smirk", "shock", "sad", "deadpan", "angry", "worried", "sly")


def draw_face(ctx, cx, cy, R, lw, expr, t, talk):
    ink = INK
    ctx.set_source_rgb(*ink)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ey = cy - R * 0.05
    ex = R * 0.36
    thin = max(1.2, lw * 0.42)

    def dot(x, y, r=0.065):
        ctx.arc(x, y, R * r, 0, 2 * math.pi)
        ctx.set_source_rgb(*ink)
        ctx.fill()

    def arc_line(x, y, rx, a0, a1, w=thin):
        ctx.new_path()
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(rx, rx * 0.8)
        ctx.arc(0, 0, 1, a0, a1)
        ctx.restore()
        ctx.set_line_width(w)
        ctx.set_source_rgb(*ink)
        ctx.stroke()

    def brow(sd, lift=0.0, tilt=0.0):
        x = cx + sd * ex
        y = ey - R * (0.3 + lift)
        ctx.move_to(x - R * 0.13, y + sd * tilt * R)
        ctx.curve_to(x - R * 0.05, y - R * 0.06, x + R * 0.05, y - R * 0.06, x + R * 0.13, y - sd * tilt * R)
        ctx.set_line_width(thin)
        ctx.set_source_rgb(*ink)
        ctx.stroke()

    blink = (t % 3.7) < 0.09
    my = cy + R * 0.45
    if expr in ("happy", "laugh"):
        for sd in (-1, 1):
            arc_line(cx + sd * ex, ey + R * 0.04, R * 0.12, math.pi * 1.1, math.pi * 1.9)
            brow(sd, 0.05)
    elif expr == "shock":
        for sd in (-1, 1):
            ctx.arc(cx + sd * ex, ey, R * 0.12, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill_preserve()
            ctx.set_source_rgb(*ink)
            ctx.set_line_width(thin)
            ctx.stroke()
            dot(cx + sd * ex, ey, 0.045)
            brow(sd, 0.12)
    elif blink:
        for sd in (-1, 1):
            ctx.move_to(cx + sd * ex - R * 0.07, ey)
            ctx.line_to(cx + sd * ex + R * 0.07, ey)
            ctx.set_line_width(thin)
            ctx.stroke()
    else:
        for sd in (-1, 1):
            dot(cx + sd * ex, ey)
        if expr in ("smirk", "sly"):
            brow(-1, 0.06, 0.04)
            brow(1, -0.02, -0.03)
            # half lids
            for sd in (-1, 1):
                ctx.move_to(cx + sd * ex - R * 0.1, ey - R * 0.04)
                ctx.line_to(cx + sd * ex + R * 0.1, ey - R * 0.04)
                ctx.set_line_width(thin)
                ctx.stroke()
        elif expr == "angry":
            brow(-1, -0.02, 0.07)
            brow(1, -0.02, 0.07)
        elif expr in ("sad", "worried"):
            brow(-1, 0.04, -0.06)
            brow(1, 0.04, -0.06)
        else:
            brow(-1)
            brow(1)

    # mouth
    open_k = 0.0
    if talk:
        open_k = 0.5 + 0.5 * math.sin(t * 22)
    if expr == "laugh" or (expr == "happy" and talk):
        k = 0.85 + 0.15 * math.sin(t * 18)
        w, h = R * 0.42, R * 0.34 * k
        ctx.new_path()
        ctx.move_to(cx - w, my - R * 0.08)
        ctx.curve_to(cx - w * 0.9, my + h * 1.4, cx + w * 0.9, my + h * 1.4, cx + w, my - R * 0.08)
        ctx.close_path()
        ctx.set_source_rgb(0.35, 0.08, 0.08)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        ctx.rectangle(cx - w, my - R * 0.1, 2 * w, R * 0.11)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        ctx.arc(cx, my + h * 1.15, w * 0.55, 0, 2 * math.pi)
        ctx.set_source_rgb(0.93, 0.45, 0.45)
        ctx.fill()
        ctx.restore()
        ctx.new_path()
        ctx.move_to(cx - w, my - R * 0.08)
        ctx.curve_to(cx - w * 0.9, my + h * 1.4, cx + w * 0.9, my + h * 1.4, cx + w, my - R * 0.08)
        ctx.close_path()
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(thin)
        ctx.stroke()
    elif expr == "shock":
        ctx.save()
        ctx.translate(cx, my + R * 0.05)
        ctx.scale(R * 0.14, R * 0.2)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.35, 0.08, 0.08)
        ctx.fill_preserve()
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(thin)
        ctx.stroke()
    elif talk and open_k > 0.2:
        ctx.save()
        ctx.translate(cx, my)
        ctx.scale(R * 0.16, R * 0.11 * open_k)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.35, 0.08, 0.08)
        ctx.fill()
    else:
        ctx.new_path()
        if expr == "happy":
            ctx.move_to(cx - R * 0.2, my - R * 0.03)
            ctx.curve_to(cx - R * 0.08, my + R * 0.1, cx + R * 0.08, my + R * 0.1, cx + R * 0.2, my - R * 0.03)
        elif expr in ("smirk", "sly"):
            ctx.move_to(cx - R * 0.16, my + R * 0.03)
            ctx.curve_to(cx, my + R * 0.06, cx + R * 0.12, my + R * 0.03, cx + R * 0.2, my - R * 0.06)
        elif expr in ("sad", "worried"):
            ctx.move_to(cx - R * 0.16, my + R * 0.05)
            ctx.curve_to(cx - R * 0.05, my - R * 0.04, cx + R * 0.05, my - R * 0.04, cx + R * 0.16, my + R * 0.05)
        elif expr == "angry":
            ctx.move_to(cx - R * 0.16, my + R * 0.02)
            ctx.line_to(cx + R * 0.16, my - R * 0.02)
        elif expr == "deadpan":
            ctx.move_to(cx - R * 0.12, my)
            ctx.line_to(cx + R * 0.12, my)
        else:
            ctx.move_to(cx - R * 0.13, my)
            ctx.curve_to(cx - R * 0.05, my + R * 0.05, cx + R * 0.05, my + R * 0.05, cx + R * 0.13, my)
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(thin)
        ctx.stroke()
    if expr in ("shock", "worried"):
        # sweat drop
        sx, sy = cx + R * 0.82, cy - R * 0.35 + (t * 30 % 12) * R * 0.01
        ctx.new_path()
        ctx.move_to(sx, sy - R * 0.16)
        ctx.curve_to(sx + R * 0.1, sy, sx + R * 0.08, sy + R * 0.1, sx, sy + R * 0.1)
        ctx.curve_to(sx - R * 0.08, sy + R * 0.1, sx - R * 0.1, sy, sx, sy - R * 0.16)
        ctx.set_source_rgb(0.62, 0.85, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(thin * 0.8)
        ctx.stroke()


# ---------------------------------------------------------------------- items
def draw_item(ctx, item, x, y, R, t):
    if item == "wine":
        ctx.save()
        ctx.translate(x, y)
        bw, bh = R * 0.32, R * 0.42
        ctx.move_to(-bw, -bh * 1.5)
        ctx.curve_to(-bw, -bh * 0.2, bw, -bh * 0.2, bw, -bh * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(max(1, R * 0.03))
        ctx.stroke()
        ctx.move_to(-bw * 0.92, -bh * 1.0)
        ctx.curve_to(-bw * 0.85, -bh * 0.25, bw * 0.85, -bh * 0.25, bw * 0.92, -bh * 1.0)
        ctx.close_path()
        ctx.set_source_rgb(0.62, 0.08, 0.12)
        ctx.fill()
        ctx.move_to(0, -bh * 0.55)
        ctx.line_to(0, bh * 0.25)
        ctx.move_to(-bw * 0.6, bh * 0.25)
        ctx.line_to(bw * 0.6, bh * 0.25)
        ctx.set_source_rgb(*INK)
        ctx.stroke()
        ctx.restore()
    elif item == "phone":
        ctx.save()
        ctx.translate(x, y - R * 0.3)
        ctx.rectangle(-R * 0.22, -R * 0.38, R * 0.44, R * 0.76)
        ctx.set_source_rgb(0.12, 0.12, 0.14)
        ctx.fill()
        ctx.rectangle(-R * 0.17, -R * 0.31, R * 0.34, R * 0.6)
        ctx.set_source_rgb(0.55, 0.85, 1.0)
        ctx.fill()
        ctx.restore()
