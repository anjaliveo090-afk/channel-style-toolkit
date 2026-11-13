"""6-second style sample, 16:9 1280x720 @ 24 fps (the reference format).
Original characters and text. Shots:
  0.00-2.45  wide dinner two-shot, slow push-in, glass raised, laugh on the beat, name tag slides in
  2.45-2.75  whip-pan with horizontal motion blur
  2.75-4.55  close-up on the banker, push-in; laugh snaps to shock + punch-in, red label pops in
  4.55-6.00  hard cut to a black card, white handwritten script typed letter by letter
Run:  python3 animator/sample6.py  ->  output/sample6/sample6.mp4
"""
import math
import subprocess
import sys
from pathlib import Path

import cairo
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio  # noqa: E402
import sets  # noqa: E402
from style import Char  # noqa: E402

W, H, FPS, TOTAL = 1280, 720, 24, 6.0
OUT = Path(__file__).resolve().parent.parent / "output" / "sample6"

BANKER = Char(body="#6b5a3e", hair="bald", hair_col="#d8d2c8", skin="#e8b385", glasses="round",
              collar="lapel", tie="#9b1c22", light=(0.75, -0.35))
GUEST = Char(body="#1f6f63", hair="bun", hair_col="#7a2e1c", skin="#edbd8f", glasses=None,
             collar="shirt", earrings="#e8c050", light=(-0.75, -0.35))

T_WHIP0, T_WHIP1, T_CARD = 2.45, 2.75, 4.55
T_SNAP, T_LABEL = 3.35, 3.5
CARD_TEXT = "Nobody told him."
CARD_CPS = 16.0


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def surfaces():
    bg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    fg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ov = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return bg, fg, ov


def arr(surf):
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))
    return a.astype(np.float32) / 255.0


def cam(ctx, zoom, cx, cy):
    """Zoom about (cx, cy) in world space, keeping it at the same screen point."""
    ctx.translate(cx, cy)
    ctx.scale(zoom, zoom)
    ctx.translate(-cx, -cy)


def clear(surf):
    c = cairo.Context(surf)
    c.set_operator(cairo.OPERATOR_CLEAR)
    c.paint()


# ------------------------------------------------------------------ shots
def shot_wide(t):
    bg, fg, ov = surfaces()
    z = 1.0 + 0.07 * ease(t / 2.6)
    c = cairo.Context(bg)
    cam(c, 1 + (z - 1) * 0.6, 640, 330)
    sets.restaurant_bg(c, t)
    sets.booth(c, 230, 200, 360, 460)
    sets.booth(c, 690, 200, 360, 460)
    c = cairo.Context(fg)
    cam(c, z, 640, 330)
    k_raise = ease((t - 0.55) / 0.35)
    BANKER.draw(c, 410, 640, 2.7, expr="laugh" if t > 0.9 else "happy", t=t, pose="sit",
                arms=("raise_r", 0.25 + 0.75 * k_raise), item="wine", item_hand="r", look=0.3)
    GUEST.draw(c, 870, 640, 2.7, expr="smirk", t=t + 1.3, pose="sit",
               arms=("raise_l", 0.25 + 0.6 * ease((t - 0.7) / 0.35)), item="wine", item_hand="l", look=-0.35)
    sets.table(c, 640, 545, 700, t)
    c = cairo.Context(ov)
    sets.name_tag(c, "THE BANKER", 70, 600, ease((t - 0.45) / 0.3))
    return compose(bg, fg, ov, dof=3.0)


