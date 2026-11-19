# Toby (3D) — notes
- Built with the 3d-animator skill (.claude/skills/3d-animator). three.js scene, every frame a pure function of t.
- Timing: timeline.json is exported from the 2D story engine (animator/toby_noob.py beats), so shots land on the
  same words and the 2D mix (output/toby/mix.wav: voice + music + SFX) lines up unchanged.
- 1280x720, 24 fps, n=6 sub-frames (software GL in the cloud container: ~2.2 s/frame single, ~9 s/frame x4 parallel).
- Render: 4 chunks of 352 frames (`node render.mjs --video --fps=24 --n=6 --from=A --to=B`), concat, mux mix.wav.
- Re-render one shot: find its beat t0/t1 in timeline.json, render that range, splice it in. Audio never moves.
- No camera shake inside the film (skill rule): impact words get a pop label / stamp instead.
