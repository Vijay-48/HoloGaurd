import cv2, mediapipe as mp, numpy as np

class FaceCropper:
    def __init__(self):
        self.face = mp.solutions.face_mesh.FaceMesh(static_image_mode=True)

    def crop(self, image_path: str) -> np.ndarray:
        img = cv2.imread(image_path)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = self.face.process(rgb)
        if not res.multi_face_landmarks:
            return img
        lm = res.multi_face_landmarks[0].landmark
        h, w, _ = img.shape
        xs = [pt.x*w for pt in lm]; ys = [pt.y*h for pt in lm]
        x1, x2 = int(min(xs)), int(max(xs))
        y1, y2 = int(min(ys)), int(max(ys))
        return img[y1:y2, x1:x2]
