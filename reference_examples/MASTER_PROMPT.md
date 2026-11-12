# Master prompt: new voice + SRT → same-style animated short

Open a new Claude Code chat on the repository `anjaliveo090-afk/my-project` (from any device: claude.ai/code or the Claude app → Code).
1. Attach your voiceover (mp3/wav) and the SRT.
2. Paste the text inside the box below.
3. Change the style line if you want the kings/medieval look.

```
I am attaching a voiceover and its SRT. Make a 9:16 animated short from it in exactly
the same style as my previous videos in this repository (latest example: the pachinko video).

SETUP
- Work on branch `claude/dazzling-hypatia-7p55ue`: fetch it and check it out first.
- Run `bash setup.sh` (installs packages, ffmpeg and the analysis model).
- Read these first and follow them strictly:
  CLAUDE.md, visual_grammar.md (all sections, especially 2, 10, 11), sound_design.md,
  style_bible.md, animator/README.md, assembler/README.md.
- Style: office/Japan look (style2.Char2 + office.py + arcade.py).
  [For kings/medieval instead: read style_medieval.md, use style3.py + medieval.py, template spear_shield2.py.]
- Template to copy: animator/speedrun2.py (newest: every line in a real place, the avatar dressed like the kid, game UI like a boss bar / loot chest / comments, render(fade_in=0) for a seamless loop) or animator/speedrun.py ( on-screen timer HUD, labels kept below it via shot top=250, loopable ending) or animator/mom_owner.py / animator/gambling.py (newest: literal visual per phrase, ~31 shots,
  SFX list at ~1 per second). Also see job_room.py and clock_tower2.py.
  Do not change engine.py / style2.py / style3.py unless something is broken.

STEP 1 - WORDS
- Strip any "(Transcribed by ...)" text from the SRT.
- Run `python3 analysis/align_words.py <voice> <subs.srt> output/<story_name>` for word timings.

STEP 2 - VISUAL PLAN
- Split the narration into phrases of 2-4 words.
- Tag each phrase with a rule from visual_grammar.md section 2 / 11.
- Show what is SAID, literally (an object for each noun, a counter for numbers, a diagram for
  explanations, a big X for "not / no", a face close-up for reactions).
- Aim for a new visual every ~1.5 s; the camera arrives on the key word.
- Safe zone: the WHOLE character and key props inside x 38-680, y 149-1013 (below y 678 only up to x 599).
  Call safezone.fit(SHOTS, sys.modules[__name__]) right before render() (animator/safezone.py).

STEP 3 - BUILD AND CHECK FRAMES
- Write animator/<story_name>.py (plus a new set module if new places are needed).
- Before the full render, draw one frame per shot into a contact sheet and look at it.
  Fix anything small, cut off, hidden or too dark.

STEP 4 - MY DEFAULTS
- No lip-sync, no captions, no camera whoosh.
- SFX cues scaled to 10%.
- Music: audio.music_ref() at --music-volume 0.4.
- Synthesised SFX and music only (animator/audio.py).

STEP 5 - MEASURE, THEN SEND
- analysis/new_visuals.py: a new visual every 1.5-2.6 s.
- analysis/flow.py on the animation: camera median of 4 or more.
- analysis/audio_ref.py on the final mp4:

  | Measure | Target |
  |---|---|
  | Music vs voice | -20 ± 2 dB |
  | SFX per 10 s | 7-12 |
  | SFX median vs voice | -11 to -15 dB |
  | SFX on cuts | under 15% |

- Send me the final mp4, and commit and push the code (output/ is git-ignored).
- Tell me honestly what could not match the reference.
- For fixes later: patch only the needed shots, never regenerate everything.
```

## Notes
- Everything (engine, characters, sets, rules, measured sound targets) lives on the branch
  `claude/dazzling-hypatia-7p55ue`. If it is merged into the default branch, the "check out
  the branch" line is no longer needed.
- The reference videos are not needed again. Their analysis is saved in:
  - `style_bible.md`
  - `visual_grammar.md`
  - `sound_design.md`
  - `analysis/ref_data/`
- To skip `setup.sh` in every new chat, paste `bash setup.sh` into the cloud environment's
  **Setup script** (session title bar → environment menu → Edit).
- A ~55 s video takes about 20-40 minutes in total: planning, drawing new scenes, a ~3-6 min
  render, then checks.
