#!/usr/bin/env bash
# Render some parts of a story at 4K 30 fps, in parallel (one wave).
#   bash render_wave.sh <story_module> <N_parts> K1 K2 K3 K4
# Run each wave as its own background command (a wave of 4 x 65 s parts takes ~45-50 min on 4 CPUs).
# 4 workers fit in 15 GB because story.py encodes with -threads 4 -rc-lookahead 20.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
story=$1; n=$2; shift 2
export PB_SCALE=${PB_SCALE:-3} PB_FPS=${PB_FPS:-30}
date
for k in "$@"; do python3 "animator/$story.py" part "$k" "$n" & done
wait
date
echo "oom kills so far: $(dmesg 2>/dev/null | grep -c 'Killed process' || true)"
