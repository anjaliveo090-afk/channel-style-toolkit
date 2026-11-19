"""This Noob Is the Reason Roblox Has a Leave Button: shot plan for the user's voiceover (~57 s, one chapter).
Sentence indices come from output/toby/align.json (analysis/script_align.py). Toby and every player are original
characters; the game worlds and UI are generic blocky designs (no real game's logo, avatar or interface).
Run:
  python3 animator/toby_noob.py beats           # list beats
  python3 animator/toby_noob.py still T ...     # check frames
  python3 animator/toby_noob.py audio           # mix.wav
  python3 animator/toby_noob.py part K N        # render part K of N (run N in parallel)
  python3 animator/toby_noob.py concat N        # join parts + mix -> final mp4
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import devices as D  # noqa: E402
import places_game as PG  # noqa: E402
import sets  # noqa: E402
import story  # noqa: E402
import style  # noqa: E402
from style import Char  # noqa: E402

story.ALL_PLACES.update(PG.PLACES_GAME)

ROOT = Path(__file__).resolve().parent.parent
ALIGN = ROOT / "output/toby/align.json"
VOICE = ROOT / "output/toby/voice.mp3"
OUT = ROOT / "output/toby"
TITLE = "This Noob Is the Reason Roblox Has a Leave Button"

CHAPTER_MOOD = {1: ("major", 55)}


# ---------------------------------------------------------------- Toby: an original noob with a party hat
class Toby(Char):
    def draw(self, ctx, x, y, s=1.0, **kw):
        res = super().draw(ctx, x, y, s, **kw)
        hx, hy, R = res["head"]
        lw = 0.045 * R + 0.6
        ctx.save()
        ctx.translate(hx + 0.12 * R, hy - 0.78 * R)
        ctx.rotate(0.18)
        ctx.move_to(-0.48 * R, 0)
        ctx.line_to(0, -1.2 * R)
        ctx.line_to(0.48 * R, 0)
        ctx.close_path()
        sets._fill_line(ctx, style.hexc("#3b82d6"), lw)
        for i, f in enumerate((0.25, 0.55)):
            ctx.move_to(-0.48 * R * (1 - f), -1.2 * R * f)
            ctx.line_to(0.48 * R * (1 - f), -1.2 * R * f)
            ctx.set_source_rgb(*style.hexc("#f2c230"))
            ctx.set_line_width(0.12 * R)
            ctx.stroke()
        ctx.arc(0, -1.22 * R, 0.17 * R, 0, 2 * math.pi)
        sets._fill_line(ctx, style.hexc("#e5483c"), lw * 0.8)
        ctx.restore()
        return res


_draw_item = style.draw_item


def draw_item(ctx, item, x, y, R, t):
    if item == "megaphone":
        PG.megaphone(ctx, x, y, R)
    elif item == "pizza":
        PG.pizza(ctx, x, y - 0.35 * R, 0.75 * R)
    elif item == "balloons":
        PG.balloon_bunch(ctx, x, y, 99, n=5, t=t, spread=1.2 * R)
    else:
        _draw_item(ctx, item, x, y, R, t)


style.draw_item = draw_item

TOBY = Toby(body="#f28b2c", hair="bowl", hair_col="#6a3a1a", collar="round", pants="#2a5fa8", blush=True, zipper=True)
CAST = {
    "TOBY": TOBY,
    "PLAYER ONE": Char(body="#3b82d6", hair="spiky", hair_col="#1d1716", collar="round", pants="#2a2a30"),
    "PLAYER TWO": Char(body="#9b59d0", hair="bob", hair_col="#e0a23a", collar="round", build=0.9, pants="#2a2a30"),
    "PLAYER THREE": Char(body="#4cb050", hair="curly", hair_col="#3a2a20", glasses="round", collar="round"),
    "PLAYER FOUR": Char(body="#e5483c", hair="bun", hair_col="#1d1716", collar="round", build=0.9),
    "MOD": Char(body="#26303f", hair="short", hair_col="#1d1716", glasses="shades", collar="shirt", pin="#f2c230"),
    "ADMIN": Char(body="#c8312c", hair="side", hair_col="#d8d2c8", glasses="rect", collar="shirt", lapels=True,
                  pin="#f2c230", pants="#1b1b22"),
    "DEV ONE": Char(body="#3a3a42", hair="curly", hair_col="#1d1716", glasses="round", collar="round"),
    "DEV TWO": Char(body="#2f7a4f", hair="bun", hair_col="#6e2a18", glasses="rect", collar="round", build=0.9),
}


# ---------------------------------------------------------------- helpers
def who(c, t, b, name, x, y, s, **kw):
    ch = CAST[name]
    ch.scene()
    kw.setdefault("bob", 0.006 * math.sin(t * 2.3 + x))
    return ch.draw(c, x, y, s, t=t + x * 0.01, talk=b.talking(name, t), **kw)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lane_cars(c, t, n=4, s=0.85, speed=1500, y=548, seed=0):
    cols = ["#3b82d6", "#4cb050", "#9b59d0", "#f2c230"]
    for i in range(n):
        x = (t * speed + i * 3000 / n + seed * 400) % 3000 - 700
        PG.racecar(c, x, y, s, cols[(i + seed) % 4], str(3 + i * 2), speed=1.0)


def hidden_players(c, t, b, names=("PLAYER ONE", "PLAYER TWO", "PLAYER THREE", "PLAYER FOUR"), peek=True):
    """players crouched behind the bushes: only the tops of their heads show"""
    for i, (name, (x, y)) in enumerate(zip(names, PG.HIDE_SPOTS)):
        if peek:
            up = 10 * math.sin(t * 2 + i)
            who(c, t, b, name, x + 20, y + 112 + up, 1.35, look=0.5 if i % 2 else -0.5, expr="smirk" if i % 2 else "neutral")
        PG.bush(c, x, y, 0.9)


def mini_party(c, x0, y0, w, h, t, text=None):
    c.rectangle(x0, y0 + h * 0.62, w, h)
    c.set_source_rgb(*style.hexc("#5cb04e"))
    c.fill()
    for i in range(14):
        bx = x0 + 18 + (i * 37) % (w - 30)
        by = y0 + 30 + (i * 23) % int(h * 0.5) + 4 * math.sin(t * 3 + i)
        c.arc(bx, by, 11, 0, 2 * math.pi)
        c.set_source_rgb(*style.hexc(PG.BALLOON_COLS[i % 7]))
        c.fill()
    c.arc(x0 + w / 2, y0 + h * 0.55, 16, 0, 2 * math.pi)
    c.set_source_rgb(*style.hexc("#fdd480"))
    c.fill()
    c.rectangle(x0 + w / 2 - 14, y0 + h * 0.6, 28, 34)
    c.set_source_rgb(*style.hexc("#f28b2c"))
    c.fill()
    if text:
        PG._ui_text(c, text, x0 + w / 2, y0 + 34, 20, (1, 1, 1))


def doorbell(c, x, y, t, presses=()):
    """the LEAVE GAME button mounted on a post like a doorbell"""
    c.rectangle(x - 10, y + 120, 20, 330)
    sets._fill_line(c, style.hexc("#8a5a32"), 4)
    PG._panel(c, x - 130, y - 150, 260, 280, a=0.95)
    press = any(0 <= t - p < 0.07 for p in presses)
    r = 70 * (0.9 if press else 1.0)
    sets.glow(c, x, y - 30, 200, style.hexc("#ff5a4a"), 0.4)
    c.arc(x, y - 30, r, 0, 2 * math.pi)
    sets._fill_line(c, style.hexc("#b8241c" if press else "#e0352b"), 5)
    c.arc(x - 22, y - 52, 18, 0, 2 * math.pi)
    c.set_source_rgba(1, 1, 1, 0.3)
    c.fill()
    PG._ui_text(c, "LEAVE", x, y + 80, 34)
    PG._ui_text(c, "GAME", x, y + 116, 34)


def fall_y(t, t_fall, floor=560):
    k = t - t_fall
    return floor if k < 0 else floor + 1600 * k * k


def tag(c, t, b, text, word=None, w=360, accent="#f2c230"):
    t0 = b.wt(word) if word else b.t0 + 0.15
    sets.name_tag(c, text, 60, 600, w, 76, (t - t0) / 0.35, accent=accent)


A = story.audio
CLICKS20 = [i * 0.135 for i in range(20)]

BEATS = [
    # ---- hook: the noob, then the button he caused
    {"at": 0, "tpl": "scene", "place": "party_park", "tr": "cut", "amp": 0.6, "shake": ["leave button"],
     "cast": [("PLAYER ONE", 290, 1.6, {"look": 0.4, "expr": "angry", "arms": "hips"}),
              ("TOBY", 640, 1.9, {"arms": "wave", "expr": "happy"}),
              ("PLAYER TWO", 1000, 1.6, {"look": -0.4, "expr": "deadpan"})],
     "fg": lambda c, t, b: PG.balloon_bunch(c, 760, 520, t - b.t0 - 0.2, n=6, t=t, seed=1),
     "ov": lambda c, t, b: (sets.pop_label(c, "THIS NOOB", 640, 110, t - b.wt("noob"), col="#f2d23a", size=60),
                            PG.game_menu(c, 1060, 300, t - b.wt("leave button"), glow_k=t - b.wt("leave button"), s=0.42)),
     "sfx": lambda b: [(b.wt("noob"), A.pop(), "pop", 0), (b.wt("leave button"), A.thud(), "thud", 2)]},
    {"at": 1, "tpl": "tag", "who": "TOBY", "place": "obby", "name": "TOBY", "sub": "LEVEL 1 NOOB", "expr": "happy",
     "label": "ONE DREAM", "label_at": "dream", "accent": "#f28b2c"},
    {"at": 2, "tpl": "scene", "place": "party_park", "amp": 0.6,
     "cast": [("TOBY", 400, 1.9, {"arms": "cheer", "expr": "happy", "look": 0.3})],
     "fg": lambda c, t, b: PG.confetti(c, t - b.wt("welcome"), 400, 260),
     "ov": lambda c, t, b: (sets.pop_label(c, "MAKE EVERY PLAYER", 880, 260, t - b.wt("every player"), col="#f2d23a", size=54),
                            sets.pop_label(c, "FEEL WELCOME", 880, 350, t - b.wt("welcome"), col="#3dff7a", size=54)),
     "sfx": lambda b: [(b.wt("every player"), A.pop(), "pop", 0), (b.wt("welcome"), A.sparkle(), "ding", -2)]},
    # ---- the obby
    {"at": 3, "tpl": "scene", "place": "obby", "amp": 0.25, "center": (600, 380),
     "cast": [("PLAYER ONE", 110, 1.5, {"look": 0.5, "expr": "neutral"}),
              ("TOBY", lambda t, b: -150 + 420 * min(1.0, (t - b.t0) / 1.4), 1.6,
               {"walk_phase": lambda t, b: (t - b.t0) * 7 if t - b.t0 < 1.4 else None, "expr": "happy", "look": 0.3})],
     "ov": lambda c, t, b: tag(c, t, b, "OBBY", "obby", w=220),
     "sfx": lambda b: [(b.wt("obby"), A.pop(), "pop", -2)]},
    {"at": 3, "word": "built a giant", "tpl": "scene", "place": "obby", "amp": 0.4, "tr": "cut", "center": (600, 380),
     "shake": ["giant welcome"],
     "cast": [("PLAYER ONE", 110, 1.5, {"look": 0.5, "expr": lambda t, b: "shock" if t > b.wt("giant") + 0.3 else "neutral"}),
              ("TOBY", 250, 1.6, {"arms": "cheer", "expr": "happy", "look": 0.3})],
     "fg": lambda c, t, b: PG.welcome_sign(c, 640, t - b.wt("giant"), 1.0, t),
     "ov": lambda c, t, b: sets.pop_label(c, "THE FIRST JUMP", 640, 665, t - b.wt("first jump"), col="#f2d23a", size=50),
     "sfx": lambda b: [(b.wt("giant"), A.whoosh(), "swish", -2), (b.wt("giant") + 0.3, A.thud(), "thud", 2),
                       (b.wt("first jump"), A.pop(), "pop", 0)]},
    {"at": 4, "tpl": "slam", "who": "TOBY", "place": "obby", "text": "YOU'RE WELCOME!", "col": "#2f9a3a", "size": 66,
     "expr": "happy", "arms": "cheer", "at_s": 0.06},
    {"at": 5, "tpl": "scene", "place": "obby", "amp": 0.25, "center": (600, 380), "tr": "cut",
     "cast": [("PLAYER ONE", lambda t, b: 120 + 260 * min(1.0, (t - b.t0) / 0.7), 1.5,
               {"walk_phase": lambda t, b: (t - b.t0) * 7, "look": 0.5, "expr": lambda t, b: "scared" if t > b.t0 + 0.7 else "neutral",
                "y": lambda t, b: fall_y(t, b.t0 + 0.7), "show": lambda t, b: fall_y(t, b.t0 + 0.7) < 900}),
              ("PLAYER TWO", lambda t, b: -100 + 480 * min(1.0, (t - b.t0) / 1.2), 1.5,
               {"walk_phase": lambda t, b: (t - b.t0) * 7, "look": 0.5, "expr": lambda t, b: "scared" if t > b.t0 + 1.2 else "neutral",
                "y": lambda t, b: fall_y(t, b.t0 + 1.2), "show": lambda t, b: fall_y(t, b.t0 + 1.2) < 900})],
     "fg": lambda c, t, b: (PG.welcome_sign(c, 640, 9.0, 1.0, t), D.puff(c, 400, 620, t - b.t0 - 1.0, r=90),
                            D.puff(c, 400, 620, t - b.t0 - 1.5, r=90)),
     "ov": lambda c, t, b: sets.pop_label(c, "WHERE'S THE JUMP?", 640, 665, t - b.t0 - 0.3, col="#ff5a4a", size=48),
     "sfx": lambda b: [(b.t0 + 0.3, A.pop(), "pop", -2), (b.t0 + 0.75, A.whoosh(), "swish", -4), (b.t0 + 1.0, A.thud(), "thud", -2),
                       (b.t0 + 1.25, A.whoosh(), "swish", -4), (b.t0 + 1.5, A.thud(), "thud", -2)]},
    # ---- the racing game
    {"at": 6, "tpl": "scene", "place": "race_track", "amp": 0.25, "center": (680, 400),
     "fg": lambda c, t, b: (lane_cars(c, t), PG.pizza_stand(c, 1030, 640, t),
                            who(c, t, b, "TOBY", 780, 670, 1.7, expr="happy", arms="wave", look=-0.2)),
     "ov": lambda c, t, b: tag(c, t, b, "RACING GAME", "racing", w=330),
     "sfx": lambda b: [(b.wt("pizza"), A.pop(), "pop", 0), (b.wt("racing"), A.pop(), "pop", -2)]
     + [(b.t0 + 0.3 + i * 0.5, A.whoosh(), "swish", -10) for i in range(4)]},
    {"at": 7, "tpl": "scene", "place": "race_track", "amp": 0.25, "center": (680, 400),
     "fg": lambda c, t, b: (lane_cars(c, t, n=3, speed=1800, seed=1), PG.pizza_stand(c, 1030, 640, t),
                            who(c, t, b, "TOBY", 780, 670, 1.7, expr="happy", look=-0.4, arms="present_l", item="pizza",
                                item_hand="l")),
     "sfx": lambda b: [(b.t0 + 0.2 + i * 0.45, A.whoosh(), "swish", -10) for i in range(3)]},
    {"at": 7, "word": "toby stopped it", "tpl": "scene", "place": "race_track", "amp": 0.4, "tr": "cut", "center": (720, 400),
     "shake": ["stopped"],
     "fg": lambda c, t, b: (PG.racecar(c, -500 + 1060 * ease((t - b.t0 + 0.4) / 0.75), 548, 0.95, "#e5483c", "7",
                                       speed=max(0.0, 1 - (t - b.t0) / 0.35)),
                            who(c, t, b, "TOBY", 960, 650, 1.8, expr="happy", look=-0.5, arms="present_l", item="pizza",
                                item_hand="l")),
     "ov": lambda c, t, b: (sets.pop_label(c, "PEPPERONI", 640, 100, t - b.wt("pepperoni"), col="#ff5a4a", size=58),
                            sets.pop_label(c, "OR CHEESE?", 700, 180, t - b.wt("cheese"), col="#f2d23a", size=58)),
     "sfx": lambda b: [(b.t0 + 0.3, A.thud(), "thud", 0), (b.wt("pepperoni"), A.pop(), "pop", 0), (b.wt("cheese"), A.pop(), "pop", 0)]},
    {"at": 8, "tpl": "scene", "place": "race_track", "amp": 0.5, "center": (560, 400), "shake": ["traffic"],
     "fg": lambda c, t, b: ([PG.racecar(c, 820 - i * 330 + 6 * math.sin(t * 9 + i) * (t > b.wt("traffic") + i * 0.1), 548, 0.8,
                                        ["#e5483c", "#3b82d6", "#4cb050", "#9b59d0", "#f2c230", "#3b82d6"][i], str(7 + i))
                            for i in range(6)],
                            who(c, t, b, "TOBY", 1110, 650, 1.6, expr="happy", look=-0.4, arms="present_l", item="pizza", item_hand="l"),
                            [sets.pop_label(c, "BEEP!", 820 - i * 330, 380, t - b.t0 - 0.3 - i * 0.18, col="#f2d23a", size=34)
                             for i in range(4)]),
     "ov": lambda c, t, b: sets.pop_label(c, "TRAFFIC JAM", 640, 110, t - b.wt("traffic"), col="#ff5a4a", size=64),
     "sfx": lambda b: [(b.wt("traffic"), A.thud(), "thud", 0)] + [(b.t0 + 0.3 + i * 0.18, A.pop(), "pop", -6) for i in range(4)]},
    {"at": 9, "tpl": "card"},
    # ---- hide and seek
    {"at": 10, "tpl": "scene", "place": "party_park", "amp": 0.5, "shake": ["surprise"],
     "fg": lambda c, t, b: (hidden_players(c, t, b),
                            who(c, t, b, "TOBY", 1500 - 800 * min(1.0, (t - b.t0) / 1.0), 690, 1.8, look=-0.3, expr="happy",
                                walk_phase=(t - b.t0) * 7 if t - b.t0 < 1.0 else None,
                                arms="cheer" if t > b.wt("surprise") else "rest"),
                            PG.confetti(c, t - b.wt("surprise"), 700, 250)),
     "ov": lambda c, t, b: (sets.pop_label(c, "SURPRISE PARTY!", 640, 110, t - b.wt("surprise"), col="#f2d23a", size=58),
                            tag(c, t, b, "HIDE & SEEK", "hide", w=320)),
     "sfx": lambda b: [(b.wt("surprise"), A.sparkle(), "ding", 0), (b.wt("hide"), A.pop(), "pop", -2)]},
    {"at": 11, "tpl": "scene", "place": "party_park", "amp": 0.5, "center": (680, 380),
     "fg": lambda c, t, b: (hidden_players(c, t, b),
                            [PG.balloon_bunch(c, x, y - 90, t - b.wt("balloons") - i * 0.3, n=5, t=t, seed=i)
                             for i, (x, y) in enumerate(PG.HIDE_SPOTS)]),
     "ov": lambda c, t, b: sets.pop_label(c, "EVERY HIDING SPOT", 640, 100, t - b.wt("every hiding"), col="#f2d23a", size=54),
     "sfx": lambda b: [(b.wt("balloons") + i * 0.3, A.pop(), "pop", 0) for i in range(4)]},
    {"at": 11, "word": "and he shouted", "tpl": "scene", "place": "party_park", "amp": 0.4, "tr": "cut", "center": (560, 330),
     "zoom": 1.15,
     "cast": [("TOBY", 470, 2.1, {"arms": "raise_r", "item": "megaphone", "expr": "happy", "look": 0.3})],
     "fg": lambda c, t, b: megaphone_waves(c, 700, 300, t),
     "ov": lambda c, t, b: [sets.pop_label(c, n.upper() + "!", x, y, t - b.wt("names") - i * 0.35, col=col, size=40)
                            for i, (n, x, y, col) in enumerate((("BlockyBen", 960, 150, "#f2d23a"), ("Pixel_Pam", 1040, 260, "#3dff7a"),
                                                                 ("LavaLuke", 930, 370, "#ff5a4a"), ("HideMaster", 1060, 480, "#f2d23a")))],
     "sfx": lambda b: [(b.wt("names") + i * 0.35, A.pop(), "pop", -2) for i in range(4)]},
    {"at": 12, "tpl": "slam", "who": "TOBY", "place": "party_park", "text": "FOUND YOU!", "col": "#e5483c", "size": 84,
     "expr": "happy", "arms": "cheer", "at_s": 0.05},
    {"at": 13, "tpl": "slam", "who": "TOBY", "place": "party_park", "side": "right", "text": "HAPPY BIRTHDAY!", "col": "#9b59d0",
     "size": 62, "expr": "laugh", "arms": "cheer", "at_s": 0.05},
    # ---- the players fight back
    {"at": 14, "tpl": "scene", "place": "party_park", "amp": 0.5, "center": (700, 360),
     "cast": [("PLAYER ONE", 700, 1.6, {"look": 0.4, "expr": "angry", "arms": "present_r"}),
              ("PLAYER TWO", 880, 1.6, {"look": 0.4, "expr": "sad", "arms": "cheer"}),
              ("MOD", 1110, 1.7, {"look": -0.4, "expr": "deadpan", "arms": "hips"})],
     "ov": lambda c, t, b: (PG.chat_box(c, 40, 120, t, [(b.t0 + 0.1, "BlockyBen", "pls remove him", "#3b82d6"),
                                                         (b.t0 + 0.5, "Pixel_Pam", "MODS HELP!!", "#9b59d0"),
                                                         (b.t0 + 0.9, "HideMaster", "he found me 9 times", "#4cb050"),
                                                         (b.t0 + 1.3, "LavaLuke", "i'm begging u", "#e5483c")], w=520),
                            sets.name_tag(c, "MODERATOR", 840, 620, 300, 70, (t - b.wt("moderators")) / 0.35, accent="#2a4fa0")),
     "sfx": lambda b: [(b.t0 + 0.1 + i * 0.4, A.tick(), "tick", -2) for i in range(4)]},
    {"at": 15, "tpl": "scene", "place": "party_park", "amp": 0.4, "center": (640, 360), "shake": ["kicked"],
     "cast": [("ADMIN", 380, 1.8, {"look": 0.4, "expr": "angry", "arms": lambda t, b: "point_r" if t > b.wt("kicked") - 0.2 else "hips"}),
              ("TOBY", 900, 1.8, {"look": -0.3, "expr": "happy", "arms": "raise_r", "item": "balloons",
                                  "show": lambda t, b: t < b.wt("kicked")})],
     "fg": lambda c, t, b: D.puff(c, 900, 470, t - b.wt("kicked"), r=180),
     "ov": lambda c, t, b: (sets.name_tag(c, "ADMIN", 60, 600, 220, 76, (t - b.wt("admin")) / 0.35, accent="#c8312c"),
                            PG.kick_dialog(c, 900, 330, t - b.wt("kicked") - 0.2)),
     "sfx": lambda b: [(b.wt("admin"), A.pop(), "pop", -2), (b.wt("kicked"), A.whoosh(), "swish", 0), (b.wt("kicked") + 0.2, A.thud(), "thud", 0)]},
    {"at": 16, "tpl": "scene", "place": "party_park", "amp": 0.5, "center": (640, 380), "shake": ["twice"],
     "cast": [("PLAYER ONE", 260, 1.6, {"look": 0.4, "expr": lambda t, b: "shock" if t > b.t0 + 0.3 else "neutral"}),
              ("TOBY", 760, 1.8, {"look": -0.2, "expr": "laugh", "arms": "cheer", "show": lambda t, b: t > b.t0 + 0.25})],
     "fg": lambda c, t, b: (D.puff(c, 760, 470, t - b.t0 - 0.1, r=170),
                            PG.balloon_bunch(c, 640, 380, t - b.t0 - 0.3, n=8, t=t, seed=2, spread=80),
                            PG.balloon_bunch(c, 880, 380, t - b.wt("twice"), n=8, t=t, seed=5, spread=80)),
     "ov": lambda c, t, b: (PG.join_toast(c, 640, 90, t - b.t0 - 0.2, "Toby_Welcome joined the server"),
                            sets.pop_label(c, "x2 BALLOONS", 1060, 640, t - b.wt("twice"), col="#f2d23a", size=50)),
     "sfx": lambda b: [(b.t0 + 0.1, A.pop(), "pop", 0), (b.t0 + 0.2, A.bell(), "ding", -6), (b.wt("twice"), A.sparkle(), "ding", -2)]},
    # ---- the developers build a button
    {"at": 17, "tpl": "scene", "place": "tech_office", "amp": 0.5,
     "cast": [("DEV ONE", 270, 1.7, {"look": 0.5, "expr": "worried", "arms": "chin"}),
              ("DEV TWO", 1010, 1.7, {"look": -0.5, "expr": "angry", "arms": "hips"})],
     "fg": lambda c, t, b: PG.monitor(c, 640, 520, lambda cc, x0, y0, w, h: mini_party(cc, x0, y0, w, h, t), w=380, h=230),
     "ov": lambda c, t, b: tag(c, t, b, "THE DEVELOPERS", "developers", w=380, accent="#2a4fa0"),
     "sfx": lambda b: [(b.wt("developers"), A.pop(), "pop", -2)]},
    {"at": 17, "word": "brand new button", "tpl": "label", "place": "tech_office", "react": False, "tr": "cut",
     "fg": lambda c, t, b: PG.game_menu(c, 640, 390, t - b.wt("button"), glow_k=t - b.wt("escape"), t=t),
     "labels": [("ESCAPE ANY SERVER", "escape", 640, 85), ("INSTANTLY", "instantly", 1060, 640)], "size": 52},
    {"at": 18, "tpl": "scene", "place": "party_park", "amp": 0.3, "zoom": 1.2, "center": (640, 470), "shake": ["leave"],
     "fg": lambda c, t, b: PG.game_menu(c, 640, 360, 9.0, glow_k=t - b.t0, t=t),
     "sfx": lambda b: [(b.t0 + 0.08, A.thud(), "thud", 2)]},
    {"at": 19, "tpl": "scene", "place": "party_park", "amp": 0.3, "tr": "cut",
     "fg": lambda c, t, b: (PG.game_menu(c, 640, 360, 9.0, glow_k=1.0, t=t, presses=[b.t0 + 0.25 + i * 0.16 for i in range(5)]),
                            [PG.cursor(c, 640 + dx + (1 - ease((t - b.t0 - i * 0.16) / 0.25)) * dx * 3,
                                       470 + dy + (1 - ease((t - b.t0 - i * 0.16) / 0.25)) * dy * 3,
                                       pressed=0 <= t - b.t0 - 0.25 - i * 0.16 < 0.12)
                             for i, (dx, dy) in enumerate(((-150, 10), (120, -20), (-40, 30), (170, 25), (-200, -10)))]),
     "sfx": lambda b: [(b.t0 + 0.25 + i * 0.16, A.tick(), "tick", 0) for i in range(5)]},
    {"at": 20, "tpl": "scene", "place": "party_park", "amp": 0.3, "center": (640, 380),
     "ov": lambda c, t, b: PG.player_list(c, 640, 370, t, [b.t0 + 0.15 + i * 0.14 for i in range(11)] + [None], 9.0, s=1.0),
     "sfx": lambda b: [(b.t0 + 0.15 + i * 0.14, A.tick(), "tick", -4) for i in range(11)]},
    {"at": 21, "tpl": "scene", "place": "party_park", "amp": 0.3, "center": (640, 400), "zoom": 0.95,
     "cast": [("TOBY", 640, 1.5, {"expr": "happy", "arms": "raise_r", "item": "balloons", "look": lambda t, b: 0.5 * math.sin((t - b.t0) * 2.2)})],
     "ov": lambda c, t, b: sets.pop_label(c, "1/12", 1120, 90, t - b.wt("alone"), col="#f2d23a", size=54),
     "sfx": lambda b: [(b.wt("alone"), A.pop(), "pop", -2)]},
    {"at": 22, "tpl": "card"},
    # ---- the doorbell
    {"at": 23, "tpl": "scene", "place": "party_park", "amp": 0.5, "center": (640, 370),
     "cast": [("TOBY", 420, 1.8, {"look": 0.5, "expr": lambda t, b: "happy" if t > b.wt("doorbell") else "neutral",
                                  "arms": lambda t, b: "chin" if t < b.wt("doorbell") else "cheer"})],
     "fg": lambda c, t, b: doorbell(c, 900, 330, t),
     "ov": lambda c, t, b: sets.pop_label(c, "DING DONG?", 420, 110, t - b.wt("doorbell"), col="#f2d23a", size=58),
     "sfx": lambda b: [(b.wt("spotted"), A.pop(), "pop", -2), (b.wt("doorbell"), A.bell(), "ding", 0),
                       (b.wt("doorbell") + 0.25, A.bell(), "ding", -3)]},
    {"at": 24, "tpl": "scene", "place": "party_park", "amp": 0.4, "center": (700, 370), "react": False,
     "cast": [("TOBY", 640, 1.8, {"look": 0.5, "expr": "laugh", "arms": "point_r",
                                  "show": lambda t, b: not any(0.05 <= t - b.wt("clicked") - p < 0.1 for p in CLICKS20)})],
     "fg": lambda c, t, b: (doorbell(c, 950, 330, t, presses=[b.wt("clicked") + p for p in CLICKS20]),
                            [D.puff(c, 640, 470, t - b.wt("clicked") - p - 0.05, dur=0.12, r=120) for p in CLICKS20]),
     "ov": lambda c, t, b: D.counter_box(c, 290, 120, t - b.wt("clicked"), 20, fmt="x{:,.0f}", sub="CLICKS", dur=CLICKS20[-1], w=300),
     "sfx": lambda b: [(b.wt("clicked") + p, A.tick(), "tick", 0) for p in CLICKS20]},
    {"at": 24, "word": "did somebody", "tpl": "scene", "place": "party_park", "amp": 0.4, "tr": "cut", "center": (560, 340),
     "zoom": 1.1,
     "cast": [("TOBY", 520, 2.1, {"expr": "laugh", "arms": "present_r", "item": "pizza", "look": 0.2})],
     "fg": lambda c, t, b: D.puff(c, 520, 420, t - b.t0, r=200),
     "ov": lambda c, t, b: (sets.pop_label(c, "DID SOMEBODY", 920, 220, t - b.wt("did somebody"), col="#f2d23a", size=56),
                            sets.pop_label(c, "ORDER PIZZA?", 940, 310, t - b.wt("pizza"), col="#ff5a4a", size=60),
                            PG.join_toast(c, 640, 90, t - b.t0, "Toby_Welcome joined the server")),
     "sfx": lambda b: [(b.t0, A.pop(), "pop", 0), (b.wt("pizza"), A.pop(), "pop", 0)]},
    # ---- the developers log off
    {"at": 25, "tpl": "scene", "place": "tech_office", "amp": 0.5, "shake": ["logged off"],
     "cast": [("DEV ONE", 270, 1.7, {"look": 0.5, "expr": "sad", "show": lambda t, b: t < b.wt("logged off")}),
              ("DEV TWO", 1010, 1.7, {"look": -0.5, "expr": "deadpan", "show": lambda t, b: t < b.wt("logged off") + 0.15})],
     "fg": lambda c, t, b: (PG.monitor(c, 640, 520, lambda cc, x0, y0, w, h: mini_party(cc, x0, y0, w, h, t, "ORDER PIZZA?"),
                                       w=380, h=230, off=t > b.wt("logged off")),
                            D.puff(c, 270, 440, t - b.wt("logged off"), r=150),
                            D.puff(c, 1010, 440, t - b.wt("logged off") - 0.15, r=150)),
     "ov": lambda c, t, b: D.stamp(c, 640, 120, t - b.wt("logged off") - 0.3, "LOGGED OFF", col="#2a4fa0", size=80),
     "sfx": lambda b: [(b.wt("logged off"), A.whoosh(), "swish", 0), (b.wt("logged off") + 0.15, A.pop(), "pop", 0),
                       (b.wt("logged off") + 0.3, A.thud(), "thud", 2)]},
]


def megaphone_waves(c, x, y, t):
    for i in range(3):
        ph = (t * 1.6 + i / 3) % 1.0
        c.arc(x - 160, y, 60 + 160 * ph, -0.5, 0.5)
        c.set_source_rgba(1, 0.95, 0.5, 0.9 * (1 - ph))
        c.set_line_width(7)
        c.stroke()


REACTORS = {1: [("PLAYER ONE", "party_park"), ("PLAYER TWO", "obby"), ("DEV ONE", "tech_office")]}


def build():
    return story.Story(sys.modules[__name__], VOICE, OUT, TITLE)


if __name__ == "__main__":
    import numpy as np
    st = build()
    cmd = sys.argv[1]
    if cmd == "audio":
        st.render()
    elif cmd == "part":
        st.render(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "concat":
        st.concat(int(sys.argv[2]), OUT / "toby_leave_button.mp4")
    elif cmd == "still":
        import cv2
        for a in sys.argv[2:]:
            t = float(a)
            cv2.imwrite(str(OUT / f"still_{t:07.2f}.png"), (np.clip(st.frame(t), 0, 1) * 255).astype(np.uint8))
    elif cmd == "beats":
        for b in st.beats:
            print(round(b.t0, 2), round(b.dur, 2), b.p["tpl"], b.sents[0]["script_text"][:50] if b.sents else "")
