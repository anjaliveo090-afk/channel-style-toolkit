"""Keep every character (and pop-up label) inside the Shorts safe zone.

Safe zone measured from the user's template (415x739 -> 720x1280):
  x 38..680, y 149..1013; below y 678 the right edge is x 599 (like/comment buttons).
Captions go under y ~1013, the channel name / Subscribe button below that.

fit(SHOTS, story_module) draws each keyframed shot, records where the story's characters
(style2.Char2 / style3.Char3 draw calls, home.avatar) and label() stickers land on screen,
and nudges / zooms out each camera key so that its framing stays inside the zone.
Only the camera changes: story, timing, sets and SFX stay the same.
Props that must stay visible too can be listed per shot as keep=[(x0, y0, x1, y1), ...] (world coords).
Shots with a screen-space HUD at the top can set top=250 so characters and labels stay below it.
Run it right before render(): `safezone.fit(SHOTS, sys.modules[__name__])`."""
import math
import sys

import cairo
import numpy as np

import engine
from engine import W, H

X0, X1, Y0, Y1 = 38, 680, 149, 1013
NOTCH_Y, NOTCH_X = 678, 599
MARGIN = 6

_boxes = []
_story = {"g": None}


def _from_story():
    """True when the current draw call comes straight from the story module (not a set prop)."""
    return sys._getframe(2).f_globals is _story["g"]


def _rec(ctx, x0, y0, x1, y1):
    pts = [ctx.user_to_device(x, y) for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1))]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    _boxes.append((min(xs), min(ys), max(xs), max(ys)))


def _install(module):
    _story["g"] = module.__dict__
    patched = []

    def wrap_char(cls, top_k, half_k):
        orig = cls.draw

        def draw(self, ctx, x, y, s=1.0, *a, **kw):
            if _from_story():
                r = 64 * s
                _rec(ctx, x - half_k * r, y - top_k * r, x + half_k * r, y + 0.1 * r)
            return orig(self, ctx, x, y, s, *a, **kw)
        cls.draw = draw
        patched.append((cls, "draw", orig))

    from style2 import Char2
    wrap_char(Char2, 5.0, 1.0)
    try:
        from style3 import Char3
        wrap_char(Char3, 5.2, 1.0)
    except ImportError:
        pass
    try:
        import home
        orig_av = home.avatar

        def avatar(ctx, x, y, s=1.0, *a, **kw):
            if _from_story():
                j = kw.get("jump", 0.0)
                _rec(ctx, x - 48 * s, y - j - 215 * s, x + 48 * s, y - j)
            return orig_av(ctx, x, y, s, *a, **kw)
        home.avatar = avatar
        patched.append((home, "avatar", orig_av))
    except ImportError:
        pass
    if hasattr(module, "label"):
        orig_label = module.label

        def label(ctx, s, x, y, size, *a, **kw):
            sc = kw.get("scale", 1.0)
            if sc > 0.3:
                w = (len(s) * size * 0.66 + size * 0.9) * sc / 2
                h = size * 0.8 * sc
                _rec(ctx, x - w, y - h, x + w, y + h)
            return orig_label(ctx, s, x, y, size, *a, **kw)
        module.label = label
        patched.append((module, "label", orig_label))
    return patched


def _uninstall(patched):
    for obj, name, orig in reversed(patched):
        setattr(obj, name, orig)


def _bbox_at(shot, T, surf):
    """Union of the visible character/label boxes on screen at absolute time T."""
    del _boxes[:]
    ctx = cairo.Context(surf)
    z, (cx, cy) = engine.key_camera(shot["keys"], T)
    ctx.translate(W / 2, H / 2)
    if shot.get("dutch"):
        ctx.rotate(shot["dutch"])
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)
    engine._CAM.update(z=z, c=(cx, cy), z0=shot["keys"][0][1], c0=shot["keys"][0][2], strength=0.3)
    shot["draw"](ctx, T - shot["start"], shot["end"] - shot["start"])
    vis = [b for b in _boxes if 0 <= (b[0] + b[2]) / 2 <= W and 0 <= (b[1] + b[3]) / 2 <= H]
    for x0, y0, x1, y1 in shot.get("keep", ()):   # key props given in world coordinates
        vis.append(((x0 - cx) * z + W / 2, (y0 - cy) * z + H / 2, (x1 - cx) * z + W / 2, (y1 - cy) * z + H / 2))
    if not vis:
        return None
    return (min(b[0] for b in vis), min(b[1] for b in vis), max(b[2] for b in vis), max(b[3] for b in vis))


