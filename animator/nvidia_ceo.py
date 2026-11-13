"""How a Chinese Spy Brought Down Nvidia's CEO: shot plan for the user's voiceover.
Sentence indices come from output/nvidia/align.json (analysis/script_align.py). Characters are original
designs; real people appear only as simple cartoon figures identified by name tags.
Run:
  python3 animator/nvidia_ceo.py audio          # mix.wav
  python3 animator/nvidia_ceo.py part K N       # render part K of N (run N in parallel)
  python3 animator/nvidia_ceo.py concat N       # join parts + mix -> final mp4
  python3 animator/nvidia_ceo.py still T ...    # check frames
"""
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
    {"at": 0, "tpl": "stage", "jacket": True, "chip": False, "push": 0.12,
     "labels": lab(("33 YEARS", "Thirty-three", 640, 120))},
    {"at": 1, "tpl": "board", "place": "diner", "lines": ("1993", "A CHIP IDEA"), "cps": 6},
    {"at": 2, "tpl": "checklist", "title": "HOW HE LEFT", "rows": [("FIRED", "x", "Not fired"), ("RETIRED", "x", "Not retired"),
                                                               ("RESIGNED", "tick", "Resigned")],
     "stamp": ("EFFECTIVE NOW", "immediately")},
    {"at": 5, "tpl": "checklist", "title": "JENSEN HUANG", "bgcol": "#1d2c52",
     "rows": [("PRESIDENT", "x", "As president"), ("CHIEF EXECUTIVE", "x", "As chief executive"),
              ("BOARD MEMBER", "x", "As a member")], "stamp": ("ALL OF THEM", "Every title")},
    {"at": 9, "tpl": "filing", "title": "FORM 8-K", "lines": ["Item 5.02", "Departure of Officers", "Effective immediately",
                                                              "", "Reason: ______"], "circle": (4, "never once")},
    skit(11, "boardroom", L2),
    {"at": 15, "tpl": "tower", "value": 428e9, "sub": "TWO TRADING DAYS", "build": 1.6, "collapse": "economy",
     "label": ("BIGGER THAN MOST ECONOMIES", "economy")},
    {"at": 16, "tpl": "board", "lines": ("1. A DINNER", "2. A MEMO", "3. A SECOND SECRET")},
    {"at": 17, "tpl": "void", "who": "JENSEN", "drop": "brought down"},
    {"at": 18, "tpl": "calendar", "from": "OCT", "month": "NOV", "label": "ONE WEEK"},
    # ---------------- CHAPTER 2: PREVIOUSLY
    {"at": 19, "tpl": "label", "bgcol": "#1d2c52", "labels": lab(("90 SECONDS", "ninety", 640, 360))},
    {"at": 20, "tpl": "stage", "chip": True, "labels": lab(("AI", "every", 330, 200), ("AI", "big AI", 960, 220),
                                                           ("AI", "planet", 640, 470))},
    {"at": 21, "tpl": "map", "center": (700, 300), "highlight": (1180, 260, 120),
     "routes": [(200, 330, 1100, 230, "doesn't")], "stamp": ("BLOCKED", "best ones", 850, 420)},
    {"at": 22, "tpl": "news", "papers": [("Firm Finds Way Around Chip Limits", "Singapore company buys servers", "")]},
    {"at": 23, "tpl": "map", "center": (760, 420), "pins": [(760, 470, "SINGAPORE", "bought"), (1100, 230, "CHINA", "rented")],
     "routes": [(760, 470, 1100, 230, "rented")]},
    {"at": 24, "tpl": "scene", "place": "driveway",
     "cast": [("CUSTOMER", 300, 1.5, {"expr": "sad", "look": 0.5}), ("FRIEND", 560, 1.5, {"expr": "smirk", "look": -0.3,
              "arms": lambda t, b: "raise_r" if t > b.wt("keys") else "rest", "item": "key"})],
     "fg": lambda c, t, b: (P2.car(c, 920, 640, 1.1), D.stamp(c, 920, 480, t - b.wt("won't sell"), "NOT FOR SALE", size=40))},
    skit(26, "server_corridor", [("CUSTOMER", 450, 1.8, {"look": 0.4}), ("CLERK", 830, 1.8, {"look": -0.4})],
         place_kw={"photo": False}),
    {"at": 32, "tpl": "tag", "who": "ALICE", "name": "ALICE HUANG", "sub": "MEGASPEED", "side": "right",
     "place": "night_office", "expr": "smirk", "label": "NO RELATION", "label_at": "No relation", "accent": "#c8312c"},
    {"at": 34, "tpl": "cork", "photos": [("ALICE", "ALICE HUANG", 640, 300)], "circle": (0, "concluded"),
     "label": ("WORKING FOR CHINA?", "working")},
    {"at": 35, "tpl": "tv", "who": "SPOKESPERSON", "quote": "Baseless and purely slanderous smears against China.",
     "source": "BEIJING"},
    {"at": 36, "tpl": "dinner", "toast": "Drinks"},
    {"at": 39, "tpl": "cork", "photos": [("JENSEN", "DINNERS", 330, 290), ("ALICE", "DRINKS", 640, 270),
                                          ("JENSEN", "EVENTS", 950, 300)], "strings": [(0, 1, "Industry"), (1, 2, "Industry")]},
    skit(40, "night_city", [("REPORTER", 470, 2.0, {"look": 0.4}), ("SOURCE", 820, 2.0, {"look": -0.4, "pose": "stand"})],
         floor=690),
    {"at": 44, "tpl": "news", "papers": [("CEO Had 'Close Relationship' With Executive", "late October", "")]},
    {"at": 45, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "sub": "NVIDIA", "place": "tech_office",
     "expr": "neutral", "label": "NO SECRETS SHARED", "label_at": "touched"},
    {"at": 47, "tpl": "zero", "label": "CHARGES"},
    {"at": 48, "tpl": "calendar", "from": "OCT", "month": "NOV"},
    {"at": 49, "tpl": "card"},
    # ---------------- CHAPTER 3: THE LETTER
    {"at": 50, "tpl": "calendar", "month": "NOV", "day": 5},
    {"at": 51, "tpl": "letter", "labels": lab(("FOREIGN AFFAIRS", "Foreign", 300, 140), ("INTELLIGENCE", "Intelligence", 640, 110),
                                             ("CHINA", "China committees", 980, 140))},
    {"at": 53, "tpl": "filing", "title": "REQUEST", "lines": ["Closed-door briefing", "Date: November 18",
                                                              "Topic: contact with", "Alice Huang", "Also: security rules"],
     "highlight": (4, "also want")},
    skit(55, "night_office", [("AIDE", 420, 1.7, {"look": 0.4}), ("CHAIRMAN", 840, 1.7, {"look": -0.4})]),
    {"at": 62, "tpl": "tv", "who": "SPOKESPERSON",
     "quote": "Our chief executive has an outstanding security team that accompanies him where needed.",
     "source": "NVIDIA STATEMENT", "stamp": ("TRUE", "perfectly true")},
    {"at": 65, "tpl": "card"},
    {"at": 66, "tpl": "scene", "place": "gov_room" if False else "night_office",
     "cast": [("CHAIRMAN", 640, 1.9, {"expr": lambda t, b: "angry" if t > b.wt("Absolutely") else "neutral", "look": 0.0})],
     "ov": lambda c, t, b: sets.pop_label(c, "\"ABSOLUTELY.\"", 640, 130, t - b.wt("Absolutely"), col="#f2d23a", size=70),
     "sfx": lambda b: [(b.wt("Absolutely"), story.audio.thud(), "thud", 0)]},
    {"at": 68, "tpl": "calendar", "month": "NOV", "day": 8, "label": "SUNDAY"},
    {"at": 69, "tpl": "email", "subject": "To everyone at the company",
     "body": ["I have something to tell you.", "..."], "counter": (10000, "INBOXES", "Tens of thousands")},
    skit(71, "tech_office", [("EMPLOYEE ONE", 470, 1.8, {"look": 0.4, "expr": "worried"}),
                             ("EMPLOYEE TWO", 820, 1.8, {"look": -0.4, "expr": "shock"})]),
    {"at": 75, "tpl": "email", "subject": "A personal note",
     "body": ["I admit to an affair.", "", "There is no excuse", "for what I did."]},
    {"at": 78, "tpl": "card"},
    {"at": 79, "tpl": "scene", "place": "boardroom", "cast": [("BOARD MEMBER ONE", 300, 1.6, {"look": 0.3, "expr": "worried"}),
                                                              ("BOARD MEMBER TWO", 640, 1.6, {"expr": "deadpan"}),
                                                              ("BOARD MEMBER THREE", 980, 1.6, {"look": -0.3, "expr": "angry"})],
     "ov": lambda c, t, b: (D.stamp(c, 640, 120, t - b.wt("investigation"), "INVESTIGATION", size=54),
                            sets.pop_label(c, "WACHTELL, LIPTON, ROSEN & KATZ", 640, 640, t - b.wt("Wachtell"),
                                           col="#f2d23a", size=40)),
     "sfx": lambda b: [(b.wt("investigation"), story.audio.thud(), "thud", 0)]},
    {"at": 82, "tpl": "filing", "title": "BOARD STATEMENT", "lines": ["No reason to believe", "national security or",
                                                                      "company secrets were", "compromised."],
     "stamp": ("WILL LOOK ANYWAY", "look anyway")},
    {"at": 84, "tpl": "board", "lines": ("MISTAKE + CHIPS SELLING", "= FOUNDER SURVIVES"), "char": ("TRADER", "smirk")},
    {"at": 86, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": False},
     "cast": [("TRADER", 640, 1.8, {"expr": "worried", "look": 0.0})]},
    {"at": 87, "tpl": "card"},
    # ---------------- CHAPTER 4: THE BILL
    {"at": 88, "tpl": "calendar", "month": "NOV", "day": 9, "label": "MONDAY"},
    {"at": 89, "tpl": "scene", "place": "trading_floor", "cast": [("TRADER", 640, 1.8, {"expr": "shock"})],
     "ov": lambda c, t, b: sets.pop_label(c, "9:30", 640, 120, t - b.t0 - 0.1, col="#f2d23a", size=80),
     "sfx": lambda b: [(b.wt("bell") or b.t0, story.audio.bell(), "ding", 2)]},
    {"at": 91, "tpl": "stock", "values": [100, 99.5, 98, 97.5, 96.5, 96, 95.7], "price": "-4.3%",
     "labels": lab(("~$200 BILLION", "two hundred", 640, 640))},
    skit(94, "trading_floor", [("TRADER", 450, 1.8, {"look": 0.4, "expr": "shock"}), ("ANALYST", 830, 1.8, {"look": -0.4, "expr": "deadpan"})]),
    {"at": 102, "tpl": "tower", "value": 6.47e9, "sub": "HIS OWN SHARES", "collapse": "lost",
     "label": ("811 MILLION SHARES", "eight hundred")},
    {"at": 104, "tpl": "label", "bgcol": "#2a1610", "glow": "#ffcf80",
     "labels": lab(("$275,000", "two hundred", 640, 300), ("EVERY SECOND", "second", 640, 420))},
    {"at": 105, "tpl": "board", "lines": ("CITI: $285", "WELLS FARGO: $315 > $300"), "char": ("ANALYST ONE", "deadpan")},
    skit(109, "trading_floor", [("ANALYST ONE", 450, 1.8, {"look": 0.4, "expr": "deadpan"}),
                                ("ANALYST TWO", 830, 1.8, {"look": -0.4, "expr": "worried"})], place_kw={"red": True}),
    {"at": 118, "tpl": "stage", "chip": True, "cast": [("JENSEN", 640, 1.8, {"expr": "happy", "arms": "present_r"})],
     "labels": lab(("THE BETS", "bets", 300, 160), ("THE STAGE", "stage", 980, 160), ("THE LAUNCH", "launch", 640, 100))},
    {"at": 122, "tpl": "tower", "value": 428e9, "sub": "TWO SESSIONS", "build": 1.4, "collapse": "twelve hundred",
     "label": ("~$1,200 PER AMERICAN", "twelve hundred")},
    {"at": 124, "tpl": "stock", "ticker": "AMD", "values": [100, 101, 103, 104, 108, 110, 113], "price": "+13%",
     "labels": lab(("BROADCOM: BEST DAY IN A YEAR", "Broadcom", 640, 650))},
    skit(128, "trading_floor", [("INVESTOR", 450, 1.8, {"look": 0.4, "expr": "angry"}),
                                ("BROKER", 830, 1.8, {"look": -0.4, "expr": "deadpan"})], place_kw={"red": False}),
    {"at": 133, "tpl": "dinner", "empty": ("L",), "right": "INVESTOR",
     "ov": lambda c, t, b: sets.pop_label(c, "ONE SEAT DOWN", 640, 120, t - b.wt("seat"), col="#f2d23a", size=56)},
    # ---------------- CHAPTER 5: THE SECOND SECRET
    {"at": 135, "tpl": "calendar", "month": "NOV", "day": 11, "label": "WEDNESDAY"},
    {"at": 136, "tpl": "card"},
    {"at": 137, "tpl": "news", "papers": [("CEO Had Relationship With Senior Executive", "report", ""),
                                           ("Another Relationship Reported", "different employee", "Then Reuters")],
     "stamp": ("NO COMMENT", "declined")},
    {"at": 140, "tpl": "news", "place": "boardroom",
     "papers": [("Report #1", "", "three reported"), ("Report #2", "", "separate"), ("Report #3", "", "three weeks")]},
    {"at": 142, "tpl": "board", "lines": ("OUTSIDE COMPANY = PRIVATE", "WORKS FOR YOU = GOVERNANCE"),
     "char": ("BOARD MEMBER ONE", "deadpan")},
    {"at": 145, "tpl": "filing", "title": "CODE OF CONDUCT", "lines": ["Conflicts of interest", "may include:", "",
                                                                       "personal relationships"],
     "highlight": (3, "personal")},
    skit(146, "sports_field", [("FAN", 430, 1.8, {"look": 0.4, "expr": "angry"}), ("REFEREE", 820, 1.8, {"look": -0.4, "expr": "smirk"})]),
    {"at": 151, "tpl": "letter", "labels": lab(("DEADLINE: NOV 11", "deadline", 640, 140))},
    {"at": 153, "tpl": "scene", "place": "boardroom",
     "cast": [("BOARD MEMBER ONE", 300, 1.6, {"look": 0.3}), ("BOARD MEMBER TWO", 640, 1.6, {}),
              ("BOARD MEMBER THREE", 980, 1.6, {"look": -0.3})],
     "ov": lambda c, t, b: sets.pop_label(c, "11:48 PM", 1100, 100, t - b.wt("night"), col="#f2d23a", size=46)},
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
     "highlight": (3, "This one"), "stamp": ("RESIGNED", "resigned")},
    {"at": 171, "tpl": "tag", "who": "KRESS", "name": "COLETTE KRESS", "sub": "INTERIM CEO + CFO", "place": "tech_office",
     "expr": "neutral", "label": "TWO JOBS, ONE DESK", "label_at": "Two jobs", "accent": "#2a4fa0"},
    skit(176, "tech_office", [("REPORTER", 450, 1.8, {"look": 0.4}), ("SPOKESPERSON", 830, 1.8, {"look": -0.4, "expr": "deadpan"})]),
    {"at": 184, "tpl": "tv", "who": "HARVEY", "quote": "Full confidence in Colette and the leadership team.",
     "source": "HARVEY JONES, BOARD CHAIR"},
    {"at": 187, "tpl": "stock", "values": [180, 176, 170, 162, 156, 150, 149], "price": "$148.80",
     "labels": lab(("OCT 6: $239", "sixth of October", 640, 640))},
    skit(190, "trading_floor", [("TRADER ONE", 450, 1.8, {"look": 0.4, "expr": "worried"}),
                                ("TRADER TWO", 830, 1.8, {"look": -0.4, "expr": "smirk"})]),
    {"at": 201, "tpl": "stock", "values": [149, 152, 156, 160, 163, 165, 166.2], "price": "$166.19", "change": "-4.34%",
     "labels": lab(("700,000,000+ SHARES", "seven hundred", 640, 650))},
    {"at": 203, "tpl": "stage", "jacket": False, "chip": True, "labels": lab(("WITHOUT HIM", "without him", 640, 120))},
    {"at": 205, "tpl": "tv", "who": "PRESIDENT", "quote": "A horrible thing. So sad to see happen.", "source": "THE PRESIDENT",
     "pose": "back"},
    {"at": 207, "tpl": "cork", "photos": [("JENSEN", "JENSEN", 420, 290), ("ALICE", "ALICE", 860, 290)],
     "strings": [(0, 1, "ties")], "label": ("FBI: LOOKING INTO IT", "FBI")},
    {"at": 208, "tpl": "zero", "label": "CHARGES"},
    {"at": 211, "tpl": "board", "lines": ("SPYING?  ...?", "CAN HE STILL RUN IT?"), "strikes": [(0, "much simpler")],
     "stamp": ("NO", "answer was no")},
    # ---------------- CHAPTER 7: WHO RUNS NVIDIA NOW?
    {"at": 216, "tpl": "cork", "photos": [(None, "IAN BUCK?", 420, 290), (None, "RENE HAAS?", 860, 290)],
     "label": ("INSIDE OR OUTSIDE", "inside")},
    skit(221, "boardroom", [("HEADHUNTER", 450, 1.8, {"look": 0.4, "expr": "deadpan"}),
                            ("BOARD MEMBER", 830, 1.8, {"look": -0.4})]),
    {"at": 229, "tpl": "stage", "chip": True, "cast": [("JENSEN", 640, 1.8, {"expr": "happy", "arms": "present_r"})],
     "labels": lab(("SALESMAN", "salesman", 300, 160), ("KEYNOTE", "keynote", 980, 160), ("FACE", "face", 640, 100))},
    {"at": 233, "tpl": "scene", "place": "diner", "cast": [("WAITER", 640, 1.6, {"expr": "happy", "arms": "present_r"})],
     "ov": lambda c, t, b: sets.pop_label(c, "THE CHEF IS MISSING", 640, 120, t - b.wt("regulars"), col="#f2d23a", size=48)},
    skit(236, "diner", [("DINER", 450, 1.6, {"look": 0.4, "expr": "angry"}), ("WAITER", 830, 1.6, {"look": -0.4, "expr": "happy"})]),
    {"at": 239, "tpl": "label", "bgcol": "#2a3a24", "glow": "#d8ffb0", "pie": (8, "noticeable", "NVIDIA"),
     "labels": lab(("YOUR RETIREMENT FUND", "retirement", 640, 110))},
    skit(243, "living_room", [("YOU", 640, 1.8, {"expr": "shock", "arms": "hold", "item": "phone"})], center=(640, 400)),
    {"at": 245, "tpl": "scene", "place": "boardroom", "place_kw": {"lamp": True},
     "ov": lambda c, t, b: sets.pop_label(c, "EMPTY CORNER OFFICE", 640, 640, t - b.wt("empty"), col="#f2d23a", size=50)},
    {"at": 248, "tpl": "calendar", "month": "NOV", "day": 17, "label": "EARNINGS"},
    {"at": 251, "tpl": "letter", "labels": lab(("BRIEFING: NEXT WEEK", "next week", 640, 140), ("NO TITLE", "without a title", 640, 220))},
    # ---------------- CHAPTER 8: THE JACKET
    {"at": 254, "tpl": "stage", "jacket": True, "chip": False, "push": 0.14},
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

