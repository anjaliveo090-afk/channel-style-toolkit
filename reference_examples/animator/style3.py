"""Character style v3 ("medieval kingdoms" reference frames): big cream-white
egg heads with dark outlines, small dot eyes, thick expressive brows, clean
moustaches and beards, narrow capsule bodies (robes, tunics, aprons), thin
dark stick limbs with ball hands, crowns, capes, helmets. Sizes are in units
of the head radius r (r = 64 * s px); (x, y) is the point between the feet."""
import math

import cairo

import engine
from engine import PI, ellipse, hexc, rrect, src

OUT = hexc("#3a2a2c")
HEAD = hexc("#fcf6ef")
HEAD_SHADE = hexc("#d6cfd3")


def lighter(c, k=0.18):
    return tuple(min(1, v + (1 - v) * k) for v in c)


def darker(c, k=0.18):
    return tuple(v * (1 - k) for v in c)


def shade(ctx, top, bottom, y0, y1, lw):
    """Soft painted light like the reference: lit upper-left, shaded lower-right."""
    span = max(1.0, abs(y1 - y0))
    g = cairo.LinearGradient(-0.45 * span, y0, 0.45 * span, y1)
    mid = tuple((a + b) / 2 for a, b in zip(top, bottom))
    g.add_color_stop_rgb(0, *lighter(top, 0.08))
    g.add_color_stop_rgb(0.45, *mid)
    g.add_color_stop_rgb(1, *darker(bottom, 0.12))
    ctx.set_source(g)
    ctx.fill_preserve()
    if lw:
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(lw)
        ctx.stroke()
    else:
        ctx.new_path()


