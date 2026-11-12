# Style Bible: reference channel (3 videos analysed)

Videos: "The Job Nobody Wants in Japan" (60s), "The Window That Breaks Japan's Gambling Law" (45s), "The Ancient Jar That Warned an Empire" (65s, no SRT, 480p).
Method: ffprobe, 1 fps contact sheets, 4 fps dense frames of motion-heavy moments, SRT timing. Limits: motion is inferred from frames, so very fast or subtle motion is approximate.

## 1. Format
- Vertical **9:16**, 720x1280, 30 fps. Total length 45-65 s (about 5-7 clips of 10 s).
- In Flow switch **16:9 to 9:16**. Your current screenshot has 16:9 selected.
- Burned-in captions: bold white sans-serif, black outline, 1-2 words at a time, lower-middle of the frame (about 70% down), word-by-word with the narration. Add these in the editor, do not ask Omni to render text.
- Narration speed: about 3.5-4 words per second (measured per 10 s clip from the SRT: 2.9-4.9, video 1 average about 3.9). Fast, punchy delivery with almost no pauses.

## 2. Look (the core of the style)
Hybrid: **simple 2D cartoon stick characters inside rich, cinematic, 3D-looking painted environments.**
- Characters: flat color, thick dark outline, almost no shading.
- Backgrounds: detailed stylised 3D/matte-painting look with real lighting: volumetric light shafts, neon reflections on wet streets, golden-hour glow, bokeh, soft depth of field, subtle film grain.
- Colour changes with mood:
  - Office (video 1): green brick wall, saturated blue floor, yellow light beam.
  - Night alley (video 2): deep blue/purple with warm orange window glow and pink/cyan neon.
  - Pachinko hall: warm gold ceiling lights, red carpet, red stools.
  - Medieval court (video 3): red/gold throne room, blue carpet, grey stone, then pastel sunrise outdoors.
- Readable in-world signs: "FIRE", "TO DO", "PRIZE COUNTER", "CAREER DEVELOPMENT ROOM". Keep text to short signs. Omni may garble longer text.

## 3. Character template
Same template for every character, with only hair, clothes and colour changed.
- Head: very large round head (about 1/3 of body height), peach or white. Tiny body.
- Body: bean or tube torso, **thin stick arms and legs** with no hands detail (mitten hands), tiny shoes.
- Face: small black dot or line eyes, thin eyebrows, simple line mouth. No nose, or a very small one.
- Hair: simple solid shape (brown bowl cut, grey side-parted, black bowl cut).
- Cast examples:
  - Boss: grey hair, white shirt, dark suit, red tie, big white toothy grin.
  - Worker (video 1): brown hair, teal shirt.
  - Gambler (video 2): brown hair, orange hoodie, camera strap.
  - Shop clerk: black bowl cut, dark uniform, red bow tie, closed-eye smile.
  - Mystery buyer: sunglasses, purple jacket, black beret.
  - Emperor: tall black hat with beads, dark blue robe with red-gold collar.

## 4. Face reactions (a small, repeating set)
| Reaction | How it is drawn |
|---|---|
| Smirk or deadpan | Half-lidded eyes (flat top lid), one eyebrow raised, small flat or crooked mouth |
| Shock | Eyes become big white circles with tiny pupils, eyebrows jump up |
| Big fake grin | Wide row of white teeth in a rectangle, eyes closed as arcs (the boss) |
| Happy | Closed arc eyes ("^ ^"), soft smile |
| Laughing | Arc eyes, open mouth, tear drops, sometimes falling off the chair |
| Annoyed or unimpressed | Angled flat eyebrows, small frown, eyes half-closed (emperor) |
| Skeptical | One eyebrow high, side look |
- Expression changes are **snaps** (2-4 frames), not slow morphs.
- Lip-sync is simple: mouth shapes swap between closed and open, not detailed phonemes.

