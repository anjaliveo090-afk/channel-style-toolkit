# Style bible: Paper Billions look (measured)

**Coverage.** This is measured on V1 "How a Chinese Spy Got Inside Nvidia":
- part 1 (0:00-1:17.7, 24 fps) and part 4 (3:52.9-5:10.5, 30 fps), 1280x720;
- plus the user's 6 crops (living room, porch, school corridor, cheque ceremony, pointing man, dinner).

That is about 13% of V1. V2 and V3 have not been seen as video yet, so add them when they arrive.

Rule: copy the STYLE only. Our characters, names, logos and on-screen text are original.

## 1. Format
- **Output size and frame rate.**
  - Long-form: 16:9, 1280x720 (render 1920x1080 for upload).
  - The channel renders at 24 fps; part 4 arrived re-encoded at 30 fps.
  - We render at 24 fps.
- **No burned-in subtitles.** On-screen text appears only as:
  - black typed text cards;
  - name tags;
  - labels inside the scene: signs, documents, whiteboards, stamps, dollar counters.
- **Safe zone for 16:9.** Keep faces and key text inside x 64-1216, y 40-680. A 9:16 Short variant uses the repo safe zone (`animator/safezone.py`).

## 2. Characters (`animator/style.py`)
All sizes are in units of the head radius **R**.

| Part | Measured |
|---|---|
| Head | Circle R. Outline `#200a00`, 0.04-0.045 R (6-7 px at R 160). Face lines about 0.55 of that |
| Body | Capsule/bean under the head: 1.7 R wide, 2.8 R tall. The head overlaps the body top by 0.3 R. Narrow sloped top, widest at about 75% down. Thin outline (0.8 of the head line) |
| Shorts band | Bottom 0.36 R of the body, dark (`#3a2f30`, `#2f3a55` navy) |
| Arms at rest | Curved contour lines **inside** the body edge, from 25% to about 70% of the body height (no hands drawn) |
| Arms in action | One thin black line from the shoulder (body edge, 25% down) to the hand. The hand is the line end, or 3 short finger strokes when holding something |
| Legs | Two straight thin lines, 1.15 R long, 0.4 R apart, **no feet** |
| Height | About 5.8 R, i.e. about 2.9 head-heights. Kids use the same proportions at about 0.7 scale |
| Floor shadow | Soft dark ellipse, about 2.7 R wide, alpha about 0.4 in the middle |
| Light | One warm key light. The body is lighter on the key side, darker at the bottom, with a faint rim on the lit edge |

### Face
- **Skin, 3 tones.** Highlight `#fdd480`, mid `#e9a561`, shade `#b5794e`, as a gradient across the head from the key light. A soft darker crescent sits under the chin.
- **The "moon line" (chand line).** A bright crescent (`#ffd98a`, about 0.13 R thick at its widest) sits just inside the outline on the key-light side. Its inner edge is a **thin darker line**. This is the most recognisable part of the look.
- **Eyes.** Vertical dark-brown ovals (`#3a2414`, 0.11 x 0.17 R) at ±0.21 R from the face centre, with a small white highlight top-right.
- **Brows and nose.** Brows are thin arcs about 0.26 R above the eyes. There is no nose.
- **Mouth.** A small thin arc. Laugh = a big D shape (`#430b0b` inside, cream teeth band, coral tongue `#d34238`). Talk = a small dark oval that opens and closes.
- **Turning.** The face turns toward who the character looks at: all features slide up to 0.38 R sideways. Glasses keep a temple line only to the far edge of the head.
- **Extras.**
  - Crow's-feet creases: 3 tiny strokes beside the eyes, on some characters and on laughs/winks.
  - Pink hatch blush.
  - Sweat drop on shock or worry.

### Views
- **Front and 3/4.** Features are shifted sideways.
- **Side.** Features are at the edge.
- **Back.** No face. The hair covers the top 55-60% of the head with a ragged lower edge; the body has no collar.
- **Sitting.** No legs.
- **Walking.** The legs swing, with a slight bob.