class Char3:
    """Measured on the reference close-ups: head is a wide, slightly flat oval
    (width ~1.25x height); head : body : legs = 1 : 1.1 : 1.5; body is a bean about
    0.63x the head width with a small belly; long thin legs show under robes; capes
    hang separately to the floor."""

    def __init__(self, body, outfit="robe", cape=None, crown=None, beard=None, mustache=None,
                 helmet=False, hat=None, apron=None, belt=None, under=None, legs=1.7, torso=1.75):
        self.body = hexc(body)
        self.outfit = outfit          # robe | tunic
        self.cape = hexc(cape) if cape else None
        self.crown = crown            # "gold" | "silver" | None
        self.beard = beard            # "goatee" (small dark) | "bib" (wide white) | "long" (white) | None
        self.mustache = mustache      # "handlebar" | "thin" | None
        self.helmet = helmet
        self.hat = hat
        self.apron = hexc(apron) if apron else None
        self.belt = hexc(belt) if belt else None
        self.under = hexc(under) if under else None
        # leg and body length in head half-widths; kings are tall (reference: total height
        # = 3.65 x head width), the old man and the smith are shorter
        self.legs, self.torso = legs, torso

    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, arms=("down", "down"), pose="stand",
             look=0.0, bob=1.0, walk_phase=0.0, lean=0.0, item=None, item_hand=1, sweat=False,
             shake=0.0, shadow=True):
        r = 64 * s                     # head half-width
        e = engine.ENERGY * bob
        lw = 0.05 * r
        limb = 0.11 * r               # reference: limbs ~5.5% of the head width
        ctx.save()
        ctx.translate(x + (math.sin(t * 60) * 0.03 * r * shake), y)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        if shadow:
            g = cairo.RadialGradient(0, 0, 0, 0, 0, r)
            g.add_color_stop_rgba(0, 0.15, 0.1, 0.15, 0.35)
            g.add_color_stop_rgba(1, 0.15, 0.1, 0.15, 0)
            ctx.save()
            ctx.scale(1, 0.2)
            ctx.set_source(g)
            ctx.arc(0, 0, r, 0, 2 * PI)
            ctx.fill()
            ctx.restore()
        ctx.push_group()
        bounce = -abs(math.sin(t * 2 * PI * 1.8)) * 0.04 * r * e
        hem = -self.legs * r + bounce
        shoulder = hem - self.torso * r
        # cape hangs behind and flows out to one side (left), legs stay visible in front
        if self.cape:
            ctx.move_to(-0.45 * r, shoulder + 0.05 * r)
            ctx.curve_to(-0.95 * r, shoulder * 0.7, -1.35 * r, shoulder * 0.26, -1.25 * r, -0.06 * r)
            ctx.curve_to(-0.9 * r, 0.02 * r, -0.4 * r, -0.02 * r, -0.05 * r, -0.12 * r)
            ctx.curve_to(0.3 * r, shoulder * 0.17, 0.6 * r, shoulder * 0.46, 0.5 * r, shoulder + 0.1 * r)
            ctx.close_path()
            shade(ctx, lighter(self.cape, 0.08), darker(self.cape, 0.12), shoulder, 0, lw)
        # long thin legs + small feet
        for side in (-1, 1):
            hx = side * 0.17 * r
            if pose == "walk":
                sw = math.sin(walk_phase * 2 * PI + (0 if side < 0 else PI))
                fx, fy = hx + sw * 0.35 * r, -max(0, sw) * 0.12 * r
            else:
                fx, fy = hx * 1.15, 0
            ctx.move_to(hx, hem)
            ctx.line_to(fx, fy - 0.05 * r)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(limb)
            ctx.stroke()
            ellipse(ctx, fx + side * 0.08 * r, fy - 0.06 * r, 0.19 * r, 0.09 * r)
            src(ctx, OUT)
            ctx.fill()
        ctx.save()
        ctx.translate(0, hem)
        ctx.rotate(lean + math.sin(t * 2.5) * 0.02 * e)
        ctx.translate(0, -hem)
        # bean body with a small belly on the left
        w = 0.7 * r
        ctx.move_to(-w * 0.8, hem)
        ctx.curve_to(-w * 1.25, hem - 0.5 * r, -w * 1.2, shoulder + 0.9 * r, -w * 0.85, shoulder + 0.35 * r)
        ctx.curve_to(-w * 0.7, shoulder, w * 0.7, shoulder, w * 0.85, shoulder + 0.35 * r)
        ctx.curve_to(w * 1.05, shoulder + 0.9 * r, w * 1.05, hem - 0.4 * r, w * 0.85, hem)
        ctx.curve_to(w * 0.4, hem + 0.07 * r, -w * 0.4, hem + 0.07 * r, -w * 0.8, hem)
        ctx.close_path()
        shade(ctx, lighter(self.body, 0.1), darker(self.body, 0.1), shoulder, hem, lw)
        if self.apron:  # big apron from the chest to below the hem
            ctx.move_to(-w * 0.82, shoulder + 0.32 * r)
            ctx.line_to(w * 0.82, shoulder + 0.32 * r)
            ctx.curve_to(w * 1.08, hem - 0.6 * r, w * 1.0, hem + 0.1 * r, w * 0.85, hem + 0.12 * r)
            ctx.line_to(-w * 0.85, hem + 0.12 * r)
            ctx.curve_to(-w * 1.0, hem + 0.1 * r, -w * 1.15, hem - 0.6 * r, -w * 0.82, shoulder + 0.32 * r)
            ctx.close_path()
            shade(ctx, lighter(self.apron, 0.1), darker(self.apron, 0.12), shoulder, hem, lw)
            for side in (-1, 1):  # pockets
                rrect(ctx, side * 0.27 * r - 0.13 * r, hem - 0.72 * r, 0.26 * r, 0.24 * r, 0.03 * r)
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(lw * 0.7)
                ctx.stroke()
        if self.belt:
            ctx.rectangle(-w, shoulder + 1.1 * r, 2 * w, 0.14 * r)
            shade(ctx, self.belt, darker(self.belt, 0.2), 0, 1, lw * 0.6)
        # head: wide, slightly flat oval sitting on the body
        hcx = look * 0.04 * r
        hcy = shoulder - 0.62 * r + math.sin(t * 4.1) * 0.015 * r * e
        hands = []
        for i, side in enumerate((-1, 1)):
            sx, sy = side * 0.5 * r, shoulder + 0.35 * r
            tbl = {
                "down": (sx + side * 0.15 * r, hem + 0.25 * r),
                "belly": (-0.1 * r, shoulder + 1.15 * r),
                "up": (sx + side * 0.4 * r, shoulder - 1.4 * r),
                "point": (sx + side * 1.6 * r, shoulder + 0.25 * r),
                "hold": (side * 0.2 * r, shoulder + 1.2 * r),
                "show": (sx + side * 1.0 * r, shoulder - 0.4 * r),
                "hip": (sx + side * 0.42 * r, shoulder + 1.1 * r),
                "hammer": (sx + side * 0.8 * r, shoulder - 0.8 * r + abs(math.sin(t * 9)) * 1.3 * r),
                "spear": (sx + side * 0.45 * r, shoulder + 0.85 * r),
                "stick": (sx + side * 0.55 * r, shoulder + 1.45 * r),
                "shrug": (sx + side * 0.85 * r, shoulder - 0.1 * r),
                "bags": (sx + side * 0.25 * r, hem - 0.1 * r),
            }
            hx, hy = tbl.get(arms[i], tbl["down"])
            if arms[i] not in ("hammer",):
                hx += math.sin(t * 3.6 + side) * 0.03 * r * e
                hy += math.cos(t * 3.0 + side) * 0.03 * r * e
            hands.append((side, sx, sy, hx, hy, arms[i]))
        self._head(ctx, hcx, hcy, r, lw, expr, t, look, sweat)
        for i, (side, sx, sy, hx, hy, a) in enumerate(hands):
            mx, my = (sx + hx) / 2, (sy + hy) / 2
            ctx.move_to(sx, sy)
            ctx.curve_to(mx + side * 0.12 * r, my, mx + side * 0.12 * r, my, hx, hy)
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(limb)
            ctx.stroke()
            if item and i == item_hand:
                draw_item3(ctx, item, hx, hy, r, t)
            if a == "bags":
                draw_item3(ctx, "moneybag", hx, hy, r, t)
            ctx.new_sub_path()
            ctx.arc(hx, hy, 0.105 * r, 0, 2 * PI)
            src(ctx, OUT)
            ctx.fill()
        ctx.restore()
        pat = ctx.pop_group()
        rim = max(1.2, 0.035 * r)  # light rim only on the lit (left) side, like the reference
        for deg in (150, 165, 180, 195, 210):
            a = math.radians(deg)
            ctx.save()
            ctx.translate(math.cos(a) * rim, math.sin(a) * rim)
            ctx.set_source_rgba(1, 0.99, 0.96, 0.85)
            ctx.mask(pat)
            ctx.restore()
        ctx.set_source(pat)
        ctx.paint()
        ctx.restore()

    def _head(self, ctx, cx, cy, r, lw, expr, t, look, sweat):
        ry = 0.8 * r
        ctx.move_to(cx - r, cy + 0.05 * ry)
        ctx.curve_to(cx - r, cy - 1.1 * ry, cx + r, cy - 1.1 * ry, cx + r, cy + 0.05 * ry)
        ctx.curve_to(cx + r, cy + 0.85 * ry, cx + 0.55 * r, cy + 1.0 * ry, cx, cy + 1.0 * ry)
        ctx.curve_to(cx - 0.55 * r, cy + 1.0 * ry, cx - r, cy + 0.85 * ry, cx - r, cy + 0.05 * ry)
        ctx.close_path()
        g = cairo.RadialGradient(cx - 0.3 * r, cy - 0.35 * r, 0.15 * r, cx + 0.1 * r, cy + 0.1 * r, 1.12 * r)
        g.add_color_stop_rgb(0, *HEAD)
        g.add_color_stop_rgb(0.72, *HEAD)
        g.add_color_stop_rgb(1, *HEAD_SHADE)
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(lw * 1.15)
        ctx.stroke()
        if self.beard == "bib":   # wide white beard with strands (teal king)
            ctx.move_to(cx - 0.5 * r, cy + 0.42 * ry)
            ctx.curve_to(cx - 0.5 * r, cy + 1.25 * ry, cx - 0.2 * r, cy + 1.4 * ry, cx, cy + 1.42 * ry)
            ctx.curve_to(cx + 0.2 * r, cy + 1.4 * ry, cx + 0.5 * r, cy + 1.25 * ry, cx + 0.5 * r, cy + 0.42 * ry)
            ctx.curve_to(cx + 0.3 * r, cy + 0.62 * ry, cx - 0.3 * r, cy + 0.62 * ry, cx - 0.5 * r, cy + 0.42 * ry)
            ctx.close_path()
            shade(ctx, hexc("#f7f4ef"), hexc("#dcd6cf"), cy, cy + 1.4 * ry, lw)
            for k in range(-2, 3):
                ctx.move_to(cx + k * 0.15 * r, cy + 0.75 * ry)
                ctx.line_to(cx + k * 0.13 * r, cy + 1.2 * ry)
            ctx.set_source_rgba(*OUT, 0.45)
            ctx.set_line_width(lw * 0.5)
            ctx.stroke()
        elif self.beard == "long":
            ctx.move_to(cx - 0.5 * r, cy + 0.45 * ry)
            ctx.curve_to(cx - 0.45 * r, cy + 1.3 * ry, cx - 0.12 * r, cy + 2.1 * ry, cx, cy + 2.4 * ry)
            ctx.curve_to(cx + 0.12 * r, cy + 2.1 * ry, cx + 0.45 * r, cy + 1.3 * ry, cx + 0.5 * r, cy + 0.45 * ry)
            ctx.curve_to(cx + 0.3 * r, cy + 0.65 * ry, cx - 0.3 * r, cy + 0.65 * ry, cx - 0.5 * r, cy + 0.45 * ry)
            ctx.close_path()
            shade(ctx, hexc("#f7f4ef"), hexc("#dcd6cf"), cy, cy + 2.4 * ry, lw)
        elif self.beard == "goatee":  # small dark pointed beard under the mouth (red king)
            ctx.move_to(cx - 0.12 * r, cy + 0.72 * ry)
            ctx.curve_to(cx - 0.1 * r, cy + 0.95 * ry, cx - 0.03 * r, cy + 1.1 * ry, cx + 0.02 * r, cy + 1.22 * ry)
            ctx.curve_to(cx + 0.06 * r, cy + 1.05 * ry, cx + 0.12 * r, cy + 0.9 * ry, cx + 0.12 * r, cy + 0.72 * ry)
            ctx.close_path()
            src(ctx, hexc("#6b3a22"))
            ctx.fill_preserve()
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(lw * 0.6)
            ctx.stroke()
        if self.helmet:
            ctx.move_to(cx - 1.02 * r, cy - 0.05 * ry)
            ctx.curve_to(cx - 1.02 * r, cy - 1.2 * ry, cx + 1.02 * r, cy - 1.2 * ry, cx + 1.02 * r, cy - 0.05 * ry)
            ctx.close_path()
            shade(ctx, hexc("#e2e6ec"), hexc("#9aa1ad"), cy - ry, cy, lw)
        if self.crown == "gold":
            top = cy - 0.78 * ry
            cw = 0.72 * r
            ctx.move_to(-cw + cx, top + 0.18 * r)
            for k in range(5):
                px = cx - cw + (k + 0.5) * (2 * cw / 5)
                ctx.line_to(px - 0.1 * r, top - 0.05 * r)
                ctx.line_to(px, top - 0.42 * r)
                ctx.line_to(px + 0.1 * r, top - 0.05 * r)
            ctx.line_to(cx + cw, top + 0.18 * r)
            ctx.close_path()
            shade(ctx, hexc("#f6cf4f"), hexc("#d29b28"), top - 0.42 * r, top + 0.18 * r, lw)
            for k in range(5):
                px = cx - cw + (k + 0.5) * (2 * cw / 5)
                ctx.new_sub_path()
                ctx.arc(px, top - 0.44 * r, 0.055 * r, 0, 2 * PI)
                src(ctx, (1, 1, 1))
                ctx.fill_preserve()
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(lw * 0.5)
                ctx.stroke()
            for k, c in enumerate(("#d64a3a", "#3f6fd6", "#d64a3a")):
                ctx.new_sub_path()
                ctx.arc(cx - 0.32 * r + k * 0.32 * r, top + 0.07 * r, 0.05 * r, 0, 2 * PI)
                src(ctx, hexc(c))
                ctx.fill()
        elif self.crown == "silver":
            top = cy - 0.75 * ry
            cw = 0.78 * r
            ctx.move_to(cx - cw, top + 0.2 * r)
            ctx.line_to(cx - cw, top - 0.05 * r)
            for k in range(3):
                px = cx - cw + (k + 0.5) * (2 * cw / 3)
                ctx.curve_to(px - 0.25 * r, top - 0.1 * r, px - 0.18 * r, top - 0.45 * r, px, top - 0.45 * r)
                ctx.curve_to(px + 0.18 * r, top - 0.45 * r, px + 0.25 * r, top - 0.1 * r, px + 2 * cw / 6, top - 0.05 * r)
            ctx.line_to(cx + cw, top + 0.2 * r)
            ctx.close_path()
            shade(ctx, hexc("#e9ecf1"), hexc("#a9afbb"), top - 0.45 * r, top + 0.2 * r, lw)
            ctx.rectangle(cx - cw, top + 0.02 * r, 2 * cw, 0.16 * r)
            shade(ctx, hexc("#c9ced8"), hexc("#9aa1ad"), top, top + 0.18 * r, lw * 0.6)
            for k in range(3):
                px = cx - cw + (k + 0.5) * (2 * cw / 3)
                ctx.new_sub_path()
                ctx.arc(px, top - 0.47 * r, 0.06 * r, 0, 2 * PI)
                src(ctx, (1, 1, 1))
                ctx.fill_preserve()
                ctx.set_source_rgb(*OUT)
                ctx.set_line_width(lw * 0.5)
                ctx.stroke()
                ctx.new_sub_path()
                ctx.arc(px, top + 0.1 * r, 0.045 * r, 0, 2 * PI)
                src(ctx, hexc("#3fbfb0"))
                ctx.fill()
        _face3(ctx, cx, cy, r, ry, lw, expr, t, look, self, sweat)


