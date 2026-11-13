"""Contact sheet of every place with characters standing in it: python3 animator/places_sheet.py"""
import sys
from pathlib import Path

import cairo
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import places  # noqa: E402
import render16 as R  # noqa: E402
from style import Char  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "output" / "places"
A = Char(body="#e2805a", hair="bun", collar="shirt")
B = Char(body="#c9c6c0", hair="bowl", glasses="round", collar="shirt", pants="#2f3a55")
NIGHT = {"night_office", "server_corridor", "void_spotlight", "night_city"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles = []
    for name, fn in list(places.PLACES.items()):
        bg, fg, ov = R.layers()
        info = fn(cairo.Context(bg), 1.0)
        c = cairo.Context(fg)
        fl = info.get("floor")
        if fl:
            for ch, x, lk in ((A, 470, 0.3), (B, 780, -0.3)):
                if name in NIGHT:
                    ch.scene(ambient=(0.62, 0.68, 0.9), rim="#bcd4ff")
                else:
                    ch.scene()
                ch.draw(c, x, fl, 1.4, expr="happy", t=1.0, look=lk)
        img = R.post(R.compose(bg, fg, ov, dof=1.2))
        im = Image.fromarray((img.clip(0, 1)[..., ::-1] * 255).astype("uint8")).resize((640, 360))
        tiles.append(im)
        im.save(OUT / f"{name}.png")
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (640 * cols, 360 * rows), "white")
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
    sheet.save(OUT / "places_sheet.jpg", quality=88)
    print(OUT / "places_sheet.jpg")


if __name__ == "__main__":
    main()
