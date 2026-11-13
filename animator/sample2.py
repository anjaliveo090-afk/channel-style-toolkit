"""Sample 2: built on the every-frame rules (visual_grammar.md sections 12-15). Original story/characters.
Voice: placeholder TTS (output/sample2/l*.wav). Run: python3 animator/sample2.py -> output/sample2/sample2.mp4

Beats (one device per phrase, something animating ~every second):
  1 "Monday, the ninth of November."      calendar pages tear off OCT -> NOV, clock ticks
  2 "Meet Felix Brandt..."                 hard cut to close-up, name tag box then name types on, glint
  3 "...stock falls four percent."         office: whiteboard written LIVE by a marker hand, red arrow down,
                                           SELL stamp slams
  4 "two hundred million dollars, gone"    RIP transition -> cash tower stacks with a rolling counter, impact
                                           flash, tower collapses, counter turns red
  5-6 skit "Is that a lot?" / "...for a cup." two-shot, speaker's mouth talks, expression snaps
  7 "And Felix has no idea why."           black card typed with ticks
"""
import math
import sys
from pathlib import Path

import cairo
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio  # noqa: E402
import devices as D  # noqa: E402
import places as P  # noqa: E402
import render16 as R  # noqa: E402
import sets  # noqa: E402
import transitions as TR  # noqa: E402
from style import Char  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "output" / "sample2"
FELIX = Char(body="#1f2a44", hair="side", hair_col="#5a3a26", glasses="round", collar="shirt", tie="#a3161d",
             lapels=True, pants="#141a2a", light=(1.0, 0.25), pin="#d9b44a")
TRADER = Char(body="#c9502e", hair="bowl", collar="shirt", pants="#2f3a55", light=(-1, -0.2))
ANALYST = Char(body="#2f7a4f", hair="bun", hair_col="#6e2a18", glasses="round", collar="round",
               earrings="#e8c050", build=0.9, light=(1, -0.2))

# ---------------- timeline from the voice
LINES = [l.split("\t") for l in (OUT / "lines.tsv").read_text().strip().split("\n")]
T, clips, t = [], [], 0.3
for i, (who, txt) in enumerate(LINES, 1):
    x = R.trim(R.load_wav(OUT / f"l{i}.wav"))
    d = len(x) / R.SR
    T.append((t, t + d, who, txt))
    clips.append((x, t))
    t += d + (0.3 if who == "N" else 0.35)
TOTAL = T[-1][1] + 1.6
L = {k + 1: v for k, v in enumerate(T)}


def wt(line, word):
    s, e, _, txt = L[line]
    i = txt.lower().find(word.lower())
    return s + (e - s) * max(i, 0) / max(1, len(txt))


T_NAME = L[2][0]
T_OFFICE = L[3][0]
T_RIP = L[4][0] - 0.25
T_SKIT = L[5][0] - 0.2
T_CARD = L[7][0]
T_FALL = wt(3, "falls")
T_GONE = wt(4, "gone")


# ---------------- shots
def cal(t):
    bg, fg, ov = R.layers()
    c = cairo.Context(bg)
    c.set_source_rgb(*sets.hexc("#1d2c52"))
    c.paint()
    sets.glow(c, 640, 300, 560, sets.hexc("#cfe0ff"), 0.22)
    # wall clock, ticking
    c.arc(1010, 170, 60, 0, 2 * math.pi)
    sets._fill_line(c, sets.hexc("#f2efe6"), 5)
    a = -math.pi / 2 + int(t * 2) * (math.pi / 30)
    c.move_to(1010, 170)
    c.line_to(1010 + 48 * math.cos(a), 170 + 48 * math.sin(a))
    c.set_source_rgb(0.8, 0.1, 0.1)
    c.set_line_width(3)
    c.stroke()
    c = cairo.Context(fg)
    z = R.push(t, 2.2, 1.0, 1.12)
    R.cam(c, z, 640, 360)
    p = (t - 0.35) / 0.35
    if p < 1:
        TR.page_flip(c, max(0, p), 640, 360, lambda cc: P.calendar(cc, 640, 360, "OCT", 2026, 1.1),
                     lambda cc: P.calendar(cc, 640, 360, "NOV", 2026, 1.1))
    else:
        P.calendar(c, 640, 360, "NOV", 2026, 1.1)
        D.marker_circle(c, 640, 470, 70, 50, t - 1.0)
    return R.compose(bg, fg, ov, dof=2.0)


