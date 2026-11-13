# Master prompt: voiceover → video in the Paper Billions style

Open a new Claude Code chat on this repository. Attach the voiceover (MP3/WAV, under 30 MB) and its SRT. If you have the speaker-labelled script, attach it or put it in `scripts/`. Then paste:

```
I am attaching a voiceover and its SRT (and the script). Make a 16:9 animated video from it in exactly
this repository's style.

SETUP
- Run `bash setup.sh`, then copy assets/fonts/*.ttf to ~/.fonts and run fc-cache.
- Read and follow: CLAUDE.md, style_bible.md, visual_grammar.md (sections 1-3 and 12-15),
  sound_design.md, channel_breakdown.md.
- Code: animator/style.py (characters), places.py + places2.py (sets), devices.py (explaining devices),
  transitions.py, story.py (templates + engine), render16.py. Template story: animator/nvidia_ceo.py.

STEPS
1. Strip the TurboScribe line from the SRT. Run analysis/script_align.py to give every sentence its
   speaker, chapter and time.
2. Write animator/<story>.py: CAST (original characters, name tags for real people), BEATS (one device per
   phrase, a black text card every ~15-20 s, skits as `skit` beats), CHAPTER_MOOD.
3. List the beats; split any narrator beat over ~10 s. Render a grid of stills and fix anything cut off or empty.
4. Render: `audio`, then `part K 4` × 4 in parallel, then `concat 4`.
5. Measure against the targets:

   | Measure | Target |
   |---|---|
   | Shot length (motion30.py) | 2.5-3 s |
   | Animation events per 10 s (events.py) | 8-10 |
   | Music vs voice | −22 ± 2 dB |
   | SFX per 10 s | 5-7 |
   | SFX level vs voice | −15 to −18 dB |
   | Chapter pauses | 2.4 s (3.4 s after the cold open) |

6. Send me the mp4 and say honestly what fell outside the targets.
7. On fixes, patch only the beats I name and re-render only that part.
```

## Notes
- A ~13 min video takes about 30-45 min to render on 4 CPUs. Planning the beats takes longer the first time.
- To skip setup in every chat, put `bash setup.sh` in the cloud environment's setup script.
