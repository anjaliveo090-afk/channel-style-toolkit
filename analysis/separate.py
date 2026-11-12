#!/usr/bin/env python3
"""Split a video's soundtrack into voice and "everything else" (music + SFX) with the
UVR MDX-Net Inst HQ3 model (ONNX, runs on CPU with onnxruntime, no torch).
Model: https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_HQ_3.onnx
Usage: separate.py video_or_audio model.onnx out_prefix  ->  out_prefix_inst.wav, out_prefix_voice.wav"""
import subprocess
import sys
import wave

import librosa
import numpy as np
import onnxruntime as ort

SR, NFFT, HOP, DIM_F, DIM_T = 44100, 6144, 1024, 3072, 256
CHUNK = HOP * (DIM_T - 1)
TRIM = NFFT // 2
GEN = CHUNK - 2 * TRIM


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def save(path, x):
    x = np.clip(x.T, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def spec(chunk):
    out = []
    for ch in chunk:
        s = librosa.stft(ch, n_fft=NFFT, hop_length=HOP, window="hann", center=True)[:DIM_F]
        out += [s.real, s.imag]
    return np.stack(out).astype(np.float32)


def unspec(x, length):
    chans = []
    for c in range(2):
        s = x[2 * c] + 1j * x[2 * c + 1]
        s = np.concatenate([s, np.zeros((NFFT // 2 + 1 - DIM_F, s.shape[1]))])
        chans.append(librosa.istft(s, n_fft=NFFT, hop_length=HOP, window="hann", center=True, length=length))
    return np.stack(chans)


def main(src, model, prefix):
    mix = load(src)
    n = mix.shape[1]
    pad = GEN - n % GEN
    padded = np.concatenate([np.zeros((2, TRIM)), mix, np.zeros((2, pad + TRIM))], 1)
    sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    out = []
    for i in range(0, n + pad, GEN):
        seg = padded[:, i:i + CHUNK]
        y = sess.run(None, {"input": spec(seg)[None]})[0][0]
        out.append(unspec(y, CHUNK)[:, TRIM:-TRIM])
        print(f"\r{min(100, int((i + GEN) / (n + pad) * 100))}%", end="", file=sys.stderr)
    inst = np.concatenate(out, 1)[:, :n] * 1.022
    save(prefix + "_inst.wav", inst)
    save(prefix + "_voice.wav", mix - inst)
    print(file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:4])
