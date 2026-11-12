#!/usr/bin/env python3
"""Word timings for a voiceover: recognise words with pocketsphinx (offline), then
align the clean script (or the SRT text) to them so every script word gets a time.
Usage: align_words.py voice.mp3 script.txt|subs.srt out_dir
Writes out_dir/script.txt, aligned.json (word, start, end) and captions.srt (1 word per cue)."""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assembler"))
from assemble import parse_srt


def recognise(voice):
    from pocketsphinx import Decoder
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(voice), "-ar", "16000", "-ac", "1",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    d = Decoder(samprate=16000)
    d.start_utt()
    d.process_raw(raw, full_utt=True)
    d.end_utt()
    return [{"w": s.word, "s": s.start_frame / 100, "e": (s.end_frame + 1) / 100}
            for s in d.seg() if not s.word.startswith(("<", "["))]


def norm(w):
    return re.sub(r"\(\d+\)|[^a-z0-9]", "", w.lower())


def main(voice, text_path, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if text_path.endswith(".srt"):
        text = " ".join(c[2] for c in parse_srt(text_path))
    else:
        text = Path(text_path).read_text(encoding="utf-8")
    words = text.split()
    (out / "script.txt").write_text(" ".join(words) + "\n", encoding="utf-8")
    ps = recognise(voice)
    sw, pw = [norm(w) for w in words], [norm(x["w"]) for x in ps]
    t = [None] * len(words)
    for a, b, n in difflib.SequenceMatcher(None, sw, pw, autojunk=False).get_matching_blocks():
        for k in range(n):
            t[a + k] = (ps[b + k]["s"], ps[b + k]["e"])
    known = [i for i, x in enumerate(t) if x]
    end = ps[-1]["e"] if ps else 0.0
    for i in range(len(words)):  # spread unmatched words evenly between matched neighbours
        if t[i]:
            continue
        L = max((k for k in known if k < i), default=None)
        R = min((k for k in known if k > i), default=None)
        ls = t[L][1] if L is not None else 0.0
        rs = t[R][0] if R is not None else end
        li = L if L is not None else -1
        ri = R if R is not None else len(words)
        step = (rs - ls) / (ri - li)
        t[i] = (ls + step * (i - li - 1), ls + step * (i - li))
    aligned = [{"w": w, "s": round(a, 2), "e": round(b, 2)} for w, (a, b) in zip(words, t)]
    json.dump(aligned, open(out / "aligned.json", "w"))

    def ts(v):
        ms = int(round(v * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(out / "captions.srt", "w") as f:
        for i, x in enumerate(aligned):
            e = aligned[i + 1]["s"] if i + 1 < len(aligned) else x["e"]
            f.write(f"{i + 1}\n{ts(x['s'])} --> {ts(max(e, x['s'] + 0.05))}\n{x['w']}\n\n")
    print(f"matched {len(known)}/{len(words)} words; wrote {out}/aligned.json")
    for i, x in enumerate(aligned):
        print(f"{i}:{x['w']}@{x['s']:.2f}", end=" ")
    print()


if __name__ == "__main__":
    main(*sys.argv[1:4])
