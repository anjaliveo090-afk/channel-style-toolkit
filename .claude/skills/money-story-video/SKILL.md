---
name: money-story-video
description: Make a complete animated "money story" YouTube video in this repo's measured reference style (2D cartoon, AI / tech / Wall Street news) - trending topic, title, script, voiceover alignment, shot plan, 4K render, thumbnail and SEO. Use when the user asks for a new video of this kind, any single step of it (topic, title, script, thumbnail, SEO, render), or sends a voiceover + SRT.
---

# Money-story video, end to end

The user talks Hinglish (Roman Hindi). Reply in Hinglish; write titles, scripts, on-screen text, thumbnail text and SEO in English, like the references.
Copy the reference channel's STYLE only: never its characters, logos, titles, script lines, on-screen text, thumbnail drawings or audio. Real people appear only as simple original cartoon figures with name tags; quotes must be real and sourced.

Read before working: `CLAUDE.md` (render workflow), `channel_breakdown.md` (title formulas T1-T3, script formulas S1-S3), `visual_grammar.md`, `sound_design.md`, `thumbnail_bible.md`. The finished example to copy from is `animator/nvidia_ceo.py` + `scripts/spy_brought_down_nvidia_ceo_*`.

Stop and wait for the user at every step marked **[WAIT]**. Do not skip ahead.

## 1. Topic [WAIT]
- WebSearch (mode extended), several queries in one turn: this week's tech / AI / markets news, stock moves, earnings, IPOs.
- Give 3-5 topics in the niche. For each: what happened, the one shocking number, a title idea, and which facts are confirmed by a primary source (SEC filing, company release, Reuters / AP / CNBC / NYT) vs. only a newsletter or blog.
- Recommend one. List all source URLs at the end.

## 2. Title [WAIT]
- 6-8 options under 60 characters, grouped by formula: T1 "How a [villain] [did X to] [famous company]", T2 "Why the [famous thing] Just [verb]", T3 paradox "[superlative / good thing] ... [lost / still fell] $[number]".
- The number in the title must come from a primary source. Recommend one and say what the thumbnail text would be.
- Never reuse a reference channel title word for word.

## 3. Script [WAIT]
- Research the facts first (WebSearch extended). Use only facts you found; mark single-source facts.
- Formula: cold open with the paradox + the number in the first 10 s → chapters (each with one plain-English analogy) → "why" chapter → "what it means for you" (with "this isn't advice") → verdict that calls back to the opening.
- Narrator-only if the user asks; otherwise add short skits (2-8 lines, a dry punchline) as in the Nvidia script.
- Write numbers as spoken ("one hundred and fifteen point eight billion dollars"). ~150 words per minute.
- Save two files in `scripts/`:
  - `<story>_blocks.txt`: header lines `TITLE:`, `FORMAT:`, `VOICE NOTES:`, then `[CHAPTER n: NAME]` blocks, `SPEAKER: text` lines, `[beat]` between chapters (this exact format feeds `analysis/script_align.py`);
  - `<story>_VOICE.txt`: only the spoken words, for the voiceover.
- Report: word count, minutes, chapter list, and a "check before publishing" list of the weaker facts. Commit + push.

## 4. Voiceover + SRT arrive → align
- Strip the TurboScribe watermark line from the SRT.
- `python3 analysis/script_align.py voice.srt scripts/<story>_blocks.txt output/<story>/align.json`, copy the mp3 to `output/<story>/voice.mp3`.

