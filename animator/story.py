"""Story engine: voice + aligned script -> beats -> frames + mix (Paper Billions style, 16:9).

A story module provides:
  ALIGN  path to analysis/script_align.py output (sentences with speaker, chapter, start, end)
  CAST   {speaker_name: Char}
  BEATS  list of dicts: {"at": first sentence index, "tpl": template name, ...template params, "tr": transition}
  CHAPTER_MOOD {chapter: ("minor"|"major", root_midi)}
Engine:
  - inserts a pause at every chapter break (3.4 s after chapter 1: title + chapter card; 2.4 s otherwise)
    and shifts all sentence times; the voice wav is rebuilt with the silences
  - every beat runs from its first sentence until the next beat
  - camera: new framing on every sentence inside a beat (step zoom + side shift, eased 0.35 s), slow push
  - SFX: each template lists its own cues; the mixer sets them to the measured levels
Templates are below (TPL registry). Rendering can be split across processes and concatenated.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import cairo
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio  # noqa: E402
import devices as D  # noqa: E402
import places as P  # noqa: E402
import places2 as P2  # noqa: E402
import render16 as R  # noqa: E402
import sets  # noqa: E402
import transitions as TR  # noqa: E402
from style import Char  # noqa: E402

ALL_PLACES = dict(P.PLACES)
ALL_PLACES.update(P2.PLACES2)
NIGHT = {"night_office", "server_corridor", "void_spotlight", "night_city", "boardroom", "trading_floor", "stage"}
NIGHT_LIGHT = dict(ambient=(0.66, 0.72, 0.92), rim="#c4d8ff")


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


# ====================================================================== timeline
class Story:
    def __init__(self, mod, voice_path, out_dir, title):
        self.mod = mod
        self.out = Path(out_dir)
        self.title = title
        sents = json.load(open(mod.ALIGN))
        # fix weak matches: a weak sentence ends where the next starts
        for i, s in enumerate(sents):
            if s["match"] < 0.5 and i + 1 < len(sents):
                s["end"] = max(s["start"] + 0.3, sents[i + 1]["start"] - 0.05)
        # chapter pauses
        self.gaps = []          # (time in new timeline, length, chapter starting after it)
        shift, chap = 0.0, sents[0]["chapter"]
        cuts = []               # (original time, insert length)
        for s in sents:
            if s["chapter"] != chap:
                ln = 3.4 if chap == sents[0]["chapter"] else 2.4
                cuts.append((s["start"] - 0.02, ln))
                self.gaps.append((s["start"] - 0.02 + shift, ln, s["chapter"], s["chapter_name"]))
                shift += ln
                chap = s["chapter"]
            s["start"] += shift
            s["end"] += shift
        self.sents = sents
        self.cuts = cuts
        self.voice = self._build_voice(voice_path)
        self.total = len(self.voice) / R.SR + 1.5
        # beats -> time ranges
        beats = []
        for b in mod.BEATS:
            b = dict(b)
            b["t0"] = sents[b["at"]]["start"] - 0.06
            beats.append(b)
        for g0, ln, ch, name in self.gaps:
            if ch == sents[0]["chapter"] + 1:
                beats.append({"tpl": "title_card", "t0": g0, "dur_fixed": 2.0, "text": title})
                beats.append({"tpl": "chapter_card", "t0": g0 + 2.0, "name": name, "chapter": ch})
            else:
                beats.append({"tpl": "chapter_card", "t0": g0, "name": name, "chapter": ch})
        beats.sort(key=lambda b: b["t0"])
        for i, b in enumerate(beats):
            b["t1"] = beats[i + 1]["t0"] if i + 1 < len(beats) else self.total
            b["sents"] = [s for s in sents if b["t0"] - 0.01 <= s["start"] < b["t1"] - 0.01]
        cards = ("card", "title_card", "chapter_card")
        n = 0
        for i, b in enumerate(beats):
            if i == 0 or "tr" in b or b["tpl"] in cards or beats[i - 1]["tpl"] in cards:
                continue
            n += 1
            if n % 3 == 0:
                b["tr"] = "whip"
        self.beats = [Beat(b, self) for b in beats]
        rnd = np.random.default_rng(4)
        self.dust = rnd.random((70, 5))

    def _build_voice(self, path):
        x = R.load_wav(path)
        out, last = [], 0
        for t, ln in self.cuts:
            k = int(t * R.SR)
            out.append(x[last:k])
            out.append(np.zeros(int(ln * R.SR)))
            last = k
        out.append(x[last:])
        return np.concatenate(out)

    def beat_at(self, t):
        lo, hi = 0, len(self.beats) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.beats[mid].t0 <= t:
                lo = mid
            else:
                hi = mid - 1
        return lo

    # ---------------- frames
    def frame(self, t):
        i = self.beat_at(t)
        b = self.beats[i]
        img, post = b.render(t)
        tr = b.p.get("tr", "cut")
        dur = {"whip": 0.3, "rip": 0.45, "dissolve": 0.3, "wipe": 0.6}.get(tr, 0)
        if dur and i > 0 and t < b.t0 + dur:
            prev, ppost = self.beats[i - 1].render(t)
            p = (t - b.t0) / dur
            img = {"whip": R.whip, "rip": TR.rip, "dissolve": TR.dissolve,
                   "wipe": lambda a, c, q: TR.circle_wipe(a, c, q)}[tr](prev, img, p)
        if b.p.get("flash_at") is not None:
            ft = b.wt(b.p["flash_at"]) if isinstance(b.p["flash_at"], str) else b.t0 + b.p["flash_at"]
            if ft <= t < ft + 3 / R.FPS:
                s = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
                sets.impact_flash(cairo.Context(s), (t - ft) * R.FPS / 3)
                return R.flat(s)
        if not post:
            return img
        return R.post(self.ambient(img, t))

    def ambient(self, img, t):
        """floating dust in the light + a faint light flicker, so no frame is ever fully still (reference)"""
        import cv2
        ov = np.zeros_like(img)
        for x0, y0, vx, ph, sz in self.dust:
            x = (x0 * R.W + (vx - 0.5) * 40 * t + 25 * math.sin(t * 0.7 + ph * 6)) % R.W
            y = (y0 * R.H - 12 * t * (0.5 + vx) + 15 * math.sin(t * 0.9 + ph * 5)) % R.H
            a = 0.16 + 0.24 * (0.5 + 0.5 * math.sin(t * 2 + ph * 9))
            cv2.circle(ov, (int(x), int(y)), int(1.5 + sz * 3), (0.75 * a, 0.9 * a, a), -1, cv2.LINE_AA)
        bok = np.zeros_like(img)
        for x0, y0, vx, ph, sz in self.dust[:10]:
            x = (x0 * R.W + 30 * t * (vx - 0.3) + 60 * math.sin(t * 0.5 + ph * 6)) % R.W
            y = (y0 * R.H - 20 * t * (0.4 + vx) + 40 * math.sin(t * 0.6 + ph * 5)) % R.H
            a = 0.05 + 0.07 * (0.5 + 0.5 * math.sin(t * 1.4 + ph * 9))
            cv2.circle(bok, (int(x), int(y)), int(9 + sz * 12), (0.8 * a, 0.92 * a, a), -1, cv2.LINE_AA)
        ov += cv2.GaussianBlur(bok, (0, 0), 3)
        flick = 1 + 0.012 * math.sin(t * 5.3) * math.sin(t * 1.9)
        return img * flick + ov

    # ---------------- sound
    def soundtrack(self, path):
        m = R.Mixer(self.total)
        m.add_voice(self.voice, 0.0)
        chap_t = [(self.sents[0]["start"] - 0.3, self.sents[0]["chapter"])]
        for g0, ln, ch, _ in self.gaps:
            chap_t.append((g0 + ln - 0.6, ch))
        moods = self.mod.CHAPTER_MOOD
        m.add_music(audio.music_chapters(self.total, [(max(0, t), *moods.get(c, ("minor", 50))) for t, c in chap_t]))
        n = 0
        for b in self.beats:
            for at, snd, kind, db in b.sfx():
                if 0 <= at < self.total:
                    m.add_sfx(snd, at, kind, db)
                    n += 1
        m.render(path, music_db=-21.5)
        return n

    def render(self, part=None, parts=1):
        self.out.mkdir(parents=True, exist_ok=True)
        nf = int(round(self.total * R.FPS))
        if part is None:
            wav = self.out / "mix.wav"
            n = self.soundtrack(wav)
            print("sfx cues:", n, "total", round(self.total, 1), "s")
            return
        a = nf * part // parts
        e = nf * (part + 1) // parts
        out = self.out / f"part{part}.mp4"
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s",
                              f"{R.W}x{R.H}", "-r", str(R.FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                              "-preset", "medium", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
        for f in range(a, e):
            img = self.frame(f / R.FPS)
            p.stdin.write(np.ascontiguousarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).tobytes())
        p.stdin.close()
        p.wait()
        print("done", out)

    def concat(self, parts, final):
        lst = self.out / "parts.txt"
        lst.write_text("".join(f"file 'part{k}.mp4'\n" for k in range(parts)))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        str(self.out / "video.mp4")], check=True)
        R.mux(self.out / "video.mp4", self.out / "mix.wav", final)

    def srt(self, path):
        def ts(t):
            h, r = divmod(max(0, t), 3600)
            m_, s = divmod(r, 60)
            return f"{int(h):02d}:{int(m_):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
        with open(path, "w") as f:
            for i, s in enumerate(self.sents, 1):
                f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['script_text']}\n\n")


# ====================================================================== beat helpers
class Beat:
    def __init__(self, p, story):
        self.p = p
        self.st = story
        self.t0, self.t1 = p["t0"], p["t1"]
        self.dur = max(0.2, self.t1 - self.t0)
        self.sents = p["sents"]
        self.tpl = TPL[p["tpl"]]
        self.cuts = self._make_cuts()
        self._cover = None

    def _make_cuts(self):
        """hard-cut points inside the beat (measured reference: a new framing every 2.5-2.8 s):
        every sentence start, commas/colons inside long sentences, and a fill so no shot runs over ~2.8 s"""
        if self.p["tpl"] in ("card", "title_card", "chapter_card"):
            return []
        pts = []
        for s in self.sents:
            pts.append(s["start"])
            txt = s["script_text"]
            d = s["end"] - s["start"]
            for m in re.finditer(r"[,:;]", txt):
                pts.append(s["start"] + d * m.end() / max(1, len(txt)))
        pts = sorted(x for x in pts if self.t0 + 0.9 < x < self.t1 - 0.8)
        cuts, last = [], self.t0
        for x in pts:
            if x - last >= 1.8:
                cuts.append(x)
                last = x
        out, last = [], self.t0
        for x in cuts + [self.t1]:
            while x - last > 3.4:
                last += min(2.7, (x - last) / 2)
                out.append(last)
            if x < self.t1:
                out.append(x)
            last = x
        return out

    def shot_index(self, t):
        j = 0
        for c in self.cuts:
            if c <= t:
                j += 1
        return j

    PRESETS = [(1.0, 0, 0), (1.3, -110, -30), (1.12, 95, 10), (1.42, 70, -45), (1.2, -75, 12)]

    def shot(self, t, amp=1.0):
        """(zoom multiplier, dx, dy) for the current shot: preset framing per shot (hard cut), then a push
        at ~7.5 %/s with a slow side drift; every 5th shot is a pull-out"""
        j = self.shot_index(t)
        start = self.cuts[j - 1] if j > 0 else self.t0
        age = min(4.0, max(0.0, t - start))
        zf, ox, oy = self.PRESETS[j % len(self.PRESETS)]
        zf = 1 + (zf - 1) * amp
        if j % 5 == 3:
            zp = 1.22 - 0.07 * age
        else:
            zp = 1.0 + 0.075 * age * (1 - 0.3 * math.exp(-age * 3))
        drift = (14 if j % 2 else -14) * age
        return zf * zp, (ox + drift) * amp, oy * amp

    def shotcam(self, t, cx, cy, amp=1.0):
        z, dx, dy = self.shot(t, amp)
        return z, cx + dx, cy + dy

    def coverage(self):
        """what each shot shows. The reference puts a NEW picture on screen every ~2.5 s, so device beats
        alternate the device with cutaways (a reaction close-up, or the chapter's place with its people).
        A cutaway never covers a device event (a tick, stamp, pop...): those always play on the device."""
        if self._cover is None:
            n = len(self.cuts) + 1
            cov = ["main"] * n
            if self.p["tpl"] in REACT_TPLS and self.p.get("react", True) is not False:
                ev = [x[0] for x in self.sfx()]
                bounds = [self.t0] + self.cuts + [self.t1]
                kind = int(self.t0 * 7) % 2
                for j in range(1, n):
                    a, e = bounds[j], bounds[j + 1]
                    if cov[j - 1] != "main" or e - a < 1.0:
                        continue
                    if any(a - 0.2 <= x <= e + 0.1 for x in ev):
                        continue
                    cov[j] = ("react", "broll")[kind % 2] if self.p.get("broll", True) else "react"
                    kind += 1
            self._cover = cov
        return self._cover

    def cut_no(self, t):
        """how many cutaways have been shown in this beat up to time t (picks the next face / place)"""
        j = self.shot_index(t)
        return sum(1 for x in self.coverage()[:j + 1] if x != "main") + int(self.t0)

    def shot_start(self, t):
        return max([c for c in self.cuts if c <= t] or [self.t0])

    def render(self, t):
        kind = self.coverage()[self.shot_index(t)]
        if kind == "react":
            return t_react(self, t)
        if kind == "broll":
            return t_broll(self, t)
        return self.tpl[0](self, t)

    def sfx(self):
        return self.tpl[1](self) if self.tpl[1] else []

    # sentence helpers
    def k(self, t):
        """index of the sentence being spoken (or last spoken) inside this beat"""
        k = 0
        for i, s in enumerate(self.sents):
            if s["start"] <= t:
                k = i
        return k

    def sk(self, i):
        return self.sents[min(i, len(self.sents) - 1)] if self.sents else {"start": self.t0, "end": self.t1,
                                                                           "script_text": "", "speaker": ""}

    def wt(self, word):
        """time a word is said (first match inside this beat's sentences)"""
        w = word.lower()
        for s in self.sents:
            txt = s["script_text"].lower()
            i = txt.find(w)
            if i >= 0:
                return s["start"] + (s["end"] - s["start"]) * i / max(1, len(txt))
        return 1e9          # word not in this beat: the element never appears

    def talking(self, speaker, t):
        return any(s["speaker"] == speaker and s["start"] <= t <= s["end"] for s in self.sents)

    def cam(self, t, base=(640, 360), push=0.06, step=0.06, shift=34, z0=1.0, amp=None):
        """shot camera (hard cut to a new framing every ~2.5 s, fast push inside the shot)"""
        a = amp if amp is not None else self.p.get("amp", AMP.get(self.p["tpl"], 1.0))
        z, cx, cy = self.shotcam(t, base[0], base[1], a)
        return z * z0, cx, cy


REACT_TPLS = ("filing", "checklist", "board", "email", "letter", "news", "zero", "label", "calendar", "stock",
              "tower", "map", "cork", "tv", "stage")

AMP = {"filing": 0.45, "checklist": 0.45, "board": 0.5, "email": 0.45, "letter": 0.6, "news": 0.5, "zero": 0.5,
       "label": 0.55, "tag": 0.55, "calendar": 0.5, "stock": 0.45, "tower": 0.6, "tv": 0.6, "cork": 0.6,
       "dinner": 0.8, "stage": 0.8, "scene": 0.9, "skit": 0.6, "map": 0.5}


def layers():
    return R.layers()


def place(c, name, t, **kw):
    return ALL_PLACES[name](c, t, **kw) or {}


def light_cast(chars, name):
    for ch in chars:
        if name in NIGHT:
            ch.scene(**NIGHT_LIGHT)
        else:
            ch.scene()


def S(fn, kind, db=0.0):
    return (fn, kind, db)


def gesture(kw, talk, b, t, x, speaker):
    """talking characters gesture on each line (arm up over 0.25 s, then a small beat); listeners breathe"""
    if "arms" in kw or kw.get("pose") == "back":
        kw.setdefault("bob", 0.006 * math.sin(t * 2.3 + x))
        return
    if talk:
        s0 = max([s["start"] for s in b.sents if s["speaker"] == speaker and s["start"] <= t] or [b.t0])
        n = sum(1 for s in b.sents if s["speaker"] == speaker and s["start"] <= t)
        right = x < 640
        g = (["present_r", "shrug", "point_r"] if right else ["present_l", "shrug", "point_l"])[n % 3]
        amt = ease((t - s0) / 0.25) * (0.85 + 0.15 * math.sin((t - s0) * 6))
        kw["arms"] = (g, amt)
        kw["bob"] = 0.012 * math.sin(t * 7)
    else:
        kw["bob"] = 0.006 * math.sin(t * 2.3 + x)


# ====================================================================== templates
TPL = {}


def tpl(name, sfx=None):
    def deco(fn):
        TPL[name] = (fn, sfx)
        return fn
    return deco


# ---------------- cards
def _card_sfx(b):
    txt = b.p.get("text") or (b.sents[0]["script_text"] if b.sents else "")
    s = b.sents[0] if b.sents else {"start": b.t0, "end": b.t0 + 1.5}
    cps = len(txt) / max(0.6, (s["end"] - s["start"]) * 0.9)
    return [(b.t0 + 0.04 + i / cps, audio.tick(), "tick", -3) for i, ch in enumerate(txt) if ch != " " and i % 2 == 0]


@tpl("card", _card_sfx)
def t_card(b, t):
    txt = b.p.get("text") or (b.sents[0]["script_text"] if b.sents else "")
    s = b.sents[0] if b.sents else {"start": b.t0, "end": b.t0 + 1.5}
    cps = len(txt) / max(0.6, (s["end"] - s["start"]) * 0.9)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    c = cairo.Context(surf)
    if len(txt) > 42:   # long lines: smaller, left-aligned (measured)
        c.set_source_rgb(0, 0, 0)
        c.paint()
        n = int(max(0, t - b.t0 - 0.04) * cps) + 1
        sets._slanted_font(c, 44)
        c.set_source_rgb(0.98, 0.98, 0.98)
        words, lines, cur = txt.split(), [], ""
        for w in words:
            if len(cur) + len(w) > 46:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        y = 300 - 30 * (len(lines) - 1)
        for ln in lines:
            m = min(len(ln), n)
            n -= m + 1
            c.move_to(R.W * 0.09, y)
            c.show_text(ln[:max(0, m)])
            y += 64
    else:
        sets.text_card(c, txt, t - b.t0 - 0.04, cps=cps)
    return R.flat(surf), False


@tpl("title_card", lambda b: [(b.t0, audio.thud(), "thud", -2)] +
     [(b.t0 + 0.05 + i / 22, audio.tick(), "tick", -6) for i in range(0, 40, 2)])
def t_title(b, t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    sets.text_card(cairo.Context(surf), b.p["text"], t - b.t0, cps=22, size=58)
    return R.flat(surf), False


@tpl("chapter_card", lambda b: [(b.t0, audio.sting(), "sting", 0), (b.t0, audio.thud(), "thud", -3)])
def t_chapter(b, t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, R.W, R.H)
    name = b.p["name"].title() if b.p["name"].isupper() else b.p["name"]
    sets.text_card(cairo.Context(surf), name, 99, cps=99, size=60)
    return R.flat(surf), False


# ---------------- skit: one set, characters at fixed spots, camera cuts to the speaker line by line
def _skit_sfx(b):
    out = []
    for i, s in enumerate(b.sents):
        if i % 3 == 2:
            out.append((s["start"], audio.pop(), "pop", -4))
    return out


@tpl("skit", _skit_sfx)
def t_skit(b, t):
    """p: place, cast: [(speaker, x, scale, {kw})], props: optional callable(c, t, b)"""
    pl = b.p["place"]
    bg, fg, ov = layers()
    k = b.k(t)
    sp = b.sk(k)["speaker"]
    spots = {s: (x, sc) for s, x, sc, _ in b.p["cast"]}
    ls = b.sk(k)["start"]
    le = b.sk(k)["end"]
    age = t - ls
    wide = sp not in spots or (k == 0 and t < b.t0 + 1.1) or t < ls
    if not wide and le - ls > 3.4 and t > ls + (le - ls) / 2:     # long line: a cut to a closer two-shot
        xs = [x for x, _ in spots.values()]
        z = 1.3 * (1 + 0.06 * (t - ls - (le - ls) / 2))
        cx, cy = sum(xs) / len(xs), 380 - 40
    elif wide:
        z, cx, cy = b.cam(t, base=b.p.get("center", (640, 380)))
        z *= b.p.get("zoom", 1.0)
    else:
        x, sc = spots[sp]
        zc = min(2.6, max(1.55, 3.0 / sc))          # speaker's head about a third of the frame
        z = zc * (1 + 0.07 * min(3.0, age))
        cx, cy = x + (12 if k % 2 else -12) * age, None
    c = cairo.Context(bg)
    info = place(cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)), pl, t, **b.p.get("place_kw", {}))
    floor = b.p.get("floor") or info.get("floor") or 620
    if cy is None:      # close-up: centre a little below the speaker's head (head centre = floor - 4.65 R)
        cy = floor - 4.65 * 40 * sc + 0.9 * 40 * sc
    R.cam(c, 1 + (z - 1) * 0.85, cx, cy)
    place(c, pl, t, **b.p.get("place_kw", {}))
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    chars = [b.st.mod.CAST[s] for s, _, _, _ in b.p["cast"]]
    light_cast(chars, pl)
    for s, x, sc, kw in b.p["cast"]:
        ch = b.st.mod.CAST[s]
        kw = dict(kw)
        expr = kw.pop("expr", "neutral")
        if isinstance(expr, dict):     # {sentence index (global): expr}
            e = "neutral"
            for gi, ex in sorted(expr.items()):
                if b.st.sents[gi]["start"] <= t:
                    e = ex
            expr = e
        talk = b.talking(s, t)
        gesture(kw, talk, b, t, x, s)
        ch.draw(c, x, kw.pop("y", floor), sc, t=t + x * 0.01, expr=expr, talk=talk, **kw)
    if b.p.get("props"):
        b.p["props"](c, t, b)
    return R.compose(bg, fg, ov, dof=2.2), True


# ---------------- generic scene: a place + optional characters + overlay devices (callable)
def _scene_sfx(b):
    return [(b.t0 + 0.05, audio.pop(), "pop", -6)] + [x for x in (b.p.get("sfx") or (lambda bb: []))(b)]


@tpl("scene", _scene_sfx)
def t_scene(b, t):
    """p: place, place_kw, cast [(speaker/charkey, x, scale, kw)], fg (callable c,t,b), ov (callable c,t,b),
    center, push, step, dof"""
    bg, fg, ov = layers()
    z, cx, cy = b.cam(t, base=b.p.get("center", (640, 360)), push=b.p.get("push", 0.07), step=b.p.get("step", 0.06))
    z *= b.p.get("zoom", 1.0)
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.8, cx, cy)
    info = place(c, b.p["place"], t, **b.p.get("place_kw", {})) if b.p.get("place") else {}
    if b.p.get("bg"):
        b.p["bg"](c, t, b)
    floor = b.p.get("floor") or info.get("floor") or 620
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    cast = b.p.get("cast", [])
    chars = [b.st.mod.CAST[s] for s, _, _, _ in cast]
    light_cast(chars, b.p.get("place", ""))
    for s, x, sc, kw in cast:
        kw = dict(kw)
        expr = kw.pop("expr", "neutral")
        if callable(expr):
            expr = expr(t, b)
        arms = kw.pop("arms", "rest")
        if callable(arms):
            arms = arms(t, b)
        talk = b.talking(s, t)
        if arms == "rest":
            kw2 = {}
            gesture(kw2, talk, b, t, x, s)
            arms = kw2.get("arms", arms)
            kw.setdefault("bob", kw2.get("bob", 0))
        else:
            kw.setdefault("bob", 0.006 * math.sin(t * 2.3 + x))
        b.st.mod.CAST[s].draw(c, x, kw.pop("y", floor), sc, t=t + x * 0.01, expr=expr, arms=arms,
                              talk=talk, **kw)
    if b.p.get("fg"):
        b.p["fg"](c, t, b)
    c = cairo.Context(ov)
    if b.p.get("ov"):
        b.p["ov"](c, t, b)
    return R.compose(bg, fg, ov, dof=b.p.get("dof", 1.6), bloom=b.p.get("bloom", 0.9)), True


