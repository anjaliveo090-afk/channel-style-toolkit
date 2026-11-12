#!/usr/bin/env python3
"""SRT (from your voiceover) -> 10s clip plan: narration per clip, word speed, SFX hints.
Usage: plan_clips.py script.srt > plan.md"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from assemble import parse_srt

CLIP = 10.0
SFX_HINTS = [
    (r"\b(clock|ticking|time|hour)\b", "clock tick"),
    (r"\b(phone|scroll|email|inbox)\b", "phone tap / notification"),
    (r"\b(gone|disappear|vanish|empty)\b", "soft whoosh + low hit"),
    (r"\b(imagine|suddenly|then|but|until)\b", "whoosh on the cut"),
    (r"\b(impossible|never|nobody|nothing|worse|miserable)\b", "dramatic sting"),
    (r"\b(laugh|laughed|smile|paradise|happy)\b", "light pop / chime"),
    (r"\b(money|cash|yen|win|prize)\b", "coin / cash sound"),
]


def main():
    cues = parse_srt(sys.argv[1])
    total = max(e for _, e, _ in cues)
    n = int(total // CLIP) + (total % CLIP > 0.5)
    print(f"# Clip plan ({n} clips, {total:.1f}s)\n")
    for k in range(n):
        a, b = k * CLIP, (k + 1) * CLIP
        lines = [c for c in cues if a <= c[0] < b]
        text = " ".join(c[2] for c in lines)
        words = len(text.split())
        hints = sorted({h for pat, h in SFX_HINTS if re.search(pat, text, re.I)})
        print(f"## Clip {k + 1} ({a:.0f}-{b:.0f}s)")
        print(f"Narration: {text}")
        print(f"Speed: {words / CLIP:.1f} words/s")
        print(f"SFX hints: whoosh at each shot change" + "".join(f"; {h}" for h in hints))
        print("Prompt: <fill from style_bible.md CLIP TEMPLATE>\n")


if __name__ == "__main__":
    main()