def _face3(ctx, cx, cy, r, ry, lw, expr, t, look, ch, sweat):
    lx = look * 0.12 * r
    ey = cy + 0.1 * ry

    def stroke(w):
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(w)
        ctx.stroke()

    def brow(side, lift=0.0, tilt=0.0):
        bx, by = cx + side * 0.27 * r + lx, ey - 0.3 * ry - lift * r
        ctx.move_to(bx - side * 0.13 * r, by + tilt * r)
        ctx.curve_to(bx - side * 0.04 * r, by - 0.035 * r, bx + side * 0.04 * r, by - 0.035 * r,
                     bx + side * 0.13 * r, by - tilt * r)
        stroke(0.07 * r)

    for side in (-1, 1):
        ex = cx + side * 0.25 * r + lx
        if expr in ("happy", "grin", "laugh", "smug"):
            ctx.new_sub_path()
            ctx.arc(ex, ey + 0.04 * r, 0.085 * r, PI + 0.35, 2 * PI - 0.35)
            stroke(0.05 * r)
        elif expr == "shock":
            ellipse(ctx, ex, ey, 0.12 * r, 0.13 * r)
            src(ctx, (1, 1, 1))
            ctx.fill_preserve()
            stroke(0.035 * r)
            ellipse(ctx, ex, ey, 0.045 * r, 0.05 * r)
            src(ctx, OUT)
            ctx.fill()
            brow(side, 0.1)
        elif expr in ("smirk", "cold", "tired"):
            ctx.move_to(ex - 0.09 * r, ey - 0.01 * r)
            ctx.line_to(ex + 0.09 * r, ey - 0.01 * r)
            stroke(0.045 * r)
            ellipse(ctx, ex + 0.01 * r, ey + 0.035 * r, 0.04 * r, 0.03 * r)
            src(ctx, OUT)
            ctx.fill()
            if expr == "smirk":
                brow(side, 0.06 if side > 0 else 0.0, tilt=0.02 * side)
            else:
                brow(side)
        else:
            ellipse(ctx, ex, ey, 0.045 * r, 0.065 * r)
            src(ctx, OUT)
            ctx.fill()
            if expr == "angry":
                brow(side, -0.02, tilt=-0.07)
            elif expr in ("worried", "sad"):
                brow(side, 0.05, tilt=0.07)
            else:
                brow(side)

    my = cy + 0.5 * ry
    mx = cx + lx
    red = hexc("#7a2430")
    if expr in ("happy", "smug"):
        ctx.new_sub_path()
        ctx.arc(mx, my - 0.06 * r, 0.12 * r, 0.4, PI - 0.4)
        stroke(0.045 * r)
    elif expr == "grin":
        ctx.move_to(mx - 0.2 * r, my - 0.04 * r)
        ctx.curve_to(mx - 0.1 * r, my + 0.1 * r, mx + 0.1 * r, my + 0.1 * r, mx + 0.2 * r, my - 0.04 * r)
        ctx.close_path()
        src(ctx, hexc("#6b3a22"))
        ctx.fill_preserve()
        stroke(0.035 * r)
        ctx.rectangle(mx - 0.14 * r, my - 0.035 * r, 0.28 * r, 0.035 * r)
        src(ctx, (1, 1, 1))
        ctx.fill()
    elif expr == "laugh":
        ctx.new_sub_path()
        ctx.arc(mx, my - 0.04 * r, 0.16 * r, 0, PI)
        ctx.close_path()
        src(ctx, red)
        ctx.fill_preserve()
        stroke(0.035 * r)
    elif expr == "shock":
        ellipse(ctx, mx, my + 0.02 * r, 0.05 * r, 0.07 * r)
        src(ctx, red)
        ctx.fill_preserve()
        stroke(0.035 * r)
    elif expr in ("angry", "sad", "worried"):
        ctx.new_sub_path()
        ctx.arc(mx, my + 0.1 * r, 0.1 * r, PI + 0.6, 2 * PI - 0.6)
        stroke(0.045 * r)
    elif expr in ("smirk", "cold"):
        ctx.move_to(mx - 0.09 * r, my + 0.01 * r)
        ctx.curve_to(mx, my + 0.03 * r, mx + 0.07 * r, my, mx + 0.13 * r, my - 0.05 * r)
        stroke(0.045 * r)
    else:
        ctx.move_to(mx - 0.08 * r, my)
        ctx.curve_to(mx - 0.03 * r, my + 0.03 * r, mx + 0.03 * r, my + 0.03 * r, mx + 0.08 * r, my)
        stroke(0.045 * r)
    if ch.mustache == "handlebar":  # big brown handlebar (blacksmith)
        for side in (-1, 1):
            ctx.move_to(mx, cy + 0.32 * ry)
            ctx.curve_to(mx + side * 0.12 * r, cy + 0.16 * ry, mx + side * 0.32 * r, cy + 0.22 * ry,
                         mx + side * 0.42 * r, cy + 0.36 * ry)
            ctx.curve_to(mx + side * 0.46 * r, cy + 0.18 * ry, mx + side * 0.5 * r, cy + 0.2 * ry, mx + side * 0.48 * r, cy + 0.3 * ry)
            ctx.curve_to(mx + side * 0.45 * r, cy + 0.6 * ry, mx + side * 0.15 * r, cy + 0.56 * ry, mx, cy + 0.42 * ry)
            ctx.close_path()
            src(ctx, hexc("#4a2f22"))
            ctx.fill_preserve()
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(lw * 0.4)
            ctx.stroke()
    elif ch.mustache == "thin":
        for side in (-1, 1):
            ctx.move_to(mx, cy + 0.35 * ry)
            ctx.curve_to(mx + side * 0.12 * r, cy + 0.28 * ry, mx + side * 0.22 * r, cy + 0.32 * ry, mx + side * 0.27 * r, cy + 0.42 * ry)
            stroke(0.035 * r)
    if sweat:
        k = (t * 1.5) % 1
        sx, sy = cx + 0.6 * r, cy - 0.35 * ry + k * 0.25 * r
        ctx.move_to(sx, sy - 0.12 * r)
        ctx.curve_to(sx + 0.09 * r, sy, sx + 0.07 * r, sy + 0.08 * r, sx, sy + 0.08 * r)
        ctx.curve_to(sx - 0.07 * r, sy + 0.08 * r, sx - 0.09 * r, sy, sx, sy - 0.12 * r)
        src(ctx, hexc("#8fd3ff"))
        ctx.fill_preserve()
        stroke(0.025 * r)


