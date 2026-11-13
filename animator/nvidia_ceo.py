"""How a Chinese Spy Brought Down Nvidia's CEO: shot plan for the user's voiceover.
Sentence indices come from output/nvidia/align.json (analysis/script_align.py). Characters are original
designs; real people appear only as simple cartoon figures identified by name tags.
Run:
  python3 animator/nvidia_ceo.py audio          # mix.wav
  python3 animator/nvidia_ceo.py part K N       # render part K of N (run N in parallel)
  python3 animator/nvidia_ceo.py concat N       # join parts + mix -> final mp4
  python3 animator/nvidia_ceo.py still T ...    # check frames
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import devices as D  # noqa: E402
import places2 as P2  # noqa: E402
import sets  # noqa: E402
import story  # noqa: E402
from style import Char  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ALIGN = ROOT / "output/nvidia/align.json"
VOICE = ROOT / "output/nvidia/voice.mp3"
OUT = ROOT / "output/nvidia"
TITLE = "How a Chinese Spy Brought Down Nvidia's CEO"
TITLE_REDACT = "Spy"

CHAPTER_MOOD = {1: ("minor", 50), 2: ("minor", 45), 3: ("minor", 50), 4: ("minor", 52), 5: ("minor", 47),
                6: ("minor", 50), 7: ("major", 53), 8: ("minor", 50)}

JENSEN = Char(body="#151515", hair="side", hair_col="#b9b3ab", glasses="rect", collar="round", lapels=True,
              pants="#101010", light=(1.0, 0.25))
ALICE = Char(body="#b0161c", hair="bob", hair_col="#141014", collar="round", earrings="#e8c050", build=0.88,
             light=(-1.0, 0.25), skin={"hi": "#fcd08a", "mid": "#dba37c", "sh": "#b38b73", "rim": "#febd6c"})
KRESS = Char(body="#2d4f86", hair="bob", hair_col="#d9b878", collar="shirt", lapels=True, build=0.9,
             pants="#1b2333", light=(1.0, 0.2))
SUIT = dict(collar="shirt", lapels=True)
CAST = {
    "JENSEN": JENSEN, "ALICE": ALICE, "KRESS": KRESS,
    "BOARD MEMBER": Char(body="#2a2f3a", hair="bald", hair_col="#d8d2c8", glasses="round", tie="#7a1a1a", **SUIT),
    "BOARD MEMBER ONE": Char(body="#2a2f3a", hair="bald", hair_col="#d8d2c8", glasses="round", tie="#7a1a1a", **SUIT),
    "BOARD MEMBER TWO": Char(body="#3a2a22", hair="bob", hair_col="#8a8a8a", build=0.9, **SUIT),
    "BOARD MEMBER THREE": Char(body="#1f3a2a", hair="short", hair_col="#2a1c14", tie="#c8a03a", mustache="#2a1c14", **SUIT),
    "LAWYER": Char(body="#1b1e26", hair="side", hair_col="#1d1716", glasses="rect", tie="#2a4fa0", **SUIT),
    "CUSTOMER": Char(body="#e0a23a", hair="bowl", hair_col="#1d1716", collar="round"),
    "CLERK": Char(body="#3a3a42", hair="spiky", hair_col="#1d1716", glasses="shades", collar="round"),
    "REPORTER": Char(body="#c9502e", hair="bun", hair_col="#5a3a26", collar="shirt", build=0.9),
    "REPORTER TWO": Char(body="#3e6fa8", hair="short", hair_col="#2a1c14", glasses="round", collar="shirt"),
    "SOURCE": Char(body="#2b2b30", hair="short", hair_col="#111", collar="turtleneck", glasses="shades"),
    "AIDE": Char(body="#3e6fa8", hair="bowl", hair_col="#5a3a26", collar="shirt", tie="#a3161d"),
    "CHAIRMAN": Char(body="#1c2233", hair="side", hair_col="#d8d2c8", tie="#a3161d", pin="#c8a03a", **SUIT),
    "EMPLOYEE ONE": Char(body="#5c8a3c", hair="curly", hair_col="#2a1c14", collar="round"),
    "EMPLOYEE TWO": Char(body="#8a4f9e", hair="bun", hair_col="#1d1716", glasses="round", collar="round", build=0.9),
    "TRADER": Char(body="#c9c6c0", hair="side", hair_col="#3a2a20", tie="#c8312c", collar="shirt"),
    "ANALYST": Char(body="#2f7a4f", hair="bun", hair_col="#6e2a18", glasses="round", collar="round", build=0.9),
    "ANALYST ONE": Char(body="#23436b", hair="short", hair_col="#2a1c14", glasses="rect", tie="#c8a03a", **SUIT),
    "ANALYST TWO": Char(body="#7a5530", hair="bob", hair_col="#1d1716", collar="shirt", build=0.9),
    "INVESTOR": Char(body="#e2805a", hair="spiky", hair_col="#1d1716", collar="round"),
    "BROKER": Char(body="#1f2a44", hair="side", hair_col="#1d1716", tie="#3a9a4a", **SUIT),
    "FAN": Char(body="#3e6fa8", hair="bowl", hair_col="#1d1716", collar="round"),
    "REFEREE": Char(body="#f2f2f2", hair="bald", hair_col="#2a1c14", collar="round", pants="#111"),
    "SPOKESPERSON": Char(body="#2f2f3a", hair="bob", hair_col="#3a2a20", build=0.9, **SUIT),
    "TRADER ONE": Char(body="#c9c6c0", hair="side", hair_col="#3a2a20", tie="#c8312c", collar="shirt"),
    "TRADER TWO": Char(body="#1f2a44", hair="short", hair_col="#111", glasses="shades", tie="#c8a03a", **SUIT),
    "HEADHUNTER": Char(body="#6b2a4a", hair="bob", hair_col="#1d1716", glasses="rect", build=0.9, **SUIT),
    "DINER": Char(body="#e0a23a", hair="curly", hair_col="#5a3a26", collar="round"),
    "WAITER": Char(body="#f2f2f2", hair="side", hair_col="#1d1716", tie="#111", collar="shirt", pants="#111"),
    "YOU": Char(body="#5c8a3c", hair="bowl", hair_col="#3a2a20", collar="round"),
    "STAGEHAND": Char(body="#2b2b30", hair="short", hair_col="#5a3a26", collar="round"),
    "STAGE MANAGER": Char(body="#3a2a22", hair="bun", hair_col="#1d1716", glasses="round", collar="round", build=0.9),
    "FRIEND": Char(body="#3e6fa8", hair="bowl", hair_col="#1d1716", collar="round"),
    "PRESIDENT": Char(body="#1c2233", hair="side", hair_col="#e8d8a8", tie="#c8312c", **SUIT),
    "HARVEY": Char(body="#2a2f3a", hair="bald", hair_col="#d8d2c8", glasses="rect", tie="#2a4fa0", **SUIT),
    "CONGRESSMAN ONE": Char(body="#2a2a36", hair="short", hair_col="#8a8a8a", tie="#2a4fa0", pin="#c8a03a", **SUIT),
    "CONGRESSMAN TWO": Char(body="#3a2a2a", hair="bald", hair_col="#d8d2c8", tie="#a3161d", pin="#c8a03a", mustache="#5a4a3a", **SUIT),
    "EXECUTIVE": Char(body="#4a2f5e", hair="bun", hair_col="#3a2a20", glasses="rect", build=0.9, **SUIT),
    "PLAYER": Char(body="#c8312c", hair="spiky", hair_col="#1d1716", collar="round", pants="#f2f2f2"),
    "CHEF": Char(body="#f2f2f2", hair="bald", hair_col="#d8d2c8", mustache="#2a1c14", collar="round", pants="#2a2a2a"),
    "ENGINEER": Char(body="#3a3a42", hair="curly", hair_col="#1d1716", glasses="round", collar="round"),
    "ARM BOSS": Char(body="#1f2a44", hair="short", hair_col="#8a8a8a", glasses="rect", collar="shirt", lapels=True),
}


def lab(*items):
    return [(a, b, c, d) for a, b, c, d in items]


def skit(at, place, cast, **kw):
    d = {"at": at, "tpl": "skit", "place": place, "cast": cast}
    d.update(kw)
    return d


L2 = [("BOARD MEMBER", 430, 1.7, {}), ("LAWYER", 850, 1.7, {})]

BEATS = [
    # ---------------- CHAPTER 1: THE JACKET
    # hook (rebuilt to the reference's cold-open pattern: a real place with people, a time tag typing on,
    # hard cuts on every phrase, stamps that slam with a camera kick, a flashback, things that vanish and fall)
    {"at": 0, "tpl": "scene", "place": "tech_office", "tr": "cut", "amp": 0.6,
     "cast": [("EMPLOYEE ONE", lambda t, b: 140 + 290 * min(1.0, (t - b.t0) / 1.8), 1.8,
               {"walk_phase": lambda t, b: (t - b.t0) * 7 if t - b.t0 < 1.8 else None, "look": 0.3,
                "expr": "neutral"}),
              ("EMPLOYEE TWO", 930, 1.8, {"item": "phone", "arms": "chin", "look": -0.25,
                                          "expr": lambda t, b: "shock" if t > b.wt("most valuable") else "neutral"})],
     "ov": lambda c, t, b: (sets.name_tag(c, "THURSDAY MORNING", 60, 600, 400, 76, (t - b.t0 - 0.15) / 0.35),
                            sets.pop_label(c, "#1 CHIP COMPANY ON EARTH", 640, 110, t - b.wt("most valuable"),
                                           col="#f2d23a", size=54)),
     "sfx": lambda b: [(b.wt("most valuable"), story.audio.pop(), "pop", 0)]},
    {"at": 0, "word": "woke up", "tpl": "scene", "place": "tech_office", "tr": "cut", "amp": 0.5, "zoom": 1.12,
     "center": (640, 330), "push": 0.1,
     "cast": [("EMPLOYEE ONE", 250, 1.8, {"look": 0.45, "expr": "worried"}),
              ("EMPLOYEE TWO", 1030, 1.8, {"look": -0.45, "expr": "shock"})],
     "fg": lambda c, t, b: ceo_chair(c, 640, 590),
     "ov": lambda c, t, b: sets.pop_label(c, "THE FOUNDER'S CHAIR", 640, 110, t - b.wt("started"), col="#f2d23a",
                                          size=50),
     "sfx": lambda b: [(b.t0 + 0.05, story.audio.sting_low(), "sting", -8), (b.wt("started"), story.audio.pop(), "pop", 0)]},
    # flashback: 1993, a diner; he vanishes on "was gone"
    {"at": 1, "tpl": "scene", "place": "diner", "sepia": True, "tr": "dissolve", "amp": 0.6,
     "cast": [("JENSEN", 560, 1.9, {"item": "paper", "arms": "hold", "look": 0.15, "expr": "smirk"}),
              ("WAITER", 980, 1.7, {"look": -0.4, "expr": "neutral"})],
     "ov": lambda c, t, b: (sets.name_tag(c, "1993", 60, 600, 220, 76, (t - b.t0 - 0.2) / 0.35),
                            sets.pop_label(c, "33 YEARS AGO", 640, 110, t - b.wt("Thirty-three"), col="#f2d23a",
                                           size=56)),
     "sfx": lambda b: [(b.wt("Thirty-three"), story.audio.pop(), "pop", 0)]},
    {"at": 1, "word": "in a diner", "tpl": "scene", "place": "diner", "sepia": True, "tr": "cut", "amp": 0.3,
     "zoom": 1.0, "center": (560, 300), "push": 0.05,
     "cast": [("JENSEN", 560, 5.0, {"pose": "sit", "y": 1050, "item": "paper", "arms": "hold", "look": 0.2,
                                     "expr": "smirk", "show": lambda t, b: t < b.wt("gone")})],
     "fg": lambda c, t, b: (napkin(c, t, b), D.puff(c, 560, 420, t - b.wt("gone"), r=300)),
     "ov": lambda c, t, b: sets.name_tag(c, "JENSEN HUANG", 765, 532, 415, 108, (t - b.wt("Jensen Huang")) / 0.35),
     "sfx": lambda b: [(b.wt("Jensen Huang"), story.audio.pop(), "pop", -2), (b.wt("gone"), story.audio.whoosh(), "swish", 2),
                       (b.wt("gone") + 0.05, story.audio.sting_low(), "sting", -6)]},
    # not fired / not retired / resigned: three slams
    {"at": 2, "tpl": "slam", "who": "JENSEN", "place": "boardroom", "text": "FIRED", "cross": True, "cross_s": 0.42,
     "expr": "deadpan", "tr": "cut", "size": 130},
    {"at": 3, "tpl": "slam", "who": "JENSEN", "place": "porch_sunset", "side": "right", "text": "RETIRED",
     "col": "#c9a032", "cross": True, "cross_s": 0.5, "expr": "smirk", "tr": "cut", "size": 120},
    {"at": 4, "tpl": "scene", "place": "tech_office", "tr": "cut", "amp": 0.5, "shake": ["Resigned"],
     "cast": [("JENSEN", lambda t, b: 380 + 260 * min(1.0, (t - b.t0) / 2.2), 1.5,
               {"walk_phase": lambda t, b: (t - b.t0) * 6.5, "arms": "hold", "look": 0.35, "expr": "deadpan"})],
     "fg": lambda c, t, b: (D.office_door(c, 1060, 590, w=240, h=430, label="EXIT"),
                            D.cardboard_box(c, 380 + 260 * min(1.0, (t - b.t0) / 2.2) + 14, 495, 0.72)),
     "ov": lambda c, t, b: (D.stamp(c, 640, 100, t - b.wt("Resigned"), "RESIGNED", col="#2f9a3a", size=96),
                            sets.pop_label(c, "EFFECTIVE IMMEDIATELY", 640, 196, t - b.wt("immediately"),
                                           col="#f2d23a", size=46)),
     "sfx": lambda b: [(b.wt("Resigned"), story.audio.thud(), "thud", 3), (b.wt("immediately"), story.audio.pop(), "pop", 0)]},
    # every title, all at once: three name plates go up on his door, then all fall off together
    {"at": 5, "tpl": "scene", "place": "boardroom", "tr": "whip", "amp": 0.45, "center": (640, 330),
     "shake": ["all at once"],
     "cast": [("JENSEN", lambda t, b: 1010 + 40 * (t - b.t0), 1.5,
               {"pose": "back", "walk_phase": lambda t, b: (t - b.t0) * 5}),
              ],
     "fg": lambda c, t, b: plates_door(c, t, b),
     "sfx": lambda b: [(b.wt(w), story.audio.pop(), "pop", 0) for w in ("As president", "As chief", "As a member")]
     + [(b.wt("all at once") + 0.25 + i * 0.07, story.audio.thud(), "thud", -2) for i in range(3)]},
    {"at": 9, "tpl": "filing", "title": "FORM 8-K", "lines": ["Item 5.02", "Departure of Officers", "Effective immediately",
                                                              "", "Reason: ______"], "circle": (4, "never once")},
    skit(11, "boardroom", L2),
    {"at": 15, "tpl": "scene", "place": "trading_floor", "amp": 0.5,
     "cast": [("TRADER", 400, 1.8, {"expr": "shock", "arms": lambda t, b: "cheer" if int(t * 3) % 2 else "shrug"}),
              ("ANALYST", 880, 1.8, {"expr": "worried", "item": "phone", "arms": "chin", "look": -0.3})],
     "ov": lambda c, t, b: (sets.pop_label(c, "2 TRADING DAYS", 640, 110, t - b.wt("two trading"), col="#f2d23a",
                                           size=56),
                            sets.pop_label(c, "AFTER HIS FIRST CONFESSION", 640, 190, t - b.wt("confession"),
                                           col="#ff5a4a", size=40)),
     "sfx": lambda b: [(b.wt("two trading"), story.audio.pop(), "pop", 0), (b.wt("confession"), story.audio.pop(), "pop", -2)]},
    {"at": 15, "word": "his company lost", "tpl": "tower", "value": 428e9, "sub": "TWO TRADING DAYS", "build": 1.2,
     "react": False, "tr": "cut"},
    {"at": 15, "word": "than the entire", "tpl": "label", "place": "trading_floor", "react": False, "tr": "cut",
     "fg": lambda c, t, b: D.balance_scale(c, 640, 210, t - b.t0, scale_cash, scale_globe, tilt=-0.22, s=1.0),
     "labels": lab(("NVIDIA'S LOSS", "than the entire", 330, 610), ("MOST COUNTRIES' YEARLY ECONOMY", "economy", 920, 610)),
     "size": 40},
    {"at": 16, "tpl": "board", "lines": ("1. A DINNER", "2. A MEMO", "3. A SECOND SECRET")},
    {"at": 17, "tpl": "tag", "who": "ALICE", "place": "night_city", "side": "right", "expr": "smirk",
     "name": "THE ALLEGED SPY", "accent": "#d8342a", "flash_at": 0.35, "react": False},
    {"at": 17, "word": "brought down", "tpl": "void", "who": "JENSEN", "drop": "brought down", "tr": "cut"},
    {"at": 18, "tpl": "calendar", "from": "OCT", "month": "NOV", "label": "ONE WEEK"},
    # ---------------- CHAPTER 2: PREVIOUSLY
    {"at": 19, "tpl": "scene", "place": "living_room", "amp": 0.5,
     "cast": [("YOU", 520, 1.7, {"expr": "neutral", "arms": "hold", "item": "phone", "look": 0.3})],
     "fg": lambda c, t, b: stopwatch(c, 980, 300, t - b.wt("ninety")),
     "ov": lambda c, t, b: sets.pop_label(c, "90 SECONDS", 980, 500, t - b.wt("ninety"), col="#f2d23a", size=56),
     "sfx": lambda b: [(b.wt("ninety"), story.audio.bell(), "ding", -4)]},
    {"at": 20, "tpl": "stage", "chip": True, "cast": [("JENSEN", 470, 1.8, {"expr": "happy", "arms": "present_r", "look": 0.3})],
     "labels": lab(("AI", "every", 330, 200), ("AI", "big AI", 960, 220), ("AI", "planet", 640, 470))},
    {"at": 21, "tpl": "map", "center": (700, 300), "highlight": (1180, 260, 120),
     "routes": [(200, 330, 1100, 230, "doesn't")], "stamp": ("BLOCKED", "best ones", 850, 420)},
    {"at": 22, "tpl": "news", "papers": [("Firm Finds Way Around Chip Limits", "Singapore company buys servers", "")]},
    {"at": 22, "word": "found a way", "tpl": "map", "center": (760, 420), "tr": "cut", "react": False,
     "pins": [(760, 470, "SINGAPORE", "found")], "routes": [(760, 470, 1100, 230, "around")]},
    {"at": 23, "tpl": "scene", "place": "server_corridor", "place_kw": {"photo": False}, "amp": 0.5,
     "cast": [("CLERK", 360, 1.8, {"expr": "smirk", "arms": "present_r", "look": 0.3})],
     "fg": lambda c, t, b: D.cash_tower(c, 880, 660, t - b.wt("billions"), n_max=12, build=1.2),
     "ov": lambda c, t, b: D.counter_box(c, 880, 150, t - b.wt("billions"), 3e9, fmt="${:,.0f}+", sub="OF NVIDIA SERVERS", w=360),
     "sfx": lambda b: [(b.wt("billions") + i * 0.1, story.audio.tick(), "tick", -4) for i in range(12)]},
    {"at": 23, "word": "kept them", "tpl": "map", "center": (760, 420), "tr": "cut", "react": False,
     "pins": [(760, 470, "SINGAPORE", "kept"), (1100, 230, "CHINA", "outside")]},
    {"at": 23, "word": "rented", "tpl": "map", "center": (900, 340), "tr": "cut", "react": False,
     "pins": [(760, 470, "SINGAPORE", "rented"), (1100, 230, "CHINA", "Chinese")],
     "routes": [(760, 470, 1100, 230, "rented")], "stamp": ("RENTED", "internet", 930, 430)},
    {"at": 24, "tpl": "scene", "place": "driveway", "amp": 0.6, "shake": ["won't sell"],
     "cast": [("CUSTOMER", 300, 1.5, {"expr": "sad", "look": 0.5}),
              ("CLERK", 560, 1.5, {"expr": "deadpan", "look": -0.3, "arms": "hips"})],
     "fg": lambda c, t, b: (P2.car(c, 920, 640, 1.1),
                            D.stamp(c, 920, 480, t - b.wt("won't sell"), "NOT FOR SALE", size=40)),
     "sfx": lambda b: [(b.wt("won't sell"), story.audio.thud(), "thud", 0)]},
    {"at": 25, "tpl": "scene", "place": "driveway", "amp": 0.6, "tr": "cut",
     "cast": [("CUSTOMER", 300, 1.5, {"expr": lambda t, b: "happy" if t > b.wt("keys") else "neutral", "look": 0.5}),
              ("FRIEND", lambda t, b: 1400 - 840 * min(1.0, (t - b.t0) / 1.2), 1.5,
               {"walk_phase": lambda t, b: (t - b.t0) * 7 if t - b.t0 < 1.2 else None, "expr": "smirk", "look": -0.3,
                "arms": lambda t, b: "raise_r" if t > b.wt("hands") else "rest", "item": "key"})],
     "fg": lambda c, t, b: P2.car(c, 1500 - 580 * min(1.0, max(0.0, (t - b.wt("parks")) / 0.6)), 640, 1.1),
     "ov": lambda c, t, b: (sets.pop_label(c, "FRIEND BUYS IT", 560, 120, t - b.wt("buys"), col="#f2d23a", size=46),
                            sets.pop_label(c, "EVERY MORNING", 560, 200, t - b.wt("every morning"), col="#f2d23a", size=40)),
     "sfx": lambda b: [(b.wt("buys"), story.audio.pop(), "pop", 0), (b.wt("parks") + 0.5, story.audio.thud(), "thud", -4),
                       (b.wt("hands"), story.audio.sparkle(), "ding", -3)]},
    skit(26, "server_corridor", [("CUSTOMER", 450, 1.8, {"look": 0.4}), ("CLERK", 830, 1.8, {"look": -0.4})],
         place_kw={"photo": False}),
    {"at": 32, "tpl": "tag", "who": "ALICE", "name": "ALICE HUANG", "sub": "MEGASPEED", "side": "right",
     "place": "night_office", "expr": "smirk", "label": "NO RELATION", "label_at": "No relation", "accent": "#c8312c"},
    {"at": 34, "tpl": "cork", "photos": [("ALICE", "ALICE HUANG", 640, 300)], "circle": (0, "concluded"),
     "label": ("WORKING FOR CHINA?", "working")},
    {"at": 35, "tpl": "tv", "who": "SPOKESPERSON", "quote": "Baseless and purely slanderous smears against China.",
     "source": "BEIJING"},
    {"at": 36, "tpl": "scene", "place": "stage", "place_kw": {"jacket": False, "mark": False, "chip": True}, "amp": 0.6,
     "cast": [("JENSEN", 470, 1.8, {"expr": "happy", "arms": "present_r", "look": 0.3}),
              ("ALICE", lambda t, b: 1450 - 650 * min(1.0, max(0.0, (t - b.t0 - 0.4) / 1.6)), 1.6,
               {"walk_phase": lambda t, b: (t - b.t0) * 6.5 if b.t0 + 0.4 < t < b.t0 + 2.0 else None, "expr": "smirk",
                "look": -0.3})],
     "ov": lambda c, t, b: sets.pop_label(c, "2 YEARS", 640, 110, t - b.wt("two years"), col="#f2d23a", size=56),
     "sfx": lambda b: [(b.wt("two years"), story.audio.pop(), "pop", 0)]},
    {"at": 37, "tpl": "dinner", "toast": "Drinks"},
    {"at": 39, "tpl": "cork", "photos": [("JENSEN", "DINNERS", 330, 290), ("ALICE", "DRINKS", 640, 270),
                                          ("JENSEN", "EVENTS", 950, 300)], "strings": [(0, 1, "Industry"), (1, 2, "Industry")]},
    skit(40, "night_city", [("REPORTER", 470, 2.0, {"look": 0.4}), ("SOURCE", 820, 2.0, {"look": -0.4, "pose": "stand"})],
         floor=690),
    {"at": 44, "tpl": "news", "papers": [("CEO Had 'Close Relationship' With Executive", "late October", "")]},
    {"at": 45, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "sub": "NVIDIA", "place": "tech_office",
     "expr": "neutral", "label": "NO SECRETS SHARED", "label_at": "touched"},
    {"at": 46, "tpl": "slam", "who": "SPOKESPERSON", "place": "tech_office", "side": "right", "text": "SAME ANSWER",
     "col": "#2a4fa0", "size": 72, "expr": "deadpan", "at_s": "same"},
    {"at": 47, "tpl": "zero", "label": "CHARGES"},
    {"at": 48, "tpl": "scene", "place": "night_office", "amp": 0.5,
     "cast": [("JENSEN", 640, 1.9, {"expr": lambda t, b: "happy" if t > b.wt("stop there") else "worried", "arms": "chin"})],
     "fg": lambda c, t, b: clock(c, 1100, 170, t, speed=40),
     "ov": lambda c, t, b: sets.pop_label(c, "STORY OVER?", 640, 110, t - b.wt("stop there"), col="#f2d23a", size=56),
     "sfx": lambda b: [(b.wt("stop there"), story.audio.pop(), "pop", 0)]},
    {"at": 49, "tpl": "card"},
    # ---------------- CHAPTER 3: THE LETTER
    {"at": 50, "tpl": "calendar", "month": "NOV", "day": 5},
    {"at": 51, "tpl": "letter", "labels": lab(("CAPITOL HILL", "Capitol", 640, 120))},
    {"at": 52, "tpl": "scene", "place": "night_office", "amp": 0.5, "tr": "whip",
     "cast": [("CHAIRMAN", 300, 1.7, {"look": 0.2, "expr": "angry", "arms": "hips"}),
              ("CONGRESSMAN ONE", 640, 1.7, {"expr": "deadpan"}),
              ("CONGRESSMAN TWO", 980, 1.7, {"look": -0.2, "expr": "angry"})],
     "ov": lambda c, t, b: (sets.pop_label(c, "FOREIGN AFFAIRS", 300, 150, t - b.wt("Foreign"), col="#f2d23a", size=38),
                            sets.pop_label(c, "INTELLIGENCE", 640, 110, t - b.wt("Intelligence"), col="#f2d23a", size=38),
                            sets.pop_label(c, "CHINA", 980, 150, t - b.wt("China committees"), col="#f2d23a", size=38),
                            sets.pop_label(c, "3 SIGNATURES", 640, 650, t - b.wt("three"), col="#ff5a4a", size=44)),
     "sfx": lambda b: [(b.wt(w), story.audio.pop(), "pop", 0) for w in ("three", "Foreign", "Intelligence", "China committees")]},
    {"at": 53, "tpl": "scene", "place": "night_office", "amp": 0.5, "tr": "cut",
     "cast": [("JENSEN", lambda t, b: 250 + 300 * min(1.0, (t - b.t0) / 2.5), 1.7,
               {"walk_phase": lambda t, b: (t - b.t0) * 6.5 if t - b.t0 < 2.5 else None, "look": 0.4, "expr": "worried"})],
     "bg": lambda c, t, b: D.office_door(c, 900, 560, w=260, h=470, label="CLOSED DOOR"),
     "ov": lambda c, t, b: sets.pop_label(c, "LOCKED ROOM", 900, 60, t - b.wt("locked"), col="#f2d23a", size=46),
     "sfx": lambda b: [(b.wt("locked"), story.audio.pop(), "pop", 0)]},
    {"at": 53, "word": "eighteenth", "tpl": "calendar", "month": "NOV", "day": 18, "label": "BRIEFING", "tr": "cut", "react": False},
    {"at": 53, "word": "about his contact", "tpl": "cork", "tr": "cut", "react": False,
     "photos": [("JENSEN", "JENSEN", 420, 290), ("ALICE", "ALICE HUANG", 860, 290)], "strings": [(0, 1, "contact")]},
    {"at": 54, "tpl": "scene", "place": "server_corridor", "place_kw": {"photo": False}, "amp": 0.5, "shake": ["rules"],
     "cast": [("CLERK", 380, 1.8, {"expr": "deadpan", "arms": "hips", "look": 0.4}),
              ("ALICE", lambda t, b: 1400 - 560 * min(1.0, (t - b.t0) / 1.6), 1.6,
               {"walk_phase": lambda t, b: (t - b.t0) * 6.5 if t - b.t0 < 1.6 else None, "expr": "smirk", "look": -0.4})],
     "ov": lambda c, t, b: (D.stamp(c, 640, 150, t - b.wt("rules"), "RULES?", size=90),
                            sets.pop_label(c, "KEEPING SPIES OUT", 640, 650, t - b.wt("spies"), col="#f2d23a", size=46)),
     "sfx": lambda b: [(b.wt("rules"), story.audio.thud(), "thud", 0), (b.wt("spies"), story.audio.pop(), "pop", 0)]},
    skit(55, "night_office", [("AIDE", 420, 1.7, {"look": 0.4}), ("CHAIRMAN", 840, 1.7, {"look": -0.4})],
         props=lambda c, t, b: D.stamp(c, 960, 190, t - b.wt("won't be a request"), "SUBPOENA", size=54),
         sfx=lambda b: [(b.wt("won't be a request"), story.audio.thud(), "thud", 0)]),
    {"at": 62, "tpl": "tv", "who": "SPOKESPERSON",
     "quote": "Our chief executive has an outstanding security team that accompanies him where needed.",
     "source": "NVIDIA STATEMENT", "stamp": ("TRUE", "perfectly true")},
    {"at": 65, "tpl": "card"},
    {"at": 66, "tpl": "scene", "place": "night_office", "amp": 0.5,
     "cast": [("REPORTER", 330, 1.7, {"look": 0.4, "expr": "neutral", "arms": "hold", "item": "phone"}),
              ("CHAIRMAN", 880, 1.7, {"look": -0.4, "expr": "deadpan"})],
     "ov": lambda c, t, b: (sets.name_tag(c, "BRIAN MAST", 760, 600, 360, 76, (t - b.wt("Brian Mast")) / 0.35, accent="#c8312c"),
                            sets.pop_label(c, "SUBPOENA?", 330, 130, t - b.wt("subpoena"), col="#f2d23a", size=46)),
     "sfx": lambda b: [(b.wt("Brian Mast"), story.audio.pop(), "pop", -2), (b.wt("subpoena"), story.audio.pop(), "pop", 0)]},
    {"at": 67, "tpl": "slam", "who": "CHAIRMAN", "place": "night_office", "side": "left", "text": "ABSOLUTELY", "size": 86,
     "expr": "angry", "at_s": 0.08},
    {"at": 68, "tpl": "calendar", "month": "NOV", "day": 8, "label": "SUNDAY"},
    {"at": 69, "tpl": "email", "subject": "To everyone at the company", "body": ["I have something to tell you.", "..."]},
    {"at": 70, "tpl": "scene", "place": "tech_office", "amp": 0.5, "tr": "cut",
     "cast": [("EMPLOYEE ONE", 400, 1.8, {"item": "phone", "arms": "chin", "look": 0.3, "expr": "shock"}),
              ("EMPLOYEE TWO", 880, 1.8, {"item": "phone", "arms": "chin", "look": -0.3, "expr": "worried"})],
     "ov": lambda c, t, b: (D.counter_box(c, 640, 120, t - b.wt("Tens"), 10000, fmt="{:,.0f}+", sub="INBOXES", w=330),
                            sets.pop_label(c, "THE SAME EMAIL", 640, 650, t - b.wt("same email"), col="#f2d23a", size=50)),
     "sfx": lambda b: [(b.wt("Tens"), story.audio.bell(), "ding", -2), (b.wt("same email"), story.audio.pop(), "pop", 0)]},
    skit(71, "tech_office", [("EMPLOYEE ONE", 470, 1.8, {"look": 0.4, "expr": "worried"}),
                             ("EMPLOYEE TWO", 820, 1.8, {"look": -0.4, "expr": "shock"})]),
    {"at": 75, "tpl": "slam", "who": "JENSEN", "place": "night_office", "text": "AFFAIR", "size": 120, "expr": "sad",
     "at_s": "affair"},
    {"at": 76, "tpl": "slam", "who": "ALICE", "place": "night_city", "side": "right", "text": "UNNAMED", "col": "#c9a032",
     "size": 90, "expr": "neutral", "at_s": "name"},
    {"at": 77, "tpl": "map", "center": (640, 360), "react": False,
     "pins": [(300, 250, None, "quoted"), (560, 200, None, "around"), (900, 300, None, "the world"),
              (1050, 180, None, "within"), (420, 480, None, "hours"), (760, 450, None, "hours")],
     "stamp": ("WITHIN HOURS", "hours", 640, 600)},
    {"at": 78, "tpl": "card"},
    {"at": 79, "tpl": "scene", "place": "boardroom", "amp": 0.5,
     "cast": [("BOARD MEMBER ONE", 300, 1.6, {"look": 0.3, "expr": "worried"}),
              ("BOARD MEMBER TWO", 640, 1.6, {"expr": "deadpan"}),
              ("BOARD MEMBER THREE", 980, 1.6, {"look": -0.3, "expr": "angry"})],
     "ov": lambda c, t, b: sets.pop_label(c, "ALMOST NEVER DONE TO A FOUNDER", 640, 110, t - b.wt("almost never"),
                                          col="#f2d23a", size=42),
     "sfx": lambda b: [(b.wt("almost never"), story.audio.pop(), "pop", 0)]},
    {"at": 80, "tpl": "slam", "who": "JENSEN", "place": "boardroom", "text": "INVESTIGATION", "size": 78, "expr": "worried",
     "at_s": "investigation"},
    {"at": 81, "tpl": "scene", "place": "boardroom", "amp": 0.5,
     "cast": [("BOARD MEMBER ONE", 260, 1.6, {"look": 0.3, "expr": "deadpan"}),
              ("BOARD MEMBER THREE", 520, 1.6, {"look": 0.1, "expr": "deadpan"}),
              ("LAWYER", lambda t, b: 1450 - 540 * min(1.0, max(0.0, (t - b.wt("outside law")) / 1.4)), 1.6,
               {"walk_phase": lambda t, b: (t - b.wt("outside law")) * 6.5 if 0 <= t - b.wt("outside law") < 1.4 else None,
                "show": lambda t, b: t >= b.wt("outside law"), "expr": "deadpan", "look": -0.3, "arms": "hold",
                "item": "paper"})],
     "ov": lambda c, t, b: (sets.pop_label(c, "INDEPENDENT DIRECTORS", 400, 110, t - b.wt("independent"), col="#f2d23a", size=40),
                            sets.pop_label(c, "WACHTELL, LIPTON, ROSEN & KATZ", 640, 650, t - b.wt("Wachtell"),
                                           col="#f2d23a", size=40),
                            sets.pop_label(c, "FOR PROBLEMS AT THE VERY TOP", 900, 110, t - b.wt("very top"),
                                           col="#ff5a4a", size=38)),
     "sfx": lambda b: [(b.wt(w), story.audio.pop(), "pop", 0) for w in ("independent", "Wachtell", "very top")]},
    {"at": 82, "tpl": "filing", "title": "BOARD STATEMENT", "lines": ["No reason to believe", "national security or",
                                                                      "company secrets were", "compromised."],
     "stamp": ("WILL LOOK ANYWAY", "look anyway")},
    {"at": 84, "tpl": "scene", "place": "stage", "place_kw": {"jacket": False, "mark": False, "chip": False}, "amp": 0.6,
     "cast": [("JENSEN", 640, 1.8, {"expr": "sad", "arms": "shrug"})],
     "ov": lambda c, t, b: (sets.pop_label(c, "\"MY MISTAKE\"", 640, 110, t - b.wt("admit"), col="#f2d23a", size=50),
                            D.stamp(c, 920, 300, t - b.wt("survive"), "SURVIVES", col="#2f9a3a", size=70)),
     "sfx": lambda b: [(b.wt("admit"), story.audio.pop(), "pop", 0), (b.wt("survive"), story.audio.thud(), "thud", -2)]},
    {"at": 85, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": False}, "amp": 0.5,
     "cast": [("TRADER", 330, 1.8, {"expr": "happy", "arms": "present_r", "look": 0.3})],
     "fg": lambda c, t, b: D.cash_tower(c, 860, 680, t - b.wt("chips keep"), n_max=10, build=1.2),
     "ov": lambda c, t, b: (sets.pop_label(c, "INVESTORS FORGIVE ANYTHING", 640, 110, t - b.wt("forgive"), col="#f2d23a", size=46),
                            sets.pop_label(c, "AS LONG AS CHIPS SELL", 860, 650, t - b.wt("chips keep"), col="#3dff7a", size=38)),
     "sfx": lambda b: [(b.wt("forgive"), story.audio.pop(), "pop", 0)]
     + [(b.wt("chips keep") + i * 0.12, story.audio.tick(), "tick", -4) for i in range(10)]},
    {"at": 86, "tpl": "scene", "place": "trading_floor", "amp": 0.5,
     "cast": [("TRADER", 450, 1.8, {"expr": "worried", "look": 0.3}), ("ANALYST", 830, 1.8, {"expr": "worried", "look": -0.3})],
     "ov": lambda c, t, b: (sets.name_tag(c, "MONDAY MORNING", 60, 600, 400, 76, (t - b.t0 - 0.15) / 0.35),
                            sets.pop_label(c, "?", 640, 300, t - b.wt("one question"), col="#f2d23a", size=200)),
     "sfx": lambda b: [(b.wt("one question"), story.audio.pop(), "pop", 2)]},
    {"at": 87, "tpl": "card"},
    # ---------------- CHAPTER 4: THE BILL
    {"at": 88, "tpl": "calendar", "month": "NOV", "day": 9, "label": "MONDAY"},
    {"at": 89, "tpl": "scene", "place": "trading_floor", "amp": 0.5, "shake": ["bell"],
     "cast": [("TRADER", 400, 1.8, {"expr": "shock", "look": 0.3}), ("ANALYST", 880, 1.8, {"expr": "worried", "look": -0.3})],
     "fg": lambda c, t, b: bell(c, 640, 120, t - b.wt("bell")),
     "ov": lambda c, t, b: sets.pop_label(c, "9:30", 640, 330, t - b.t0 - 0.1, col="#f2d23a", size=80),
     "sfx": lambda b: [(b.wt("bell"), story.audio.bell(), "ding", 2)]},
    {"at": 91, "tpl": "stock", "values": [100, 99.5, 98, 97.5, 96.5, 96, 95.7], "price": "-4.3%"},
    {"at": 93, "tpl": "tower", "value": 200e9, "sub": "IN A SINGLE DAY", "build": 1.3,
     "label": ("CLOSE TO $200 BILLION", "two hundred")},
    skit(94, "trading_floor", [("TRADER", 450, 1.8, {"look": 0.4, "expr": "shock"}), ("ANALYST", 830, 1.8, {"look": -0.4, "expr": "deadpan"})]),
    {"at": 102, "tpl": "tower", "place": "night_office", "value": 6.47e9, "sub": "HIS OWN SHARES", "collapse": "lost",
     "label": ("811 MILLION SHARES", "eight hundred")},
    {"at": 104, "tpl": "label", "place": "trading_floor", "react": False,
     "fg": lambda c, t, b: (stopwatch(c, 400, 340, t - b.wt("second"), r=110),
                            D.counter_box(c, 880, 340, t - b.wt("two hundred"), 275000, sub="EVERY SECOND", dur=0.8, w=360)),
     "labels": lab(("MARKET HOURS ONLY", "hours", 640, 110)), "size": 44},
    {"at": 105, "tpl": "board", "lines": ("CITI: $285", "WELLS FARGO: $315 > $300"), "char": ("ANALYST ONE", "deadpan")},
    {"at": 108, "tpl": "board", "lines": ("BAIRD: $500 > $200",), "stamp": ("NOT A BUY", "stopped"),
     "char": ("ANALYST ONE", "deadpan")},
    skit(109, "trading_floor", [("ANALYST ONE", 450, 1.8, {"look": 0.4, "expr": "deadpan"}),
                                ("ANALYST TWO", 830, 1.8, {"look": -0.4, "expr": "worried"})], place_kw={"red": True}),
    {"at": 117, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "sub": "FOUNDER", "place": "night_office",
     "expr": "neutral", "label": "FAMOUS BOSS", "label_at": "famous"},
    {"at": 118, "tpl": "stage", "chip": True, "cast": [("JENSEN", 640, 1.8, {"expr": "happy", "arms": "present_r"})],
     "labels": lab(("THE BETS", "bets", 300, 160), ("THE STAGE", "stage", 980, 160), ("THE LAUNCH", "launch", 640, 100))},
    {"at": 122, "tpl": "tower", "value": 428e9, "sub": "TWO SESSIONS", "build": 1.4},
    {"at": 123, "tpl": "scene", "place": "living_room", "amp": 0.5, "shake": ["gone"],
     "cast": [("YOU", 520, 1.7, {"expr": lambda t, b: "shock" if t > b.wt("twelve hundred") else "neutral", "arms": "hold",
                                 "item": "phone", "look": 0.3})],
     "fg": lambda c, t, b: story.falling_bills(c, t, b.t0) if t > b.wt("gone") else None,
     "ov": lambda c, t, b: (D.counter_box(c, 980, 300, t - b.wt("twelve hundred"), 1200, fmt="-${:,.0f}", sub="PER AMERICAN", w=330),
                            sets.pop_label(c, "SUNDAY EMAIL TO TUESDAY CLOSE", 640, 650, t - b.wt("Sunday"), col="#f2d23a", size=40)),
     "sfx": lambda b: [(b.wt("twelve hundred"), story.audio.pop(), "pop", 0), (b.wt("gone"), story.audio.thud(), "thud", -2)]},
    {"at": 125, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": False, "ticker": "AMD"}, "amp": 0.5,
     "cast": [("TRADER ONE", 450, 1.8, {"expr": "happy", "arms": "cheer"}), ("TRADER TWO", 830, 1.8, {"expr": "smirk", "arms": "present_l"})],
     "ov": lambda c, t, b: sets.pop_label(c, "GREAT WEEK", 640, 110, t - b.wt("great"), col="#3dff7a", size=60),
     "sfx": lambda b: [(b.wt("great"), story.audio.sparkle(), "ding", 0)]},
    {"at": 126, "tpl": "stock", "ticker": "AMD", "values": [100, 101, 103, 104, 108, 110, 113], "price": "+13%"},
    {"at": 127, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": False, "ticker": "BROADCOM"}, "amp": 0.5, "tr": "cut",
     "cast": [("TRADER ONE", 450, 1.8, {"expr": "happy", "arms": "cheer"}), ("TRADER TWO", 830, 1.8, {"expr": "happy", "arms": "cheer"})],
     "fg": lambda c, t, b: story.falling_bills(c, t, b.t0),
     "ov": lambda c, t, b: sets.pop_label(c, "BROADCOM: BEST DAY IN A YEAR", 640, 110, t - b.wt("best day"), col="#3dff7a", size=46),
     "sfx": lambda b: [(b.wt("best day"), story.audio.sparkle(), "ding", 0)]},
    skit(128, "trading_floor", [("INVESTOR", 450, 1.8, {"look": 0.4, "expr": "angry"}),
                                ("BROKER", 830, 1.8, {"look": -0.4, "expr": "deadpan"})], place_kw={"red": False}),
    {"at": 133, "tpl": "dinner", "empty": ("L",), "right": "INVESTOR",
     "ov": lambda c, t, b: sets.pop_label(c, "ONE SEAT DOWN", 640, 120, t - b.wt("seat"), col="#f2d23a", size=56)},
    # ---------------- CHAPTER 5: THE SECOND SECRET
    {"at": 135, "tpl": "calendar", "month": "NOV", "day": 11, "label": "WEDNESDAY"},
    {"at": 136, "tpl": "card"},
    {"at": 137, "tpl": "news", "papers": [("CEO Had Relationship With Senior Executive", "inside the company", "")]},
    {"at": 137, "word": "senior executive", "tpl": "scene", "place": "tech_office", "amp": 0.5, "tr": "cut",
     "cast": [("JENSEN", 450, 1.8, {"expr": "neutral", "look": 0.3}), ("EXECUTIVE", 830, 1.8, {"expr": "neutral", "look": -0.3})],
     "ov": lambda c, t, b: (sets.pop_label(c, "INSIDE NVIDIA", 640, 110, t - b.wt("inside"), col="#f2d23a", size=50),
                            D.arrow_down(c, 640, 190, t - b.wt("under him"), length=120),
                            sets.pop_label(c, "WORKED UNDER HIM", 830, 650, t - b.wt("under him"), col="#ff5a4a", size=42)),
     "sfx": lambda b: [(b.wt("inside"), story.audio.pop(), "pop", 0), (b.wt("under him"), story.audio.pop(), "pop", 0)]},
    {"at": 138, "tpl": "news", "papers": [("Another Relationship Reported", "a different employee", "")]},
    {"at": 139, "tpl": "slam", "who": "SPOKESPERSON", "place": "tech_office", "side": "right", "text": "NO COMMENT", "size": 80,
     "expr": "deadpan", "at_s": "declined"},
    {"at": 140, "tpl": "news", "place": "boardroom",
     "papers": [("Report #1", "", "three reported"), ("Report #2", "", "separate"), ("Report #3", "", "three weeks")]},
    {"at": 141, "tpl": "scene", "place": "boardroom", "amp": 0.5,
     "cast": [("BOARD MEMBER ONE", 640, 1.6, {"expr": "worried", "arms": "chin"})],
     "fg": lambda c, t, b: desk_papers(c, t, b),
     "ov": lambda c, t, b: sets.pop_label(c, "THE BOARD'S DESK", 640, 110, t - b.wt("board's"), col="#f2d23a", size=50),
     "sfx": lambda b: [(b.wt("landed") + i * 0.25, story.audio.thud(), "thud", -4) for i in range(3)]},
    {"at": 142, "tpl": "board", "lines": ("OUTSIDE COMPANY = PRIVATE", "WORKS FOR YOU = GOVERNANCE"),
     "char": ("BOARD MEMBER ONE", "deadpan")},
    {"at": 145, "tpl": "filing", "title": "CODE OF CONDUCT", "lines": ["Conflicts of interest", "may include:", "",
                                                                       "personal relationships"],
     "highlight": (3, "personal")},
    {"at": 146, "tpl": "scene", "place": "sports_field", "amp": 0.6,
     "cast": [("REFEREE", 520, 1.8, {"expr": "smirk", "look": 0.3}), ("PLAYER", 800, 1.8, {"expr": "happy", "look": -0.3})],
     "fg": lambda c, t, b: heart(c, 660, 290, t - b.wt("dating")),
     "ov": lambda c, t, b: sets.pop_label(c, "REFEREE + PLAYER", 640, 110, t - b.wt("dating"), col="#f2d23a", size=50),
     "sfx": lambda b: [(b.wt("dating"), story.audio.sparkle(), "ding", -2)]},
    skit(148, "sports_field", [("FAN", 430, 1.8, {"look": 0.4, "expr": "angry"}), ("REFEREE", 820, 1.8, {"look": -0.4, "expr": "smirk"})]),
    {"at": 151, "tpl": "letter", "labels": lab(("REMEMBER THIS?", "remember", 640, 140))},
    {"at": 152, "tpl": "calendar", "month": "NOV", "day": 11, "label": "REPLY DEADLINE"},
    {"at": 153, "tpl": "scene", "place": "boardroom", "amp": 0.5,
     "cast": [("BOARD MEMBER ONE", 260, 1.6, {"look": 0.3, "expr": "worried"}),
              ("BOARD MEMBER TWO", 480, 1.6, {"look": 0.15, "expr": "deadpan"}),
              ("BOARD MEMBER THREE", 1020, 1.6, {"look": -0.3, "expr": "angry"})],
     "fg": lambda c, t, b: ceo_chair(c, 760, 660, 0.75),
     "ov": lambda c, t, b: (sets.name_tag(c, "WEDNESDAY EVENING", 60, 600, 420, 76, (t - b.t0 - 0.15) / 0.35),
                            sets.pop_label(c, "THE FOUNDER'S SEAT", 760, 110, t - b.wt("founder"), col="#f2d23a", size=46)),
     "sfx": lambda b: [(b.wt("founder"), story.audio.pop(), "pop", 0)]},
    {"at": 154, "tpl": "scene", "place": "boardroom", "amp": 0.5, "tr": "cut", "zoom": 1.12,
     "cast": [("BOARD MEMBER ONE", 260, 1.6, {"look": 0.3, "expr": "sad", "arms": "chin"}),
              ("BOARD MEMBER TWO", 480, 1.6, {"look": 0.15, "expr": "worried"}),
              ("BOARD MEMBER THREE", 1020, 1.6, {"look": -0.3, "expr": "deadpan", "arms": "hips"})],
     "fg": lambda c, t, b: (ceo_chair(c, 760, 660, 0.75), clock(c, 1000, 150, t, speed=60)),
     "ov": lambda c, t, b: sets.pop_label(c, "11:48 PM", 1000, 260, t - b.wt("night"), col="#f2d23a", size=44),
     "sfx": lambda b: [(b.wt("night"), story.audio.pop(), "pop", -2)]},
    skit(155, "boardroom", [("BOARD MEMBER ONE", 300, 1.6, {"look": 0.3, "expr": "sad"}),
                            ("BOARD MEMBER TWO", 640, 1.6, {"expr": "worried"}),
                            ("BOARD MEMBER THREE", 980, 1.6, {"look": -0.3, "expr": "angry"})]),
    {"at": 164, "tpl": "filing", "title": "FORM 8-K", "lines": ["Date of event:", "November 11, 2026"],
     "highlight": (1, "Wednesday")},
    {"at": 165, "tpl": "card"},
    # ---------------- CHAPTER 6: THURSDAY
    {"at": 166, "tpl": "calendar", "month": "NOV", "day": 12, "label": "THURSDAY"},
    {"at": 167, "tpl": "filing", "title": "FORM 8-K", "lines": ["Securities and Exchange", "Commission", "",
                                                                "Jensen Huang has resigned,", "effective immediately."],
     "cps": 30},
    {"at": 169, "tpl": "scene", "place": "trading_floor", "amp": 0.5,
     "cast": [("TRADER ONE", 400, 1.8, {"expr": "neutral", "arms": "hold", "item": "paper", "look": 0.3}),
              ("TRADER TWO", 880, 1.8, {"expr": "shock", "look": -0.3})],
     "ov": lambda c, t, b: (sets.pop_label(c, "SOMETHING BIG", 640, 110, t - b.wt("something big"), col="#f2d23a", size=56),
                            sets.pop_label(c, "RIGHT AWAY", 640, 200, t - b.wt("right away"), col="#ff5a4a", size=46)),
     "sfx": lambda b: [(b.wt("something big"), story.audio.pop(), "pop", 0), (b.wt("right away"), story.audio.pop(), "pop", 0)]},
    {"at": 170, "tpl": "filing", "title": "FORM 8-K", "lines": ["Securities and Exchange", "Commission", "",
                                                                "Jensen Huang has resigned,", "effective immediately."],
     "cps": 400, "highlight": (3, "This one"), "stamp": ("RESIGNED", "resigned"), "tr": "cut"},
    {"at": 171, "tpl": "tag", "who": "KRESS", "name": "COLETTE KRESS", "sub": "INTERIM CEO", "place": "tech_office",
     "expr": "neutral", "label": "THE NEW BOSS", "label_at": "new boss", "accent": "#2a4fa0"},
    {"at": 172, "tpl": "stage", "chip": False, "cast": [("KRESS", 520, 1.8, {"expr": "neutral", "arms": "present_r", "look": 0.2})],
     "labels": lab(("CFO FOR 10+ YEARS", "decade", 300, 160), ("THE NUMBERS", "numbers", 980, 160),
                   ("EVERY 3 MONTHS", "three months", 640, 100))},
    {"at": 173, "tpl": "scene", "place": "tech_office", "amp": 0.5,
     "cast": [("KRESS", 640, 1.8, {"expr": "neutral", "arms": "hips"})],
     "fg": lambda c, t, b: (D.nameplate(c, 430, 470, "CFO", t - b.wt("keeps"), w=200),
                            D.nameplate(c, 850, 470, "INTERIM CEO", t - b.wt("Interim"), w=290)),
     "ov": lambda c, t, b: sets.pop_label(c, "TWO JOBS, ONE DESK", 640, 110, t - b.wt("Two jobs"), col="#f2d23a", size=54),
     "sfx": lambda b: [(b.wt("keeps"), story.audio.pop(), "pop", 0), (b.wt("Interim"), story.audio.pop(), "pop", 0),
                       (b.wt("Two jobs"), story.audio.pop(), "pop", 0)]},
    skit(176, "tech_office", [("REPORTER", 450, 1.8, {"look": 0.4}), ("SPOKESPERSON", 830, 1.8, {"look": -0.4, "expr": "deadpan"})]),
    {"at": 184, "tpl": "tv", "who": "HARVEY", "quote": "Full confidence in Colette and the leadership team.",
     "source": "HARVEY JONES, BOARD CHAIR"},
    {"at": 185, "tpl": "scene", "place": "trading_floor", "amp": 0.5, "shake": ["bell"],
     "cast": [("TRADER ONE", 400, 1.8, {"expr": "shock", "look": 0.3}), ("TRADER TWO", 880, 1.8, {"expr": "deadpan", "look": -0.3})],
     "fg": lambda c, t, b: bell(c, 640, 120, t - b.wt("bell")),
     "ov": lambda c, t, b: sets.pop_label(c, "9:30", 640, 330, t - b.t0 - 0.1, col="#f2d23a", size=80),
     "sfx": lambda b: [(b.wt("bell"), story.audio.bell(), "ding", 2)]},
    {"at": 187, "tpl": "stock", "values": [180, 176, 170, 162, 156, 150, 149], "price": "$148.80",
     "labels": lab(("LOW OF THE DAY: $148.80", "low for", 640, 650))},
    {"at": 189, "tpl": "scene", "place": "trading_floor", "amp": 0.5,
     "cast": [("TRADER TWO", 400, 1.8, {"expr": "deadpan", "look": 0.3, "arms": "present_r"})],
     "ov": lambda c, t, b: (D.counter_box(c, 900, 300, t - b.wt("sixth of October"), 239, fmt="${:,.0f}", sub="OCT 6 CLOSE", w=330),
                            sets.pop_label(c, "FIVE WEEKS EARLIER", 640, 110, t - b.wt("five weeks"), col="#f2d23a", size=50)),
     "sfx": lambda b: [(b.wt("sixth of October"), story.audio.pop(), "pop", 0), (b.wt("five weeks"), story.audio.pop(), "pop", 0)]},
    skit(190, "trading_floor", [("TRADER ONE", 450, 1.8, {"look": 0.4, "expr": "worried"}),
                                ("TRADER TWO", 830, 1.8, {"look": -0.4, "expr": "smirk"})]),
    {"at": 199, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": False},
     "cast": [("TRADER ONE", 450, 1.8, {"expr": "happy", "arms": "cheer"}), ("TRADER TWO", 830, 1.8, {"expr": "smirk"})],
     "ov": lambda c, t, b: sets.pop_label(c, "BUY", 640, 130, t - b.wt("buying"), col="#3dff7a", size=80),
     "sfx": lambda b: [(b.wt("buying"), story.audio.sparkle(), "ding", 0)]},
    {"at": 201, "tpl": "stock", "values": [149, 152, 156, 160, 163, 165, 166.2], "price": "$166.19", "change": "-4.34%",
     "labels": lab(("CLOSE: $166.19", "nineteen", 640, 650))},
    {"at": 202, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": False}, "amp": 0.5,
     "cast": [("TRADER ONE", 330, 1.8, {"expr": "shock", "look": 0.3, "item": "phone", "arms": "chin"}),
              ("TRADER TWO", 950, 1.8, {"expr": "happy", "look": -0.3, "arms": "cheer"})],
     "fg": lambda c, t, b: story.falling_bills(c, t, b.t0),
     "ov": lambda c, t, b: (D.counter_box(c, 640, 300, t - b.wt("seven hundred"), 700e6, fmt="{:,.0f}+", sub="SHARES CHANGED HANDS", w=400),
                            sets.pop_label(c, "FAR MORE THAN A NORMAL DAY", 640, 650, t - b.wt("far more"), col="#3dff7a", size=40)),
     "sfx": lambda b: [(b.wt("seven hundred"), story.audio.pop(), "pop", 0), (b.wt("far more"), story.audio.pop(), "pop", 0)]},
    {"at": 203, "tpl": "slam", "who": "TRADER TWO", "place": "trading_floor", "text": "PAID", "col": "#2f9a3a", "size": 110,
     "expr": "smirk", "at_s": "paid"},
    {"at": 205, "tpl": "tv", "who": "PRESIDENT", "quote": "A horrible thing. So sad to see happen.", "source": "THE PRESIDENT",
     "pose": "back"},
    {"at": 207, "tpl": "cork", "photos": [("JENSEN", "JENSEN", 420, 290), ("ALICE", "ALICE", 860, 290)],
     "strings": [(0, 1, "ties")], "label": ("FBI: LOOKING INTO IT", "FBI")},
    {"at": 208, "tpl": "zero", "label": "CHARGES"},
    {"at": 209, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "place": "night_office", "expr": "worried",
     "label": "DENIES IT", "label_at": "denied"},
    {"at": 210, "tpl": "scene", "place": "night_office", "amp": 0.5,
     "cast": [("LAWYER", 640, 1.8, {"expr": "deadpan", "arms": "hold", "item": "paper"})],
     "fg": lambda c, t, b: clock(c, 1100, 170, t, speed=80),
     "ov": lambda c, t, b: sets.pop_label(c, "TAKES TIME", 640, 110, t - b.wt("time"), col="#f2d23a", size=50),
     "sfx": lambda b: [(b.wt("time"), story.audio.pop(), "pop", 0)]},
    {"at": 211, "tpl": "board", "lines": ("SPYING?  ...?", "CAN HE STILL RUN IT?"), "strikes": [(0, "much simpler")],
     "stamp": ("NO", "answer was no")},
    # ---------------- CHAPTER 7: WHO RUNS NVIDIA NOW?
    {"at": 215, "tpl": "scene", "place": "boardroom", "amp": 0.5,
     "fg": lambda c, t, b: ceo_chair(c, 640, 660, 0.9),
     "ov": lambda c, t, b: sets.pop_label(c, "?", 640, 240, t - b.wt("who"), col="#f2d23a", size=200),
     "sfx": lambda b: [(b.wt("who"), story.audio.pop(), "pop", 0)]},
    {"at": 216, "tpl": "cork", "photos": [(None, "IAN BUCK?", 420, 290), (None, "RENE HAAS?", 860, 290)],
     "label": ("TWO NAMES", "two names")},
    {"at": 217, "tpl": "board", "lines": ("IAN BUCK: ENGINEER", "GAMING CHIPS TO AI CHIPS"), "char": ("ENGINEER", "happy")},
    {"at": 218, "tpl": "scene", "place": "tech_office", "amp": 0.5,
     "cast": [("ARM BOSS", 520, 1.8, {"expr": "neutral", "arms": "hold", "item": "phone", "look": 0.2})],
     "ov": lambda c, t, b: (sets.name_tag(c, "RENE HAAS", 765, 600, 400, 76, (t - b.wt("Rene")) / 0.35, accent="#2a4fa0"),
                            sets.pop_label(c, "RUNS ARM", 640, 110, t - b.wt("runs Arm"), col="#f2d23a", size=50),
                            sets.pop_label(c, "IN ALMOST EVERY PHONE", 640, 190, t - b.wt("every phone"), col="#f2d23a", size=40)),
     "sfx": lambda b: [(b.wt("Rene"), story.audio.pop(), "pop", -2), (b.wt("runs Arm"), story.audio.pop(), "pop", 0),
                       (b.wt("every phone"), story.audio.pop(), "pop", 0)]},
    {"at": 220, "tpl": "scene", "place": "boardroom", "amp": 0.5,
     "cast": [("BOARD MEMBER", 640, 1.6, {"expr": "neutral",
                                          "look": lambda t, b: -0.5 if t > b.wt("outside") else (0.5 if t > b.wt("inside") else 0.0)})],
     "ov": lambda c, t, b: (sets.pop_label(c, "INSIDE", 330, 300, t - b.wt("inside"), col="#f2d23a", size=60),
                            sets.pop_label(c, "OUTSIDE", 950, 300, t - b.wt("outside"), col="#f2d23a", size=60)),
     "sfx": lambda b: [(b.wt("inside"), story.audio.pop(), "pop", 0), (b.wt("outside"), story.audio.pop(), "pop", 0)]},
    skit(221, "boardroom", [("HEADHUNTER", 450, 1.8, {"look": 0.4, "expr": "deadpan"}),
                            ("BOARD MEMBER", 830, 1.8, {"look": -0.4})]),
    {"at": 229, "tpl": "stage", "chip": True, "cast": [("JENSEN", 640, 1.8, {"expr": "happy", "arms": "present_r"})],
     "labels": lab(("SALESMAN", "salesman", 300, 160), ("KEYNOTE", "keynote", 980, 160), ("FACE", "face", 640, 100))},
    {"at": 232, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "place": "night_office", "expr": "happy",
     "label": "PART OF THE DEAL", "label_at": "buying"},
    {"at": 233, "tpl": "scene", "place": "diner", "amp": 0.5,
     "cast": [("DINER", 300, 1.6, {"expr": "neutral", "look": 0.5}),
              ("CHEF", 640, 1.6, {"expr": "happy", "arms": "wave", "look": -0.3, "show": lambda t, b: t < b.wt("kitchen")}),
              ("WAITER", 960, 1.6, {"expr": "happy", "arms": "present_l", "look": -0.2})],
     "bg": lambda c, t, b: D.office_door(c, 640, 580, w=200, h=380, label="KITCHEN"),
     "fg": lambda c, t, b: D.puff(c, 640, 430, t - b.wt("kitchen"), r=200),
     "ov": lambda c, t, b: (sets.pop_label(c, "THE CHEF GREETS EVERY TABLE", 640, 110, t - b.wt("greets"), col="#f2d23a", size=42),
                            sets.pop_label(c, "KITCHEN STILL COOKING", 640, 650, t - b.wt("keep cooking"), col="#3dff7a", size=40)),
     "sfx": lambda b: [(b.wt("greets"), story.audio.pop(), "pop", 0), (b.wt("kitchen"), story.audio.whoosh(), "swish", 0),
                       (b.wt("keep cooking"), story.audio.pop(), "pop", 0)]},
    skit(236, "diner", [("DINER", 450, 1.6, {"look": 0.4, "expr": "angry"}), ("WAITER", 830, 1.6, {"look": -0.4, "expr": "happy"})]),
    {"at": 239, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": True}, "amp": 0.5,
     "cast": [("TRADER", 640, 1.8, {"expr": "worried"})],
     "ov": lambda c, t, b: sets.pop_label(c, "NOT JUST WALL STREET", 640, 110, t - b.wt("Wall Street"), col="#f2d23a", size=50),
     "sfx": lambda b: [(b.wt("Wall Street"), story.audio.pop(), "pop", 0)]},
    {"at": 240, "tpl": "scene", "place": "living_room", "amp": 0.5, "tr": "whip",
     "cast": [("YOU", 820, 1.7, {"expr": "neutral", "arms": "hold", "item": "phone", "look": -0.3}),
              ("TRADER", lambda t, b: -150 + 560 * min(1.0, (t - b.t0) / 1.6), 1.7,
               {"walk_phase": lambda t, b: (t - b.t0) * 6.5 if t - b.t0 < 1.6 else None, "expr": "deadpan", "look": 0.3,
                "arms": "hold", "item": "paper"})],
     "ov": lambda c, t, b: sets.pop_label(c, "YOUR RETIREMENT ACCOUNT", 640, 110, t - b.wt("retirement"), col="#f2d23a", size=50),
     "sfx": lambda b: [(b.wt("retirement"), story.audio.pop(), "pop", 0)]},
    {"at": 241, "tpl": "label", "place": "living_room", "react": False, "pie": (8, "biggest", "NVIDIA"),
     "labels": lab(("S&P 500", "five hundred", 640, 110)), "size": 56},
    {"at": 242, "tpl": "scene", "place": "living_room", "amp": 0.5,
     "cast": [("YOU", 400, 1.7, {"expr": lambda t, b: "worried" if t > b.wt("noticeable") else "neutral", "arms": "hold",
                                 "item": "phone", "look": 0.4})],
     "fg": lambda c, t, b: D.pie_plate(c, 960, 330, t - b.wt("fund"), 8, label="NVIDIA", r=120),
     "ov": lambda c, t, b: sets.pop_label(c, "A NOTICEABLE PIECE", 960, 580, t - b.wt("noticeable"), col="#ff5a4a", size=40),
     "sfx": lambda b: [(b.wt("fund"), story.audio.pop(), "pop", 0), (b.wt("noticeable"), story.audio.pop(), "pop", 0)]},
    skit(243, "living_room", [("YOU", 640, 1.8, {"expr": "shock", "arms": "hold", "item": "phone"})], center=(640, 400)),
    {"at": 245, "tpl": "slam", "who": "YOU", "place": "living_room", "text": "NOT EXACTLY", "col": "#c9a032", "size": 72,
     "expr": "deadpan", "at_s": 0.1},
    {"at": 247, "tpl": "scene", "place": "boardroom", "amp": 0.5,
     "fg": lambda c, t, b: ceo_chair(c, 640, 660, 0.9),
     "ov": lambda c, t, b: sets.pop_label(c, "EMPTY CORNER OFFICE", 640, 640, t - b.wt("empty"), col="#f2d23a", size=50),
     "sfx": lambda b: [(b.wt("empty"), story.audio.pop(), "pop", 0)]},
    {"at": 248, "tpl": "calendar", "month": "NOV", "label": "TWO DATES CIRCLED"},
    {"at": 249, "tpl": "calendar", "month": "NOV", "day": 17, "label": "EARNINGS", "tr": "cut"},
    {"at": 250, "tpl": "card"},
    {"at": 251, "tpl": "letter", "labels": lab(("BRIEFING: NEXT WEEK", "next week", 640, 140))},
    # ---------------- CHAPTER 8: THE JACKET
    {"at": 254, "tpl": "scene", "place": "stage", "place_kw": {"jacket": False, "mark": True, "chip": False}, "amp": 0.6,
     "cast": [("JENSEN", 640, 1.8, {"expr": "happy", "arms": "present_r"})],
     "ov": lambda c, t, b: (sets.name_tag(c, "33 YEARS", 60, 600, 260, 76, (t - b.t0 - 0.15) / 0.35),
                            sets.pop_label(c, "THE JACKET", 640, 110, t - b.wt("jacket"), col="#f2d23a", size=56),
                            sets.pop_label(c, "MOST RECOGNISABLE OUTFIT IN TECH", 640, 650, t - b.wt("recognisable"),
                                           col="#f2d23a", size=38)),
     "sfx": lambda b: [(b.wt("jacket"), story.audio.pop(), "pop", 0), (b.wt("recognisable"), story.audio.pop(), "pop", 0)]},
    {"at": 255, "tpl": "scene", "place": "stage", "place_kw": {"jacket": False, "mark": True, "chip": True}, "amp": 0.6, "tr": "whip",
     "cast": [("JENSEN", 640, 1.8, {"expr": "happy", "arms": lambda t, b: "cheer" if t > b.wt("new chip") else "present_r"})],
     "ov": lambda c, t, b: (sets.pop_label(c, "EVERY STAGE", 300, 160, t - b.wt("every stage"), col="#f2d23a", size=46),
                            sets.pop_label(c, "EVERY LAUNCH", 980, 160, t - b.wt("every launch"), col="#f2d23a", size=46),
                            sets.pop_label(c, "EVERY NEW CHIP", 640, 100, t - b.wt("new chip"), col="#f2d23a", size=46)),
     "sfx": lambda b: [(b.wt(w), story.audio.pop(), "pop", 0) for w in ("every stage", "every launch", "new chip")]},
    {"at": 256, "tpl": "scene", "place": "stage", "place_kw": {"jacket": False, "mark": True, "chip": False}, "amp": 0.6, "tr": "cut",
     "cast": [("JENSEN", 640, 1.8, {"expr": "neutral", "show": lambda t, b: t < b.wt("someone else")}),
              ("STAGEHAND", 640, 1.8, {"expr": "worried", "show": lambda t, b: t >= b.wt("someone else") + 0.3})],
     "fg": lambda c, t, b: D.puff(c, 640, 400, t - b.wt("someone else"), r=220),
     "ov": lambda c, t, b: sets.pop_label(c, "SOMEONE ELSE", 640, 110, t - b.wt("someone else"), col="#f2d23a", size=56),
     "sfx": lambda b: [(b.wt("someone else"), story.audio.whoosh(), "swish", 0), (b.wt("someone else") + 0.3, story.audio.pop(), "pop", 0)]},
    {"at": 257, "tpl": "scene", "place": "stage", "place_kw": {"jacket": False, "mark": True, "chip": False}, "amp": 0.6, "tr": "cut",
     "fg": lambda c, t, b: (P2.leather_jacket(c, 640, 520) if t < b.wt("no jacket") else None,
                            D.puff(c, 640, 380, t - b.wt("no jacket"), r=180)),
     "ov": lambda c, t, b: (sets.pop_label(c, "A DIFFERENT JACKET?", 640, 110, t - b.wt("different"), col="#f2d23a", size=50),
                            sets.pop_label(c, "NO JACKET AT ALL?", 640, 190, t - b.wt("no jacket"), col="#ff5a4a", size=50)),
     "sfx": lambda b: [(b.wt("different"), story.audio.pop(), "pop", 0), (b.wt("no jacket"), story.audio.whoosh(), "swish", 0)]},
    skit(259, "stage", [("STAGEHAND", 430, 1.6, {"look": 0.4, "expr": "worried"}),
                        ("STAGE MANAGER", 850, 1.6, {"look": -0.4, "expr": "neutral"})],
         place_kw={"jacket": False, "mark": True, "chip": False}),
    {"at": 263, "tpl": "checklist", "title": "STILL WORKING", "bgcol": "#1d2c52",
     "rows": [("CHIPS", "tick", "chips didn't"), ("FACTORIES", "tick", "factories"), ("CUSTOMERS", "tick", "customers"),
              ("THE BUILDING", "tick", "Nothing in")]},
    {"at": 268, "tpl": "filing", "title": "BOARD STATEMENT", "lines": ["No reason to believe", "a single secret",
                                                                       "walked out the door."], "stamp": ("THE MAN DID", "What walked")},
    {"at": 270, "tpl": "dinner", "empty": ("R",), "lexpr": "sad"},
    {"at": 271, "tpl": "dinner", "empty": ("L", "R")},
    {"at": 272, "tpl": "email", "subject": "A personal note", "body": ["", "There is no excuse", "for what I did."]},
    {"at": 273, "tpl": "card"},
]


def ceo_chair(c, x, y, s=1.0):
    """empty office chair with his leather jacket over the back (y = floor)"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.translate(-x, -y)
    _ceo_chair(c, x, y)
    c.restore()


