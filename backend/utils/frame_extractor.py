import cv2, tempfile, os

class FrameExtractor:
    async def extract_frames(self, video_path: str) -> dict:
        cap = cv2.VideoCapture(video_path)
        frames, temp_files = [], []
        while True:
            ret, frame = cap.read()
            if not ret: break
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            cv2.imwrite(tmp.name, frame)
            temp_files.append(tmp.name)
            frames.append(tmp.name)
        cap.release()
        return {"frames": frames, "temp_files": temp_files}

    async def extract_audio(self, video_path: str) -> str:
        wav_path = video_path + ".wav"
        os.system(f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {wav_path} -y -loglevel panic")
        return wav_path
