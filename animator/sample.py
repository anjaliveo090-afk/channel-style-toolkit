"""~30 s sample in the Paper Billions style (16:9, 1280x720, 24 fps). Original story, characters, text.

Voice: placeholder TTS lines (espeak-ng + mbrola, output/sample/l*.wav). For a real video, replace them with
the user's voiceover + word timings (analysis/align_words.py) and keep the shot logic.

Beats (visual_grammar.md section 3):
  cold open two-shot -> close-up + name tag + number label -> whip-pan -> close-up + name tag ->
  dialogue toast (mouths talk on their own lines) -> black text card typed with the line ->
  chapter card (2.4 s pause, sting, music changes minor -> major) -> paper map + pin ->
  mill exterior + 40 workers pop in -> contract with a rolling dollar counter + impact flash.
Run: python3 animator/sample.py -> output/sample/sample.mp4
"""
import sys
from pathlib import Path

import cairo
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio  # noqa: E402
import render16 as R  # noqa: E402
import sets  # noqa: E402
from style import Char  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "output" / "sample"

FELIX = Char(body="#1f2a44", hair="side", hair_col="#5a3a26", glasses="round", collar="shirt", tie="#a3161d",
             lapels=True, pants="#141a2a", light=(1.0, 0.35), pin="#d9b44a")
NORA = Char(body="#16654f", hair="bun", hair_col="#6e2a18", collar="round", earrings="#e8c050",
            pants="#1f2a26", light=(-1.0, 0.35), build=0.9,
            skin={"hi": "#fcd08a", "mid": "#dba37c", "sh": "#b38b73", "rim": "#febd6c"})
WORKER_COLS = ["#c9502e", "#3e6fa8", "#e0a23a", "#5c8a3c", "#8a4f9e", "#c7c2b8", "#2f4f6f", "#b5482f", "#6b7a3a", "#d77a5a"]

# ------------------------------------------------------------------ timeline from the voice lines
LINES = [l.split("\t") for l in (OUT / "lines.tsv").read_text().strip().split("\n")]
GAP, DIALOG_GAP, CHAPTER_PAUSE, HEAD = 0.3, 0.35, 2.4, 0.25
T = []          # (start, end, who, text)
clips = []
t = HEAD
for i, (who, txt) in enumerate(LINES, 1):
    if who == "CH":
        T.append((t, t + CHAPTER_PAUSE - GAP, who, txt))
        t += CHAPTER_PAUSE - GAP
        continue
    x = R.trim(R.load_wav(OUT / f"l{i}.wav"))
    d = len(x) / R.SR
    T.append((t, t + d, who, txt))
    clips.append((x, t))
    nxt = LINES[i][0] if i < len(LINES) else None
    t += d + (DIALOG_GAP if (who in "FV" or nxt in ("F", "V")) else GAP)
TOTAL = T[-1][1] + 1.2
L = {k + 1: v for k, v in enumerate(T)}       # 1-based like lines.tsv


def word_time(line, word):
    """Approximate time of a word inside a line (proportional to characters)."""
    s, e, _, txt = L[line]
    i = txt.lower().find(word.lower())
    return s + (e - s) * (max(i, 0) / max(1, len(txt)))


T_FELIX, T_NORA = L[2][0], L[3][0] - 0.3
T_TOAST, T_CARD = L[4][0] - 0.15, L[6][0]
T_CH, T_MAP, T_MILL, T_DOC = L[6][1] + 0.3, L[8][0], L[9][0], L[10][0]
WHIP = 0.3


# ------------------------------------------------------------------ restaurant shots
def restaurant(c, t):
    sets.wood_wall(c)
    sets.night_window(c, 905, -10, 1290, 215, t)
    sets.curtain(c, 860, 905, 470)
    sets.sconce(c, 690, 190)
    sets.booth_side(c, -40, 150, 120, studs_x=30, studs=(262, 300, 370, 440, 505, 580))
    sets.booth_side(c, 1150, 1330, 150, studs_x=1255, studs=(232, 300), flip=True)