## 5. Shot plan: `animator/<story>.py` (copy `animator/nvidia_ceo.py`)
Set `ALIGN`, `VOICE`, `OUT`, `TITLE` (+ `TITLE_REDACT` for a word that reveals on the title card), `CHAPTER_MOOD`, `CAST`, `REACTORS`, `BEATS`.
The rules that made the Nvidia video engaging (the user rejected the earlier "slide" version as boring):
- **People doing things in real places, never a document on a flat colour.** Prefer `scene` beats: a place (`places.py` / `places2.py`) + 1-3 characters with arms / items / expressions + an `ov` label that pops on the spoken word + an `sfx` list.
- **A new picture every ~2.5 s.** Use word-anchored beats `{"at": i, "word": "..."}` to cut mid-sentence. Device beats (filing, stock, map, calendar, board, tv...) are auto-intercut with REACTORS cutaways; keep them short.
- **Motion inside every shot:** walk-ins (`x` as a lambda + `walk_phase`), people who appear / vanish (`show` + `D.puff`), `story.falling_bills`, `stopwatch`, `bell`, `clock`, `heart`, name plates that pop and fall (`D.nameplate`), `ceo_chair`, `D.cash_tower`, `D.counter_box`.
- **Impact words slam:** `slam` template (close-up + big stamp + camera kick, optional cross-out) or `"shake": [words]` on a scene.
- Hook (first ~60 s) is the most important: time tag typing on ("THURSDAY MORNING"), a flashback (`"sepia": True`), stamps, something that falls or vanishes, the number on screen.
- A black `card` on punchlines about every 15-20 s; skits as `skit` beats (camera cuts to the speaker each line).
- Every label must be on a word that is actually spoken in that beat (`b.wt(word)`), or it never appears.
- `python3 animator/<story>.py beats` (no narrator beat over ~8 s), then render stills of every beat in 4 parallel `still` calls, tile them into grids and LOOK at them. Fix overlaps (labels over faces), cut-off heads, empty frames.

## 6. Sample [WAIT]
- `python3 animator/<story>.py audio` (mix.wav).
- Render a 10 s sample at 4K 30 fps (4 processes × 2.5 s with `PB_SCALE=3 PB_FPS=30`), mux with the matching 10 s of mix.wav, send it. Full render only after the user approves.

## 7. Full render (4K 30 fps)
- 12 parts, waves of 4, each wave as its own background Bash command (a background command is killed after 2 h; one wave takes ~45-50 min):
  `bash .claude/skills/money-story-video/tools/render_wave.sh <story> 12 0 1 2 3`, then `4 5 6 7`, then `8 9 10 11`.
- Never run more than 4 at once (8 GB+ of x264 at 4K → OOM kill). After each wave check `oom kills` and the part durations.
- To re-render only one stretch, render part K of 48 (4 sub-parts of a part of 12 cover the same frames) into another folder and build the concat list by hand.
- `bash .claude/skills/money-story-video/tools/finish.sh output/<story> 12 <final_name>` → frame count check + `final/<name>_partX_of_Y.mp4` under ~360 MiB each (the file-send limit is 400 MiB).
- Measure: `analysis/events.py` and `analysis/motion30.py` on the final file. Targets: shot median 2.5-3 s, animation 8-10 / 10 s, still frames ~22 %, longest stillness under ~4 s outside cards, push-in ~70 %.
- Send the parts with an honest note on what is outside the targets.

## 8. Fix requests
Patch only the beats the user names. If the changes stay inside one part, re-render that part, re-concat, re-split and send only the changed file. If new SFX change the mix, splice the new mix into the old one at the end of the changed stretch so the other parts' audio stays identical.

## 9. Thumbnail
- Follow `thumbnail_bible.md` (measured on the 4 reference thumbnails): one top line (white hook + red `-$` number, black stroke + shadow, drawn after the vignette), one huge sweating face turned to one glowing green prop with rays and fragments, dark hard-blurred background with warm bokeh.
- Text: `python3 animator/thumbnail.py out.png "ONE EMAIL." "-$428 BILLION"`; change the prop / expression / background inside `main()` of `animator/thumbnail.py`. Run it, LOOK at the PNG, fix, send PNG + JPG (1280x720, under 2 MB).

## 10. SEO
- Save `scripts/<story>_SEO.md` (template: `scripts/spy_brought_down_nvidia_ceo_SEO.md`): 3 title options, description (2 short paragraphs + chapters + sources line + "nobody has been charged" type disclaimers where they apply + 3 hashtags), tags under 500 characters, pinned comment, upload settings.
- Chapter times: `python3 .claude/skills/money-story-video/tools/chapters.py <story>`.
- Captions: `output/<story>/final.srt` (written by the `audio` step).
- Say which tags are untested for search volume and which facts to re-check.

## Always
- Commit and push after each step (branch given by the session); end commit messages with the session's attribution lines.
- Keep a task list; a step is done only when its output was checked (frames looked at, durations and frame counts verified).
- Be honest about limits: 2D code-drawn animation matches the reference's construction, palette, camera and timing, not its painted thumbnails or every frame.