def _ceo_chair(c, x, y):
    sets._rrect(c, x - 120, y - 380, 240, 250, 40)
    sets._fill_line(c, sets.hexc("#1a1a1e"), 5)
    P2.leather_jacket(c, x, y - 30, 1.0)
    c.rectangle(x - 135, y - 165, 270, 44)
    sets._fill_line(c, sets.hexc("#1a1a1e"), 5)
    c.rectangle(x - 9, y - 121, 18, 90)
    sets._fill_line(c, sets.hexc("#4a4a50"), 3)
    for dx in (-110, -55, 55, 110):
        c.move_to(x, y - 31)
        c.line_to(x + dx, y - 6)
        c.set_source_rgb(*sets.INK)
        c.set_line_width(9)
        c.stroke()
        c.arc(x + dx, y - 4, 9, 0, 6.3)
        c.fill()


def napkin(c, t, b):
    """the napkin with the first chip sketch: in his hands, then it floats down to the counter after he vanishes"""
    k = t - b.wt("gone")
    if k < 0:
        return
    y = 330 + min(1.0, k / 0.9) ** 2 * 260
    c.save()
    c.translate(560 + 40 * math.sin(k * 5) * max(0, 1 - k / 0.9), y)
    c.rotate(0.3 * math.sin(k * 6) * max(0, 1 - k / 0.9) - 0.08)
    c.rectangle(-110, -80, 220, 160)
    sets._fill_line(c, sets.hexc("#fbf7ea"), 4)
    c.rectangle(-45, -40, 90, 80)
    c.set_source_rgb(*sets.hexc("#2a4fa0"))
    c.set_line_width(4)
    c.stroke()
    for i in range(5):
        for side in (-1, 1):
            c.move_to(side * 45, -32 + i * 16)
            c.line_to(side * 62, -32 + i * 16)
            c.move_to(-32 + i * 16, side * 40)
            c.line_to(-32 + i * 16, side * 56)
    c.stroke()
    c.restore()


