#!/usr/bin/env bash
# One-time setup for a fresh machine/cloud session: Python packages + ffmpeg,
# and the voice/music separation model (only needed to analyse new reference videos).
set -e
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg libcairo2-dev pkg-config)
pip install -q -r requirements.txt
mkdir -p analysis/models
[ -f analysis/models/UVR-MDX-NET-Inst_HQ_3.onnx ] || curl -sSL -o analysis/models/UVR-MDX-NET-Inst_HQ_3.onnx \
  https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_HQ_3.onnx
python3 -c "import cairo, cv2, librosa, onnxruntime, pocketsphinx; print('setup ok')"
