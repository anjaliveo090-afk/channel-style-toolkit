#!/usr/bin/env python3
"""Sound design of a reference video: where every SFX is, what kind, how loud
(relative to the voice), what the background music is like and how loud.

The soundtrack is first split into voice and music+SFX with analysis/separate.py
(UVR MDX-Net, ONNX). SFX are the broadband bursts in the music+SFX stem (music is
mostly tonal lines); the music bed is the quiet floor of that stem between SFX.

Usage: audio_ref.py video.mp4 [subs.srt] out_prefix
  env MDX_MODEL = path of UVR-MDX-NET-Inst_HQ_3.onnx (stems are cached as out_prefix_inst/voice.wav)
Writes out_prefix.json, out_prefix_spec.png (spectrogram + markers), out_prefix_sfx.png
(the frame at every SFX, to see which visual it was put on)."""
import json
import os
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import librosa
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "assembler"))
sys.path.insert(0, str(HERE))
from assemble import parse_srt  # noqa: E402

SR = 44100
HOP = 441          # 10 ms
NFFT = 2048
THR = 0.4          # share of high bins that must jump at once


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-6))


def smooth(x, n):
    return np.convolve(x, np.ones(n) / n, mode="same")


def rolling_pct(x, win, q):
    out = np.empty_like(x)
    h = win // 2
    for i in range(0, len(x), 10):
        out[i:i + 10] = np.percentile(x[max(0, i - h):i + h], q)
    return out


def stems(video, prefix):
    inst, voice = prefix + "_inst.wav", prefix + "_voice.wav"
    if not os.path.exists(inst):
        import separate
        model = os.environ.get("MDX_MODEL", str(HERE / "models" / "UVR-MDX-NET-Inst_HQ_3.onnx"))
        separate.main(video, model, prefix)
    return (librosa.load(inst, sr=SR, mono=True)[0], librosa.load(voice, sr=SR, mono=True)[0])


def cuts(video, thr=0.25):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", video, "-vf", f"select='gt(scene,{thr})',showinfo",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    return [float(l.split("pts_time:")[1].split()[0]) for l in out.splitlines() if "showinfo" in l and "pts_time:" in l]


def classify(f):
    """Rough SFX family, named like animator/audio.py."""
    d, c, flat, low, high, slope, tonal = (f["dur"], f["centroid"], f["flatness"], f["low_ratio"], f["high_ratio"],
                                           f["centroid_slope"], f["tonal"])
    if low > 0.45 and d < 1.0:
        return "thud/boom (low hit)"
    if d >= 0.3 and tonal < 0.35 and abs(slope) > 600:
        return "whoosh (sweep " + ("up" if slope > 0 else "down") + ")"
    if d >= 0.3 and tonal < 0.35:
        return "whoosh/air (noise swell)"
    if tonal >= 0.35 and d >= 0.3:
        return "ding/chime/sting (tonal ring)"
    if d < 0.12 and c > 3000:
        return "tick/click"
    if d < 0.3:
        return "pop/snap/swish (short)"
    return "impact/other"


def sfx_events(inst, times, i_db):
    """SFX = wide-band bursts: many high-frequency bins jump >12 dB over their own
    running median at once (a music note lights up only a few harmonics)."""
    S = np.abs(librosa.stft(inst, n_fft=NFFT, hop_length=HOP))
    f = librosa.fft_frequencies(sr=SR, n_fft=NFFT)
    D = db(S[(f > 1500) & (f < 14000)][::4])
    med = np.stack([rolling_pct(r, 400, 50) for r in D])
    frac = smooth(np.mean(D - med > 12, axis=0), 5)
    lo = smooth(db(np.sqrt(np.mean(S[(f > 30) & (f < 150)] ** 2, axis=0))), 3)
    lo_jump = lo - rolling_pct(lo, 400, 50)
    n = min(len(frac), len(times), len(i_db))
    ev, i = [], 0
    while i < n:
        if not (frac[i] > THR or lo_jump[i] > 15):
            i += 1
            continue
        j = i
        while j < n and (frac[j] > THR * 0.5 or lo_jump[j] > 8):
            j += 1
        s, j = i, max(j, i + 3)
        seg = S[:, s:j]
        spec = seg.mean(axis=1)
        cent = librosa.feature.spectral_centroid(S=seg, sr=SR)[0]
        srt = np.sort(spec)[::-1]
        pk = s + int(np.argmax(i_db[s:j]))
        e = dict(t=round(float(times[s]), 2), peak_t=round(float(times[pk]), 2), dur=round((j - s) * HOP / SR, 2),
                 peak_db=round(float(i_db[pk]), 1),
                 centroid=int(np.median(cent)), flatness=round(float(np.median(librosa.feature.spectral_flatness(S=seg))), 3),
                 low_ratio=round(float(spec[f < 200].sum() / max(spec.sum(), 1e-9)), 2),
                 high_ratio=round(float(spec[f > 2500].sum() / max(spec.sum(), 1e-9)), 2),
                 tonal=round(float(srt[:12].sum() / max(srt.sum(), 1e-9)) * 3, 2),
                 centroid_slope=int(np.polyfit(np.arange(len(cent)), cent, 1)[0] * 100) if len(cent) > 3 else 0)
        e["kind"] = classify(e)
        ev.append(e)
        i = j + 20
    return ev


