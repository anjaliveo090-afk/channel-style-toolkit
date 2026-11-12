# Project: reference-style animated shorts

When the user gives a voiceover, SRT or script, follow this workflow without being asked.

1. Read `style_bible.md` (the analysed look of the 3 reference videos: format, characters, face reactions, camera, pacing, STYLE LOCK, CLIP TEMPLATE) and `visual_grammar.md` (measured camera numbers and the sentence-type → shot rules). Tag every sentence with a rule from `visual_grammar.md` section 2 before designing shots.
2. If only audio is given, get an SRT first (ask the user for CapCut auto-captions, or transcribe with a speech-to-text tool if installed).
3. Run `python3 assembler/plan_clips.py <srt>` to split the narration into 10 s clips with speed and SFX hints.
4. For each clip write a detailed prompt: STYLE LOCK + characters + 3-4 timed shots (camera move, action, face reaction, soft cross-dissolve). Keep the same character looks across clips. Give Image-mode prompts for each character and location so the user can use them as Flow Ingredients.
5. Give an SFX cue sheet per clip, following `sound_design.md` (measured on 8 reference videos: ~1 SFX per second on visual events, mostly pops/ticks, thuds on impacts and punchlines, ding on reveals, no camera whoosh; music one minor-key bed at -20 dB under the voice), as `sfx_cues.example.json` format.
6. After the user generates clips in Flow (9:16, Omni, 10 s) and saves them, assemble with `assembler/assemble.py` (see `assembler/README.md`).
7. If the user shares a generated frame, compare it with the Style Bible and fix the prompt.

Without Flow: `animator/` draws the whole video in code (`clock_tower2.py` is the model to copy: keyframed camera, a new framing every 2-4 words landing on the key word, see `visual_grammar.md` section 10) (see `animator/README.md`); use it when the user wants Claude Code to make the video itself. Use `style2.Char2` characters (the user's reference style). Call `ref_camera()` on the shot list, give each shot a `focus` on the main subject's face (keeps it centred, clear of captions and the Subscribe button), add `dof` and vary angles (`back_figure`, `dutch`), aim for a new visual every ~2 s, give each shot a `speaker` and pass the voice so mouths lip-sync, then check pace with `analysis/flow.py` (sections 8-9 of `visual_grammar.md`).

Second style (kings / medieval / war look): read `style_medieval.md` and use `animator/style3.py` + `animator/medieval.py` instead of style2/office.

Safe zone (animator, every video): the whole character must sit inside x 38-680, y 149-1013 (below y 678 only up to x 599). Call `safezone.fit(SHOTS, sys.modules[__name__])` right before `render()` (see `animator/safezone.py`, template `mom_owner.py`), add `keep=[...]` boxes for key props, and look at a contact sheet with the zone drawn.

Sound defaults (animator): music `audio.music_ref()` mixed with `--music-volume 0.4`, SFX cues scaled to 10%, no whoosh; check with `analysis/audio_ref.py final.mp4 srt out` against `sound_design.md` section 3. Pace check: `analysis/new_visuals.py` (reference: a new visual every 1.5-2.6 s) and `analysis/flow.py`.

New reference videos: run `analysis/frame_log.py` (4 fps sheets with subtitles), `analysis/audio_ref.py` (SFX + music, needs the UVR model in `analysis/models/`, see `sound_design.md`) and `analysis/new_visuals.py`, then add what you learn to `visual_grammar.md` section 11 and `sound_design.md`.

Limits to state honestly: Claude Code cannot generate the AI video; Flow's Omni does. Face consistency needs Ingredients images. Do not copy the reference channel's characters or SFX files, only the style.

New style (different characters / look) in a new repo: follow `NEW_STYLE_GUIDE.md` and `MASTER_PROMPT_NEW_STYLE.md`.