def draw_item3(ctx, item, x, y, r, t):
    if item == "spear":
        ctx.move_to(x, y + 2.6 * r)
        ctx.line_to(x, y - 2.4 * r)
        ctx.set_source_rgb(*hexc("#b07a3a"))
        ctx.set_line_width(0.08 * r)
        ctx.stroke()
        ctx.move_to(x, y - 3.1 * r)
        ctx.curve_to(x + 0.18 * r, y - 2.8 * r, x + 0.14 * r, y - 2.5 * r, x, y - 2.38 * r)
        ctx.curve_to(x - 0.14 * r, y - 2.5 * r, x - 0.18 * r, y - 2.8 * r, x, y - 3.1 * r)
        shade(ctx, hexc("#eef1f5"), hexc("#a5abb8"), y - 3.1 * r, y - 2.4 * r, 0.04 * r)
        ctx.move_to(x, y - 2.36 * r)
        ctx.line_to(x - 0.06 * r, y - 2.0 * r)
        ctx.line_to(x + 0.06 * r, y - 2.0 * r)
        ctx.close_path()
        src(ctx, hexc("#d64a3a"))
        ctx.fill()
    elif item == "shield":
        shield(ctx, x + 0.3 * r, y, 1.05 * r)
    elif item == "stick":
        ctx.move_to(x, y - 0.4 * r)
        ctx.line_to(x + 0.12 * r, y + 2.9 * r)
        ctx.set_source_rgb(*hexc("#8a5a33"))
        ctx.set_line_width(0.07 * r)
        ctx.stroke()
    elif item == "hammer":
        ctx.move_to(x, y)
        ctx.line_to(x, y - 0.6 * r)
        ctx.set_source_rgb(*hexc("#8a5a33"))
        ctx.set_line_width(0.07 * r)
        ctx.stroke()
        rrect(ctx, x - 0.2 * r, y - 0.8 * r, 0.4 * r, 0.22 * r, 0.04 * r)
        shade(ctx, hexc("#c8ccd4"), hexc("#80858f"), y - 0.8 * r, y - 0.58 * r, 0.035 * r)
    elif item == "moneybag":
        ellipse(ctx, x, y + 0.3 * r, 0.26 * r, 0.24 * r)
        shade(ctx, hexc("#f0d48a"), hexc("#c49a4a"), y, y + 0.55 * r, 0.04 * r)
        ctx.move_to(x - 0.1 * r, y + 0.04 * r)
        ctx.line_to(x + 0.1 * r, y + 0.04 * r)
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(0.05 * r)
        ctx.stroke()
        ctx.new_sub_path()
        ctx.arc(x, y + 0.33 * r, 0.11 * r, 0, 2 * PI)
        src(ctx, hexc("#4f9a43"))
        ctx.fill()
        engine.text(ctx, "$", x, y + 0.33 * r, 0.16 * r, (1, 1, 1), outline=False)


