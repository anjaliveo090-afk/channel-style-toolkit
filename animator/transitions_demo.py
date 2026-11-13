"""Reel of every place + transition (about 31 s, 16:9). The small yellow label bottom-left names each
transition (demo only, not part of the style). Run: python3 animator/transitions_demo.py"""
import math
import sys
from pathlib import Path

import cairo
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio  # noqa: E402
import places as P  # noqa: E402
import render16 as R  # noqa: E402
import sets  # noqa: E402
import transitions as TR  # noqa: E402
from style import Char  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "output" / "transitions"
A = Char(body="#e2805a", hair="bun", collar="shirt")
B = Char(body="#c9c6c0", hair="bowl", glasses="round", collar="shirt", pants="#2f3a55")
SPY = Char(body="#1c1c22", hair="bowl", collar="shirt", lapels=True)
BOSS = Char(body="#23436b", hair="side", hair_col="#5a4030", glasses="rect", tie="#a3161d", lapels=True)
NIGHT = dict(ambient=(0.62, 0.68, 0.9), rim="#bcd4ff")

SEG = [  # (start, name)
    (0.0, "whip-pan"), (3.0, "zoom-through"), (6.0, "black text card"), (8.2, "chapter card"),
    (10.0, "viewfinder + polaroids"), (13.0, "calendar page flip"), (15.5, "split screen (phone call)"),
    (19.0, "whiteboard + magnifier lens"), (23.0, "fast pull-out reveal"), (25.5, "impact flash"),
    (28.0, "circle wipe"), (31.0, "end")]
TOTAL = 31.0


def scene(place, t, zoom=1.0, center=(640, 360), chars=(), dof=1.5, night=False, extra=None, kw=None, parallax=0.8):
    bg, fg, ov = R.layers()
    c = cairo.Context(bg)
    R.cam(c, 1 + (zoom - 1) * parallax, *center)
    info = P.PLACES[place](c, t, **(kw or {}))
    c = cairo.Context(fg)
    R.cam(c, zoom, *center)
    for ch, x, s, a in chars:
        ch.scene(**NIGHT) if night else ch.scene()
        ch.draw(c, x, info["floor"], s, t=t, **a)
    if extra:
        extra(c, t)
    return R.compose(bg, fg, ov, dof=dof), info


def living(t, z=1.0):
    return scene("living_room", t, z, chars=((A, 470, 1.4, dict(expr="talk", look=0.3)),
                                             (B, 780, 1.4, dict(expr="happy", look=-0.3))))[0]


def porch(t, z=1.0, center=(665, 155)):
    return scene("porch_sunset", t, z, center=center, parallax=1.0, chars=((A, 470, 1.3, dict(expr="happy", pose="back")),
                                                               (B, 1000, 1.3, dict(expr="neutral", look=-0.4))))[0]


def card(text, t, cps=16.0):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    sets.text_card(cairo.Context(s), text, t, cps=cps)
    return R.flat(s)


def corridor(t):
    def extra(c, tt):
        c.identity_matrix()
        for k, (x, y, a) in enumerate(((330, 170, -0.1), (640, 150, 0.06), (950, 175, -0.04))):
            TR.polaroid(c, x, y, tt - (10.6 + k * 0.35), lambda cc, w, h, k=k: _photo(cc, w, h, k), angle=a)
        TR.viewfinder(c, tt)
    z = R.push(t - 10, 3.0, 1.0, 1.12)
    return scene("school_corridor", t, z, center=(640, 420), chars=((SPY, 640, 1.5, dict(expr="sly", look=0.0)),),
                 extra=extra)[0]


def _photo(c, w, h, k):
    c.set_source_rgb(*sets.hexc(["#e9a561", "#8ab4d8", "#c8d8a0"][k]))
    c.paint()
    Char(body=["#c9502e", "#3e6fa8", "#5c8a3c"][k], hair=["bun", "bowl", "side"][k]).draw(c, w / 2, h + 60, 1.0, expr="neutral", t=k)