def plates_door(c, t, b):
    D.office_door(c, 640, 640, w=300, h=560, label="J. HUANG")
    fall = t - b.wt("all at once") - 0.15
    for i, (txt, w) in enumerate((("PRESIDENT", "As president"), ("CHIEF EXECUTIVE", "As chief"),
                                  ("BOARD MEMBER", "As a member"))):
        D.nameplate(c, 640, 330 + i * 78, txt, t - b.wt(w), fall - i * 0.06 if fall > 0 else -1, seed=i)


def scale_cash(c, x, y):
    for i in range(6):
        c.rectangle(x - 55, y - 22 - i * 22, 110, 20)
        sets._fill_line(c, sets.hexc("#6fbf5a"), 3)


def scale_globe(c, x, y):
    for i, dx in enumerate((-30, 30)):
        c.arc(x + dx, y - 34, 30, 0, 6.3)
        sets._fill_line(c, sets.hexc("#3d7fd0"), 3)
        c.arc(x + dx - 8, y - 40, 11, 0, 6.3)
        c.set_source_rgb(*sets.hexc("#5aa04a"))
        c.fill()


def stopwatch(c, x, y, k, r=70):
    """stopwatch that pops in and runs (k s since it was said); the hand sweeps once every 2 s"""
    p = D._pop(k)
    if p <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(p, p)
    c.rectangle(-14, -r - 26, 28, 20)
    sets._fill_line(c, sets.hexc("#c9a032"), 3)
    c.arc(0, 0, r, 0, 2 * math.pi)
    sets._fill_line(c, sets.hexc("#f2efe6"), 5)
    for i in range(12):
        a = i * math.pi / 6
        c.move_to(0.82 * r * math.cos(a), 0.82 * r * math.sin(a))
        c.line_to(0.92 * r * math.cos(a), 0.92 * r * math.sin(a))
    c.set_source_rgb(*sets.INK)
    c.set_line_width(3)
    c.stroke()
    a = -math.pi / 2 + k * math.pi
    c.move_to(0, 0)
    c.line_to(0.78 * r * math.cos(a), 0.78 * r * math.sin(a))
    c.set_source_rgb(*sets.hexc("#d0302a"))
    c.set_line_width(5)
    c.stroke()
    c.arc(0, 0, 6, 0, 2 * math.pi)
    c.fill()
    c.restore()


