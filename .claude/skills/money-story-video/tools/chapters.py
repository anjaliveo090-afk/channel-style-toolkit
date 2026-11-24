"""Print YouTube chapter timestamps for a story (the time each chapter card appears).
   python3 chapters.py <story_module>"""
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root / "animator"))
mod = __import__(sys.argv[1])
st = mod.build()
first = st.sents[0]["chapter"]


def ts(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


print(f"0:00 {st.sents[0]['chapter_name'].title()}")
for g0, ln, ch, name in st.gaps:
    t = g0 + 2.0 if ch == first + 1 else g0      # after chapter 1 the title card comes first
    print(f"{ts(t)} {name.title()}")