def shield(ctx, x, y, R, teal="#55c1ba"):
    ctx.new_sub_path()
    ctx.arc(x, y, R, 0, 2 * PI)
    shade(ctx, hexc("#f2c443"), hexc("#c48a1c"), y - R, y + R, 0.06 * R)
    ctx.new_sub_path()
    ctx.arc(x, y, R * 0.86, 0, 2 * PI)
    shade(ctx, lighter(hexc(teal), 0.15), darker(hexc(teal), 0.15), y - R, y + R, 0.04 * R)
    ctx.new_sub_path()
    ctx.arc(x, y, R * 0.62, 0, 2 * PI)
    shade(ctx, hexc("#e9edf2"), hexc("#a5abb8"), y - R, y + R, 0.04 * R)
    for k in range(24):
        a = k * PI / 12
        ctx.move_to(x + math.cos(a) * R * 0.3, y + math.sin(a) * R * 0.3)
        ctx.line_to(x + math.cos(a) * R * 0.6, y + math.sin(a) * R * 0.6)
    ctx.set_source_rgba(0.5, 0.52, 0.58, 0.5)
    ctx.set_line_width(0.015 * R * 4)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x, y, R * 0.24, 0, 2 * PI)
    shade(ctx, hexc("#ffffff"), hexc("#9aa1ad"), y - R * 0.24, y + R * 0.24, 0.04 * R)