def bell(c, x, y, k):
    """brass bell hanging from the top; it swings for a second after it rings (k s since the ring)"""
    sw = 0.45 * math.sin(k * 22) * max(0.0, 1 - k / 1.2) if k > 0 else 0.0
    c.save()
    c.translate(x, y - 90)
    c.rotate(sw)
    c.move_to(0, 0)
    c.line_to(0, 40)
    c.set_source_rgb(*sets.INK)
    c.set_line_width(5)
    c.stroke()
    c.move_to(-42, 120)
    c.curve_to(-42, 60, -24, 40, 0, 40)
    c.curve_to(24, 40, 42, 60, 42, 120)
    c.close_path()
    sets._fill_line(c, sets.hexc("#c9a032"), 4)
    c.rectangle(-50, 118, 100, 12)
    sets._fill_line(c, sets.hexc("#c9a032"), 4)
    c.arc(0, 138, 9, 0, 2 * math.pi)
    sets._fill_line(c, sets.hexc("#5a3a22"), 3)
    c.restore()
    if 0 < k < 0.9:
        for sd in (-1, 1):
            for i in range(2):
                a = 0.35 + i * 0.25
                c.arc(x, y + 20, 70 + i * 22 + 30 * k, sd * a - 0.3 if sd > 0 else math.pi - a - 0.3,
                      sd * a + 0.3 if sd > 0 else math.pi - a + 0.3)
                c.set_source_rgba(1, 0.9, 0.5, 0.8 * (1 - k / 0.9))
                c.set_line_width(4)
                c.stroke()


