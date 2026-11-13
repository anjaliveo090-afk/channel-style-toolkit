#!/usr/bin/env python3
"""Align a voiceover SRT to the speaker-labelled script so every spoken sentence gets its speaker and chapter.

Script format (scripts/*_blocks.txt): [CHAPTER n: NAME] headers, "SPEAKER: text" blocks, [beat] lines.
Usage: script_align.py subs.srt script_blocks.txt out.json
Output: list of {"i","start","end","text","speaker","chapter","chapter_name","script_text","match"}
Timing is spread over SRT cues proportionally to characters, so sentences that share a cue get split.
"""
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assembler"))
from assemble import parse_srt  # noqa: E402


def norm(s):
    s = s.lower().replace("’", "'")
    return re.sub(r"[^a-z0-9' ]+", " ", s).split()


def script_sentences(path):
    out, chap, cname = [], 0, ""
    for line in Path(path).read_text().splitlines():
        m = re.match(r"\[CHAPTER (\d+): (.*)\]", line)
        if m:
            chap, cname = int(m.group(1)), m.group(2)
            continue
        m = re.match(r"([A-Z][A-Z ]+): (.*)", line)
        if not m or line.startswith(("TITLE", "FORMAT", "VOICE")):
            continue
        spk, txt = m.group(1), m.group(2)
        for s in re.split(r'(?<=[.!?"”])\s+(?=[A-Z"“])', txt):
            if s.strip():
                out.append({"speaker": spk, "chapter": chap, "chapter_name": cname, "script_text": s.strip()})
    return out


def word_times(cues):
    """every spoken word with an estimated time (proportional to characters inside its cue)"""
    words = []
    for s, e, t in cues:
        toks = t.split()
        total = sum(len(x) + 1 for x in toks) or 1
        acc = 0
        for x in toks:
            ws = s + (e - s) * acc / total
            acc += len(x) + 1
            we = s + (e - s) * acc / total
            for w in norm(x):
                words.append((w, ws, we))
    return words


NUM = {"thirty-three": "33", "ninety": "90"}


def main(srt, script, out):
    cues = parse_srt(srt)
    sents = script_sentences(script)
    words = word_times(cues)
    spoken = [w for w, _, _ in words]
    # script words in order, with sentence index; numbers in the SRT are digits, script spells them out:
    # match on a relaxed basis (difflib on word sequences)
    sw, owner = [], []
    for i, s in enumerate(sents):
        for w in norm(s["script_text"]):
            sw.append(w)
            owner.append(i)
    sm = difflib.SequenceMatcher(None, sw, spoken, autojunk=False)
    first, last = {}, {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            i = owner[a + k]
            j = b + k
            first.setdefault(i, j)
            last[i] = j
    res = []
    prev_end = cues[0][0] if cues else 0.0
    for i, s in enumerate(sents):
        if i in first:
            st, en = words[first[i]][1], words[last[i]][2]
            match = round((last[i] - first[i] + 1) / max(1, len(norm(s["script_text"]))), 2)
        else:
            st, en, match = prev_end, prev_end + 0.5, 0.0
        st = max(st, prev_end)
        en = max(en, st + 0.2)
        res.append(dict(i=i, start=round(st, 3), end=round(en, 3), match=match, **s))
        prev_end = en
    json.dump(res, open(out, "w"), indent=1)
    bad = [r for r in res if r["match"] < 0.5]
    print(len(res), "sentences;", len(bad), "weak matches")
    for r in bad[:20]:
        print("  weak:", r["i"], r["speaker"], r["script_text"][:60], r["match"])


if __name__ == "__main__":
    main(*sys.argv[1:4])