## 5. Body motion
- Limited animation feel. Characters often hold a pose with small idle sway or bounce.
- Big actions are exaggerated and rubbery: legs dangling off a chair, leaning back in shock, falling over laughing, slow chair swivel.
- Props are animated simply: a clock's second hand ticking, a phone being scrolled, cobweb in the inbox, a hand sliding tokens through a window.
- Crowds are copies of the same simple character in different colours, moving in small loops.

## 6. Camera
The camera is **almost always moving**. Typical moves, from most to least common:
1. Slow push-in on a character or prop over the whole shot.
2. Forward dolly down a corridor or aisle (pachinko hall).
3. Crane or aerial descent from skyline to street (night city).
4. Slow orbit or tilt around an object (the jar, the desk).
5. Close-up insert on a prop (clock, bowl of wine, cup, pendulum) before cutting back.
6. Top-down or odd angle for tension (pendulum from above).
7. Pull-back reveal from a close-up to wide.
- Characters are usually framed medium or close, in the lower half of the vertical frame, leaving room for captions.

## 7. Pacing and transitions
- Average shot length about **2-3 s**, so a 10 s clip holds roughly 3-4 shots.
- Transitions are mostly **soft cross-dissolves (about 0.3-0.5 s)**, with some match cuts. Few hard cuts.
- Each new line of narration usually triggers a new angle or a new prop insert.
- Structure: hook in the first 3 s (a bold claim plus a striking visual), then a story with a twist, then a short punchline or closing question.

## 8. Reusable prompt blocks

**STYLE LOCK** (paste at the top of every clip):
```
Vertical 9:16 animated short. Simple 2D cartoon stick-figure characters: very large round
head, tiny bean body, thin stick limbs, thick dark outlines, flat colours, dot eyes and simple
line mouths. They live inside a richly lit, stylised 3D painted environment with volumetric
light, soft depth of field and cinematic colour grading. Limited-animation feel: held poses,
small idle sway, snappy exaggerated expressions (2-4 frame snaps), rubbery limbs.
Constantly moving camera. No text, no captions, no watermark, no logos.
```

**CLIP TEMPLATE** (one per 10 s):
```
[STYLE LOCK]
Location: <place, colour mood, light>
Characters: <names + look, as in the reference images>
0-3s: <shot type, camera move, action, face reaction>
3-6s: <shot type, camera move, action, face reaction>
6-10s: <shot type, camera move, action, face reaction>
Transition between shots: soft cross-dissolve.
Pace: medium, snappy.
```

## 9. Worked example: video 1, 0-10 s ("It's impossible to get fired... a tiny room with no computer and no work")
```
[STYLE LOCK]
Location: modern Japanese office, green brick walls, blue floor, bright cold light.
Characters: boss (grey side-parted hair, dark suit, red tie, big white toothy grin).
0-3s: Close-up of a big red "FIRE EMPLOYEE" button on a desk, camera slowly pushes in, light flickers.
3-6s: Medium shot, the boss grins at the camera holding a small red key, snaps from deadpan to toothy grin in 3 frames, slow push-in.
6-10s: Wide shot, boss walks a worker past rows of desks to a tiny door labelled CAREER DEVELOPMENT ROOM, camera tracks forward behind them.
Transition between shots: soft cross-dissolve.
```

## 10. Workflow in Flow
1. Generate each recurring character and each location once in **Image mode** (9:16), using the character template above.
2. Add those images as **Ingredients** in every clip.
3. Paste STYLE LOCK + CLIP TEMPLATE. Test with x1 (15 credits), then x2-x4 for the final pick.
4. For continuity, use the last frame of clip N as the **Frames** start of clip N+1.
5. In CapCut or DaVinci: join clips, add the narration, add word-by-word captions, add 0.3-0.5 s dissolves, trim speed to 90-110%.

## 11. What stays approximate
- Exact character faces: need Ingredients images in every clip.
- Exact frame timing and tiny motion details: Omni will interpret, not copy.
- Text inside the scene (signs): may come out garbled, fix in the editor if needed.
- Video 3 had no SRT, so its timing comes from burned-in captions and frames only.
