"""16:9 render engine for the Paper Billions style (1280x720 @ 24 fps by default).

All drawing is in a 1280x720 design space. PB_SCALE renders it at a higher pixel size (cairo device scale):
PB_SCALE=1.5 -> 1920x1080, PB_SCALE=3 -> 3840x2160 (4K). PB_FPS sets the frame rate (24 or 30).

Layers per frame: bg (blurred for depth of field) -> fg (characters, props) -> ov (tags, labels),
then bloom from real light sources, vignette and light grain (style_bible.md section 4).
Sound: voice + music + SFX mixed to the measured targets (sound_design.md section 4):
music -22 dB under the voice, SFX by kind (pop -15, tick -20, ding -10, thud -6, sting 0 dB).
"""
import math
import os
import subprocess
import wave

import cairo
import cv2
import numpy as np

W, H = 1280, 720                       # design space (all drawing code uses these)
S = float(os.environ.get("PB_SCALE", "1"))
FPS = int(os.environ.get("PB_FPS", "24"))
PW, PH = int(round(W * S)), int(round(H * S))   # pixel size of the output
SR = 44100


def surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, PW, PH)
    s.set_device_scale(S, S)
    return s


def layers():
    return [surface() for _ in range(3)]


def arr(surf):
    surf.flush()
    a = np.ndarray((surf.get_height(), surf.get_width(), 4), np.uint8, surf.get_data(),
                   strides=(surf.get_stride(), 4, 1))
    return a.astype(np.float32) / 255.0


def cam(ctx, zoom, cx, cy, dx=0.0, dy=0.0):
    """Zoom about world point (cx, cy) and slide by (dx, dy) screen px."""
    ctx.translate(cx + dx, cy + dy)
    ctx.scale(zoom, zoom)
    ctx.translate(-cx, -cy)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def push(t, dur, z0=1.0, z1=1.16):
    """Measured push-in: starts fast, settles (ease-out), ~6-9 %/s."""
    return z0 + (z1 - z0) * ease_out(t / max(dur, 1e-3))


