"""Transitions and overlays measured on the references (visual_grammar.md section 2).

Image-level transitions take two float images (H, W, 3, B-G-R order as in render16) and a progress
p = 0..1:  dissolve, circle_wipe, magnifier, split_screen, page_flip (needs the cairo calendar).
Camera-style transitions are curves you use inside a shot:  zoom_through(), pull_out().
Overlays draw on a cairo context:  viewfinder(), polaroid().
Already elsewhere: render16.whip (whip-pan), sets.impact_flash, sets.text_card (black / chapter cards).
"""
import math

import cairo
import cv2
import numpy as np

from style import INK, _rrect, hexc

W, H = 1280, 720
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)


def _ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def dissolve(a, b, p):
    p = _ease(p)
    return a * (1 - p) + b * p


def circle_wipe(a, b, p, cx=W / 2, cy=H / 2, edge=True):
    """b grows inside a circle from (cx, cy) (or shrinks if p goes 1->0)."""
    r = _ease(p) * math.hypot(W, H)
    d = np.sqrt((_xx - cx) ** 2 + (_yy - cy) ** 2)
    m = np.clip((r - d) / 3.0, 0, 1)[..., None]
    out = a * (1 - m) + b * m
    if edge and 0 < p < 1:
        ring = (np.abs(d - r) < 5)[..., None]
        out = np.where(ring, 0.08, out)
    return out


def magnifier(a, detail, p, cx, cy, r0=90):
    """A magnifying lens appears at (cx, cy) on image a showing `detail` (the zoomed view), then grows to
    fill the frame (V1 4:52: lens over the whiteboard). p 0..0.3 lens pops in, 0.3..1 it grows."""
    if p < 0.3:
        r = r0 * _ease(p / 0.3)
    else:
        r = r0 + (math.hypot(W, H) - r0) * _ease((p - 0.3) / 0.7) ** 1.5
    d = np.sqrt((_xx - cx) ** 2 + (_yy - cy) ** 2)
    m = np.clip((r - d) / 2.0, 0, 1)[..., None]
    out = a * (1 - m) + detail * m
    rim = np.clip(1 - np.abs(d - r) / (6 + r * 0.02), 0, 1)[..., None]
    out = out * (1 - rim) + 0.06 * rim
    if r < math.hypot(W, H) * 0.7:          # handle
        img = (np.clip(out, 0, 1) * 255).astype(np.uint8).copy()
        ang = math.radians(40)
        x0, y0 = int(cx + math.cos(ang) * r), int(cy + math.sin(ang) * r)
        x1, y1 = int(cx + math.cos(ang) * (r + 140)), int(cy + math.sin(ang) * (r + 140))
        cv2.line(img, (x0, y0), (x1, y1), (20, 10, 0), 22, cv2.LINE_AA)
        cv2.line(img, (x0, y0), (x1, y1), (40, 70, 110), 14, cv2.LINE_AA)
        out = img.astype(np.float32) / 255
    return out


