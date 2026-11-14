# Thumbnail bible (measured on the 4 reference thumbnails, 1280x720)

Source: the channel's 4 thumbnails (V1 spy dinner, V2 market crash, V3 IPO bell, V4 "fail without Jensen").
Measured with `analysis`-style pixel passes (text masks, skin blob, k-means palette, Laplacian sharpness).
Copy the STYLE only: never the channel's drawings, props (zipper, cracking chip, bell), text or layout 1:1.

## 1. The formula (all 4)
| Part | Measured | Rule for ours |
|---|---|---|
| Text | One line across the top, 2-4 words, ALL CAPS, heavy grotesque sans. Cap height 67-101 px (9-14% of H), centre y = 0.07-0.11 H, spans 62-85% of W, starts 6-13% from the left. | One line, cap height ~94 px (13% H), baseline y ≈ 130, x from ~110, DejaVu Sans Bold (closest installed match: widths within 2%). |
| Text colours | White `#f5f4ed` for the noun / phrase, red `#fd3b31` (V1, V4) to `#ff4b3d` (V2, V3) for the dollar figure. The figure carries `$` and a minus. Black outline ~5-6 px + a soft black drop shadow offset ~8 px down-right. | White phrase + red number, stroke 7 px black, shadow 8 px at 55%. |
| Text pattern | V1 `$2 BILLION OF CHIPS` (red number first). V2 `NVIDIA -$400B` (white noun, red number). V3 `-$80 BILLION` (red only). V4 `ONE ZIPPER. -$2 TRILLION` (white "one [prop]." then red number). | White 1-2 word hook + red `-$` number. |
| Character | One caricature, head 42-59% of H tall, head centre at x = 0.25-0.39 W, y = 0.40-0.64 H, turned toward the prop. Face (skin blob) 22-31% W wide. Extreme expression: eyes wide with big black pupils, brows pulled up in the middle, 2-3 sweat drops, gritted teeth (V3, V4) or an open shouting mouth (V2) or a grin (V1). Thick black outline. Grey swept hair, glasses, black leather jacket with a zipper and studs (their Jensen); V3 is a curly-haired round-glasses character. | Our own cartoon figure (style.Char at 5.5-6x, pose sit, expr scared/shock), 3 sweat drops, head centre (0.33 W, 0.55 H), looking at the prop. |
| Prop | Exactly one, held or touched, at x = 0.50-0.68 W, y = 0.65-0.89 H, glowing Nvidia green `#5ad01a`-`#6ad822` (2-10% of the frame) with rays and flying fragments. | One prop from our story (memo / jacket on its stand / name plate), green glow, rays, 4-6 fragments. |
| Background | Night, painterly: restaurant with warm lamps and candles (V1, V4), stormy cliff (V2), burning trading floor (V3). Dark: 52-62% of pixels under 0.2 luminance, mean luminance 0.27-0.28, saturation 0.56-0.65. Strong vignette: corners 0.13-0.16 vs centre 0.18-0.60. The two newest (V2, V4) blur the background hard (Laplacian variance 4-39 vs 2400-2800 on the face). | Dark set from `places2` + warm bokeh lights, Gaussian blur sigma ~8 px, vignette, grain. |
| Palette (k-means, 6) | ~45-61% near-black (`#130f10`, `#112027`), 17-20% dark warm brown/green, 13-16% skin `#eeb57b`, 5-9% white, 3-8% red, 3-7% green glow. | Same proportions: mostly dark, one warm, one green, one red. |

## 2. Per-thumbnail notes
- **V1 "$2 BILLION OF CHIPS"** (spy dinner). Two characters for once: him laughing with a wine glass, her in red with sunglasses and a smirk; a chip passed under the table in a green glow at the very bottom centre (0.50 W, 0.89 H). Candles, roses, warm bokeh. The number sits red on the left, the noun white on the right.
- **V2 "NVIDIA -$400B"** (crash). Him on a cliff edge, shouting, hands on a cracking GPU board that glows green; fragments fly; stormy teal-black sky. Background fully blurred.
- **V3 "-$80 BILLION"** (IPO). A different, curly-haired character grins and sweats while ringing a golden bell; trading floor on fire; small panicking figures run; money flies. Red text only.
- **V4 "ONE ZIPPER. -$2 TRILLION"** (fail without Jensen). Him close, gritted teeth, one sweat drop, pulling a broken zipper pull off his jacket; green light bursts from the open zipper; restaurant bokeh behind, hard blur. The newest and the biggest head (59% H).

## 3. What makes them click (and what we keep)
1. One number, red, with `$` and a minus. The number is the story.
2. One face, huge, in trouble. Sweat and pupils read at 160 px wide.
3. One glowing prop that explains the number without words.
4. Darkness everywhere else, so the three things above are the only bright things.
5. No logos, no small text, no second line.

## 4. Our builder
`python3 animator/thumbnail.py [out.png]` renders at 2x and writes 1280x720 PNG + JPG. Text, number, prop and
expression are set at the top of `main()`. Rendered 2D (code), not painted: the layout, sizes, colours, blur
and lighting are matched to the numbers above; the painterly shading of the reference is not reproduced.
