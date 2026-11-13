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

## 12. Line-by-line log (V1 parts 1 and 4; frames at start, middle and end of every sentence)
Sheets: `output/ref/cues/v1_part{1,4}_*.jpg`, made by `analysis/cue_sheets.py` with `references/srt/*_sentences.srt`.

| Time | Sentence | What is shown (the device) |
|---|---|---|
| 0:00 | "In Singapore, the boss … having dinner with a Chinese spy." | Two-shot at the dinner, then a whip to a world map with glowing chip pins, then a **black text card** typing the punch phrase |
| 0:06 | "He's Jensen Huang, who runs NVIDIA." | Big close-up laughing, raising a fork; the **name tag types on** |
| 0:08 | "She's Alice Huang, no relation…" | Whip-pan to her close-up + name tag; back to the two-shot; a **"VIP CUSTOMER" sign** pops on the table |
| 0:13 | "But here's the strange part." | Push out through the restaurant window into the rainy street (**camera leaves the room**) |
| 0:15 | "…agents are taking pictures." | Dark street, two agents with a long lens; **polaroids pop in one by one with a camera flash each** |
| 0:18 | "They know exactly who she is." | Corkboard file; a **hand draws a red circle** around her photo |
| 0:20 | "Jensen has no idea." | **Black text card** |
| 0:22-0:25 | "To our customers!" / "To friends." | Two-shot toast; the **speaker's mouth talks**, glasses clink |
| 0:25 | "Under that table…billions of dollars of his chips" | Under-the-table view: a glowing green chip passed across, a **money counter label** above it ("$23,…" → "$ BILLIONS") |
| 0:29 | "The kind China isn't allowed to have." | **Black text card** |
| 0:32 | "This is the story of how China got a spy into that seat" | **Top-down seating plan**; a red **CHINA star stamp** lands on her seat |
| 0:35 | "…and who was watching." | **Viewfinder** through the window (REC, crosshair), shutter flash |
| 0:37 | "It starts with a phone call from Washington." | Night desk with a rotary phone; the **title** types onto the desk scene, then the chapter card |
| 0:44 | "…who picked it up…the man in the leather jacket" | Push through skyscraper windows (**zoom-through**) to a desk, then a dark door |
| 0:50 | "He started in a bathroom in Kentucky." | **Black text card** |
| 0:53 | "Jensen's story begins in Taiwan." | **Paper map**: zoom to Taiwan, which turns orange; a pin drops with a label |
| 0:55-1:04 | "At nine…put on a plane…parents sold almost everything" | Kids appear on the map with an "AGE 9" label; **plane arc** across the Pacific to the USA (USA highlighted); living room where the parents hand over an envelope marked "SCHOOL" (the TV says "BREAKING NEWS") |
| 1:04 | "Oneida Baptist Institute, a boarding school in Kentucky." | Porch at sunset, suitcases; a **brochure with a picture** hangs in the air |
| 1:08-1:10 | "Very strict." / "Strict is good." | Single shots of each speaker; the brochure is pointed at |
| 1:11 | "It wasn't a fancy boarding school." | Top-down desk: brochure; a **magnifying glass reveals the fine print "FOR TROUBLED BOYS"** |
| 1:13 | "It was a reform school…signed them up by mistake." | **Black text card**, then a **checkbox form**: "REFORM PROGRAM ☑" |
| 3:53 | "It calls it the booth that launched a $1 trillion company." | Diner exterior, neon sign, the **plaque** close-up |
| 3:56 | "…put on an apron, balanced 10 plates…" | Crowded diner; he holds a stack of plates, and a **"10 PLATES" counter** pops |
| 4:02-4:03 | "Still remember how?" / "Dishes first." | **Callback set**: the same dish station as his teenage job, now with the old him |
| 4:04 | "Two years later, NVIDIA became…$5 trillion." | **Black text card** (a long line, typed left-aligned) |
| 4:10 | "Every dollar…had become about $8 billion." | The booth table: a **green counter box "$1 FROM EVERY $1"** rolls up while a **money tower** grows out of the booth; **impact flash**; "$8 BILLION" |
| 4:14 | "The kid who scrubbed the toilets…" | Bathroom stalls, the kid with a mop; then **black card** "now holds the key to artificial intelligence." |
| 4:20 | "…who should be allowed to buy his chips, Washington listens." | A glowing **golden key** in a black void, a **fast pull-out** to him on a platform, a **podium in front of a domed government building** with listeners |
| 4:24-4:28 | "Every AI lab on Earth needs this man." / "Then so do we." | Dark blue corridor: a man on a stepladder pins **his photo** to the wall; a second man reacts |
| 4:28 | "That made him the one man China needed most." | **Black text card** + chapter card ("The Locked Door") |
| 4:33 | "October 2022, Washington calls NVIDIA." | **Calendar** (AUG → SEP, **page flip**); a **map with a dotted route line** Santa Clara ↔ Washington |
| 4:37-4:44 | The phone call dialogue | **Split screen**: night government office | bright tech office, a phone cord across the divider; a **"A YEAR LATER" sticky label** slides down; **"BLOCKED" stamp** on a document |
| 4:45 | "$17 billion a year, 13% of everything we sell." | **Whiteboard handwriting appears as the words are said**; a pie chart showing 13% |
| 4:50 | "Was." | Back to the split screen; the whiteboard line is **struck through** |
| 4:51-5:02 | "How many chips…? Tens of thousands. …$30,000. A new car per chip." | Corridor between server racks: **rack lights switch on in sequence**, a **counter label "10,000s"** rolls; a **balance scale**: a chip on one pan, a toy **car** on the other, with a price tag |
| 5:02 | "And how many can we buy?" / "Zero." | Clipboard close-up via a **circular lens wipe** |
| 5:03 | "NVIDIA's share of China's market went from 95% to zero." | **Pie on a plate with a "95%" tag**, then an **empty plate** |
| 5:09 | "And he told Washington so every chance he got." | Spotlight on stage, then a **TV interview set with a "LIVE" bug** |