def split_screen(left, right, p=1.0, cord=True, t=0.0):
    """Two rooms side by side (V1 4:35 phone call): the right panel slides in, ragged white divider,
    a coiled phone cord crossing it."""
    p = _ease(p)
    x_div = int(W / 2 + (1 - p) * W / 2)
    out = left.copy()
    out[:, x_div:] = right[:, W // 2:W // 2 + (W - x_div)]      # right half of the right room slides in
    img = (np.clip(out, 0, 1) * 255).astype(np.uint8).copy()
    pts = []
    for y in range(0, H + 20, 20):
        pts.append((x_div + (6 if (y // 20) % 2 else -6), y))
    cv2.polylines(img, [np.array(pts, np.int32)], False, (245, 245, 245), 10, cv2.LINE_AA)
    cv2.polylines(img, [np.array(pts, np.int32)], False, (20, 10, 0), 3, cv2.LINE_AA)
    if cord and p > 0.6:
        y0 = int(H * 0.72)
        cps = []
        for k in range(0, 260):
            x = x_div - 330 + k * 2.6
            cps.append((int(x + 9 * math.cos(k * 0.9 + t * 3)), int(y0 + 9 * math.sin(k * 0.9 + t * 3) + 0.0006 * (x - x_div) ** 2)))
        cv2.polylines(img, [np.array(cps, np.int32)], False, (40, 40, 200), 4, cv2.LINE_AA)
    return img.astype(np.float32) / 255


def page_flip(ctx, p, cx, cy, draw_page_old, draw_page_new):
    """Calendar page flip (V1 4:41 Aug -> Sep): new page underneath, old page tears off, rotates and flies
    down-right. draw_page_* (ctx) draw a page centred at (cx, cy)."""
    draw_page_new(ctx)
    if p >= 1:
        return
    e = _ease(p)
    ctx.save()
    ctx.translate(cx + e * 520, cy + e * e * 520)
    ctx.rotate(e * 0.9)
    ctx.translate(-cx, -cy)
    draw_page_old(ctx)
    ctx.restore()


def zoom_through(t, t_start, dur=0.45, z0=1.0, z1=4.0):
    """Camera zoom for a push-through into a window/object (> 1.25x in 0.4 s), cut at the end."""
    k = min(1.0, max(0.0, (t - t_start) / dur))
    return z0 * (z1 / z0) ** (k ** 2.2)


def pull_out(t, t_start, dur=1.4, z0=5.0, z1=1.0):
    """Fast reveal: zoom 5x -> 1x in ~1.4 s, ease-out (V1 4:20 key -> man on a platform)."""
    k = min(1.0, max(0.0, (t - t_start) / dur))
    return z1 + (z0 - z1) * (1 - k) ** 3


# ------------------------------------------------------------------ overlays (cairo, screen space)
def viewfinder(ctx, t, label="600mm f/4"):
    """Camera viewfinder (V1 0:35): white frame, corner brackets, crosshair, blinking REC."""
    ctx.save()
    ctx.set_source_rgb(0.96, 0.96, 0.96)
    ctx.set_line_width(10)
    ctx.rectangle(40, 30, W - 80, H - 60)
    ctx.stroke()
    ctx.set_line_width(4)
    for (x, y, sx, sy) in ((90, 80, 1, 1), (W - 90, 80, -1, 1), (90, H - 80, 1, -1), (W - 90, H - 80, -1, -1)):
        ctx.move_to(x, y + sy * 50)
        ctx.line_to(x, y)
        ctx.line_to(x + sx * 50, y)
        ctx.stroke()
    ctx.arc(W / 2, H / 2, 26, 0, 2 * math.pi)
    ctx.move_to(W / 2 - 45, H / 2)
    ctx.line_to(W / 2 + 45, H / 2)
    ctx.move_to(W / 2, H / 2 - 45)
    ctx.line_to(W / 2, H / 2 + 45)
    ctx.set_line_width(2.5)
    ctx.stroke()
    if int(t * 2) % 2 == 0:
        ctx.arc(120, 110, 10, 0, 2 * math.pi)
        ctx.set_source_rgb(0.9, 0.15, 0.15)
        ctx.fill()
    ctx.select_font_face("Caveat Brush")
    ctx.set_font_size(26)
    ctx.set_source_rgb(0.96, 0.96, 0.96)
    ctx.move_to(140, 120)
    ctx.show_text("REC")
    ctx.move_to(W - 230, H - 100)
    ctx.show_text(label)
    ctx.restore()


def polaroid(ctx, x, y, k, draw_photo, w=220, h=190, angle=-0.08):
    """A polaroid drops in (k = seconds since start) with a tiny bounce; draw_photo(ctx, w, h) paints
    the picture in a local box (0,0)-(w,h)."""
    if k <= 0:
        return
    drop = max(0.0, 1 - k / 0.22)
    bounce = math.exp(-k * 9) * math.sin(k * 28) * 0.06
    ctx.save()
    ctx.translate(x, y - drop * 160)
    ctx.rotate(angle + bounce)
    ctx.rectangle(-w / 2 + 6, -h / 2 + 8, w, h + 46)
    ctx.set_source_rgba(0, 0, 0, 0.3)
    ctx.fill()
    ctx.rectangle(-w / 2, -h / 2, w, h + 46)
    ctx.set_source_rgb(0.98, 0.98, 0.96)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.save()
    ctx.translate(-w / 2 + 14, -h / 2 + 14)
    ctx.rectangle(0, 0, w - 28, h - 28)
    ctx.clip()
    draw_photo(ctx, w - 28, h - 28)
    ctx.restore()
    ctx.restore()


def rip(a, b, p, seed=3):
    """Rip / tear transition (V1 4:21, 4:58): a jagged crack opens down the middle; the two halves of `a`
    slide apart revealing `b`, with a white torn edge."""
    import random as _r
    rnd = _r.Random(seed)
    p = _ease(p)
    gap = p * W * 0.62
    pts = np.array([rnd.uniform(-28, 28) for _ in range(H // 24 + 2)], np.float32)
    jag = np.interp(np.arange(H), np.arange(len(pts)) * 24, pts)[:, None]
    cx = W / 2 + jag
    xs = _xx
    out = b.copy()
    left = xs < cx - gap / 2
    right = xs > cx + gap / 2
    sh = int(gap / 2)
    a_l = np.roll(a, -sh, axis=1)
    a_r = np.roll(a, sh, axis=1)
    out = np.where(left[..., None], a_l, out)
    out = np.where(right[..., None], a_r, out)
    edge = (np.abs(xs - (cx - gap / 2)) < 5) | (np.abs(xs - (cx + gap / 2)) < 5)
    out = np.where(edge[..., None], 0.97, out)
    return out