def table_front(c, t):
    sets.tablecloth(c, 660, 603, 568, 42, glow_x=655)
    sets.plate(c, 430, 600)
    sets.plate(c, 885, 600)
    sets.roses_candle(c, 655, 600, t)


def two_shot(t, t0, dur, felix_kw, nora_kw):
    bg, fg, ov = R.layers()
    z = R.push(t - t0, dur, 1.0, 1.12)
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.7, 640, 360)
    restaurant(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, 640, 360)
    FELIX.draw(c, 255, 300 + 3.5 * 160, 4.0, pose="sit", t=t, **felix_kw)
    NORA.draw(c, 1040, 310 + 3.5 * 150, 3.75, pose="sit", t=t + 1.7, **nora_kw)
    table_front(c, t)
    FELIX.draw_arms_over(c, only=("l",))
    NORA.draw_arms_over(c, only=("r",))
    return R.compose(bg, fg, ov, dof=3.5)


def shot_open(t):
    k = R.ease((t - 1.6) / 0.4)
    return two_shot(t, 0, L[1][1], dict(expr="happy" if t < 3.2 else "laugh", look=0.35,
                                        arms={"r": (560 - (1 - k) * 60, 330 + (1 - k) * 220), "l": (455, 630)},
                                        item="wine", item_hand="r"),
                    dict(expr="smirk", look=-0.3, arms={"l": (1230, 640), "r": (850, 630)}))


def shot_toast(t):
    tf0, tf1 = L[4][0], L[4][1]
    tn0, tn1 = L[5][0], L[5][1]
    kf = R.ease((t - T_TOAST) / 0.35)
    kn = R.ease((t - (tn0 - 0.3)) / 0.35)
    return two_shot(t, T_TOAST, 3.0,
                    dict(expr="laugh" if tf0 <= t <= tf1 + 0.3 else "happy", talk=tf0 <= t <= tf1, look=0.35,
                         arms={"r": (600 - (1 - kf) * 60, 300 + (1 - kf) * 220), "l": (455, 630)},
                         item="wine", item_hand="r"),
                    dict(expr="sly" if t > tn1 else "smirk", talk=tn0 <= t <= tn1, look=-0.3,
                         arms={"l": (720 + (1 - kn) * 60, 300 + (1 - kn) * 220), "r": (850, 630)},
                         item="wine", item_hand="l"))


def close_felix(t):
    bg, fg, ov = R.layers()
    lt = t - T_FELIX
    z = R.push(lt, 2.0, 1.0, 1.15)
    c = cairo.Context(bg)
    R.cam(c, 2.1 * z, 380, 300)
    restaurant(c, t)
    c.identity_matrix()
    c.save()
    c.translate(1160, 600)
    c.scale(1.3, 1.3)
    c.translate(-1160, -600)
    sets.roses_candle(c, 1160, 690, t)
    c.restore()
    c = cairo.Context(fg)
    R.cam(c, z, 478, 250)
    t_num = word_time(2, "two billion")
    FELIX.draw(c, 478, 250 + 3.5 * 225, 5.625, pose="sit", t=t, look=0.2,
               expr="happy" if t < t_num else "smirk",
               arms={"r": (905, 420), "l": (300, 1000)}, item="wine", item_hand="r")
    c = cairo.Context(ov)
    sets.name_tag(c, "FELIX BRANDT", 765, 532, 415, 108, (lt - 0.15) / 0.35)
    sets.pop_label(c, "2,000,000,000 CUPS", 960, 150, t - t_num, col="#3d8b2f", size=62)
    return R.compose(bg, fg, ov, dof=4.0)


def close_nora(t):
    bg, fg, ov = R.layers()
    lt = t - T_NORA
    z = R.push(lt, 2.0, 1.0, 1.15)
    t_key = word_time(3, "every")
    z *= 1 + 0.12 * R.ease((t - t_key) / 0.4)               # punch-in on the key word
    c = cairo.Context(bg)
    R.cam(c, 2.1 * z, 960, 300)
    restaurant(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, 800, 250)
    NORA.draw(c, 800, 260 + 3.5 * 220, 5.5, pose="sit", t=t + 1.7, look=-0.25,
              expr="smirk" if t < t_key else "sly")
    c = cairo.Context(ov)
    sets.name_tag(c, "NORA VALE", 100, 532, 360, 108, (lt - 0.35) / 0.35, accent="#c8963a")
    return R.compose(bg, fg, ov, dof=4.0)


