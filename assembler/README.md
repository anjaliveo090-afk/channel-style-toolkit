# Assembler

Joins Flow clips, your voiceover and an SRT into a 9:16 short with crossfades, word-by-word captions and SFX.

Needs `ffmpeg` and `ffprobe` on PATH, and Python 3.

## Folder layout
```
my_video/
  clips/        clip01.mp4, clip02.mp4, ... (sorted by name)
  voice.wav     your voiceover
  script.srt    captions timing (line level is fine, words are split evenly)
  sfx/          whoosh.wav, clock_tick.wav, ...
  cues.json     see sfx_cues.example.json
```

## Run
```bash
python3 assembler/assemble.py --clips my_video/clips --voice my_video/voice.wav \
  --srt my_video/script.srt --sfx my_video/cues.json --sfx-dir my_video/sfx \
  --transition-sfx my_video/sfx/whoosh.wav --out final.mp4
```

Options: `--xfade 0.4` (crossfade seconds), `--words 2` (words per caption), `--music bg.mp3` (looped, low volume), `--font Arial`.

## Notes
- Output: 720x1280, 30 fps, H.264 + AAC.
- If clips are shorter than the voiceover, the last frame is held. If longer, the video is trimmed to the voiceover.
- Each clip must be longer than twice the crossfade.
- Captions: bold white, black outline, about 70% down the frame.
- Get the voiceover SRT from the voice track (CapCut auto-captions or any transcription tool) so word timing matches your voice.
