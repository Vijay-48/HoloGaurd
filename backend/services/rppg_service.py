import cv2, numpy as np, time
import mediapipe as mp
from scipy.signal import butter, filtfilt

mp_face = mp.solutions.face_mesh.FaceMesh(static_image_mode=False)

class RPPGService:
    async def detect_physiological(self, frame_paths: list) -> dict:
        start = time.time()
        signals = []
        for fp in frame_paths[:: max(1, len(frame_paths)//30)]:
            img = cv2.imread(fp)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            res = mp_face.process(rgb)
            if not res.multi_face_landmarks: continue
            lm = res.multi_face_landmarks[0].landmark
            h, w, _ = rgb.shape
            pts = np.array([[lm[i].x*w, lm[i].y*h] for i in [10,338,297,332]], np.int32)
            mask = np.zeros(rgb.shape[:2], np.uint8)
            cv2.fillConvexPoly(mask, pts, 255)
            col = cv2.mean(rgb, mask=mask)[:3]
            signals.append(np.mean(col))
        if len(signals)<5:
            return {"prediction":"unknown","score":0.0,"processing_time": time.time()-start}
        sig = np.array(signals)
        b,a = butter(1, [0.75/30, 2.5/30], btype='band')
        filt = filtfilt(b,a,sig)
        power = float(np.var(filt))
        return {"prediction":"physio_present" if power>0.5 else "absent", "score":power, "processing_time": time.time()-start}