# ---------------- close-up with a name tag
def _tag_sfx(b):
    out = [(b.t0 + 0.05, audio.pop(), "pop", 0)]
    out += [(b.t0 + 0.12 + i * 0.04, audio.tick(), "tick", -8) for i in range(len(b.p.get("name", "")) // 2)]
    if b.p.get("label"):
        out.append((b.wt(b.p.get("label_at", "")) if b.p.get("label_at") else b.t0 + 0.8, audio.sparkle(), "ding", -3))
    return out


@tpl("tag", _tag_sfx)
def t_tag(b, t):
    """big close-up of one character with a name tag (box, then types on)."""
    bg, fg, ov = layers()
    lt = t - b.t0
    z = b.shot(t, AMP["tag"])[0]
    if b.p.get("punch"):
        z *= 1 + 0.12 * ease((t - b.wt(b.p["punch"])) / 0.15)
    side = b.p.get("side", "left")
    hx = 478 if side == "left" else 800
    c = cairo.Context(bg)
    R.cam(c, 2.0 * z, 640, 300)
    pl = b.p.get("place", "tech_office")
    place(c, pl, t, **b.p.get("place_kw", {}))
    c = cairo.Context(fg)
    R.cam(c, z, hx, 280)
    ch = b.st.mod.CAST[b.p["who"]]
    light_cast([ch], pl)
    expr = b.p.get("expr", "neutral")
    if callable(expr):
        expr = expr(t, b)
    ch.draw(c, hx, 280 + 4.0 * 210, 5.4, pose="sit", t=t, look=0.22 if side == "left" else -0.22, expr=expr,
            arms=b.p.get("arms", "rest"), item=b.p.get("item"), item_hand="r" if side == "left" else "l",
            talk=b.talking(b.p["who"], t))
    c = cairo.Context(ov)
    if b.p.get("name"):
        tx = 765 if side == "left" else 100
        sets.name_tag(c, b.p["name"], tx, 532, 415, 108, (lt - 0.12) / 0.35, accent=b.p.get("accent", "#7ab51d"))
        if b.p.get("sub"):
            c.save()
            sets._slanted_font(c, 26)
            c.move_to(tx + 34, 532 + 108 + 34)
            c.set_source_rgb(0.95, 0.92, 0.85)
            n = int(max(0, lt - 0.6) * 30)
            c.show_text(b.p["sub"][:n])
            c.restore()
    if b.p.get("label"):
        lk = t - (b.wt(b.p["label_at"]) if b.p.get("label_at") else b.t0 + 0.8)
        D.glow_label(c, 1020 if side == "left" else 260, 170, lk, b.p["label"], size=50)
    if b.p.get("ov"):
        b.p["ov"](c, t, b)
    return R.compose(bg, fg, ov, dof=4.0), True


# ---------------- whiteboard written live
def _board_sfx(b):
    n = sum(len(x) for x in b.p["lines"])
    start = b.t0 + 0.25
    cps = b.p.get("cps") or n / max(1.0, b.dur * 0.8)
    out = [(start + i / cps, audio.tick(), "tick", -6) for i in range(0, n, 2)]
    for w, kind in b.p.get("marks", []):
        out.append((b.wt(w) + 0.05, audio.thud() if kind == "stamp" else audio.page(), "thud" if kind == "stamp" else "swish", 0))
    return out


@tpl("board", _board_sfx)
def t_board(b, t):
    """tech office whiteboard; lines written as the voice says them. p: lines, stamp (text, word), strikes
    [(line, word)], pie (pct, word), char"""
    bg, fg, ov = layers()
    z, cx, cy = b.cam(t, base=(870, 240), push=0.08, step=0.04, shift=18)
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.6, 640, 360)
    place(c, b.p.get("place", "tech_office"), t)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    n = sum(len(x) for x in b.p["lines"])
    cps = b.p.get("cps") or n / max(1.0, b.dur * 0.8)

    def extra(cc):
        for li, w in b.p.get("strikes", []):
            yy = 70 + 30 + 48 + li * 48 * 1.45 - 14
            sets._slanted_font(cc, 48)
            e = cc.text_extents(b.p["lines"][li])
            D.strike(cc, 650, yy, 656 + e.x_advance, t - b.wt(w))
        if b.p.get("stamp"):
            txt, w = b.p["stamp"]
            D.stamp(cc, 1010, 330, t - b.wt(w), txt, size=54)
        if b.p.get("pie"):
            pct, w = b.p["pie"]
            D.pie_plate(cc, 1080, 300, t - b.wt(w), pct, r=60)
    D.whiteboard_live(c, 620, 70, 560, 320, b.p["lines"], t - b.t0 - 0.25, cps=cps, size=46, extra=extra)
    if b.p.get("char"):
        who, expr = b.p["char"]
        ch = b.st.mod.CAST[who]
        ch.scene()
        ch.draw(c, 380, 640, 1.5, t=t, look=0.6, expr=expr, arms="point_r", talk=b.talking(who, t))
    return R.compose(bg, fg, ov, dof=1.4), True


# ---------------- calendar page flip to a date (+ marker circle)
@tpl("calendar", lambda b: [(b.t0 + 0.3, audio.page(), "swish", 0), (b.t0 + 1.0, audio.tick(), "tick", 0)])
def t_calendar(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    c = cairo.Context(bg)
    c.set_source_rgb(*sets.hexc("#1d2c52"))
    c.paint()
    sets.glow(c, 640, 300, 560, sets.hexc("#cfe0ff"), 0.22)
    c.arc(1010, 170, 60, 0, 2 * math.pi)
    sets._fill_line(c, sets.hexc("#f2efe6"), 5)
    a = -math.pi / 2 + int(t * 2) * (math.pi / 30)
    c.move_to(1010, 170)
    c.line_to(1010 + 48 * math.cos(a), 170 + 48 * math.sin(a))
    c.set_source_rgb(0.8, 0.1, 0.1)
    c.set_line_width(3)
    c.stroke()
    c = cairo.Context(fg)
    R.cam(c, *b.shotcam(t, 640, 360, AMP["calendar"]))
    m0, m1 = b.p.get("from", "OCT"), b.p.get("month", "NOV")
    p = (lt - 0.3) / 0.35
    if m0 != m1 and p < 1:
        TR.page_flip(c, max(0, p), 640, 360, lambda cc: P.calendar(cc, 640, 360, m0, 2026, 1.1),
                     lambda cc: P.calendar(cc, 640, 360, m1, 2026, 1.1))
    else:
        P.calendar(c, 640, 360, m1, 2026, 1.1)
        day = b.p.get("day")
        if day:
            # Nov 2026 starts on a Sunday: column = (day-1) % 7, row = (day-1)//7
            col, row = (day - 1) % 7, (day - 1) // 7
            x0 = 640 - 165 + 22 * 1.1 + col * 37 * 1.1 + 15
            y0 = 360 - 198 + 170 * 1.1 + row * 34 * 1.1 + 14
            sets.pop_label(c, str(day), x0, y0 + 2, 1.0, col="#200a00", size=22, angle=0)
            D.marker_circle(c, x0, y0, 26, 22, lt - 0.95, hand=False)
        if b.p.get("label"):
            sets.pop_label(c, b.p["label"], 640, 620, lt - 1.2, col="#f2d23a", size=50)
    return R.compose(bg, fg, ov, dof=2.0), True


# ---------------- money counter (+ cash tower that can collapse)
def _tower_sfx(b):
    out = [(b.t0 + 0.05 + i * b.p.get("build", 1.0) / 14, audio.tick(), "tick", -4) for i in range(14)]
    if b.p.get("collapse"):
        out += [(b.wt(b.p["collapse"]), audio.thud(), "thud", 2), (b.wt(b.p["collapse"]) + 0.05, audio.sting_low(), "sting", -5)]
    return out


@tpl("tower", _tower_sfx)
def t_tower(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    z, cx, cy = b.shotcam(t, 640, 400, AMP["tower"])
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.7, cx, cy)
    place(c, b.p.get("place", "trading_floor"), t)
    c.identity_matrix()
    c.rectangle(0, 0, R.W, R.H)
    c.set_source_rgba(0, 0, 0, 0.3)
    c.fill()
    sets.glow(c, 640, 360, 640, sets.hexc("#ffcf80"), 0.25)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    c.save()
    c.translate(640, 575)
    c.scale(1, 0.18)
    c.arc(0, 0, 260, 0, 2 * math.pi)
    c.restore()
    c.set_source_rgba(0, 0, 0, 0.35)
    c.fill()
    col = (b.wt(b.p["collapse"]) - b.t0 + 0.1) if b.p.get("collapse") else None
    D.cash_tower(c, 640, 570, lt, n_max=14, build=b.p.get("build", 1.0), collapse_at=col)
    if lt > b.p.get("build", 1.0) and (col is None or lt < col):
        falling_bills(c, t, b.t0)
    c = cairo.Context(ov)
    val, fmt = b.p["value"], b.p.get("fmt", "${:,.0f}")
    if col is None or lt < col:
        D.counter_box(c, 1010, 600, lt, val, fmt=fmt, sub=b.p.get("sub"), dur=b.p.get("build", 1.0), w=380)
    else:
        c.rectangle(820, 557, 380, 86)
        sets._fill_line(c, sets.hexc("#3a0d0d"), 3)
        sets.pop_label(c, b.p.get("loss_text", "-" + fmt.format(val)), 1010, 600, 1.0, col="#ff5a4a", size=42, angle=0)
    if b.p.get("label"):
        lt2, w = b.p["label"]
        sets.pop_label(c, lt2, 640, 110, t - b.wt(w), col="#f2d23a", size=52)
    return R.compose(bg, fg, ov, dof=1.4, bloom=0.6), True


def falling_bills(c, t, seed_t, n=9):
    """paper bills drifting down past the camera (keeps money shots alive)"""
    rnd = np.random.default_rng(int(seed_t * 10) % 1000)
    for x0, ph, sp, rot in rnd.random((n, 4)):
        y = ((t * (0.18 + 0.12 * sp) + ph) % 1.0) * 900 - 120
        x = 140 + x0 * 1000 + 40 * math.sin(t * 2 + ph * 9)
        c.save()
        c.translate(x, y)
        c.rotate(math.sin(t * 2.5 + rot * 7) * 0.8)
        c.scale(1, 0.55 + 0.45 * math.cos(t * 3 + ph * 5))
        c.rectangle(-34, -16, 68, 32)
        sets._fill_line(c, sets.hexc("#6fbf5a"), 2.5)
        c.arc(0, 0, 8, 0, 2 * math.pi)
        c.set_source_rgb(*sets.hexc("#3f8a35"))
        c.fill()
        c.restore()


# ---------------- stock chart on a trading screen
def _stock_sfx(b):
    n = len(b.p["values"])
    d = b.p.get("draw", 1.6)
    out = [(b.t0 + 0.1 + i * d / n, audio.tick(), "tick", -6) for i in range(n)]
    out.append((b.t0 + 0.1 + d, audio.thud() if b.p["values"][-1] < b.p["values"][0] else audio.coin(),
                "thud" if b.p["values"][-1] < b.p["values"][0] else "ding", -2))
    return out


@tpl("stock", _stock_sfx)
def t_stock(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    c = cairo.Context(bg)
    place(c, "trading_floor", t, red=b.p["values"][-1] < b.p["values"][0], ticker=b.p.get("ticker", "NVDA"))
    c = cairo.Context(fg)
    R.cam(c, *b.shotcam(t, 640, 360, AMP["stock"]))
    P2.stock_chart(c, (lt - 0.1) / b.p.get("draw", 1.6), b.p["values"], ticker=b.p.get("ticker", "NVDA"),
                   price=b.p.get("price"), change=b.p.get("change"))
    c = cairo.Context(ov)
    for txt, w, x, y in b.p.get("labels", []):
        sets.pop_label(c, txt, x, y, t - b.wt(w), col="#f2d23a", size=44)
    return R.compose(bg, fg, ov, dof=2.5), True


# ---------------- newspapers slamming in
@tpl("news", lambda b: [(b.wt(w) if w else b.t0, audio.thud(), "thud", -2) for (_, _, w) in b.p["papers"]])
def t_news(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    c = cairo.Context(bg)
    place(c, b.p.get("place", "boardroom"), t)
    c = cairo.Context(fg)
    R.cam(c, *b.shotcam(t, 640, 360, AMP["news"]))
    for i, (head, sub, w) in enumerate(b.p["papers"]):
        k = t - (b.wt(w) if w else b.t0)
        P2.newspaper(c, k, head, sub, x=640 + (i - (len(b.p["papers"]) - 1) / 2) * 90, y=360 + i * 30,
                     angle=-0.08 + i * 0.07, s=0.95 - 0.05 * len(b.p["papers"]))
    c = cairo.Context(ov)
    if b.p.get("stamp"):
        txt, w = b.p["stamp"]
        D.stamp(c, 900, 520, t - b.wt(w), txt)
    return R.compose(bg, fg, ov, dof=3.0), True


# ---------------- official filing
def _filing_sfx(b):
    out = [(b.t0 + 0.1, audio.page(), "swish", 0)]
    if b.p.get("stamp"):
        out.append((b.wt(b.p["stamp"][1]), audio.thud(), "thud", 0))
    return out


@tpl("filing", _filing_sfx)
def t_filing(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    z, cx, cy = b.cam(t, base=(640, 380), push=0.1, step=0.07, shift=20)
    desk_bg(b, cairo.Context(bg), t, z, cx, cy)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    hl = b.p.get("highlight")
    hl_on = hl is not None and t >= b.wt(hl[1])
    P2.filing(c, lt - 0.2, b.p["title"], b.p["lines"], highlight=hl[0] if hl_on else None,
              cps=b.p.get("cps", 40))
    if b.p.get("circle"):
        ln, w = b.p["circle"]
        D.marker_circle(c, 640, 380 - 280 + 150 + ln * 52 - 10, 260, 34, t - b.wt(w), hand=False)
    c = cairo.Context(ov)
    if b.p.get("stamp"):
        txt, w = b.p["stamp"]
        D.stamp(c, 900, 520, t - b.wt(w), txt)
    if b.p.get("magnify"):
        pass
    return R.compose(bg, fg, ov, dof=1.0), True


# ---------------- checklist form (rows appear, get struck or ticked as said)
def _check_sfx(b):
    out = []
    for i, (row, act, w) in enumerate(b.p["rows"]):
        out.append((b.wt(w), audio.pop() if act == "x" else audio.bell(), "pop" if act == "x" else "ding", -2))
    if b.p.get("stamp"):
        out.append((b.wt(b.p["stamp"][1]), audio.thud(), "thud", 0))
    return out


@tpl("checklist", _check_sfx)
def t_check(b, t):
    bg, fg, ov = layers()
    z, cx, cy = b.cam(t, base=(640, 360), push=0.08, step=0.03, shift=14)
    desk_bg(b, cairo.Context(bg), t, z, cx, cy)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    rows = b.p["rows"]
    w, h = 560, 140 + 74 * len(rows)
    c.save()
    c.translate(640, 360)
    c.rotate(-0.04)
    c.rectangle(-w / 2 + 12, -h / 2 + 14, w, h)
    c.set_source_rgba(0, 0, 0, 0.3)
    c.fill()
    c.rectangle(-w / 2, -h / 2, w, h)
    sets._fill_line(c, sets.hexc("#fbf8ef"), 4)
    P._text(c, b.p.get("title", ""), 0, -h / 2 + 62, 38)
    for i, (row, act, wd) in enumerate(rows):
        tw = b.wt(wd)
        if t < tw - 0.15:
            continue
        yy = -h / 2 + 120 + i * 74
        c.rectangle(-w / 2 + 40, yy, 38, 38)
        c.set_source_rgb(*sets.INK)
        c.set_line_width(3)
        c.stroke()
        P._text(c, row, -w / 2 + 100, yy + 32, 38, "#200a00", center=False)
        k = t - tw
        if act == "tick" and k > 0:
            p = ease_out(k / 0.15)
            c.move_to(-w / 2 + 46, yy + 18)
            c.line_to(-w / 2 + 58, yy + 32)
            c.line_to(-w / 2 + 58 + 30 * p, yy + 32 - 40 * p)
            c.set_source_rgb(*sets.hexc("#2f9a3a"))
            c.set_line_width(7)
            c.stroke()
        if act == "x" and k > 0:
            sets._slanted_font(c, 38)
            e = c.text_extents(row)
            D.strike(c, -w / 2 + 96, yy + 20, -w / 2 + 104 + e.x_advance, k, w=7)
    # one marker hand: comes in for a mark, glides to the next mark if it follows soon, else leaves
    marks = []
    for i, (row, act, wd) in enumerate(rows):
        yy = -h / 2 + 120 + i * 74
        sets._slanted_font(c, 38)
        ex = c.text_extents(row).x_advance
        marks.append((b.wt(wd), act, yy, ex))
    marks = [m for m in sorted(marks) if m[0] < 1e8]

    def tip(m, k):
        tw, act, yy, ex = m
        if act == "tick":
            p = ease_out(min(1, max(0, k) / 0.15))
            return -w / 2 + 58 + 30 * p, yy + 32 - 40 * p
        return -w / 2 + 96 + (8 + ex) * ease_out(min(1, max(0, k) / 0.3)), yy + 20
    live = [i for i, m in enumerate(marks) if t >= m[0] - 0.4]
    if live:
        i = live[-1]
        k = t - marks[i][0]
        hx, hy = tip(marks[i], k)
        off = 0.0
        near_prev = i > 0 and marks[i][0] - marks[i - 1][0] < 1.3
        near_next = i + 1 < len(marks) and marks[i + 1][0] - marks[i][0] < 1.3
        if k < 0 and near_prev:                    # glide from the previous mark
            px, py = tip(marks[i - 1], 9)
            q = ease((k + 0.4) / 0.4)
            hx, hy = px + (hx - px) * q, py + (hy - py) * q
        elif not near_prev:
            off = (1 - ease((k + 0.4) / 0.3)) * 520
        if not near_next:
            off += ease((k - 0.4) / 0.35) * 520
        if off < 519:
            D.marker_hand(c, hx + off, hy + off * 0.55, t, col="#2f9a3a" if marks[i][1] == "tick" else "#d0302a")
    c.restore()
    c = cairo.Context(ov)
    if b.p.get("stamp"):
        txt, w2 = b.p["stamp"]
        D.stamp(c, 900, 560, t - b.wt(w2), txt, size=52)
    return R.compose(bg, fg, ov, dof=0.8), True


# ---------------- zero device: clipboard with a circled, slashed 0
@tpl("zero", lambda b: [(b.t0 + 0.4, audio.pop(), "pop", 0)])
def t_zero(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    z, cx, cy = b.shotcam(t, 640, 380, AMP["zero"])
    desk_bg(b, cairo.Context(bg), t, z, cx, cy)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    P2.paper_shadow(c, 640, 380, 460, 600, angle=-0.04, lift=18)
    c.save()
    c.translate(640, 380)
    c.rotate(-0.04)
    sets._rrect(c, -230, -300, 460, 600, 14)
    sets._fill_line(c, sets.hexc("#8a5a2c"), 4)
    c.rectangle(-200, -250, 400, 520)
    sets._fill_line(c, sets.hexc("#f6f3ea"), 3)
    sets._rrect(c, -70, -320, 140, 50, 10)
    sets._fill_line(c, sets.hexc("#b8b8b8"), 3)
    P._text(c, b.p.get("label", "CHARGES"), 0, -170, 44)
    p = ease_out((lt - 0.3) / 0.35)
    if p > 0:
        P._text(c, "0", 0, 60, int(200 * p), "#200a00")
        D.marker_circle(c, 0, -10, 120, 120, lt - 0.6, hand=False)
        D.strike(c, -110, 90, 110, lt - 1.0, col="#d8342a", w=9)
    c.restore()
    return R.compose(bg, fg, ov, dof=1.0), True


# ---------------- TV interview set with a quote box
def _tv_sfx(b):
    return [(b.t0 + 0.05, audio.pop(), "pop", -2)] + [(b.t0 + 0.4 + i / 30, audio.tick(), "tick", -10)
                                                       for i in range(0, len(b.p["quote"]), 3)]


@tpl("tv", _tv_sfx)
def t_tv(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    c = cairo.Context(bg)
    D.live_tv(c, t)
    c = cairo.Context(fg)
    R.cam(c, *b.shotcam(t, 640, 360, AMP["tv"]))
    ch = b.st.mod.CAST[b.p.get("who", "SPOKESPERSON")]
    ch.scene()
    ch.draw(c, 400, 640, 1.9, t=t, pose=b.p.get("pose", "stand"), look=0.4, expr="neutral",
            talk=b.p.get("talk", False) and (b.sk(0)["start"] <= t <= b.sk(0)["end"]))
    c = cairo.Context(ov)
    q = b.p["quote"]
    n = int(max(0, lt - 0.4) * 30)
    c.rectangle(560, 170, 640, 260)
    c.set_source_rgba(0.05, 0.05, 0.1, 0.85)
    c.fill()
    c.rectangle(560, 170, 10, 260)
    c.set_source_rgb(*sets.hexc("#d0302a"))
    c.fill()
    words, lines, cur = q.split(), [], ""
    for w in words:
        if len(cur) + len(w) > 26:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    y = 230
    for ln in lines[:4]:
        m = min(len(ln), n)
        n -= m + 1
        P._text(c, ln[:max(0, m)], 590, y, 38, "#ffffff", center=False)
        y += 52
    P._text(c, b.p.get("source", ""), 590, 410, 24, "#f2d23a", center=False)
    if b.p.get("stamp"):
        txt, w = b.p["stamp"]
        D.stamp(c, 880, 520, t - b.wt(w), txt, size=48)
    return R.compose(bg, fg, ov, dof=0.8), True


# ---------------- dinner at the restaurant (callback scene)
@tpl("dinner", lambda b: [(b.t0 + 0.9, audio.bell(), "ding", -6)])
def t_dinner(b, t):
    bg, fg, ov = layers()
    z, cx, cy = b.cam(t, base=(640, 360), push=0.06, step=0.05, shift=30)
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.7, cx, cy)
    sets.wood_wall(c)
    sets.night_window(c, 905, -10, 1290, 215, t)
    sets.curtain(c, 860, 905, 470)
    sets.sconce(c, 690, 190)
    sets.booth_side(c, -40, 150, 120, studs_x=30, studs=(262, 300, 370, 440, 505, 580))
    sets.booth_side(c, 1150, 1330, 150, studs_x=1255, studs=(232, 300), flip=True)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    empty = b.p.get("empty", ())
    toast = b.p.get("toast")
    kt = ease((t - b.wt(toast)) / 0.4) if toast else 0
    if "L" not in empty:
        L = b.st.mod.CAST[b.p.get("left", "JENSEN")]
        L.scene()
        L.draw(c, 255, 300 + 3.5 * 160, 4.0, pose="sit", t=t, look=0.35, expr=b.p.get("lexpr", "happy"),
               arms={"r": (575 - (1 - kt) * 60, 330 + (1 - kt) * 220), "l": (455, 635)}, item="wine", item_hand="r")
    else:
        _empty_chair(c, 255, 560)
    if "R" not in empty:
        Rr = b.st.mod.CAST[b.p.get("right", "ALICE")]
        Rr.scene()
        Rr.draw(c, 1040, 310 + 3.5 * 150, 3.75, pose="sit", t=t + 1.7, look=-0.3, expr=b.p.get("rexpr", "smirk"),
                arms={"l": (720 + (1 - kt) * 60, 330 + (1 - kt) * 220), "r": (1210, 640)}, item="wine", item_hand="l")
    else:
        _empty_chair(c, 1040, 560)
    sets.tablecloth(c, 660, 603, 568, 42, glow_x=655)
    sets.plate(c, 430, 600)
    sets.plate(c, 885, 600)
    sets.roses_candle(c, 655, 600, t)
    c = cairo.Context(ov)
    if b.p.get("ov"):
        b.p["ov"](c, t, b)
    return R.compose(bg, fg, ov, dof=3.5), True


def _empty_chair(c, x, y):
    c.save()
    c.translate(x, y)
    sets._rrect(c, -110, -330, 220, 330, 30)
    sets._fill_line(c, sets.hexc("#7a0f14"), 5)
    c.restore()


# ---------------- corkboard with photos, string, marker circle
@tpl("cork", lambda b: [(b.t0 + 0.2 + i * 0.35, audio.pop(), "pop", -2) for i in range(len(b.p["photos"]))]
     + ([(b.wt(b.p["circle"][1]), audio.page(), "swish", -4)] if b.p.get("circle") else []))
def t_cork(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    c = cairo.Context(bg)
    P2.corkboard(c, t)
    c = cairo.Context(fg)
    z, cx, cy = b.cam(t, base=(640, 360), push=0.08, step=0.05, shift=30)
    R.cam(c, z, cx, cy)
    pos = []
    for i, (who, label, x, y) in enumerate(b.p["photos"]):
        k = lt - 0.2 - i * 0.35
        if k <= 0:
            continue
        drop = max(0.0, 1 - k / 0.2) * 120
        ch = b.st.mod.CAST[who] if who else None

        def draw(cc, w, h, ox, oy, ch=ch):
            cc.set_source_rgb(*sets.hexc("#c8d6e6"))
            cc.rectangle(ox, oy, w, h)
            cc.fill()
            if ch is None:
                cc.arc(ox + w / 2, oy + h * 0.5, 45, 0, 6.3)
                cc.set_source_rgb(0.15, 0.15, 0.18)
                cc.fill()
                P._text(cc, "?", ox + w / 2, oy + h * 0.6, 60, "#ffffff")
            else:
                ch.scene()
                ch.draw(cc, ox + w / 2, oy + h + 150, 1.6, t=0.4, expr="neutral", shadow=False)
        P2.pinned_photo(c, x, y - drop, draw, label, angle=(-0.06 if i % 2 else 0.05))
        pos.append((x, y - 90))
    for a, bb, w in b.p.get("strings", []):
        if a < len(pos) and bb < len(pos):
            P2.red_string(c, pos[a], pos[bb], (t - b.wt(w)) / 0.5)
    if b.p.get("circle"):
        i, w = b.p["circle"]
        x, y = b.p["photos"][i][2], b.p["photos"][i][3]
        D.marker_circle(c, x, y + 10, 150, 150, t - b.wt(w))
    c = cairo.Context(ov)
    if b.p.get("label"):
        txt, w = b.p["label"]
        sets.pop_label(c, txt, 640, 660, t - b.wt(w), col="#f2d23a", size=48)
    if b.p.get("viewfinder"):
        TR.viewfinder(c, t)
    return R.compose(bg, fg, ov, dof=0.5), True


# ---------------- map
@tpl("map", lambda b: [(b.wt(w), audio.pop(), "pop", 0) for (_, _, _, w) in b.p.get("pins", [])] +
     [(b.wt(r[4]), audio.whoosh(), "swish", -6) for r in b.p.get("routes", [])])
def t_map(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    z = (1.0 + 0.25 * ease_out(lt / max(2.0, b.dur))) * b.shot(t, AMP["map"])[0]
    cx, cy = b.p.get("center", (640, 360))
    c = cairo.Context(bg)
    R.cam(c, z, cx, cy)
    sets.paper_map(c, t, highlight=b.p.get("highlight"))
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    for x0, y0, x1, y1, w in b.p.get("routes", []):
        D.route_arc(c, x0, y0, x1, y1, (t - b.wt(w)), dur=0.8)
    for x, y, label, w in b.p.get("pins", []):
        sets.map_pin(c, x, y, t - b.wt(w), label=label)
    c = cairo.Context(ov)
    if b.p.get("stamp"):
        txt, w, x, y = b.p["stamp"]
        D.stamp(c, x, y, t - b.wt(w), txt)
    return R.compose(bg, fg, ov, dof=0, bloom=0), True


# ---------------- stage (keynote / jacket)
@tpl("stage", lambda b: [(b.wt(w), audio.pop(), "pop", -2) for (_, w, _, _) in b.p.get("labels", [])])
def t_stage(b, t):
    bg, fg, ov = layers()
    z, cx, cy = b.cam(t, base=b.p.get("center", (640, 360)), push=b.p.get("push", 0.08), step=0.05, shift=20)
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.8, cx, cy)
    info = P2.stage(c, t, jacket=b.p.get("jacket", False), mark=b.p.get("mark", False),
                    chip=b.p.get("chip", True))
    for i in range(2):                            # sweeping spotlights (V1: light is always animated)
        a = math.pi / 2 + 0.45 * math.sin(t * 0.9 + i * 2.6)
        x0 = 200 + i * 880
        c.move_to(x0, -60)
        c.line_to(x0 + 900 * math.cos(a - 0.09), -60 + 900 * math.sin(a - 0.09))
        c.line_to(x0 + 900 * math.cos(a + 0.09), -60 + 900 * math.sin(a + 0.09))
        c.close_path()
        c.set_source_rgba(1, 0.95, 0.8, 0.10)
        c.fill()
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    for who, x, sc, kw in b.p.get("cast", []):
        ch = b.st.mod.CAST[who]
        ch.scene(**NIGHT_LIGHT) if b.p.get("night") else ch.scene()
        kw = dict(kw)
        ch.draw(c, x, kw.pop("y", info["floor"]), sc, t=t, talk=b.talking(who, t), **kw)
    c = cairo.Context(ov)
    for txt, w, x, y in b.p.get("labels", []):
        sets.pop_label(c, txt, x, y, t - b.wt(w), col="#f2d23a", size=50)
    return R.compose(bg, fg, ov, dof=1.0, bloom=1.0), True


# ---------------- black void + spotlight + key (power)
@tpl("void", lambda b: [(b.t0 + 0.1, audio.sparkle(), "ding", -2)] +
     ([(b.wt(b.p["drop"]), audio.thud(), "thud", 0)] if b.p.get("drop") else []))
def t_void(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    z = TR.pull_out(t, b.t0, 1.4, 3.0, 1.0)
    c = cairo.Context(bg)
    R.cam(c, z, 640, 380)
    P.void_spotlight(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, 640, 380)
    who = b.p.get("who")
    dropping = b.p.get("drop") and t >= b.wt(b.p["drop"])
    if who:
        ch = b.st.mod.CAST[who]
        ch.scene()
        ch.draw(c, 640, 610, 1.8, t=t, expr="worried" if dropping else b.p.get("expr", "smirk"),
                arms="raise_r" if not dropping else "rest", look=0.0)
    if not dropping:
        P2.key_prop(c, 640 + 95, 610 - 330 + (0 if who else 40), 1.2)
    else:
        k = t - b.wt(b.p["drop"])
        P2.key_prop(c, 735 + 40 * k, 280 + 900 * k * k, 1.2, glow_on=False)
    return R.compose(bg, fg, ov, dof=0, bloom=1.0), True


# ---------------- envelope arriving on the night-office desk
@tpl("letter", lambda b: [(b.t0 + 0.05, audio.whoosh(), "swish", -2), (b.t0 + 0.32, audio.thud(), "thud", -6)])
def t_letter(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    z, cx, cy = b.cam(t, base=(640, 420), push=0.08, step=0.05, shift=24)
    c = cairo.Context(bg)
    R.cam(c, 1 + (z - 1) * 0.6, cx, cy)
    P.night_office(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    P2.envelope(c, 640, 470, lt, label=b.p.get("label", "U.S. HOUSE OF REPRESENTATIVES"), s=0.9)
    c = cairo.Context(ov)
    for txt, w, x, y in b.p.get("labels", []):
        sets.pop_label(c, txt, x, y, t - b.wt(w), col="#f2d23a", size=42)
    return R.compose(bg, fg, ov, dof=1.2), True


# ---------------- laptop with an email
@tpl("email", lambda b: [(b.t0 + 0.1, audio.bell(), "ding", -4)] +
     [(b.t0 + 0.4 + i / 30, audio.tick(), "tick", -10) for i in range(0, 60, 3)])
def t_email(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    z, cx, cy = b.cam(t, base=(640, 360), push=0.1, step=0.05, shift=16)
    c = cairo.Context(bg)
    P.tech_office(c, t)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    P2.laptop_email(c, 640, 360, lt - 0.3, b.p.get("subject", "A personal note"), b.p.get("body", []))
    c = cairo.Context(ov)
    if b.p.get("counter"):
        val, sub, w = b.p["counter"]
        D.counter_box(c, 1040, 110, t - b.wt(w), val, fmt="{:,.0f}+", sub=sub, w=330)
    return R.compose(bg, fg, ov, dof=2.4), True


# ---------------- generic big label on a coloured backdrop (+ optional pie / scale)
@tpl("label", lambda b: [(b.wt(w), audio.pop(), "pop", 0) for (_, w, _, _) in b.p.get("labels", [])])
def t_label(b, t):
    bg, fg, ov = layers()
    lt = t - b.t0
    c = cairo.Context(bg)
    z, cx, cy = b.shotcam(t, 640, 360, AMP["label"])
    R.cam(c, 1 + (z - 1) * 0.5, cx, cy)
    ch_no = b.sents[0]["chapter"] if b.sents else 1
    pl = b.p.get("place") or b.st.mod.REACTORS.get(ch_no, [("", "night_office")])[0][1]
    place(c, pl, t)
    c.identity_matrix()
    c.rectangle(0, 0, R.W, R.H)
    c.set_source_rgba(0, 0, 0, 0.25)
    c.fill()
    sets.glow(c, 640, 340, 620, sets.hexc(b.p.get("glow", "#cfe0ff")), 0.22)
    c = cairo.Context(fg)
    R.cam(c, z, cx, cy)
    if b.p.get("pie"):
        pct, w, lab = b.p["pie"]
        D.pie_plate(c, 640, 400, t - b.wt(w), pct, label=lab, r=170)
    if b.p.get("fg"):
        b.p["fg"](c, t, b)
    c = cairo.Context(ov)
    for txt, w, x, y in b.p.get("labels", []):
        sets.pop_label(c, txt, x, y, t - b.wt(w), col=b.p.get("col", "#f2d23a"), size=b.p.get("size", 60))
    return R.compose(bg, fg, ov, dof=2.6), True


# ---------------- reaction close-up (inserted every 3rd shot of device beats)
def t_react(b, t):
    mod = b.st.mod
    ch_no = b.sents[0]["chapter"] if b.sents else 1
    who, pl, expr = None, None, None
    if isinstance(b.p.get("react"), tuple):
        who, expr = b.p["react"][0], b.p["react"][1]
        pl = b.p["react"][2] if len(b.p["react"]) > 2 else None
    opts = mod.REACTORS.get(ch_no, [("JENSEN", "night_office")])
    n = b.cut_no(t)
    if who is None:
        who, pl = opts[n % len(opts)]
    pl = pl or opts[0][1]
    if expr is None:
        expr = ["worried", "shock", "deadpan", "sad", "smirk"][(n + int(b.t0 * 3)) % 5]
    age = t - b.shot_start(t)
    bg, fg, ov = layers()
    side = n % 2
    hx = 478 if side == 0 else 800
    z = 1.0 + 0.07 * age
    c = cairo.Context(bg)
    R.cam(c, 2.0 * z, 640, 300)
    place(c, pl, t)
    c = cairo.Context(fg)
    R.cam(c, z, hx, 280)
    ch = mod.CAST[who]
    light_cast([ch], pl)
    e = "neutral" if age < 0.2 else expr          # expression snaps just after the cut
    l0 = 0.22 if side == 0 else -0.22
    look = l0 - 0.3 * l0 / abs(l0) * ease((age - 1.0) / 0.2) * (1 - ease((age - 1.7) / 0.2))   # a glance away
    ch.draw(c, hx, 280 + 4.0 * 210, 5.4, pose="sit", t=t, look=look, expr=e,
            bob=0.012 * math.sin(t * 3), lean=0.02 * math.sin(t * 1.3))
    return R.compose(bg, fg, ov, dof=4.0), True


# ---------------- establishing cutaway: the chapter's place, with its people busy in it
def t_broll(b, t):
    mod = b.st.mod
    ch_no = b.sents[0]["chapter"] if b.sents else 1
    opts = mod.REACTORS.get(ch_no, [("JENSEN", "night_office")])
    n = b.cut_no(t)
    pl = opts[(n // 2) % len(opts)][1]
    if n % 4 == 3:
        pl = "night_city"
    people = [w for w, q in opts if q == pl][:2] or [opts[(n // 2) % len(opts)][0]]
    age = t - b.shot_start(t)
    side = 1 if n % 2 else -1
    z = 1.06 + 0.07 * age
    cx = 640 + side * (30 + 16 * age)
    bg, fg, ov = layers()
    c = cairo.Context(bg)
    R.cam(c, z, cx, 360)
    info = place(c, pl, t)
    c = cairo.Context(fg)
    R.cam(c, z * 1.04, cx, 360)
    if pl == "night_city":                        # back view, looking out at the city (V1 f1146)
        ch = mod.CAST[people[0]]
        light_cast([ch], pl)
        ch.draw(c, 880 - side * 260, 860, 2.6, pose="back", t=t, bob=0.006 * math.sin(t * 2.1))
    else:
        floor = info.get("floor") or 640
        chars = [mod.CAST[w] for w in people]
        light_cast(chars, pl)
        xs = [640] if len(people) == 1 else [400, 880]
        for i, (w, x) in enumerate(zip(people, xs)):   # medium shot, cropped at the waist
            busy = (i + n) % 2 == 0
            look = 0.45 * math.sin(t * 0.7 + i) if not busy else (0.3 if x < 640 else -0.3)
            mod.CAST[w].draw(c, x, 860, 2.5, t=t + i * 0.37, look=look,
                             expr="deadpan" if busy else ["worried", "neutral", "smirk"][(n + i) % 3],
                             arms="chin" if busy else "rest", item="phone" if busy else None,
                             bob=0.008 * math.sin(t * 2.4 + i * 2))
    return R.compose(bg, fg, ov, dof=1.8, bloom=1.0), True


def desk_bg(b, c, t, z, cx, cy):
    """documents always lie on a desk (animated: steam, lamp, phone buzz)"""
    R.cam(c, z, cx, cy)
    P2.desk_top(c, t, wood=b.p.get("wood", "#6b4226"))
