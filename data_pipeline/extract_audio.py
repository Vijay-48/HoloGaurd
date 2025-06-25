#!/usr/bin/env python3
# data_pipeline/extract_audio.py
import os
import argparse
import subprocess
from pathlib import Path

def extract_audio(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    wav_path = os.path.join(output_dir, Path(video_path).stem + ".wav")
    subprocess.run([
        "ffmpeg", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        wav_path, "-y", "-loglevel", "error"
    ], check=True)
    return wav_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()
    for vid in Path(args.videos_dir).glob("*.mp4"):
        extract_audio(vid, args.output_dir)
    print("Audio extraction complete.")