def shot_close(t):
    """t is shot-local time (0 at T_WHIP0 so the whip has content)."""
    bg, fg, ov = surfaces()
    tl = t
    z = 1.0 + 0.05 * ease(tl / 1.8)
    snap = ease((t + T_WHIP0 - T_SNAP) / 0.12)
    z *= 1 + 0.12 * snap
    c = cairo.Context(bg)
    cam(c, 2.1, 380, 300)
    sets.restaurant_bg(c, t + 2.5)
    sets.booth(c, 210, 250, 380, 400)
    c.identity_matrix()
    sets.candle_at(c, 1150, 760, t, s=1.6)
    c = cairo.Context(fg)
    cam(c, z, 470, 380)
    shocked = (t + T_WHIP0) >= T_SNAP
    BANKER.draw(c, 470, 870, 4.6, expr="shock" if shocked else "laugh", t=t + 2.5, pose="sit",
                arms=("raise_r", 1.0 - 0.6 * snap), item="wine", item_hand="r", look=0.15 + 0.2 * snap)
    c = cairo.Context(ov)
    sets.pop_label(c, "-$40 MILLION", 960, 190, (t + T_WHIP0) - T_LABEL)
    return compose(bg, fg, ov, dof=9.0)


def shot_card(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    sets.text_card(c, CARD_TEXT, t - 0.05, W, H, cps=CARD_CPS, size=58)
    return arr(surf)[..., :3]


# ------------------------------------------------------------------ compositing
def compose(bg, fg, ov, dof=0.0):
    b = arr(bg)[..., :3]
    if dof > 0:
        b = cv2.GaussianBlur(b, (0, 0), dof)
    f = arr(fg)
    img = b * (1 - f[..., 3:4]) + f[..., :3]
    # bloom from the bright warm sources
    lum = img.max(axis=2, keepdims=True)
    bright = img * np.clip((lum - 0.9) / 0.1, 0, 1)
    img = img + cv2.GaussianBlur(bright, (0, 0), 16) * 0.4
    o = arr(ov)
    img = img * (1 - o[..., 3:4]) + o[..., :3]
    return img


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.55 * (((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2)).clip(0.35, 1)[..., None]
RNG = np.random.default_rng(7)


def hblur(img, n):
    n = int(n)
    if n < 3:
        return img
    k = np.ones((1, n), np.float32) / n
    return cv2.filter2D(img, -1, k)


def frame(t):
    if t < T_WHIP0:
        img = shot_wide(t)
    elif t < T_WHIP1:
        p = ease((t - T_WHIP0) / (T_WHIP1 - T_WHIP0))
        a = shot_wide(t)
        b = shot_close(t - T_WHIP0)
        dx = int(p * W)
        img = np.zeros_like(a)
        img[:, :W - dx] = a[:, dx:]
        img[:, W - dx:] = b[:, :dx]
        img = hblur(img, 140 * math.sin(math.pi * p) + 1)
    elif t < T_CARD:
        img = shot_close(t - T_WHIP0)
    else:
        return shot_card(t - T_CARD)
    img = img * VIG
    img = img + RNG.normal(0, 0.012, img.shape[:2])[..., None].astype(np.float32)
    return img


# ------------------------------------------------------------------ sound
def soundtrack(path):
    n = int(audio.SR * TOTAL)
    mix = np.zeros(n)

    def put(x, at, vol):
        s = int(at * audio.SR)
        e = min(n, s + len(x))
        mix[s:e] += np.asarray(x[:e - s]) * vol

    put(audio.music_ref(TOTAL), 0, 0.55)
    put(audio.pop(), 0.45, 0.55)              # name tag
    put(audio.bell(), 0.92, 0.18)             # glasses clink
    put(audio.whoosh(), T_WHIP0 - 0.03, 0.35)  # whip-pan
    put(audio.sting_soft(), T_SNAP, 0.6)      # the snap to shock
    put(audio.pop(), T_LABEL, 0.7)            # label pops in
    for i in range(len(CARD_TEXT)):
        if CARD_TEXT[i] != " ":
            put(audio.tick(), T_CARD + 0.05 + i / CARD_CPS, 0.35)
    audio.save(path, mix)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wav = OUT / "sample6.wav"
    soundtrack(wav)
    silent = OUT / "sample6_video.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                          "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    nf = int(TOTAL * FPS)
    for i in range(nf):
        img = frame(i / FPS)
        bgr = (np.clip(img, 0, 1) * 255).astype(np.uint8)   # cairo ARGB32 bytes are B,G,R,A
        p.stdin.write(np.ascontiguousarray(bgr).tobytes())
    p.stdin.close()
    p.wait()
    out = OUT / "sample6.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main()
