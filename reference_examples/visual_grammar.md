# Visual grammar: how the reference turns each sentence into a shot

Source: the 3 reference videos. Method:
- `analysis/shots.py`: tracks features at 10 fps and measures every shot's camera move (zoom, pan, tilt) and lighting (brightness, warmth, saturation).
- `analysis/cue_sheets.py`: 3 frames (start, middle, end) for every SRT line, so each sentence can be matched to its picture. Video 3 has no SRT, so it was read from 1 fps frames and burned-in captions.

This is a rulebook, not model training: Claude reads it and applies it to every new voiceover.

## 1. Measured numbers

| What | Value |
|---|---|
| New visual per narration line | about 1 per SRT line, every **~2 s** (shots measured 0.9-2.2 s median per video) |
| Push-in | **55%** of shots. Median **1.3x per shot**, about **0.17x per second** at a near-constant speed; 1.5-3x on a reveal |
| Pull-out | **32%**. Median 0.77x. Used to reveal context or end a scene |
| Slow drift | 6% |
| Static hold | 3%. Only on emotional beats ("gone.") |
| Pans / tilts | ~2%. Rare |
| Push-in direction | 88% drift **upward**: the camera pushes toward a face or object, usually off-centre, not a dead-centre zoom |

Measured with the caption band masked out (`analysis/shots.py`); static captions otherwise hide the camera move. Tracker checked on a synthetic 1.5x zoom: it reads 1.49-1.50.
| Transitions | Soft cross-dissolve 0.3-0.4 s between almost every shot |
| Lighting | Brightness mostly 0.34-0.57 (mid-dark, never flat bright). Saturation 0.34-0.51 |

The camera never sits still. A shot with no move is a deliberate pause.

## 2. Sentence type → shot (rules)

| # | When the sentence... | Show | Camera | Character | Example in reference |
|---|---|---|---|---|---|
| 1 | Opens with a bold claim (the hook) | A **symbol object** for the idea, big and close | Fast push-in | Character appears second, reacting | "impossible to get fired" → giant red **FIRE** button, then boss grinning holding a key |
| 2 | Names a concrete thing (clock, phone, desk, bucket, police) | **That exact object**, close up, as an insert | Push-in on it | None or a hand | "ticking clock" → clock insert; "steel balls" → stacked buckets |
| 3 | Names an abstract idea (law, rule, money, time) | A **physical metaphor** with a label | Push-in | Optional | "law" → padlock labelled LABOR LAW on a fire alarm; "on paper nobody gambles" → clipboard "GAMBLING: NONE ☑" |
| 4 | Says "Imagine..." / "you" | Introduce the **you** character in the place, medium-wide | Track or push with them | Neutral, looking around | "Imagine your boss walks you past your desk" → walk through office |
| 5 | Quotes someone ("your boss says") | **Close-up of the speaker** looking at camera | Push-in on face | Big expression snap on the key word | "is nothing." → boss holds up an empty gift box, toothy grin |
| 6 | Is a punchline or ironic thought | **Close-up face to camera**, often holding the prop | Short push, then hold | Exaggerated reaction (grin, shock) | "wait, I'm getting paid for this?" → grin at camera with a phone showing pay |
| 7 | Contains a list ("cookies, chocolate, shampoo...") | **Same framing**, one item per word | Slight drift | Picks each item, expression changes each beat | prize counter items |
| 8 | Marks time ("every Friday", "one Monday", "a week") | **Calendar page** or time-lapse | Push-in on date | None | "Every Friday" → calendar NOV FRI 25 |
| 9 | Moves to a new place | **Establishing wide**: aerial, street or one-point corridor | Push-in or crane down | Small in frame | "almost every street" → neon city aerial; "inside" → long pachinko aisle |
| 10 | Is a twist or loss ("then... he's gone") | **Empty space** where the thing was | Static hold or very slow push, 2-3 beats | Absent, or small and confused | empty desk, chair pushed in |
| 11 | Explains why ("You see, ...") | **Lighting change** to darker blue with one warm lamp; the "explainer" character in a new set | Pull-out to reveal | Smug or calm, talks to camera | boss in blue corridor with lamp |
| 12 | Shows group reaction | Crowd in one row, all turn **in sync** | Push toward the protagonist | Same expression snap together | co-workers staring |
| 13 | Ends the story | **Return to an earlier location or symbol** | Pull-out or push to a sign | Small, alone | CAREER DEVELOPMENT ROOM door; police with clipboard |