def restaurant_bg(c, t):
    sets.wood_wall(c, rail_y=470, panel=(700, 960))
    sets.night_window(c, 1040, -10, 1290, 470, t)
    sets.curtain(c, 965, 1040, 470)
    sets.sconce(c, 775, 175, 1.1)


def felix_close(t):
    bg, fg, ov = R.layers()
    lt = t - T_NAME
    z = R.push(lt, 2.5, 1.0, 1.1)
    c = cairo.Context(bg)
    R.cam(c, 2.0 * z, 760, 260)
    P.tech_office(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, 478, 280)
    k_big = wt(2, "biggest")
    FELIX.draw(c, 478, 280 + 3.5 * 225 - 30, 5.6, pose="sit", t=t, look=0.25,
               expr="happy" if t < k_big else "smirk", talk=False,
               arms={"r": (900, 420 - 80 * R.ease((t - k_big) / 0.3)), "l": (300, 1000)}, item="phone", item_hand="r")
    c = cairo.Context(ov)
    sets.name_tag(c, "FELIX BRANDT", 765, 532, 415, 108, (lt - 0.15) / 0.35)
    D.glow_label(c, 1000, 170, t - wt(2, "paper cup"), "#1 CUPS", size=56)
    return R.compose(bg, fg, ov, dof=4.0)


BOARD = ("CUPWELL  -4%",)


def office(t):
    bg, fg, ov = R.layers()
    lt = t - T_OFFICE
    z = R.push(lt, 3.0, 1.0, 1.1)
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.6, 640, 360)
    P.tech_office(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, 860, 260)
    kw = t - (T_OFFICE + 0.15)

    def extra(cc):
        D.arrow_down(cc, 1030, 140, t - (T_FALL + 0.35), 150)
        D.stamp(cc, 960, 330, t - (T_FALL + 0.8), "SELL", angle=-0.15, size=58)
    D.whiteboard_live(c, 620, 70, 560, 320, BOARD, kw, cps=12, size=56, extra=extra)
    FELIX.draw(c, 360, 640, 1.5, t=t, look=0.6, expr="worried" if t > T_FALL + 0.5 else "neutral",
               arms="point_r" if t > T_FALL else "rest")
    return R.compose(bg, fg, ov, dof=1.5)


def tower(t):
    bg, fg, ov = R.layers()
    lt = t - T_RIP
    c = cairo.Context(bg)
    c.set_source_rgb(*sets.hexc("#2a1610"))
    c.paint()
    sets.glow(c, 640, 360, 640, sets.hexc("#ffcf80"), 0.35)
    c.rectangle(-10, 560, 1300, 200)
    c.set_source_rgb(*sets.hexc("#5a3020"))
    c.fill()
    c = cairo.Context(fg)
    z = 1.0 + 0.12 * R.ease_out(lt / 1.2)
    R.cam(c, z, 640, 400)
    collapse = T_GONE - T_RIP + 0.1
    D.cash_tower(c, 640, 570, lt, n_max=14, build=1.0, collapse_at=collapse)
    c = cairo.Context(ov)
    if lt < collapse:
        D.counter_box(c, 1030, 600, lt, 200_000_000, sub="CUPWELL VALUE", dur=0.9, w=330)
    else:
        sh = 6 * math.exp(-(lt - collapse) * 8) * math.sin((lt - collapse) * 60)
        c.save()
        c.translate(sh, 0)
        c.rectangle(865, 557, 330, 86)
        sets._fill_line(c, sets.hexc("#3a0d0d"), 3)
        sets.pop_label(c, "-$200,000,000", 1030, 600, 1.0, col="#ff5a4a", size=46, angle=0)
        c.restore()
    return R.compose(bg, fg, ov, dof=0, bloom=0.6)