def calendar_flip(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    c = cairo.Context(s)
    c.set_source_rgb(*sets.hexc("#1d2c52"))
    c.paint()
    sets.glow(c, 640, 330, 520, sets.hexc("#cfe0ff"), 0.25)
    p = (t - 14.0) / 0.7
    TR.page_flip(c, max(0.0, p), 640, 360, lambda cc: P.calendar(cc, 640, 360, "AUG", 2022),
                 lambda cc: P.calendar(cc, 640, 360, "SEP", 2022))
    return R.flat(s)


def office_pair(t):
    left, _ = scene("night_office", t, 1.25, center=(420, 420), night=True,
                    chars=((BOSS, 330, 1.6, dict(expr="talk" if int(t * 1.5) % 2 == 0 else "neutral", look=0.4,
                                                 arms={"r": (420, 470)}, item="phone")),))
    right, _ = scene("tech_office", t, 1.25, center=(860, 420), kw=dict(board_lines=("BEST CHIPS: OK",)),
                     chars=((B, 900, 1.6, dict(expr="worried" if t > 17.5 else "talk", look=-0.4,
                                                arms={"l": (820, 470)}, item="phone", item_hand="l")),))
    return TR.split_screen(left, right, (t - 15.5) / 0.6, t=t)


LINES = ("BEST CHIPS: BLOCKED", "CHINA CHIPS: BLOCKED", "$17B / YEAR")


def office_board(t, k):
    return scene("tech_office", t, 1.0 + 0.05 * k, kw=dict(board_lines=LINES[:0]),
                 chars=((B, 420, 1.4, dict(expr="worried", look=0.5, arms="point_r")),),
                 extra=lambda c, tt: P.whiteboard(c, 620, 70, 560, 320, LINES, (tt - 19.2) / 1.6))[0]


def board_detail(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    c = cairo.Context(s)
    c.translate(900, 200)
    c.scale(2.2, 2.2)
    c.translate(-900, -200)
    P.whiteboard(c, 620, 70, 560, 320, LINES, 1.0)
    return R.flat(s)


def void(t):
    z = TR.pull_out(t, 23.2, 1.4, 5.0, 1.0)
    return scene("void_spotlight", t, z, center=(700, 330), dof=0,
                 chars=((BOSS, 640, 1.8, dict(expr="smirk", arms="raise_r", item="key")),))[0]


def diner_cheque(t, big=False):
    def extra(c, tt):
        c.identity_matrix()
        P.cheque(c, 640, 400, "PAPERWORKS CO.", "$2,000,000", 1.25 if big else 0.95, (tt - 25.8) / 0.8)
    return scene("diner", t, 1.0 + (0.08 if big else 0.0), chars=((A, 300, 1.4, dict(expr="laugh")),
                                                                  (B, 980, 1.4, dict(expr="shock"))), extra=extra)[0]


def city(t):
    return scene("night_city", t, R.push(t - 28, 3.0, 1.0, 1.1), dof=0)[0]


def frame(t):
    if t < 2.6:
        img = living(t, R.push(t, 2.6, 1.0, 1.08))
    elif t < 2.95:
        img = R.whip(living(t, 1.08), porch(t), (t - 2.6) / 0.35)
    elif t < 5.4:
        img = porch(t, R.push(t - 3, 2.4, 1.0, 1.06))
    elif t < 6.0:
        img = porch(t, TR.zoom_through(t, 5.4, 0.55, 1.06, 4.5))        # push through the window, then cut
    elif t < 8.2:
        return card("They know exactly who she is.", t - 6.0)
    elif t < 10.0:
        return card("The Paper Trail", 99, cps=99)
    elif t < 13.0:
        img = corridor(t)
    elif t < 15.5:
        img = calendar_flip(t)
    elif t < 19.0:
        img = office_pair(t)
    elif t < 21.2:
        img = office_board(t, (t - 19) / 2.2)
    elif t < 23.0:
        img = TR.magnifier(office_board(t, 1.0), board_detail(t), (t - 21.2) / 1.6, 900, 200)
    elif t < 25.5:
        img = void(t)
    elif t < 26.9:
        img = diner_cheque(t)
    elif t < 27.0:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
        sets.impact_flash(cairo.Context(s), (t - 26.9) / 0.1)
        return R.flat(s)
    elif t < 28.0:
        img = diner_cheque(t, big=True)
    elif t < 29.0:
        img = TR.circle_wipe(diner_cheque(t, big=True), city(t), (t - 28.0) / 1.0, 640, 360)
    else:
        img = city(t)
    img = R.post(img)
    # demo label
    name = [n for s, n in SEG if s <= t][-1]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    c = cairo.Context(s)
    c.select_font_face("Caveat Brush")
    c.set_font_size(30)
    c.move_to(24, R.H - 24)
    c.text_path(name)
    c.set_source_rgb(0, 0, 0)
    c.set_line_width(6)
    c.stroke_preserve()
    c.set_source_rgb(1, 0.92, 0.2)
    c.fill()
    o = R.arr(s)
    return img * (1 - o[..., 3:4]) + o[..., :3]


def soundtrack(path):
    m = R.Mixer(TOTAL)
    m.voice[int(0.1 * R.SR)] = 0.5            # no voice in this reel: tiny anchor so levels compute
    m.add_music(audio.music_chapters(TOTAL, [(0, "major", 53), (8.2, "minor", 50), (23.0, "major", 55)]))
    ev = [(2.6, audio.whoosh(), "swish"), (5.4, audio.whoosh(), "swish"), (8.2, audio.sting(), "sting"),
          (10.6, audio.pop(), "pop"), (10.95, audio.pop(), "pop"), (11.3, audio.pop(), "pop"),
          (14.0, audio.page(), "swish"), (15.5, audio.bell(), "ding"), (19.2, audio.tick(), "tick"),
          (21.2, audio.whoosh(), "swish"), (23.2, audio.whoosh(), "swish"), (25.8, audio.pop(), "pop"),
          (26.9, audio.thud(), "thud"), (27.0, audio.coin(), "ding"), (28.0, audio.whoosh(), "swish")]
    for i, ch in enumerate("They know exactly who she is."):
        if ch != " ":
            ev.append((6.0 + i / 16, audio.tick(), "tick"))
    for k in range(18):
        ev.append((19.2 + k * 0.09, audio.tick(), "tick"))
    for at, x, kind in ev:
        m.add_sfx(x, at, kind, 14)            # no voice: lift SFX so they are audible over the music
    m.render(path, music_db=8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wav = OUT / "reel.wav"
    soundtrack(wav)
    R.encode(frame, TOTAL, OUT / "reel_video.mp4")
    R.mux(OUT / "reel_video.mp4", wav, OUT / "transitions_reel.mp4")
    print(OUT / "transitions_reel.mp4")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        import cv2
        for a in sys.argv[1:]:
            tt = float(a)
            cv2.imwrite(str(OUT / f"still_{tt:.2f}.png"), (np.clip(frame(tt), 0, 1) * 255).astype(np.uint8))
    else:
        main()