## 3. Composition
- **Safe zone for Shorts (720x1280), from the user's template:** the WHOLE character (head to feet) and key props/labels stay inside x 38-680, y 149-1013; below y 678 the right edge is x 599 (like/comment buttons). Captions are added under y ~1013. Enforced automatically by `animator/safezone.py`: call `safezone.fit(SHOTS, sys.modules[__name__])` right before `render()`; list key props per shot as `keep=[(x0, y0, x1, y1)]` (world coords). Check with `safezone.overlay()` on frames.
- In the animator, give every shot a `focus` at the subject's face: push-ins end with it centred, pull-outs end with it at 45% height.
- Subject sits in the middle or lower-middle third, leaving the caption zone (about 70% down) readable.
- **Foreground framing** for depth: a shoulder, a head, a cat or a desk edge cut off at the frame edge and slightly blurred.
- Characters break the fourth wall: punchlines are delivered looking straight at the camera.
- Strong depth of field: the background is softer than the subject in close-ups (`dof=3-5` on a shot blurs everything away from the focus).
- Angle variety: over-the-shoulder (`style2.back_figure` in the foreground corner), dutch tilt for tension (`dutch=±0.05`), extreme close-ups, wide establishing shots, prop inserts.
- One-point perspective for long spaces (corridors, aisles, streets).

## 4. Character performance
- Expressions **snap on the key word** of the sentence, not at the start of the shot.
- Recurring set: deadpan, smirk (half-lid + one brow), shock (circle eyes), toothy grin (boss), happy arcs, laugh with tears, angry brows, sad brows.
- Bodies mostly hold a pose with a small idle sway. Big actions are short: lean back, point, raise a prop, lie back with sunglasses.
- Props are held up to the camera when they matter (phone, box, tokens).

## 5. Lighting by mood (measured warmth: positive = warm, negative = cool)
| Mood | Look | Reference |
|---|---|---|
| Normal / neutral | Cool white daylight, green or white walls | office (warmth −0.1 to −0.2) |
| Happy, reward, paradise | Warm yellow sun patch or golden glow | corner guy, prize counter (+0.2 to +0.3) |
| Menace, explanation, the system | Deep blue with **one warm lamp** spotlight | boss corridor (−0.3 to −0.45, saturation up to 0.79) |
| Night / city | Blue-purple with pink and cyan neon, wet reflections | v2 streets |
| Loss, emptiness | Cool, desaturated, quiet | empty desk |
| History / legend | Warm golden or sunset palette | v3 ending landscapes |

## 6. Rhythm of a ~60 s video
1. 0-5 s: hook claim + symbol object + main character reaction.
2. 5-20 s: "Imagine / you" setup in the main location, 1 visual per line.
3. 20-40 s: escalation, with time markers (calendar), lists and crowd reactions.
4. 40-50 s: twist (empty space, hold) then "You see," explanation with the lighting change.
5. 50-60 s: closing line on a returning symbol, pull-out, fade.

## 7. How to apply to a new voiceover
1. Transcribe and split into sentences with times.
2. Tag each sentence with a rule number from section 2 (a long sentence gets 2-3 visuals, one per clause, about every 2 s).
3. Pick the camera from the rule, then the lighting from section 5 by mood.
4. Put the expression snap on the key word's timestamp.
5. Join every shot with a 0.3-0.4 s cross-dissolve and a whoosh.

