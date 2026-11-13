# Visual grammar: how Paper Billions turns narration into pictures (measured)

**Sources:**
- `analysis/motion30.py`: every frame at native fps (camera zoom/pan by ECC, transitions, shot list).
- `analysis/frame_log.py`: 4 fps sheets with the spoken line.
- Frame strips around every transition.

**Coverage:** V1 parts 1 and 4 (0:00-1:17.7 and 3:52.9-5:10.5). Raw data is in `analysis/ref_data/v1_part{1,4}_motion.json`.

## 1. Measured numbers
| What | Part 1 | Part 4 | Target for our renders |
|---|---|---|---|
| Shot length median | 2.5 s | 2.8 s | **2.5-3.0 s** |
| A new shot every | 3.1 s | 3.1 s | 2.6-3.4 s |
| A visual change inside a shot (pop-in, label, expression, prop) | about every 1-1.5 s | same | **at least 1 per 1.5 s** |
| Push-in shots | 62% | 76% | about 70% |
| Pull-out shots | 29% | 14% | about 20% (reveals, scale) |
| Static holds | 10% | 5% | under 10% (emotional beats, text cards) |
| Zoom speed while moving (median) | 5.9%/s | 8.5%/s | **6-9%/s**; reveals 25-40%/s; punch-in 2x in 0.5 s |
| Pan speed median | n/a | 53 px/s at 720p | 40-70 px/s; travelling moves 300-900 px per shot |
| Black text cards | 4 in 77 s | 4 in 77 s | **about 1 per 18-20 s**, 1.5-5.5 s long |
| Chapter cards | 1 (0:41.6) | 1 (4:28.6) | 1 per chapter, about 2.2 s |

The camera almost never sits still. Most shots start fast and decelerate (ease-out), and the next shot often starts already moving.

## 2. Transitions seen (frame-verified)
| Kind | How it looks | When |
|---|---|---|
| **Hard cut** | One frame. The most common | Between beats inside a chapter |
| **Black text card** | Hard cut to black. White script types on letter by letter with a tick per letter. Hard cut out | Key sentence, irony, "X has no idea." Lines under 40 characters are typed whole |
| **Chapter card** | Black, centred title, about 2.2 s, a sting + music change | Chapter start |
| **Whip-pan** | 0.25-0.4 s heavy horizontal motion blur from one framing to the next | Jumping between two people or places (part 1: 8) |
| **Zoom-through** | The camera pushes hard into a window/object (>1.25x in 0.4 s) and cuts to the inside | "To see why..." / going inside a place |
| **Fast pull-out** | Zoom 5x → 1x in about 1.4 s from a detail to a wide reveal | Revealing who holds the key, the scale |
| **Impact flash** | 2 frames of white radial speed-lines (manga burst), then the scene continues bigger | A big number or growth jump ("$1 → $8 billion") |
| **Magnifier lens** | A circular lens appears on a document/whiteboard and grows to fill the frame | Zooming into text or numbers |
| **Circle wipe** | Circular lens edge sweeps across | Into a document close-up |
| **Page flip** | Calendar pages fly off (Aug → Sep) | Time passing |
| **Split screen** | Two rooms side by side, a phone cord across the divider | Phone calls between two sides |

## 3. Sentence type → what is shown
| # | Sentence | Show | Camera | Example (ref time) |
|---|---|---|---|---|
| 1 | Cold-open claim in present tense | The scene itself, characters mid-action, warm cinematic light | Slow push-in, whip to a close-up on the name | Dinner in Singapore, 0:00-0:13 |
| 2 | Names a person | Close-up + **name tag** lower third | Push-in on the face | "He's Jensen Huang" 0:06 |
| 3 | Dramatic irony / "X has no idea" | **Black text card** typed | Static | 0:20 |
| 4 | Someone is watching | Viewfinder overlay with REC, polaroids dropping, corkboard with string | Push through the window | 0:14-0:21, 0:37 |
| 5 | A number / amount | The object labelled with the number; a counter rolling up; a green-glow money label | Push-in; impact flash on a huge jump | "$ BILLIONS" 0:27; "$1 → $61M" 4:13 |
| 6 | A place + year | Establishing shot of the place; a calendar page for dates | Push-in / crane | "October, 2022" → calendar 4:33 |
| 7 | Travel / origin | **Paper map** with clouds, pins and characters on the map; plane arc | Zoom map → pan | Taiwan → USA 0:53-1:00 |
| 8 | Dialogue between two people | Two-shot in a real set; the speaker's mouth talks; expressions snap on the key word | Small push-in, cut between singles | Throughout |
| 9 | A phone call | Split screen with a phone cord | Static/slow push | Washington call 4:35 |
| 10 | A rule / list / what changed | Whiteboard or document filling with handwriting; strike-throughs | Magnifier zoom into the text | "BEST CHIPS: BLOCKED" 4:37-4:50 |
| 11 | Comparing values | A literal balance scale with props | Push-in | "One chip = ?" 5:03 |
| 12 | Becomes important / "holds the key" | Black void, spotlight, a glowing symbolic prop | Fast pull-out reveal | Golden key 4:18-4:22 |
| 13 | Analogy ("one chef vs 10,000 cooks") | The analogy acted out literally in its own set | Push-in | 3:03 |
| 14 | Crowd / everyone | Wide shot with many characters in rows | Push toward the main character | Denny's crowd 3:56 |
| 15 | Chapter ends | Black chapter card, 2.2 s | Static | 0:41, 4:28 |

## 4. Performance
- **Expression timing.** Expressions snap on the key word, not at shot start.
- **Talking.** The speaker's mouth talks (an oval opening) only while they speak. Listeners blink and react.
- **Body motion.**
  - Gestures are short: point, raise a glass, hold up a document, toast.
  - Small idle breathing and blinks.
  - Walks are simple leg swings with a slight bob.
- **Pop-ins.** Labels, stamps, props and characters pop in with a slight overshoot (0.15 s) and a pop SFX.

## 5. Rhythm of a chapter (from the 3 transcripts + parts 1 and 4)
1. Chapter card (2.2 s) + sting.
2. An establishing place shot + a date/calendar or a map.
3. Narration beats at one shot per 2.5-3 s, each with 1-2 pop-ins.
4. A dialogue skit every 30-75 s (two-shot ↔ close-ups).
5. A black text card on the chapter's sharpest line (about 1 per 20 s).
6. The chapter ends on a punchline beat, then 2-2.7 s of silence into the next chapter card.

## 6. Checking our render
1. Run `python3 analysis/motion30.py our.mp4 out [srt]`.
2. Compare it with the table in section 1: shot length 2.5-3 s, push-in about 70%, zoom 6-9%/s while moving, text cards about 1 per 20 s.
3. Look at `out_plot.png` and at the frame strips around every transition.
