"""16:9 render engine for the Paper Billions style (1280x720 @ 24 fps by default).

Layers per frame: bg (blurred for depth of field) -> fg (characters, props) -> ov (tags, labels),
then bloom from real light sources, vignette and light grain (style_bible.md section 4).
Sound: voice + music + SFX mixed to the measured targets (sound_design.md section 4):
music -22 dB under the voice, SFX by kind (pop -15, tick -20, ding -10, thud -6, sting 0 dB).
"""
import math
import subprocess
import wave

import cairo
import cv2
import numpy as np

W, H, FPS = 1280, 720, 24
SR = 44100


def layers():
    return [cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H) for _ in range(3)]


def arr(surf):
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))
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


def compose(bg, fg, ov, dof=0.0, bloom=0.9):
    b = arr(bg)[..., :3]
    if dof > 0:
        b = cv2.GaussianBlur(b, (0, 0), dof)
    f = arr(fg)
    img = b * (1 - f[..., 3:4]) + f[..., :3]
    lum = img[..., 0:1] * 0.114 + img[..., 1:2] * 0.587 + img[..., 2:3] * 0.299
    bright = img * np.clip((lum - 0.95) / 0.05, 0, 1)
    img = img + cv2.GaussianBlur(bright, (0, 0), 24) * bloom
    o = arr(ov)
    return img * (1 - o[..., 3:4]) + o[..., :3]


def flat(surf):
    return arr(surf)[..., :3]


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.42 * (((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2)).clip(0.4, 1)[..., None]
_RNG = np.random.default_rng(7)


def post(img, vignette=True, grain=0.008):
    if vignette:
        img = img * VIG
    if grain:
        img = img + _RNG.normal(0, grain, img.shape[:2])[..., None].astype(np.float32)
    return img


def hblur(img, n):
    n = int(n)
    if n < 3:
        return img
    return cv2.filter2D(img, -1, np.ones((1, n), np.float32) / n)


def whip(a, b, p):
    """Whip-pan from image a to image b, p = 0..1 (measured 0.25-0.4 s)."""
    p = ease(p)
    dx = int(p * W)
    img = np.zeros_like(a)
    img[:, :W - dx] = a[:, dx:]
    img[:, W - dx:] = b[:, :dx]
    return hblur(img, 150 * math.sin(math.pi * p) + 1)


def encode(frame_fn, total, out_path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
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