## 8. Pace: why the reference feels fast
Measured with `analysis/flow.py`: optical flow on edges only, so flat cartoon art and detailed art are compared fairly. The caption band is ignored. Units: % of frame width per second.

| | Reference (3 videos) | Clock tower v1 | Clock tower v3 |
|---|---|---|---|
| Camera speed on screen (median) | 5.9 / 15.1 / 9.1 | 6.4 | **10.0** |
| Camera speed (mean) | 10.4 / 23.5 / 15.7 | 8.6 | **11.0** |
| Non-camera motion (characters, objects, parallax) | 3.6 / 7.2 / 7.2 | 2.9 | **4.5** |

What makes it fast:
1. **The camera travels, not only zooms.** It slides sideways and up while pushing in (`ref_camera(travel_px=...)`), and starts fast then settles.
2. **Faces carry the motion, not bodies.** Mouths change shape every 2-3 frames with the narration (grin → open laugh → flat), and expressions snap on key words. Bodies mostly hold a pose with a small sway. `set_voice()` drives the speaking character's mouth from the voiceover loudness.
3. **Depth.** Near things move more than far things when the camera moves (parallax). Sky, stars, hills, far houses are drawn as slower layers.
4. **A new frame every ~2 s.** Long shots get a punch-in cut halfway (`beats`).
5. **Short dissolves** (0.22 s).

`analysis/pace.py` (pixels changed) is kept for reference but over-reads detailed art, so use `flow.py` to compare.

## 9. Checking a render against the reference
Run `python3 analysis/flow.py <animation.mp4>` (use the caption-free render) and `python3 analysis/shots.py <video> out.json`, then compare with sections 1 and 8.

`animator/engine.py: ref_camera()` applies sections 1 and 8 to every shot. Give each shot a `focus` (the face or object to push toward), a `cap` for busy frames, and a `speaker` (the character whose mouth follows the voice).

## 10. Phrase-level camera (a new framing every 2-4 words)
Read at 5 fps, the reference never waits for a sentence to end. Every phrase gets its own framing, and the camera **travels** to it:
- **Crane / drone up to reveal:** building-side tilt up into an aerial over the city ("gambling hall on almost every street"); pull back and rise to show the army ("had the biggest army in the world"), then come back down to the character.
- **Follow the object:** tilt from the dragon's mouth down to the frog's mouth as the ball would fall ("a frog's open mouth").
- **Move through space:** walk alongside characters, push through the doorway into the room ("to a tiny room").
- **Insert on the noun:** "ticking clock" → clock, "pocket watch" → watch close-up.
- Dissolves only when the place changes, and the camera keeps moving through them.

Rule used by the animator: a shot has `keys = [(word_time, zoom, (x, y)), ...]`. The camera **arrives on the word** it illustrates, moving over ~0.4-0.75 s with an ease in-out, dips its zoom on long moves (drone feel), gets motion blur when fast, and keeps creeping (zoom +7%/s, slight slide) while it holds. Whooshes are added under every big move.

