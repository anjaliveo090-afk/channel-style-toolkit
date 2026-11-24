#!/usr/bin/env bash
# Join parts 0..N-1, add the mix, check the frame count, split into files under 400 MiB.
#   bash finish.sh <out_dir> <N_parts> <final_name>
set -euo pipefail
out=$1; n=$2; name=$3
cd "$out"
: > parts.txt
for ((k = 0; k < n; k++)); do echo "file 'part$k.mp4'" >> parts.txt; done
ffmpeg -v error -y -f concat -safe 0 -i parts.txt -c copy video.mp4
ffmpeg -v error -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest "$name.mp4"
ffprobe -v error -select_streams v -show_entries stream=width,height,r_frame_rate,nb_frames -of csv=p=0 video.mp4
size=$(stat -c %s "$name.mp4"); dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$name.mp4")
pieces=$(( size / (360 * 1048576) + 1 ))
seg=$(python3 -c "print(int(float('$dur') / $pieces) + 2)")
mkdir -p final
ffmpeg -v error -y -i "$name.mp4" -map 0 -c copy -f segment -segment_time "$seg" -reset_timestamps 1 \
  -segment_start_number 1 "final/${name}_part%d_of_${pieces}.mp4"
for f in final/*.mp4; do echo "$f $(( $(stat -c %s "$f") / 1048576 )) MiB"; done
