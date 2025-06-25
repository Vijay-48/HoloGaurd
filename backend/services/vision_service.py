import torch, time, cv2, numpy as np, logging
from pathlib import Path
import torchvision.transforms as T
from PIL import Image
from utils.config import get_settings
from utils.face_cropper import FaceCropper
from models.image_model import ImageDeepfakeModel
from models.video_model import VideoDeepfakeModel

settings = get_settings()
logger = logging.getLogger(__name__)

class VisionService:
    allowed_image_ext = settings.ALLOWED_IMAGE_EXTENSIONS
    allowed_video_ext = settings.ALLOWED_VIDEO_EXTENSIONS
    max_size = settings.MAX_FILE_SIZE

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.face_cropper = FaceCropper()
        self.image_model = ImageDeepfakeModel().to(self.device).eval()
        self.video_model = VideoDeepfakeModel().to(self.device).eval()
        self.transform = T.Compose([
            T.Resize((settings.TARGET_IMAGE_SIZE, settings.TARGET_IMAGE_SIZE)),
            T.ToTensor(),
            T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
        ])

        if Path(settings.VIT_MODEL_PATH).exists():
            self.image_model.load_state_dict(torch.load(settings.VIT_MODEL_PATH, map_location=self.device))
            logger.info("Loaded ViT weights")
        if Path(settings.TIMESFORMER_MODEL_PATH).exists():
            self.video_model.load_state_dict(torch.load(settings.TIMESFORMER_MODEL_PATH, map_location=self.device))
            logger.info("Loaded Video weights")

    async def detect_image(self, path: str) -> dict:
        start = time.time()
        face = self.face_cropper.crop(path)
        img = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
        x = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            prob = torch.sigmoid(self.image_model(x)).item()
        return {"prediction": "fake" if prob>0.5 else "real", "score": prob, "processing_time": time.time()-start}

    async def detect_image_array(self, arr: np.ndarray) -> dict:
        start = time.time()
        img = Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))
        x = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            prob = torch.sigmoid(self.image_model(x)).item()
        return {"prediction": "fake" if prob>0.5 else "real", "score": prob, "processing_time": time.time()-start}

    async def detect_video(self, frame_paths: list) -> dict:
        start = time.time()
        # sample CLIP_LENGTH frames uniformly
        idxs = np.linspace(0, len(frame_paths)-1, settings.CLIP_LENGTH, dtype=int)
        frames = [cv2.imread(frame_paths[i]) for i in idxs]
        clip = [self.transform(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))) for f in frames]
        x = torch.stack(clip, dim=1).unsqueeze(0).to(self.device)  # [1,3,T,H,W]
        with torch.no_grad():
            prob = torch.sigmoid(self.video_model(x)).item()
        return {"prediction": "fake" if prob>0.5 else "real", "score": prob, "processing_time": time.time()-start}