Example (the user's): "A mill owner | built | the clock tower | that lied | to the entire city | for ten years | nobody noticed" → owner close-up under the tower → he points up, camera cranes up the tower → clock → clock smirks, push in → drone pull back over the city → day/night time-lapse → camera comes down to the street where people walk past.

Measured on that cut (`analysis/flow.py`): camera median 6.2 / mean 23.8 % width/s (reference 5.9-15.1 / 10.4-23.5).


## 11. Lessons from 8 reference videos (frame logs at 4 fps, `analysis/frame_log.py`)
Videos: Job, Window, Jar (first 3) + Button, Tree, Grave Bell, Upload Brain, Idea Zone (5 more).

**Pace (measured with `analysis/new_visuals.py`, counts cuts AND soft dissolves):**
- A new visual every **1.55-2.6 s** (median gap 1.2-1.75 s; 90% of gaps under 3-3.6 s). The fastest videos (Job, Jar, Bell) change every ~1.6 s.
- Our animator target: a new framing every **1.2-1.8 s**, never a gap over ~3.5 s.
- Camera speed (`flow.py`): median 4-15 % width/s across the 8. Non-camera motion (characters/objects) 3.6-8.6.
- Hard cuts are rare. Almost every change is a **0.25 s cross-dissolve** or the camera itself travelling (tilt/crane/push) to the next subject.

**More sentence → shot rules seen in the 5 new videos:**

| # | When the sentence... | Show | Example |
|---|---|---|---|
| 14 | Explains what happens **inside** something (body, plant, brain, ground) | A **cutaway diagram** in the same cartoon style: X-ray skeleton, thermal lungs, skin cross-section with labels, leaf veins glowing, brain inside a see-through blue head, underground soil layers with the coffin | "milky sap" → leaf turns to glowing veins + label MILKY SAP; "scorches your lungs" → THERMAL lung view with temperature bar; "nature calls" → X-ray gut |
| 15 | Gives a number / count / data | A **physical counter or diegetic UI**: mechanical tally counter 0046→0047, digital 1000 counter, satellite map "NIGHT 1 · 9:42 PM" + red SEVERE STORM badge, game HUD with score, "100%" on a form | "47 tiny scratches" → hand clicker with 0047; "a thousand times thinner" → counter rolling to 1000 |
| 16 | Talks about "everyone / the whole town / people" | **Huge crowd** or drone pull-out to show scale, then back to one face | "the whole town is standing in an empty field" → aerial pull-back to a ring of people |
| 17 | Says something is forbidden / a warning | A **big symbol mark** on the object: red X painted on the tree, sign, label, padlock | "big red X painted on its trunk" |
| 18 | Describes ideas, memories, connections | **Corkboard** with pinned cards/photos and red string being drawn | "pattern of connections", "ideas that never connect" |
| 19 | Time passes in one place | Same framing, **lighting changes**: day→night tint, sky glow getting brighter, sunrise through the window, snow | glow on the wall brighter every year; rocking chair from night to sunrise |
| 20 | A thing is destroyed / goes wrong | Show the result **physically and literally**: palace becomes a smoking pile of rubble, the car paint peels, blisters grow, fire turns to black smoke | "can strip the paint off a car" |
| 21 | A character feels a sensation (burning, cold, sick) | **Face close-up with a body-colour change + emoji effects**: face goes red with steam puffs, blue + shivering, eyes stream tears, sweat drops | "your mouth starts burning" |
| 22 | Says "you" in a hypothetical ("If you...", "Imagine you're stranded") | The **"you" character** acts it out in the place (sits under the tree, falls asleep in the chair) and keeps the same look all video | Tree, Idea, Brain |
| 23 | The last line | A **callback** to the first image (same place / object / counter: 0047→0048, the sand, the bell) and the character's final reaction to camera | all 8 |

**Look & characters (all 8 share them):** one cartoon cast (round cream head, dot eyes, thick dark limbs) inside soft 3D-lit sets with depth of field, bloom from lamps/windows, light rays. Expressions snap on the key word; a face close-up (head filling 60-80% of frame) appears every ~10 s for emotional beats.

**Sound:** see `sound_design.md` (SFX ~1 per second on visual events, music −20 dB, D minor, no drums).

| 24 | Counts seconds / steps down ("Second 10... Second 9...") | An **on-screen timer HUD** (screen-space overlay) that ticks at every spoken number, plus a big "SECOND N" label; shots with a HUD set `top=250` so safezone.fit keeps characters and labels below it | speedrun.py `make_hud`, `HUD` list |
| 25 | Last line asks to replay ("comment loop") | A loop-arrow + comment bubble, then **return to the first frame** (same scene as shot 1, fade_out=0) so the Short loops | speedrun.py `s_loop`, `s_end` |
