import os, time
from PIL import Image
import numpy as np
import cv2

class ExplainService:
    async def explain_image(self, image_path: str, vision_result: dict) -> dict:
        # Grad-CAM or heatmap placeholder—you can integrate Captum or torchcam here
        return {"text_explanation": "Potential artifact detected on face edges", "heatmap_path": None}

    async def explain_video(self, video_path: str, scores: dict) -> dict:
        # Placeholder
        return {"text_explanation": "Temporal inconsistency detected", "heatmap_path": None}
