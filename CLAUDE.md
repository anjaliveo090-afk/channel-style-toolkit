# Paper Billions style toolkit: workflow for a new voiceover

This repo turns a voiceover (+ its script) into a 16:9 animated money-story video in the measured style of the
reference channel. The look, pace and sound targets live in:
- `style_bible.md`: characters, faces, palette, sets, graphics;
- `visual_grammar.md`: pace and camera numbers, sentence → device rules (sections 12-15 are frame-by-frame);
- `sound_design.md`: music, SFX and pause targets;
- `channel_breakdown.md`: topics, title formulas T1-T3, script formulas S1-S3.

Copy the STYLE only. Never use the reference channel's characters, logos, on-screen text, script lines or audio.
Real people appear only as simple original cartoon figures identified by name tags; quotes must be real and sourced.

## When the user sends a voiceover + SRT (+ the script)
1. **Align words to the script.**
   - Strip the TurboScribe watermark from the SRT.
   - Run `python3 analysis/script_align.py voice.srt scripts/<story>_blocks.txt output/<story>/align.json`. It gives every sentence its speaker, chapter and time.
   - If there is no labelled script, use `analysis/align_words.py` and label the speakers by hand.
2. **Plan the shots** with `visual_grammar.md` sections 3, 13 and 15:
   - one device per phrase;
   - a new framing on every sentence;
   - a black text card about every 15-20 s on punchlines;
   - skits as `skit` beats (the camera cuts to the speaker line by line, and only the speaker's mouth talks).
3. **Build `animator/<story>.py`** from `animator/nvidia_ceo.py`:
   - CAST: original characters from `style.Char`;
   - BEATS: sentence index → template;
   - CHAPTER_MOOD.

   Templates are in `animator/story.py`: card, skit, scene, tag, board, calendar, tower, stock, news, filing, checklist, zero, tv, dinner, cork, map, stage, void, letter, email, label. Places are in `places.py` / `places2.py`; devices in `devices.py`; transitions in `transitions.py`.
4. **Check frames:**
   - Run `python3 animator/<story>.py beats` to list the beats. No narrator beat should be over ~10 s; split long ones.
   - Run `python3 animator/<story>.py still T1 T2 …` and look at a grid of stills.
   - Fix anything cut off, empty or wrong.
   - A 9:16 Short uses the safe zone in `animator/safezone.py`.
5. **Render and assemble:**
   - `python3 animator/<story>.py audio` builds the mix: the voice with chapter pauses inserted (3.4 s after chapter 1, 2.4 s at the others), chapter-mood music at −21.5 dB, and template SFX.
   - Then run `part K 4` × 4 in parallel.
   - Then `concat 4`.
6. **Measure:**
   - `analysis/motion30.py`: shot length 2.5-3 s; push-in about 70%.
   - `analysis/events.py`: 8-10 animations per 10 s.
   - `analysis/audio_ref.py`: music −22 ± 2 dB; SFX 5-7 / 10 s at −15 to −18 dB. Note that audio_ref under-counts our dense SFX.
7. **Send the mp4** plus a short note on anything outside the targets.
8. **On fix requests,** patch only the beats the user names, re-render only the affected part, and re-concat.

## Defaults
- 16:9, 1280x720, 24 fps.
- No captions. Speaker-only mouth movement, no lip-sync to phonemes. No whoosh on ordinary cuts; a whip-pan gets a swish.
- Placeholder voice for tests only: `espeak-ng` + mbrola (robotic). Real videos use the user's voiceover.

## Setup
Run `bash setup.sh`. It installs packages, ffmpeg and the UVR separation model. The fonts are in `assets/fonts`; copy them to `~/.fonts` and run `fc-cache`.