def _solve(box, y0=Y0):
    """Zoom factor f (about the screen centre) and screen shift (sx, sy) that put box in the zone
    (top edge y0: raise it above 149 when a HUD/timer overlay sits at the top)."""
    l, t, r, b = box
    f = min(1.0, (Y1 - y0 - 2 * MARGIN) / max(1.0, b - t))
    l, t, r, b = [(v - c) * f + c for v, c in ((l, W / 2), (t, H / 2), (r, W / 2), (b, H / 2))]
    sy = 0.0
    if b > Y1 - MARGIN:
        sy = Y1 - MARGIN - b
    elif t < y0 + MARGIN:
        sy = y0 + MARGIN - t
    right = NOTCH_X if b + sy > NOTCH_Y else X1
    if r - l > right - X0 - 2 * MARGIN:   # too wide: zoom out more and solve again
        f2 = (right - X0 - 2 * MARGIN) / (r - l)
        f3, sx, sy = _solve(tuple((v - c) * f2 + c for v, c in
                                  ((l, W / 2), (t - sy, H / 2), (r, W / 2), (b - sy, H / 2))), y0)
        return f * f2 * f3, sx, sy
    sx = 0.0
    if r > right - MARGIN:
        sx = right - MARGIN - r
    elif l < X0 + MARGIN:
        sx = X0 + MARGIN - l
    return f, sx, sy


def fit(shots, module, fps=5, iters=4, verbose=True):
    """Adjust the camera keys of every shot in place so characters stay in the safe zone."""
    patched = _install(module)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    moved = 0
    try:
        for shot in shots:
            keys = shot.get("keys")
            if not keys:
                continue
            keys = [list(k) for k in keys]
            for _ in range(iters):
                changed = False
                for i, k in enumerate(keys):
                    a = max(shot["start"], k[0])
                    if i + 1 < len(keys):
                        nk = keys[i + 1]
                        m = nk[3] if len(nk) > 3 else min(0.55, 0.75 * (nk[0] - k[0]))
                        b = min(shot["end"], nk[0] - m)
                    else:
                        b = shot["end"]
                    # the moment the camera arrives on this key, plus the settled part of its hold
                    ts = [min(max(k[0], shot["start"] + 0.02), shot["end"] - 0.02)]
                    if b - a > 0.1:
                        a = a + 0.4 * (b - a)      # entrances happen early in a hold
                        ts += list(np.linspace(a, b - 0.01, max(2, int((b - a) * fps) + 1)))
                    worst = None
                    for T in ts:
                        box = _bbox_at(dict(shot, keys=[tuple(x) for x in keys]), T, surf)
                        if box is None:
                            continue
                        worst = box if worst is None else (min(worst[0], box[0]), min(worst[1], box[1]),
                                                           max(worst[2], box[2]), max(worst[3], box[3]))
                    if worst is None:
                        continue
                    f, sx, sy = _solve(worst, shot.get("top", Y0))
                    if f > 0.995 and abs(sx) < 3 and abs(sy) < 3:
                        continue
                    z = k[1] * f
                    k[1] = z
                    k[2] = (k[2][0] - sx / z, k[2][1] - sy / z)
                    changed = True
                if not changed:
                    break
            new = [tuple(k) for k in keys]
            if new != [tuple(k) for k in shot["keys"]]:
                moved += 1
                if verbose:
                    print(f"safezone: shot @{shot['start']:.2f}s ({shot['draw'].__name__}) re-framed")
            shot["keys"] = new
    finally:
        _uninstall(patched)
    if verbose:
        print(f"safezone: {moved} shots re-framed")
    return shots


def overlay(png_in, png_out):
    """Draw the safe zone outline on a frame (for checking)."""
    import cv2
    img = cv2.imread(png_in)
    sx, sy = img.shape[1] / W, img.shape[0] / H
    pts = np.array([(X0, Y0), (X1, Y0), (X1, NOTCH_Y), (NOTCH_X, NOTCH_Y), (NOTCH_X, Y1), (X0, Y1)], np.float32)
    pts[:, 0] *= sx
    pts[:, 1] *= sy
    cv2.polylines(img, [pts.astype(np.int32)], True, (60, 60, 255), max(1, int(3 * sx)))
    cv2.imwrite(png_out, img)