def clock(c, x, y, t, speed=1.0, r=56):
    """wall clock whose hands race (time passing)"""
    c.arc(x, y, r, 0, 2 * math.pi)
    sets._fill_line(c, sets.hexc("#f2efe6"), 5)
    m = t * speed
    for ln, a_, w in ((0.55, (m / 60) * math.pi / 6 - math.pi / 2, 6), (0.8, m * math.pi / 30 - math.pi / 2, 4)):
        c.move_to(x, y)
        c.line_to(x + ln * r * math.cos(a_), y + ln * r * math.sin(a_))
        c.set_source_rgb(*sets.INK)
        c.set_line_width(w)
        c.stroke()
    c.arc(x, y, 5, 0, 2 * math.pi)
    c.fill()


def heart(c, x, y, k, col="#e23b2e"):
    p = D._pop(k)
    if p <= 0:
        return
    s_ = p * (1 + 0.06 * math.sin(k * 9))
    c.save()
    c.translate(x, y)
    c.scale(s_, s_)
    c.move_to(0, 30)
    c.curve_to(-60, -20, -30, -60, 0, -25)
    c.curve_to(30, -60, 60, -20, 0, 30)
    c.close_path()
    sets._fill_line(c, sets.hexc(col), 4)
    c.restore()


def desk_papers(c, t, b):
    """three reports slam onto the board table one after another"""
    for i, (x, ang) in enumerate(((400, -0.25), (640, 0.08), (880, 0.3))):
        k = t - b.wt("landed") - i * 0.25
        if k > 0:
            P2.newspaper(c, k, f"REPORT {i + 1}", "", x=x, y=540, angle=ang, s=0.36)

