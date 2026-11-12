"""Script statistics for a timed transcript (.tsv "start<TAB>text", last line "end<TAB>END")
or an .srt file, or a plain .txt script (no timing).

Usage:
  python3 analysis/script_stats.py <file> [--srt out.srt] [--chapters "0:00 Name,0:41 Name,..."]

Prints: words, characters (with/without spaces), duration, words per minute,
sentence-length stats, pauses > 1.5 s (section breaks), and per-chapter share of runtime.
"""
import re
import sys
import json


def parse(path):
    rows = []
    if path.endswith(".srt"):
        blocks = open(path, encoding="utf-8").read().strip().split("\n\n")
        for b in blocks:
            ls = b.strip().splitlines()
            if len(ls) < 3:
                continue
            m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)", ls[1])
            if not m:
                continue
            g = [int(x) for x in m.groups()]
            s = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
            e = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
            rows.append([s, e, " ".join(ls[2:])])
        return rows
    if path.endswith(".txt"):
        return [[None, None, open(path, encoding="utf-8").read()]]
    raw = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        t, txt = line.split("\t", 1)
        raw.append((float(t), txt))
    for i, (t, txt) in enumerate(raw):
        if txt == "END":
            continue
        nxt = raw[i + 1][0] if i + 1 < len(raw) else t + 2
        rows.append([t, nxt, txt])
    return rows


def ts(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"


def write_srt(rows, out):
    with open(out, "w", encoding="utf-8") as f:
        for i, (s, e, txt) in enumerate(rows, 1):
            f.write(f"{i}\n{ts(s)} --> {ts(e - 0.02)}\n{txt}\n\n")


def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def main():
    path = sys.argv[1]
    rows = parse(path)
    text = " ".join(r[2] for r in rows)
    words = re.findall(r"[A-Za-z0-9'’$%.-]+", text)
    words = [w for w in words if re.search(r"[A-Za-z0-9]", w)]
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if re.search(r"\w", s)]
    slen = sorted(len(re.findall(r"\w[\w'’-]*", s)) for s in sentences)
    out = {
        "file": path,
        "words": len(words),
        "chars_with_spaces": len(text),
        "chars_no_spaces": len(re.sub(r"\s", "", text)),
        "sentences": len(sentences),
        "sentence_words_median": slen[len(slen) // 2] if slen else 0,
        "sentence_words_mean": round(sum(slen) / len(slen), 1) if slen else 0,
        "sentences_<=4_words_pct": round(100 * sum(1 for x in slen if x <= 4) / max(1, len(slen))),
        "sentences_>=15_words_pct": round(100 * sum(1 for x in slen if x >= 15) / max(1, len(slen))),
    }
    if rows[0][0] is not None:
        dur = rows[-1][1]
        out["duration_s"] = round(dur, 1)
        out["duration"] = mmss(dur)
        out["wpm"] = round(len(words) / (dur / 60), 1)
        out["chars_per_min"] = round(len(text) / (dur / 60))
        gaps = []
        for a, b in zip(rows, rows[1:]):
            # a pause = the next line starts well after this line's spoken length would end
            pass
        # pauses: SRT start gaps where the line before was short relative to the gap
        for i in range(1, len(rows)):
            prev_s, _, prev_t = rows[i - 1]
            need = len(prev_t.split()) / 2.9  # ~174 wpm speaking
            gap = rows[i][0] - prev_s - need
            if gap > 1.5:
                gaps.append((round(rows[i][0], 1), mmss(rows[i][0]), round(gap, 1), rows[i][2][:60]))
        out["pauses_over_1.5s"] = gaps
    chap = None
    if "--chapters" in sys.argv:
        chap = sys.argv[sys.argv.index("--chapters") + 1]
    if chap and rows[0][0] is not None:
        marks = []
        for c in chap.split(","):
            c = c.strip()
            m = re.match(r"(\d+):(\d+)\s+(.*)", c)
            marks.append((int(m.group(1)) * 60 + int(m.group(2)), m.group(3)))
        dur = rows[-1][1]
        res = []
        for i, (t, name) in enumerate(marks):
            end = marks[i + 1][0] if i + 1 < len(marks) else dur
            wtxt = " ".join(r[2] for r in rows if t <= r[0] < end)
            res.append({"start": mmss(t), "name": name, "secs": round(end - t),
                        "pct": round(100 * (end - t) / dur, 1),
                        "words": len(wtxt.split()), "chars": len(wtxt)})
        out["chapters"] = res
    if "--srt" in sys.argv and rows[0][0] is not None:
        write_srt(rows, sys.argv[sys.argv.index("--srt") + 1])
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
