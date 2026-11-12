#!/usr/bin/env python3
"""Join Flow clips + voiceover + SRT into a 9:16 short with crossfades,
word-by-word captions and SFX. Needs ffmpeg/ffprobe on PATH."""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path

W, H, FPS = 720, 1280, 30
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}


def probe_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], text=True)
    return float(out.strip())


def parse_ts(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8").strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        timing = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if timing is None:
            continue
        a, b = [t.strip() for t in lines[timing].split("-->")]
        text = " ".join(lines[timing + 1:])
        text = re.sub(r"\(Transcribed by TurboScribe[^)]*\)\s*", "", text).strip()
        if text:
            cues.append((parse_ts(a), parse_ts(b), text))
    return cues


def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def build_ass(cues, words_per_caption, font):
    head = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {W}\nPlayResY: {H}\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding\n"
        f"Style: Cap,{font},68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,"
        "-1,0,0,0,100,100,0,0,1,6,2,2,40,40,380,1\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
    events = []
    for start, end, text in cues:
        words = text.split()
        groups = [words[i:i + words_per_caption] for i in range(0, len(words), words_per_caption)]
        total = sum(len(g) for g in groups)
        t = start
        for g in groups:
            d = (end - start) * len(g) / total
            events.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},Cap,,0,0,0,,{' '.join(g)}")
            t += d
    return head + "\n".join(events) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--clips", required=True, help="folder of clips, sorted by name")
    p.add_argument("--voice", help="voiceover audio file")
    p.add_argument("--srt", help="SRT for captions")
    p.add_argument("--sfx", help="JSON cue list, see sfx_cues.example.json")
    p.add_argument("--sfx-dir", default=".", help="folder the SFX files are in")
    p.add_argument("--transition-sfx", help="SFX file played at every crossfade")
    p.add_argument("--music", help="background music, looped and kept quiet")
    p.add_argument("--music-volume", type=float, default=0.12)
    p.add_argument("--xfade", type=float, default=0.4, help="crossfade seconds")
    p.add_argument("--words", type=int, default=2, help="words per caption")
    p.add_argument("--font", default="Arial")
    p.add_argument("--crf", type=int, default=20, help="x264 quality, higher = smaller file")
    p.add_argument("--out", default="final.mp4")
    a = p.parse_args()

    clips = sorted(f for f in Path(a.clips).iterdir() if f.suffix.lower() in VIDEO_EXT)
    if not clips:
        sys.exit(f"no video clips found in {a.clips}")
    durs = [probe_duration(c) for c in clips]
    n, d = len(clips), a.xfade
    if any(x <= d * 2 for x in durs):
        sys.exit("a clip is shorter than twice the crossfade, lower --xfade")
    vid_len = sum(durs) - (n - 1) * d
    target = max(vid_len, probe_duration(a.voice)) if a.voice else vid_len
    # offsets where each crossfade starts
    offsets = [sum(durs[:k]) - k * d for k in range(1, n)]

    inputs, fc = [], []
    for i, c in enumerate(clips):
        inputs += ["-i", str(c.resolve())]
        fc.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
                  f"crop={W}:{H},fps={FPS},setsar=1,format=yuv420p,settb=AVTB[v{i}]")
    last = "v0"
    for k in range(1, n):
        fc.append(f"[{last}][v{k}]xfade=transition=fade:duration={d}:offset={offsets[k-1]:.3f}[x{k}]")
        last = f"x{k}"
    vf = [f"tpad=stop_mode=clone:stop_duration={max(0.0, target - vid_len) + 0.1:.3f}"]
    tmp = Path(tempfile.mkdtemp())
    if a.srt:
        (tmp / "cap.ass").write_text(build_ass(parse_srt(a.srt), a.words, a.font), encoding="utf-8")
        vf.append("ass=cap.ass")
    fc.append(f"[{last}]{','.join(vf)}[vout]")

    # audio
    mix, idx = [], n
    def add_input(path):
        nonlocal idx
        inputs.extend(["-i", str(Path(path).resolve())])
        idx += 1
        return idx - 1
    if a.voice:
        i = add_input(a.voice)
        fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo[a_voice]")
        mix.append("a_voice")
    cues = []
    if a.sfx:
        cues += json.loads(Path(a.sfx).read_text())
    if a.transition_sfx:
        cues += [{"time": o + d / 2 - 0.15, "file": a.transition_sfx, "volume": 0.6} for o in offsets]
    for j, cue in enumerate(cues):
        f = Path(cue["file"])
        f = f if f.is_absolute() or f.exists() else Path(a.sfx_dir) / f
        i = add_input(f)
        ms = max(0, int(cue["time"] * 1000))
        fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
                  f"adelay={ms}|{ms},volume={cue.get('volume', 1.0)}[s{j}]")
        mix.append(f"s{j}")
    if a.music:
        i = add_input(a.music)
        fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
                  f"aloop=loop=-1:size=2000000000,volume={a.music_volume}[a_mus]")
        mix.append("a_mus")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs]
    if mix:
        fc.append("".join(f"[{m}]" for m in mix) +
                  f"amix=inputs={len(mix)}:normalize=0:duration=longest,alimiter=limit=0.89[aout]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[vout]"]
    cmd += ["-map", "[aout]"] if mix else []
    out = Path(a.out).resolve()
    cmd += ["-t", f"{target:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf),
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True, cwd=tmp)
    print(f"wrote {out} ({target:.1f}s, {n} clips)")


if __name__ == "__main__":
    main()