REACTORS = {
    1: [("BOARD MEMBER ONE", "boardroom"), ("LAWYER", "boardroom"), ("TRADER", "trading_floor")],
    2: [("JENSEN", "night_office"), ("ALICE", "night_city"), ("REPORTER", "night_city")],
    3: [("CHAIRMAN", "night_office"), ("EMPLOYEE ONE", "tech_office"), ("BOARD MEMBER TWO", "boardroom")],
    4: [("TRADER", "trading_floor"), ("ANALYST", "trading_floor"), ("INVESTOR", "trading_floor")],
    5: [("BOARD MEMBER ONE", "boardroom"), ("BOARD MEMBER THREE", "boardroom"), ("REPORTER", "tech_office")],
    6: [("KRESS", "tech_office"), ("TRADER ONE", "trading_floor"), ("REPORTER TWO", "tech_office")],
    7: [("HEADHUNTER", "boardroom"), ("YOU", "living_room"), ("BOARD MEMBER", "boardroom")],
    8: [("STAGEHAND", "stage"), ("STAGE MANAGER", "stage"), ("JENSEN", "night_office")],
}

# punchlines on black cards (reference: one about every 15-20 s)
BEATS += [{"at": i, "tpl": "card"} for i in (10, 83, 92, 116, 124, 147, 204, 214, 219, 235, 246, 253, 267, 269)]


def build():
    return story.Story(sys.modules[__name__], VOICE, OUT, TITLE)


if __name__ == "__main__":
    import numpy as np
    st = build()
    cmd = sys.argv[1]
    if cmd == "audio":
        st.render()
        st.srt(OUT / "final.srt")
    elif cmd == "part":
        st.render(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "concat":
        st.concat(int(sys.argv[2]), OUT / "how_a_chinese_spy_brought_down_nvidias_ceo.mp4")
    elif cmd == "still":
        import cv2
        for a in sys.argv[2:]:
            t = float(a)
            cv2.imwrite(str(OUT / f"still_{t:07.2f}.png"), (np.clip(st.frame(t), 0, 1) * 255).astype(np.uint8))
    elif cmd == "beats":
        for b in st.beats:
            print(round(b.t0, 2), round(b.dur, 2), b.p["tpl"], b.sents[0]["script_text"][:50] if b.sents else b.p.get("name", ""))
