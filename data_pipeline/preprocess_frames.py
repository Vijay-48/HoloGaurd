#!/usr/bin/env python3
# data_pipeline/preprocess_frames.py
import os
import cv2
import argparse
from pathlib import Path

def extract_and_augment(video_path, output_dir, fps=1, size=(224,224)):
    os.makedirs(output_dir, exist_ok=True)
    vidcap = cv2.VideoCapture(str(video_path))
    count = 0
    success, frame = vidcap.read()
    while success:
        if count % int(vidcap.get(cv2.CAP_PROP_FPS)//fps) == 0:
            frame_resized = cv2.resize(frame, size)
            out_path = os.path.join(output_dir, f"{Path(video_path).stem}_{count:05d}.jpg")
            cv2.imwrite(out_path, frame_resized)
        success, frame = vidcap.read()
        count += 1
    vidcap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--fps", type=int, default=1)
    args = parser.parse_args()
    for vid in Path(args.videos_dir).glob("*.mp4"):
        out = os.path.join(args.output_dir, vid.stem)
        extract_and_augment(vid, out, fps=args.fps)
    print("Done preprocessing frames.")