def skit(t):
    bg, fg, ov = R.layers()
    s5, e5 = L[5][0], L[5][1]
    s6, e6 = L[6][0], L[6][1]
    single = (t >= s6 - 0.05)
    c = cairo.Context(bg)
    if not single:
        R.cam(c, 1.4, 640, 360)
    else:
        R.cam(c, 2.0, 900, 330)
    P.server_corridor(c, t, photo=False)
    c = cairo.Context(fg)
    for ch in (TRADER, ANALYST):
        ch.scene(ambient=(0.62, 0.68, 0.9), rim="#bcd4ff")
    if not single:
        R.cam(c, R.push(t - T_SKIT, 1.5, 1.0, 1.06), 640, 360)
        TRADER.draw(c, 470, 820, 2.8, t=t, look=0.4, expr="worried", talk=s5 <= t <= e5)
        ANALYST.draw(c, 820, 820, 2.8, t=t + 1, look=-0.4, expr="deadpan")
    else:
        R.cam(c, R.push(t - s6, 1.2, 1.0, 1.06), 760, 300)
        ANALYST.draw(c, 760, 300 + 4.3 * 160, 4.0, t=t + 1, look=-0.3,
                     expr="smirk" if t > e6 else "deadpan", talk=s6 <= t <= e6)
    return R.compose(bg, fg, ov, dof=2.5)


def card(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    txt = L[7][3]
    sets.text_card(cairo.Context(s), txt, t - T_CARD, cps=len(txt) / max(0.8, (L[7][1] - L[7][0]) * 0.9))
    return R.flat(s)


def frame(t):
    if t < T_NAME:
        img = cal(t)
    elif t < T_OFFICE:
        img = felix_close(t)
    elif t < T_RIP:
        img = office(t)
    elif t < T_RIP + 0.45:
        img = TR.rip(office(t), tower(t), (t - T_RIP) / 0.45)
    elif t < T_SKIT:
        fl = T_GONE - 0.02
        if fl <= t < fl + 3 / R.FPS:
            s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
            sets.impact_flash(cairo.Context(s), (t - fl) * R.FPS / 3)
            return R.flat(s)
        img = tower(t)
    elif t < T_CARD:
        img = skit(t)
    else:
        return card(t)
    return R.post(img)


def soundtrack(path):
    m = R.Mixer(TOTAL)
    for x, at in clips:
        m.add_voice(x, at)
    m.add_music(audio.music_chapters(TOTAL, [(0, "minor", 50)]))
    m.add_sfx(audio.thud(), 0.05, "thud", 3)
    m.add_sfx(audio.page(), 0.35, "swish")
    m.add_sfx(audio.tick(), 1.0, "tick")
    m.add_sfx(audio.pop(), T_NAME + 0.05, "pop")
    for i in range(12):
        m.add_sfx(audio.tick(), T_NAME + 0.1 + i * 0.04, "tick", -6)
    m.add_sfx(audio.sparkle(), wt(2, "paper cup"), "ding")
    for i in range(len(BOARD[0])):
        m.add_sfx(audio.tick(), T_OFFICE + 0.15 + i / 12, "tick", -4)
    m.add_sfx(audio.whoosh(), T_FALL + 0.35, "swish", -2)
    m.add_sfx(audio.thud(), T_FALL + 0.8, "thud")
    m.add_sfx(audio.whoosh(), T_RIP, "swish")
    for i in range(14):
        m.add_sfx(audio.pop(), T_RIP + i * 1.0 / 14, "tick", -2)
    m.add_sfx(audio.thud(), T_GONE, "thud", 2)
    m.add_sfx(audio.sting_low(), T_GONE + 0.05, "sting", -4)
    m.add_sfx(audio.pop(), L[5][0], "pop", -2)
    m.add_sfx(audio.pop(), L[6][1] + 0.1, "pop")
    txt = L[7][3]
    cps = len(txt) / max(0.8, (L[7][1] - L[7][0]) * 0.9)
    for i, ch in enumerate(txt):
        if ch != " ":
            m.add_sfx(audio.tick(), T_CARD + i / cps, "tick", -3)
    m.render(path, music_db=-21)


def main():
    wav = OUT / "sample2.wav"
    soundtrack(wav)
    R.encode(frame, TOTAL, OUT / "video.mp4")
    R.mux(OUT / "video.mp4", wav, OUT / "sample2.mp4")
    print(OUT / "sample2.mp4", round(TOTAL, 2))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        import cv2
        for a in sys.argv[1:]:
            cv2.imwrite(str(OUT / f"still_{float(a):.2f}.png"), (np.clip(frame(float(a)), 0, 1) * 255).astype(np.uint8))
        print({k: (round(v[0], 2), round(v[1], 2)) for k, v in L.items()})
    else:
        main()