# ---------------- extra beats so no shot runs much longer than ~8 s (reference: a new shot every ~3 s)
BEATS += [
    {"at": 81, "tpl": "scene", "place": "boardroom",
     "cast": [("LAWYER", 450, 1.6, {"look": 0.3, "expr": "deadpan", "arms": "hold", "item": "paper"}),
              ("LAWYER", 830, 1.6, {"look": -0.3, "expr": "deadpan"})],
     "ov": lambda c, t, b: (sets.pop_label(c, "WACHTELL, LIPTON, ROSEN & KATZ", 640, 110, t - b.wt("Wachtell"),
                                           col="#f2d23a", size=46),
                            sets.pop_label(c, "THE FIRM FOR PROBLEMS AT THE TOP", 640, 650, t - b.wt("very top"),
                                           col="#f2d23a", size=40))},
    {"at": 108, "tpl": "board", "lines": ("BAIRD: $500 > $200",), "stamp": ("NOT A BUY", "stopped"),
     "char": ("ANALYST ONE", "deadpan")},
    {"at": 116, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "sub": "FOUNDER", "place": "night_office",
     "expr": "neutral", "label": "FAMOUS BOSS", "label_at": "famous"},
    {"at": 123, "tpl": "label", "bgcol": "#2a1610", "glow": "#ffcf80",
     "labels": lab(("~$1,200", "twelve hundred", 640, 300), ("FOR EVERY AMERICAN", "every person", 640, 420),
                   ("SUNDAY EMAIL > TUESDAY CLOSE", "Sunday", 640, 560)), "size": 64},
    {"at": 138, "tpl": "news", "papers": [("Another Relationship Reported", "different employee", "")],
     "stamp": ("NO COMMENT", "declined")},
    {"at": 173, "tpl": "label", "bgcol": "#1d2c52",
     "labels": lab(("INTERIM CEO", "Interim", 400, 300), ("+ CFO", "finance chief", 880, 300),
                   ("TWO JOBS, ONE DESK", "Two jobs", 640, 470))},
    {"at": 185, "tpl": "scene", "place": "trading_floor", "cast": [("TRADER ONE", 640, 1.8, {"expr": "shock"})],
     "ov": lambda c, t, b: sets.pop_label(c, "9:30", 640, 120, t - b.t0 - 0.1, col="#f2d23a", size=80),
     "sfx": lambda b: [(b.wt("bell"), story.audio.bell(), "ding", 2)]},
    {"at": 199, "tpl": "scene", "place": "trading_floor", "place_kw": {"red": False},
     "cast": [("TRADER ONE", 450, 1.8, {"expr": "happy", "arms": "cheer"}), ("TRADER TWO", 830, 1.8, {"expr": "smirk"})],
     "ov": lambda c, t, b: sets.pop_label(c, "BUY", 640, 130, t - b.wt("buying"), col="#3dff7a", size=80)},
    {"at": 209, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "place": "night_office", "expr": "worried",
     "label": "DENIES IT", "label_at": "denied"},
    {"at": 215, "tpl": "scene", "place": "boardroom",
     "ov": lambda c, t, b: sets.pop_label(c, "?", 640, 360, t - b.t0 - 0.3, col="#f2d23a", size=200)},
    {"at": 219, "tpl": "label", "bgcol": "#1d2c52",
     "labels": lab(("INSIDE", "inside", 400, 340), ("OUTSIDE", "outside", 880, 340), ("NO COMMENT", "Neither", 640, 520))},
    {"at": 232, "tpl": "tag", "who": "JENSEN", "name": "JENSEN HUANG", "place": "night_office", "expr": "happy",
     "label": "PART OF THE DEAL", "label_at": "buying"},
    {"at": 241, "tpl": "label", "bgcol": "#2a3a24", "glow": "#d8ffb0", "pie": (8, "biggest", "NVIDIA"),
     "labels": lab(("YOUR INDEX FUND", "fund", 640, 110))},
    {"at": 250, "tpl": "card"},
    {"at": 256, "tpl": "stage", "jacket": True, "mark": True, "chip": False, "push": 0.1},
]
BEATS[BEATS.index(next(b for b in BEATS if b["at"] == 239))] = {
    "at": 239, "tpl": "scene", "place": "living_room",
    "cast": [("YOU", 640, 1.7, {"expr": "worried", "arms": "hold", "item": "phone"})],
    "ov": lambda c, t, b: sets.pop_label(c, "YOUR RETIREMENT", 640, 110, t - b.wt("retirement"), col="#f2d23a", size=56)}


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