### Hair
A solid cap with its own outline that comes down past the head outline at the sides (like a helmet), with the fringe at brow level. Styles seen:
- bowl, bun on top, bob, side part, curly, swept grey, long (falls behind the body), bald with side tufts.

### Expressions in `style.py`
neutral, happy (open eyes + smile), joy (closed arcs), laugh, talk, smirk, wink, shock, scared, sad, worried, angry, deadpan, blush, sly.

### Clothes
Colour only, plus:
- white shirt-collar V;
- round collar;
- lapel lines for suits;
- tie;
- a centre line (zip or cardigan);
- a pin.

Overalls, hard hats and plasters are drawn as props per story.

### Scene light
`Char.scene(ambient, rim)`:
- Night and blue scenes tint the clothes fully and the skin only by half (faces stay warm).
- The moon crescent takes the scene light colour (for example `#bcd4ff` under blue light).

## 3. Palette (sampled hex)
| Use | Hex |
|---|---|
| Outline / ink | `#200a00` |
| Skin highlight / mid / shade / rim | `#fdd480` / `#e9a561` / `#b5794e` / `#ffd98a` (alt face: `#dba37c` mid, `#b38b73` shade, `#febd6c` rim) |
| Restaurant wall (mid / dark) | `#3b170b` / `#1f1008` |
| Red booth / gold piping | `#65090f` / `#c8963a` |
| Roses / candle core / wine | `#fc301b` / `#fefeaa` / `#932a27` |
| Night window | `#04071b` → `#0c1a44` |
| Living room warm wall / floor | `#eea86a` → `#d99c68` / `#9e5e30` |
| Night office / corridor | blues `#1c2c55` → `#0a1028`, cold ceiling light `#cfe0ff` |
| Name tag box / accent / text | `rgba(23,15,13,0.86)` / `#7ab51d` / `#f4ecd6` |
| Black text card / text | `#000000` / `#fafafa` |
| Money labels | green `#3d8b2f` on paper, yellow-green glow `#c8ff4a` |

## 4. Sets and backgrounds
- **Flat vector sets with real lighting.**
  - Practical lights (lamps, sconces, windows, ceiling strips) that glow and bloom.
  - Vignette, and light falloff toward the edges.
  - Background blur in close-ups (DOF sigma about 3.5-4 px at 720p).
- **Places seen.** Restaurant at night, family living room, porch at sunset, school corridor with lockers, school bathroom, diner (Denny's-like) with a crowd, night office with the Capitol in the window, bright Silicon Valley office with whiteboard and cactus, MSS-style dark blue server corridor, black void with a spotlight, maps (paper-map palette with clouds), calendar close-ups, whiteboards, documents, cheques.
- **Depth.** One-point perspective for corridors and aisles. Foreground props (roses, plates, tables) frame close-ups.
- **Lighting by mood.**
  - Warm amber for home, past and success.
  - Cold blue for spies, government and night.
  - Bright daylight for offices and maps.
  - Black void + spotlight for "the key/the man" moments.

## 5. On-screen graphics (`animator/sets.py`)
- **Black text card.**
  - White **Caveat Brush** (OFL), widened 1.12x and slanted about 14°, 64 px at 720p, typed letter by letter at about 16 letters/s.
  - Short lines are centred (y about 0.47 H). Long lines start at the left (x about 0.09 W, y about 0.3-0.45 H).
  - It holds about 0.5-1 s after the last letter.
- **Chapter card.** The same font, centred, holding about 2.2 s, on a 2-4.5 s pause in the voice.
- **Name tag (lower third).** Dark rounded box, green bar on the left with a small pointer under it, cream slanted brush caps. The box appears first, then the name **types on** at about one letter per frame (~0.5 s; measured frame by frame).
- **Labels and documents.** Hand-lettered slanted caps on paper, whiteboards, plaques and stamps ("SECRET", "BLOCKED" red stamp). Money counters roll up ("$1M → $8M → $61M").
- **Effects.** Comic speed-lines/impact flash (white radial burst, 2 frames), magnifier lens, camera viewfinder with REC, polaroids dropping in, split screen with a phone cord across the divider.
