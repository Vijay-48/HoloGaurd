import librosa, numpy as np, time
from pathlib import Path
from utils.config import get_settings
from models.lip_model import SyncNetWrapper

settings = get_settings()

class LipSyncService:
    def __init__(self):
        self.model = SyncNetWrapper(Path(settings.SYNCNET_MODEL_PATH))

    async def detect_sync(self, frame_paths: list, audio_path: str) -> dict:
        start = time.time()
        y, sr = librosa.load(audio_path, sr=None)
        score = self.model.predict(frame_paths, y, sr)
        return {"prediction": "sync" if score>0.5 else "mismatch", "score": score, "processing_time": time.time()-start}