def visual_change(video):
    """Mean frame difference at 10 fps: peaks are cuts, whip pans, dissolves, pops."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", "fps=10,scale=72:128,format=gray", "-f", "rawvideo",
                          "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 128, 72).astype(np.float32)
    d = np.r_[0, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))]
    return d


def music_profile(y):
    if len(y) < SR * 2 or np.sqrt(np.mean(y ** 2)) < 1e-4:
        return {}
    tempo, _ = librosa.beat.beat_track(y=y, sr=SR, hop_length=512)
    h, p = librosa.effects.hpss(y)
    perc = float(np.sum(p ** 2) / max(np.sum(y ** 2), 1e-12))
    chroma = librosa.feature.chroma_cqt(y=h, sr=SR).mean(axis=1)
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    names = "C C# D D# E F F# G G# A A# B".split()
    best = max((np.corrcoef(np.roll(prof, k), chroma)[0, 1], names[k] + mode)
               for prof, mode in ((major, " major"), (minor, " minor")) for k in range(12))
    S = np.abs(librosa.stft(h, n_fft=4096, hop_length=1024))
    f = librosa.fft_frequencies(sr=SR, n_fft=4096)
    tot = S.sum() + 1e-9
    bands = {"bass<200": S[f < 200].sum() / tot, "mid200-2k": S[(f >= 200) & (f < 2000)].sum() / tot,
             "high>2k": S[f >= 2000].sum() / tot}
    return dict(tempo_bpm=round(float(np.atleast_1d(tempo)[0])), key=best[1], key_fit=round(float(best[0]), 2),
                percussive_share=round(perc, 2), brightness_hz=int(np.median(librosa.feature.spectral_centroid(y=h, sr=SR))),
                notes_per_s=round(len(librosa.onset.onset_detect(y=h, sr=SR)) / (len(y) / SR), 1),
                energy_bands={k: round(float(v), 2) for k, v in bands.items()})


def grab(video, t, w=150):
    from PIL import Image
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-vf",
                          f"scale={w}:-1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(BytesIO(out)).convert("RGB")


def line_at(cues, t):
    for a, b, txt in cues:
        if a - 0.15 <= t <= b + 0.15:
            return txt
    return ""


def main(video, srt, prefix):
    inst, voice = stems(video, prefix)
    dur = len(inst) / SR
    cues = parse_srt(srt) if srt else []
    v_db = db(librosa.feature.rms(y=voice, frame_length=NFFT, hop_length=HOP)[0])
    i_db = db(librosa.feature.rms(y=inst, frame_length=NFFT, hop_length=HOP)[0])
    times = librosa.frames_to_time(np.arange(len(i_db)), sr=SR, hop_length=HOP)
    active = v_db > np.percentile(v_db, 90) - 20
    voice_db = float(np.median(v_db[active]))

    ev = sfx_events(inst, times, i_db)
    mask = np.ones(len(i_db), bool)
    for e in ev:
        a = int(e["t"] * 100)
        mask[a:a + int(e["dur"] * 100) + 10] = False
    music_db = float(np.median(i_db[mask])) if mask.any() else float(np.median(i_db))
    per_s = [round(float(np.median(i_db[k * 100:k * 100 + 100][mask[k * 100:k * 100 + 100]]))
                   if mask[k * 100:k * 100 + 100].any() else -99, 1) for k in range(int(dur))]
    vc = cuts(video, 0.1)
    vis = visual_change(video)
    peaks = [k for k in range(1, len(vis) - 1) if vis[k] >= vis[k - 1] and vis[k] >= vis[k + 1]
             and vis[k] > np.percentile(vis, 80)]
    def near_vis(t):
        return any(abs(k / 10 - t) <= 0.2 for k in peaks)
    rnd = np.random.default_rng(0).uniform(0, dur, 400)
    for e in ev:
        e["vs_voice_db"] = round(e["peak_db"] - voice_db, 1)
        e["volume_factor"] = round(10 ** ((e["peak_db"] - voice_db) / 20), 2)
        e["near_cut"] = bool(any(abs(c - e["peak_t"]) < 0.25 or abs(c - e["t"]) < 0.25 for c in vc))
        e["line"] = line_at(cues, e["peak_t"])
        e["on_visual_change"] = bool(near_vis(e["t"]) or near_vis(e["peak_t"]))

    clean = inst.copy()
    for e in ev:  # music only, for the music profile
        clean[int(e["t"] * SR):int((e["t"] + e["dur"]) * SR)] = 0
    segs = [dict(t0=s, t1=round(min(dur, s + 15), 1), **music_profile(clean[int(s * SR):int(min(dur, s + 15) * SR)]))
            for s in range(0, int(dur), 15)]
    kinds = {}
    for e in ev:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    report = dict(video=Path(video).name, duration=round(dur, 2), voice_db=round(voice_db, 1),
                  music_db=round(music_db, 1), music_vs_voice_db=round(music_db - voice_db, 1),
                  music_volume_factor=round(10 ** ((music_db - voice_db) / 20), 3),
                  music_db_per_s=per_s, music_whole=music_profile(clean), music_segments=segs,
                  cuts=[round(c, 2) for c in vc], sfx_count=len(ev), sfx_per_10s=round(len(ev) / dur * 10, 1),
                  sfx_kinds=kinds,
                  sfx_on_visual_change_share=round(float(np.mean([e["on_visual_change"] for e in ev])), 2) if ev else 0,
                  random_on_visual_change_share=round(float(np.mean([near_vis(t) for t in rnd])), 2),
                  visual_change_peaks_per_10s=round(len(peaks) / dur * 10, 1),
                  sfx_on_cuts_share=round(float(np.mean([e["near_cut"] for e in ev])), 2) if ev else 0,
                  sfx_median_vs_voice_db=round(float(np.median([e["vs_voice_db"] for e in ev])), 1) if ev else None,
                  sfx=ev)
    Path(prefix + ".json").write_text(json.dumps(report, indent=1))
    plots(video, inst, report, cues, prefix)
    return report


def plots(video, inst, rep, cues, prefix):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dur = rep["duration"]
    fig, ax = plt.subplots(2, 1, figsize=(max(16, dur / 2.5), 7), sharex=True, gridspec_kw=dict(height_ratios=[3, 1]))
    S = librosa.amplitude_to_db(np.abs(librosa.stft(inst, n_fft=NFFT, hop_length=512)), ref=np.max)
    ax[0].imshow(S[:700], origin="lower", aspect="auto", extent=[0, dur, 0, 700 * SR / NFFT], vmin=-80, vmax=0,
                 cmap="magma")
    ax[0].set_ylabel("music + SFX stem, Hz")
    for e in rep["sfx"]:
        ax[0].axvline(e["t"], color="lime", lw=0.8)
        ax[0].text(e["t"], 14500, e["kind"].split()[0], color="lime", fontsize=7, rotation=90, va="top")
    for c in rep["cuts"]:
        ax[0].axvline(c, color="cyan", lw=0.6, ls=":")
    for a, b, txt in cues:
        ax[1].text(a, 0.5, txt[:30], fontsize=6, rotation=90, va="center")
    ax[1].set_xticks(np.arange(0, dur, 2))
    ax[1].set_xlabel("s  (green = SFX, cyan = picture cut)")
    plt.tight_layout()
    plt.savefig(prefix + "_spec.png", dpi=60)
    plt.close()

    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.load_default(size=12)
    tiles = []
    for e in rep["sfx"]:
        im = grab(video, e["peak_t"])
        tile = Image.new("RGB", (im.width, im.height + 58), "white")
        tile.paste(im, (0, 0))
        d = ImageDraw.Draw(tile)
        d.text((3, im.height + 2), f"{e['t']}s {e['kind'][:17]}", fill="red", font=font)
        d.text((3, im.height + 16), f"{e['vs_voice_db']} dB vs voice", fill="black", font=font)
        d.text((3, im.height + 30), e["line"][:24], fill="blue", font=font)
        d.text((3, im.height + 43), e["line"][24:48], fill="blue", font=font)
        tiles.append(tile)
    if tiles:
        cols = 10
        w, h = tiles[0].size
        sheet = Image.new("RGB", (w * cols, h * ((len(tiles) + cols - 1) // cols)), "white")
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * w, (i // cols) * h))
        sheet.save(prefix + "_sfx.png")


if __name__ == "__main__":
    a = sys.argv[1:]
    r = main(a[0], a[1] if len(a) == 3 else None, a[-1])
    print(f"{r['video']}: voice {r['voice_db']} dB, music {r['music_db']} dB "
          f"({r['music_vs_voice_db']} dB = x{r['music_volume_factor']} of voice); "
          f"{r['sfx_count']} SFX ({r['sfx_per_10s']}/10s, {int(r['sfx_on_cuts_share'] * 100)}% on cuts, "
          f"median {r['sfx_median_vs_voice_db']} dB vs voice; on a visual change {r['sfx_on_visual_change_share']} "
          f"vs random {r['random_on_visual_change_share']})")
    print("kinds:", r["sfx_kinds"])
    print("music:", r["music_whole"])
    for s in r["music_segments"]:
        print("  ", s)
    for e in r["sfx"]:
        print(f"  {e['t']:6.2f}s {e['dur']:4.2f}s {e['vs_voice_db']:6.1f}dB vis={int(e['on_visual_change'])} "
              f"{e['kind']:30s} {e['line'][:45]}")
