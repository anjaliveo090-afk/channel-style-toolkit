# Sound design: Paper Billions (measured)

**Sources:**
- `analysis/audio_ref.py`: UVR MDX-Net separation into voice and music+SFX, then SFX detection, music key/tempo and levels.
- SRT gap analysis on all 3 videos (pauses).

**Coverage:** V1 parts 1 and 4 for music/SFX, all 3 videos for pauses. Raw data is in `analysis/ref_data/v1_part{1,4}_audio.json`. The frame at every SFX is in `output/ref/audio/v1_part1_sfx.png`.

## 1. Music
| What | Part 1 | Part 4 | Rule |
|---|---|---|---|
| Level vs voice | **−22.4 dB** | **−22.4 dB** | Music about x0.075 of the voice. Quiet, never competes |
| Key | A major (hook) → D minor (spy setup) → G# major (childhood backstory) | D# major (Denny's success) → A minor (MSS/spy) → D minor | **The music changes with the chapter's mood**: major for success, home and the past; minor for spies, government and danger |
| Tempo | about 105-110 (segments read 105-161, double-time) | about 110-125 | About 110 bpm, light |
| Density | 0.7-1.6 notes/s | 0.9-1.4 notes/s | Sparse plucks/keys |
| Drums | Percussive share 0.07-0.13 | 0.06-0.18 | Almost none |
| Shape | Swells into the chapter card (−27 dB at 0:41), then a new cue starts quietly | Swell at 4:28 (−35 dB), then quieter (−44 to −51) | **At every chapter card: a swell + hit, then a new cue for the new chapter** |

Our generator: `animator/audio.py` `music_ref()` (D minor) plus a major-key variant per chapter mood (see B2 notes in `CLAUDE.md`).

## 2. SFX
| What | Part 1 | Part 4 | Target |
|---|---|---|---|
| How many | 5.9 / 10 s | 6.2 / 10 s | **about 6 per 10 s** |
| Median loudness vs voice | −16.6 dB | −16.8 dB | **−15 to −18 dB** |
| On cuts | 35% | 19% | 20-35% (more than the old channel: hits land on cuts and card entrances) |
| Mix | pop/swish 46%, tick 39%, ding 9%, thud 7% | pop 35%, tick 44%, ding 6%, thud 15% | About 40% pop, 40% tick, 8% ding/sting, 12% thud |

### Where they land (from the frame at every SFX)
- **First frame of the video.** A heavy thud at −3 dB, the hook impact.
- **Name tag appears.** A pop at −17 dB.
- **Black text card.** A soft tick per typed letter (−20 to −27 dB), so the typing is heard.
- **A money label or glowing reveal.** A ding at −10 dB.
- **A stamp ("CHINA", "BLOCKED").** A thud at −6 dB.
- **Chapter card.** **The loudest hit of the section**: a ding/sting at +2 dB (part 1) or a thud at −2 dB (part 4), on top of the music swell.
- **Maps and travel.** Pops for pins and characters, a swish for the plane arc.
- **Documents and polaroids.** Ticks and pops as each element appears.
- **Impact flash / growth jumps.** A thud.

There are no whooshes on ordinary cuts. A whip-pan gets a short swish.

## 3. Pauses (from the SRTs of all 3 videos)
| Where | Measured | Rule for our assembly |
|---|---|---|
| Between sentences | Median 0.24-0.32 s (p90 0.45-0.58 s) | Keep the voice's own gaps |
| Inside a sentence | 0 s | — |
| After the cold open (hook → title/chapter card) | 2.6-4.5 s | **Insert about 3.5 s** of music + sting + chapter card if the voice has no gap |
| Chapter break | 2.1-2.7 s, every chapter | **Insert about 2.4 s** at each chapter break (card + sting) |
| Before a punchline reply / big reveal | 1.3-3.5 s ("Next question.", "$895 billion.") | Leave the gap the voice gives. If the script marks `[beat]`, insert 1.2 s |

## 4. Mix targets (check with `analysis/audio_ref.py final.mp4 subs.srt out`)
| Measure | Target |
|---|---|
| Music vs voice | −22 ± 2 dB |
| SFX per 10 s | 5-7 |
| SFX median vs voice | −15 to −18 dB |
| Loudest SFX | Chapter-card hit, −3 to +2 dB |
| SFX on cuts | 20-35% |
| Music key per chapter | Matches the chapter mood (major/minor) |
