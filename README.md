# Channel style toolkit (Paper Billions look)

This repo turns a voiceover + script into a 16:9 animated "money story" video. The style is measured frame by frame on the reference channel, and the cartoon is drawn in code (pycairo).

## What is in the repo
- `channel_breakdown.md`: niche, why the videos work, title formulas T1-T3, script formulas S1-S3.
- `style_bible.md`, `visual_grammar.md`, `sound_design.md`: the measured style, pace, camera and sound.
- `analysis/`: tools for measuring a video:
  - `frame_log.py`, `motion30.py`, `events.py`, `audio_ref.py`, `script_align.py`, `script_stats.py`.
- `animator/`: drawing and rendering:
  - characters `style.py`, sets `places*.py`, devices `devices.py`, `transitions.py`;
  - engine `story.py`; sample stories `sample*.py` and `nvidia_ceo.py`.
- `scripts/`: written scripts. `references/`: reference transcripts, SRTs and frame notes (the videos themselves are not in git).

## Opening message for a new chat
> I am attaching a voiceover and its SRT. Run bash setup.sh, then read MASTER_PROMPT.md and follow the prompt inside it exactly.

## Limits
- 2D code animation. The reference look is matched in construction, palette, camera and timing, not pixel-identical.
- Analysed so far: V1 parts 1 and 4 (about 2.6 min) as video, plus the transcripts of all three reference videos.
