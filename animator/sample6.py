"""6-second style sample, 16:9 1280x720 @ 24 fps, built on the measured V1 frames
(two-shot = V1 0:23, close-up = V1 0:07, text card = V1 0:04-0:06). Original characters and text.
  0.00-2.45  two-shot across a candle-lit table, slow push-in; glass up, laugh on the beat
  2.45-2.75  whip-pan with horizontal motion blur
  2.75-4.55  big close-up (head radius 225 px at 478,250), fork raised; name tag wipes in;
             laugh snaps to shock with a punch-in; red label pops in
  4.55-6.00  hard cut to black, white slanted brush script typed letter by letter
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

# original characters built with the reference construction rules
BANKER = Char(body="#1c2233", hair="swept", hair_col="#4a3426", glasses="round", collar="shirt",
              tie="#a3161d", light=(0.9, 0.45), pin="#d9b44a")
GUEST = Char(body="#16654f", hair="bun", hair_col="#6e2a18", glasses=None, collar="round",
             earrings="#e8c050", light=(-0.9, 0.45), build=0.82,
             skin={"hi": "#fcd08a", "mid": "#dba37c", "sh": "#b38b73", "rim": "#febd6c"})

T_WHIP0, T_WHIP1, T_CARD = 2.45, 2.75, 4.55
T_SNAP, T_LABEL = 3.35, 3.5
CARD_TEXT = "Nobody told him."
CARD_CPS = 16.0


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def surfaces():
    return [cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H) for _ in range(3)]


def arr(surf):
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))
    return a.astype(np.float32) / 255.0


def cam(ctx, zoom, cx, cy):
    ctx.translate(cx, cy)
    ctx.scale(zoom, zoom)
    ctx.translate(-cx, -cy)


# ------------------------------------------------------------------ shots
def shot_wide(t):
    """Layout measured on V1 0:23: heads at (255,300) R160 and (1040,310) R150, table top y 603."""
    bg, fg, ov = surfaces()
    z = 1.0 + 0.05 * ease(t / 2.5)
    c = cairo.Context(bg)
    cam(c, 1 + (z - 1) * 0.7, 640, 360)
    sets.wood_wall(c)
    sets.night_window(c, 905, -10, 1290, 215, t)
    sets.curtain(c, 860, 905, 470)
    sets.sconce(c, 690, 190)
    sets.booth_side(c, -40, 150, 120, studs_x=30, studs=(262, 300, 370, 440, 505, 580))
    sets.booth_side(c, 1150, 1330, 150, studs_x=1255, studs=(232, 300), flip=True)
    c = cairo.Context(fg)
    cam(c, z, 640, 360)
    k = ease((t - 0.45) / 0.4)
    BANKER.draw(c, 255, 711, 4.0, expr="laugh" if t > 0.85 else "happy", t=t, pose="sit", look=0.35,
                arms={"r": (575 - (1 - k) * 60, 330 + (1 - k) * 200), "l": (455, 635)}, item="wine", item_hand="r")
    GUEST.draw(c, 1040, 695, 3.75, expr="smirk", t=t + 1.7, pose="sit", look=-0.3,
               arms={"l": (850, 630), "r": (1210, 640)})
    sets.tablecloth(c, 660, 603, 568, 42, glow_x=655)
    sets.plate(c, 430, 600)
    sets.plate(c, 885, 600)
    sets.standing_wine(c, 800, 600, 140)
    sets.roses_candle(c, 655, 600, t)
    BANKER.draw_arms_over(c, only=("l",))      # hands rest on the plates, over the cloth
    GUEST.draw_arms_over(c, only=("l",))
    return compose(bg, fg, ov, dof=3.5)


def shot_close(t):
    """Layout measured on V1 0:07: head (478,250) R225, raised hand at (905,345), name tag box
    (765,532) 415x108. t is local (0 = whip start)."""
    bg, fg, ov = surfaces()
    ga = t + T_WHIP0
    z = 1.0 + 0.04 * ease(t / 1.8)
    snap = ease((ga - T_SNAP) / 0.12)
    z *= 1 + 0.1 * snap
    c = cairo.Context(bg)
    cam(c, z, 478, 250)
    sets.wood_wall(c, rail_y=470, panel=(700, 960))
    sets.night_window(c, 1040, -10, 1290, 470, t + 3)
    sets.curtain(c, 965, 1040, 470)
    sets.sconce(c, 775, 175, 1.1)
    sets.booth_side(c, 20, 330, 120, studs_x=65, studs=(195, 258, 352, 452, 550, 650))
    c.save()
    c.translate(1160, 600)
    c.scale(1.3, 1.3)
    c.translate(-1160, -600)
    sets.roses_candle(c, 1160, 690, t)
    c.restore()
    c = cairo.Context(fg)
    cam(c, z, 478, 250)
    shocked = ga >= T_SNAP
    BANKER.draw(c, 478, 250 + 2.57 * 225, 5.625, expr="shock" if shocked else "laugh", t=ga, pose="sit",
                look=0.2 + 0.15 * snap, arms={"r": (905 - 15 * snap, 345 + 35 * snap), "l": (300, 900)},
                item="fork", item_hand="r")
    sets.tablecloth(c, 640, 705, 760, 40, glow_x=1100)
    sets.plate(c, 770, 700, 150, 30)
    c = cairo.Context(ov)
    sets.name_tag(c, "MARCUS VALE", 765, 532, 415, 108, (ga - (T_WHIP1 + 0.15)) / 0.35)
    sets.pop_label(c, "-$40 MILLION", 1000, 150, ga - T_LABEL, size=76)
    return compose(bg, fg, ov, dof=4.0)


def shot_card(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    sets.text_card(c, CARD_TEXT, t - 0.05, W, H, cps=CARD_CPS)
    return arr(surf)[..., :3]


# ------------------------------------------------------------------ compositing
def compose(bg, fg, ov, dof=0.0):
    b = arr(bg)[..., :3]
    if dof > 0:
        b = cv2.GaussianBlur(b, (0, 0), dof)
    f = arr(fg)
    img = b * (1 - f[..., 3:4]) + f[..., :3]
    # bloom only from real light sources (flames, bulbs): luminance above 0.95
    lum = (img[..., 0:1] * 0.114 + img[..., 1:2] * 0.587 + img[..., 2:3] * 0.299)   # B,G,R order
    bright = img * np.clip((lum - 0.95) / 0.05, 0, 1)
    img = img + cv2.GaussianBlur(bright, (0, 0), 24) * 0.9
    o = arr(ov)
    return img * (1 - o[..., 3:4]) + o[..., :3]


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.45 * (((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2)).clip(0.4, 1)[..., None]
RNG = np.random.default_rng(7)


def hblur(img, n):
    n = int(n)
    if n < 3:
        return img
    return cv2.filter2D(img, -1, np.ones((1, n), np.float32) / n)


def frame(t):
    if t < T_WHIP0:
        img = shot_wide(t)
    elif t < T_WHIP1:
        p = ease((t - T_WHIP0) / (T_WHIP1 - T_WHIP0))
        a, b = shot_wide(t), shot_close(t - T_WHIP0)
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
    return img + RNG.normal(0, 0.01, img.shape[:2])[..., None].astype(np.float32)


# ------------------------------------------------------------------ sound
def soundtrack(path):
    n = int(audio.SR * TOTAL)
    mix = np.zeros(n)

    def put(x, at, vol):
        s = int(at * audio.SR)
        e = min(n, s + len(x))
        mix[s:e] += np.asarray(x[:e - s]) * vol

    put(audio.music_ref(TOTAL), 0, 0.55)
    put(audio.bell(), 0.9, 0.18)
    put(audio.whoosh(), T_WHIP0 - 0.03, 0.35)
    put(audio.pop(), T_WHIP1 + 0.15, 0.45)
    put(audio.sting_soft(), T_SNAP, 0.6)
    put(audio.pop(), T_LABEL, 0.7)
    for i, ch in enumerate(CARD_TEXT):
        if ch != " ":
            put(audio.tick(), T_CARD + 0.05 + i / CARD_CPS, 0.35)
    audio.save(path, mix)


def main(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    if only is not None:      # quick still frames: python3 animator/sample6.py 1.2 3.0
        for tt in only:
            img = (np.clip(frame(tt), 0, 1) * 255).astype(np.uint8)
            cv2.imwrite(str(OUT / f"still_{tt:.2f}.png"), img)
        return
    wav = OUT / "sample6.wav"
    soundtrack(wav)
    silent = OUT / "sample6_video.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                          "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)):
        bgr = (np.clip(frame(i / FPS), 0, 1) * 255).astype(np.uint8)   # cairo bytes are B,G,R,A
        p.stdin.write(np.ascontiguousarray(bgr).tobytes())
    p.stdin.close()
    p.wait()
    out = OUT / "sample6.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main([float(a) for a in sys.argv[1:]] or None)