## 13. Explaining devices (concept → picture), the core of the style
**Rule: every sentence shows its meaning literally.** If the sentence has a noun, show that object. If it has a number, show the number on an object in the scene. If it has an idea, show a physical metaphor. Skits keep the set and cut between the speakers.

| Concept in the line | Device | Code |
|---|---|---|
| A person is introduced | Close-up + **name tag (box, then the name types on)** | `sets.name_tag` |
| Money / amount | **Green counter box** that rolls up; dollar labels with a glow; a money tower for growth | `devices.counter_box`, `sets.contract_doc` |
| A big jump or growth | Counter rolls + **impact flash** + the object grows | `sets.impact_flash` |
| Market share / a part of a whole | **Pie / cake slice with a % tag**; "to zero" = **empty plate** | `devices.pie_plate` |
| Comparing values ("a new car per chip") | **Balance scale** with both objects | `devices.balance_scale` |
| A rule, a list, what changed | **Whiteboard / document handwriting** in sync with the words; **strike-through** when it stops being true; **"BLOCKED"/"APPROVED" stamp** | `places.whiteboard`, `devices.stamp`, `devices.strike` |
| A hidden truth / fine print | **Magnifying glass** reveals small text | `transitions.magnifier` |
| A decision on paper / a mistake | **Form with a checkbox** that ticks | `devices.checkbox_form` |
| Being watched / evidence | **Viewfinder** + **polaroids with a flash**; a **corkboard** with a **hand-drawn red circle** | `transitions.viewfinder`, `transitions.polaroid`, `devices.marker_circle` |
| "Into that seat" / position, who sits where | **Top-down seating plan**, **stamp** on a seat | `devices.stamp` |
| Time passes | **Sticky label slides in** ("A YEAR LATER"); **calendar page flip**; "Two years later" black card | `devices.sticky_label`, `transitions.page_flip` |
| Place / journey / origin | **Paper map**: highlight a region, pin drop, plane arc or dotted route | `sets.paper_map`, `sets.map_pin`, `devices.route_arc` |
| Power / importance ("holds the key") | **Glowing symbolic prop** in a black void + **fast pull-out** | `places.void_spotlight`, `transitions.pull_out` |
| Two sides talking | **Split screen** + phone cord | `transitions.split_screen` |
| Counting / quantity | **Things switch on or pop in one by one** (rack lights, plates), plus a counter label | `devices.counter_box` |
| Punchline / thesis / irony / chapter end | **Black text card** typed with the line (about 1 per 15-20 s) | `sets.text_card` |
| Callback to the past | **Reuse the exact earlier set**, with the character older | — |
| Public statements | **TV interview set with a LIVE bug** / podium | `devices.live_tv` |

## 14. Animation timing (measured frame by frame, `output/ref/motion/entrances.png`)
| Element | How it moves | Duration |
|---|---|---|
| Name tag | The box fades in (2 frames), then letters type on at about 1 per frame | about 0.5 s |
| Black text card | Letters type on | about 16 letters/s |
| Polaroids | Each drops in with a **white camera flash** over the whole frame | about 0.15 s apart |
| Red marker circle | A hand with a marker slides in and the stroke grows around the target | about 0.5 s |
| Sticky label | Slides down from the top edge and settles | about 0.2 s |
| Counter | Digits step up (slow at first, then faster), ending on the round number | 0.6-1.2 s |
| Pop-in props/labels | Scale 0 → 1.1 → 1.0 | about 0.15 s |
| Rack lights / counted things | Switch on in sequence | about 0.03 s apart |
| Expression change | Snaps in 1 frame on the key word | — |
| Mouth (speaker only) | Opens and closes every 2-3 frames while talking | — |
| Camera | Cuts between speakers line by line in skits; push-ins ease-out; a pull-out reveal about 1.4 s | — |

## 15. Every-frame pass (all 4,193 frames of V1 parts 1 and 4)
Notes: `references/frame_notes_v1_part1.md` and `references/frame_notes_v1_part4.md`. Sheets with animated frames outlined: `output/ref/allframes/`. Detector: `analysis/events.py`.

| Measure | Part 1 | Part 4 | Target |
|---|---|---|---|
| Animation events inside shots per 10 s | 9.5 | 8.6 | **8-10** |
| Frames with nothing moving | 22% | 21% | about 20% (mostly black cards) |
| Longest stretch without animation | 3.8 s | 5.5 s (card) | under 4 s outside cards |
| Median animation event | 0.29 s | 0.37 s | 0.3-0.4 s |

Rules added by this pass:
1. **Animated light everywhere:** candle flicker, rain, flickering windows, searchlights, lamps clicking on, lens flares, glints sweeping across signs.
2. **The camera travels between scenes physically** (out through a window, down under a table, through a light tunnel, a rip/tear through the wall) about as often as it cuts.
3. **Text is always typed.** Long black-card lines are small and left-aligned.
4. **"Everything" or lists are shown one item at a time** (map beams, furniture sold with price tags, polaroids, plates, rack lights).
5. **Places fill with colour** (Taiwan orange, the USA blue); routes draw as dotted arcs.
6. **Writing happens live** with a visible marker hand; the board scrolls.
7. **Numbers grow physically** (a cash tower with a counter), peak with a speed-line burst, and spill particles.
8. **Props always enter with motion** (slide, drop with a bounce, fly in).
9. **Zero:** a circled and slashed 0, or an empty plate with crumbs.
10. **Rip/tear transition** for "became" moments.