def gblur(img, sigma):
    """Gaussian blur; a big radius is done on a smaller copy (same look, a fraction of the cost at 4K)"""
    f = int(sigma / 3)
    if f < 2:
        return cv2.GaussianBlur(img, (0, 0), sigma)
    h, w = img.shape[:2]
    small = cv2.resize(img, (max(1, w // f), max(1, h // f)), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / f)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


def u8(surf):
    """the surface's pixels as a writable uint8 (H, W, 4) B-G-R-A view"""
    surf.flush()
    return np.ndarray((surf.get_height(), surf.get_width(), 4), np.uint8, surf.get_data(),
                      strides=(surf.get_stride(), 4, 1))


def compose_float(bg, fg, ov, dof=0.0, bloom=0.9):
    """reference implementation (numpy, slow at 4K); compose() gives the same picture"""
    b = arr(bg)[..., :3]
    if dof > 0:
        b = gblur(b, dof * S)
    f = arr(fg)
    img = b * (1 - f[..., 3:4]) + f[..., :3]
    lum = img[..., 0:1] * 0.114 + img[..., 1:2] * 0.587 + img[..., 2:3] * 0.299
    bright = img * np.clip((lum - 0.95) / 0.05, 0, 1)
    img = img + gblur(bright, 24 * S) * bloom
    o = arr(ov)
    return img * (1 - o[..., 3:4]) + o[..., :3]


def compose(bg, fg, ov, dof=0.0, bloom=0.9):
    """bg (blurred for depth of field) -> fg over it -> bloom from the bright parts -> ov on top.
    Layers are stacked by cairo in 8-bit (fast at 4K); only the blurs touch numpy."""
    if dof > 0:
        v = u8(bg)
        v[:] = gblur(v, dof * S)
        bg.mark_dirty()
    c = cairo.Context(bg)
    c.set_source_surface(fg, 0, 0)
    c.paint()
    bl = None
    if bloom > 0:                    # bloom is found on a small copy, then added in float (keeps the >1 headroom)
        v = u8(bg)
        h, w = v.shape[:2]
        f = max(2, int(8 * S))
        sw, sh = max(1, w // f), max(1, h // f)
        small = cv2.resize(v[..., :3], (sw, sh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        lum = small[..., 0:1] * 0.114 + small[..., 1:2] * 0.587 + small[..., 2:3] * 0.299
        bright = small * np.clip((lum - 0.95) / 0.05, 0, 1)
        bl = cv2.GaussianBlur(bright, (0, 0), 24 * S / f) * bloom
        if bl.max() < 1 / 512:
            bl = None
    c.set_source_surface(ov, 0, 0)
    c.paint()
    img = arr(bg)[..., :3]
    if bl is not None:
        up = cv2.resize(bl, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
        oa = u8(ov)[..., 3]
        if oa.any():
            up *= 1 - oa[..., None].astype(np.float32) / 255.0
        img += up
    return img


def flat(surf):
    return arr(surf)[..., :3]


_yy, _xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
VIG = (1 - 0.42 * (((_xx - PW / 2) / (PW * 0.62)) ** 2 + ((_yy - PH / 2) / (PH * 0.62)) ** 2)).clip(0.4, 1)[..., None]
del _yy, _xx
_RNG = np.random.default_rng(7)
_GRAIN = []


def post(img, vignette=True, grain=0.008):
    if vignette:
        img = img * VIG
    if grain:
        if not _GRAIN:      # 12 pre-made grain fields, picked at random per frame (fresh noise each frame is slow at 4K)
            _GRAIN.extend(_RNG.normal(0, 1, img.shape[:2]).astype(np.float16) for _ in range(12))
        img = img + (grain * _GRAIN[int(_RNG.integers(12))].astype(np.float32))[..., None]
    return img


def hblur(img, n):
    n = int(n)
    if n < 3:
        return img
    return cv2.filter2D(img, -1, np.ones((1, n), np.float32) / n)


def whip(a, b, p):
    """Whip-pan from image a to image b, p = 0..1 (measured 0.25-0.4 s)."""
    p = ease(p)
    w = a.shape[1]
    dx = int(p * w)
    img = np.zeros_like(a)
    img[:, :w - dx] = a[:, dx:]
    img[:, w - dx:] = b[:, :dx]
    return hblur(img, (150 * math.sin(math.pi * p) + 1) * S)


def encode(frame_fn, total, out_path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{PW}x{PH}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                          "-pix_fmt", "yuv420p", str(out_path)], stdin=subprocess.PIPE)
    for i in range(int(round(total * FPS))):
        bgr = (np.clip(frame_fn(i / FPS), 0, 1) * 255).astype(np.uint8)
        p.stdin.write(np.ascontiguousarray(bgr).tobytes())
    p.stdin.close()
    p.wait()


def mux(video, wav, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)


# ------------------------------------------------------------------ sound
def load_wav(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def trim(x, th_db=-40):
    env = np.abs(x)
    th = env.max() * 10 ** (th_db / 20)
    idx = np.where(env > th)[0]
    if len(idx) == 0:
        return x
    a, b = max(0, idx[0] - int(0.01 * SR)), min(len(x), idx[-1] + int(0.03 * SR))
    return x[a:b]


def active_rms(x):
    env = np.abs(x)
    k = int(0.02 * SR)
    fr = np.sqrt(np.convolve(x * x, np.ones(k) / k, "same"))
    act = fr[fr > fr.max() * 0.1] if fr.max() > 0 else fr
    return float(np.sqrt(np.mean(act ** 2))) if len(act) else 1e-9


SFX_DB = {"pop": -27, "tick": -29, "ding": -20, "thud": -13, "sting": -6, "swish": -24, "coin": -21}   # calibrated: audio_ref reads these ~14 dB higher (ref median -16.7)


class Mixer:
    def __init__(self, total):
        self.n = int(SR * total)
        self.voice = np.zeros(self.n)
        self.music = np.zeros(self.n)
        self.sfx = np.zeros(self.n)
        self.sfx_list = []

    @staticmethod
    def _put(buf, x, at):
        s = int(at * SR)
        e = min(len(buf), s + len(x))
        if 0 <= s < len(buf):
            buf[s:e] += x[:e - s]

    def add_voice(self, x, at):
        self._put(self.voice, x, at)

    def add_music(self, x):
        self._put(self.music, x, 0)

    def add_sfx(self, x, at, kind, db_offset=0.0):
        self.sfx_list.append((np.asarray(x, np.float64), at, kind, db_offset))

    def render(self, path, music_db=-22.0):
        v = self.voice / (np.abs(self.voice).max() or 1) * 0.5
        vr = active_rms(v)
        if np.abs(self.music).max() > 0:
            self.music *= vr * 10 ** (music_db / 20) / (active_rms(self.music) or 1)
        for x, at, kind, off in self.sfx_list:
            g = vr * 10 ** ((SFX_DB.get(kind, -15) + off) / 20) / (active_rms(x) or 1)
            self._put(self.sfx, x * g, at)
        mix = v + self.music + self.sfx
        peak = np.abs(mix).max() or 1
        if peak > 0.97:
            mix *= 0.97 / peak
        st = np.stack([mix, mix], 1)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((st * 32767).astype(np.int16).tobytes())