# ------------------------------------------------------------------ cards
def text_card(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    c = cairo.Context(s)
    txt = L[6][3]
    cps = len(txt) / max(0.8, (L[6][1] - L[6][0]) * 0.9)
    sets.text_card(c, txt, t - T_CARD, cps=cps)
    return R.flat(s)


def chapter_card(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    c = cairo.Context(s)
    sets.text_card(c, L[7][3], 99, cps=99)
    return R.flat(s)


# ------------------------------------------------------------------ chapter 2
FIN = (840, 190)


def shot_map(t):
    bg, fg, ov = R.layers()
    lt = t - T_MAP
    z = 1.0 + 1.1 * R.ease_out(lt / 1.8)
    c = cairo.Context(bg)
    R.cam(c, z, *FIN)
    sets.paper_map(c, t, highlight=(FIN[0], FIN[1], 70))
    c = cairo.Context(fg)
    R.cam(c, z, *FIN)
    sets.map_pin(c, FIN[0], FIN[1], t - word_time(8, "Finland"), label="FINLAND")
    return R.compose(bg, fg, ov, dof=0, bloom=0)


def shot_mill(t):
    bg, fg, ov = R.layers()
    lt = t - T_MILL
    z = 1.0 + 1.3 * (1 - R.ease_out(lt / 1.4))        # measured fast pull-out reveal (chimney -> wide)
    c = cairo.Context(bg)
    R.cam(c, z, 860, 300)
    sets.mill_exterior(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, 860, 300)
    t_w = word_time(9, "Forty")
    for k in range(10):
        kk = t - (t_w + k * 0.06)
        if kk <= 0:
            continue
        sc = 1 + 0.25 * np.exp(-kk * 10) * np.sin(kk * 30)
        x = 150 + k * 108
        c.save()
        c.translate(x, 680)
        c.scale(sc, sc)
        Char(body=WORKER_COLS[k], hair=["bowl", "short", "bun", "curly", "side"][k % 5], collar="round",
             hair_col=["#1d1716", "#5a3a26", "#2b1d14"][k % 3]).draw(c, 0, 0, 0.62, expr="happy", t=t + k)
        c.restore()
    c = cairo.Context(ov)
    sets.pop_label(c, "40 WORKERS", 1060, 120, t - (t_w + 0.7), col="#2b2b2b", size=60)
    return R.compose(bg, fg, ov, dof=0, bloom=0)


def shot_doc(t):
    bg, fg, ov = R.layers()
    lt = t - T_DOC
    z = R.push(lt, 2.5, 1.0, 1.12)
    c = cairo.Context(bg)
    c.set_source_rgb(*sets.hexc("#6b4428"))
    c.paint()
    for k in range(9):
        c.rectangle(0, k * 90, R.W, 4)
        c.set_source_rgba(0, 0, 0, 0.18)
        c.fill()
    sets.glow(c, 640, 300, 700, sets.hexc("#ffd890"), 0.35)
    c = cairo.Context(fg)
    R.cam(c, z, 640, 380)
    t0 = word_time(10, "sixty")
    sets.contract_doc(c, 640, 380, 700, 560, 60_000_000, (t - t0) / 1.0, t)
    return R.compose(bg, fg, ov, dof=1.5, bloom=0.3)


T_FLASH = word_time(10, "sixty") + 1.0


def frame(t):
    if t < T_FELIX:
        img = shot_open(t)
    elif t < T_NORA - WHIP:
        img = close_felix(t)
    elif t < T_NORA:
        img = R.whip(close_felix(t), close_nora(T_NORA), (t - (T_NORA - WHIP)) / WHIP)
    elif t < T_TOAST:
        img = close_nora(t)
    elif t < T_CARD:
        img = shot_toast(t)
    elif t < T_CH:
        return text_card(t)
    elif t < T_MAP:
        return chapter_card(t)
    elif t < T_MILL:
        img = shot_map(t)
    elif t < T_DOC:
        img = shot_mill(t)
    elif T_FLASH <= t < T_FLASH + 3 / R.FPS:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
        sets.impact_flash(cairo.Context(s), (t - T_FLASH) * R.FPS / 3)
        return R.flat(s)
    else:
        img = shot_doc(t)
    return R.post(img)


# ------------------------------------------------------------------ sound
def soundtrack(path):
    m = R.Mixer(TOTAL)
    for x, at in clips:
        m.add_voice(x, at)
    m.add_music(audio.music_chapters(TOTAL, [(0, "minor", 50), (T_MAP - 0.2, "major", 53)]))
    m.add_sfx(audio.thud(), 0.03, "thud", +3)                         # hook impact
    m.add_sfx(audio.pop(), T_FELIX + 0.15, "pop")                     # name tag
    m.add_sfx(audio.coin(), word_time(2, "two billion"), "ding")       # money label
    m.add_sfx(audio.whoosh(), T_NORA - WHIP, "swish")                  # whip-pan
    m.add_sfx(audio.pop(), T_NORA + 0.35, "pop")                      # name tag
    m.add_sfx(audio.pop(), word_time(3, "every"), "pop", -2)          # punch-in
    m.add_sfx(audio.bell(), L[5][1] + 0.05, "ding", -4)               # glasses clink
    txt = L[6][3]
    cps = len(txt) / max(0.8, (L[6][1] - L[6][0]) * 0.9)
    for i, ch in enumerate(txt):
        if ch != " ":
            m.add_sfx(audio.tick(), T_CARD + i / cps, "tick", -3)     # typing
    m.add_sfx(audio.sting(), T_CH, "sting")                           # chapter card: loudest hit
    m.add_sfx(audio.thud(), T_CH, "thud", -4)
    m.add_sfx(audio.pop(), 3.2, "pop")                                 # Felix laugh snap
    m.add_sfx(audio.pop(), 1.6, "tick")                                # glass raised
    m.add_sfx(audio.pop(), L[5][0] - 0.3, "tick")                      # Nora raises glass
    m.add_sfx(audio.pop(), L[5][1] + 0.3, "pop")                       # sly snap
    m.add_sfx(audio.page(), T_MAP, "swish")                            # map zoom
    m.add_sfx(audio.whoosh(), T_MILL, "swish")                         # pull-out reveal
    m.add_sfx(audio.pop(), word_time(8, "Finland"), "pop")            # map pin
    m.add_sfx(audio.pop(), word_time(8, "Finland") + 0.15, "tick")
    t_w = word_time(9, "Forty")
    for k in range(10):
        m.add_sfx(audio.tick(), t_w + k * 0.06, "tick", -2)           # workers pop in
    m.add_sfx(audio.pop(), t_w + 0.7, "pop")                          # label
    t0 = word_time(10, "sixty")
    for k in range(12):
        m.add_sfx(audio.tick(), t0 + k * 0.08, "tick", -4)            # counter rolling
    m.add_sfx(audio.thud(), T_FLASH, "thud")                          # impact flash
    m.add_sfx(audio.coin(), T_FLASH + 0.15, "ding")
    m.render(path, music_db=-20.5)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wav = OUT / "sample.wav"
    soundtrack(wav)
    silent = OUT / "sample_video.mp4"
    R.encode(frame, TOTAL, silent)
    R.mux(silent, wav, OUT / "sample.mp4")
    print(OUT / "sample.mp4", round(TOTAL, 2), "s")


if __name__ == "__main__":
    if len(sys.argv) > 1:      # stills: python3 animator/sample.py 1.0 5.0 ...
        import cv2
        for a in sys.argv[1:]:
            tt = float(a)
            cv2.imwrite(str(OUT / f"still_{tt:.2f}.png"), (np.clip(frame(tt), 0, 1) * 255).astype(np.uint8))
        print({k: (round(v[0], 2), round(v[1], 2), v[2]) for k, v in L.items()})
    else:
        main()
