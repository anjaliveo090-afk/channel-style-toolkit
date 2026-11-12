# Sound design: what the reference channel does (8 videos measured)

Source: the 8 reference videos the user uploaded:
- The Job Nobody Wants in Japan
- The Window That Breaks Japan's Gambling Law
- The Ancient Jar That Warned an Empire
- The Town Built Around a Button
- This Tree Hates You
- What the Grave Bell Really Meant
- Would You Upload Your Brain
- Your Brain's Secret Idea Zone

Raw numbers for every video, including each SFX with its time, kind, loudness and the line spoken, are in `analysis/ref_data/<name>.json`.

## How it was measured
1. **Split the soundtrack.** `analysis/separate.py` uses the UVR MDX-Net Inst HQ3 model (ONNX, CPU, about 35 s per video) to split each soundtrack into a voice stem and a music+SFX stem. The model is not in git; download it once into `analysis/models/` from https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_HQ_3.onnx
2. **Find the SFX and music.** `analysis/audio_ref.py video.mp4 [subs.srt] out_prefix` finds every SFX in the music+SFX stem, classifies it, and measures:
   - SFX loudness against the voice;
   - music loudness, key, tempo and drum share;
   - whether each SFX lands on a picture change.

   It also writes a spectrogram and a contact sheet showing the frame at each SFX.
3. **Check our own render.** Run the same command on our finished mp4 and compare it with the targets below.

Loudness is RMS in dB relative to the voice (0 dB = as loud as the narration).

## 1. Background music (same recipe in all 8 videos)

| What | Measured | Rule for our videos |
|---|---|---|
| Loudness | **−20 dB under the voice** (−19.7 to −22.0 in 7 of 8; one outlier at −7) | Music about x0.1 of the voice. With `animator/audio.py music_ref()` that is `--music-volume 0.4`; the old `music()` needs about 0.3 |
| Key | **D minor in 6 of 8**, E minor and A minor in the others | Always minor. Curious / mysterious, never sad, never happy-major |
| Tempo | Mostly 82-108 bpm (two read 144-161, which is double-time of the same feel) | About 96 bpm |
| Drums | Percussive share 0.05-0.26: almost none | No drum loop, no beat. Soft plucks only |
| Density | 1.3-2.3 notes per second | Sparse plucked notes with gaps |
| Tone | Mostly mid-range (200 Hz-2 kHz = 46-63% of energy), soft bass | Warm plucks/pizzicato over a soft sustained bass, nothing bright |
| Shape | Constant all video: no drop, no silence, no change of track between scenes | One bed from first frame to last, starting at 0 s, with a short swell and resolve at the very end |
| Story type | Same bed for funny, creepy and science topics: the tension in the video comes from the SFX, not the music | Do not change music per mood. Use `music_ref()` for every story |

Our generator: `animator/audio.py music_ref(total, swell_at)` (D minor, 96 bpm, sustained bass, sparse plucks, end swell). Measured in a test mix at `--music-volume 0.4`:
- music −19.4 dB under the voice;
- D minor;
- 1.9 notes/s;
- percussive share 0.04.

All four match the reference.

## 2. SFX: how many, how loud, what kind

| What | Measured (8 videos) | Rule |
|---|---|---|
| How many | **7-13.5 per 10 s, median ~10/10 s**: about **one every second**, nearly every 2-3 words | One SFX per visual event: every pop-in, expression snap, impact, counter tick, prop action |
| Length | Median 0.08-0.19 s | Short and dry. Nothing longer than ~0.5 s except the rare sting |
| Loudness | Median **−13 dB under the voice** (videos range −10 to −15.5); loud ones reach −2 to +6 dB | Most SFX sit well under the voice. Only big hits are as loud as the voice |
| Placement | Only 0-6% on picture cuts; landing on a visual change is no more likely than chance | **No transition whooshes.** SFX follow what happens inside the shot (a thing appears, hits, ticks, a face reacts), not the cut |

**Mix by kind** (all 8 videos, 465 SFX):

| Kind | Share | Loudness vs voice (median) | Used for | Our file |
|---|---|---|---|---|
| pop / snap / swish (short) | 41% | −12 dB | Something pops in, an expression snaps, an arm swings, a label appears | `pop.wav`, `boing.wav` (comic) |
| tick / click | 32% | −16 dB | Small motions, counter/number digits, clock ticks, footsteps, light switch, typing | `tick.wav`, `step.wav`, `page.wav` |
| thud / boom (low hit) | 14% | **−3 dB** (loudest) | Impact, door slam, stamp, emphasis word ("FIRE", "miserable", "gone"), ground crack | `thud.wav` |
| ding / chime / sting (tonal) | 11% | −9 dB | Realisation, reveal, money, magic glow, a "bad news" sting | `bell.wav`, `sparkle.wav`, `coin.wav`, `sting*.wav` |
| whoosh | 1-2% | −10 dB | Only for a physical thing flying (a jar thrown), never for the camera | `whoosh.wav`, rarely |

### Where the SFX land (from the frame at every SFX, `ref/*_sfx.png`)
- **On the hook word:** a thud/ding under the first symbol object ("FIRE" button at 0.5 s; "a man alive" in the coffin).
- **On the key noun of each phrase:** the moment its visual pops in (key, jar, bell, counter).
- **On every expression change:** a small pop (sweat drop, eyes widen, grin).
- **On every digit or number:** ticks on a counter (0046 → 0047), clock hands, the "1000" counter.
- **On physical actions:** footsteps = ticks, dig = thud, pressing a button = click + thud, glass lifted = tick.
- **On the punchline / twist word:** the loudest hit of the section ("making them miserable.", "fatal.", "He faked his death.").
- **On the last word of the video:** a ding/sting, often the loudest SFX of the video (+2 to +6 dB).

## 3. Defaults for every new video (Claude Code animator)
1. **Music:** `music_ref()` at `--music-volume 0.4` (−20 dB vs voice), one track for the whole video.
2. **SFX in each shot's script:** about one per second, put on visual events.
   - Kind mix: about 40% pop, 30% tick, 15% thud, 10% ding/sting, no camera whoosh.
   - Cue volumes inside the script: pop 0.6-0.8, tick 0.4-0.8, thud 0.8-1.0, bell/sting 0.5-0.8.
3. **Global SFX level:** scale all cues to **10%** before assembling. This is the user's setting, and it measures −12 to −13 dB under the voice, which matches the reference median.
4. **Check the mix:** run `python3 analysis/audio_ref.py final.mp4 captions.srt /tmp/check` and compare with the targets:

   | Measure | Target |
   |---|---|
   | Music vs voice | −20 ± 2 dB |
   | SFX per 10 s | about 7-12 |
   | SFX median vs voice | −11 to −15 dB |
   | SFX on cuts | under 15% |
