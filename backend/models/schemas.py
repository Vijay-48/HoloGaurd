from pydantic import BaseModel
from typing import Optional

class DetectionResult(BaseModel):
    overall_score: float
    overall_prediction: str
    confidence: float
    vision_score: float
    vision_prediction: str
    audio_sync_score: Optional[float]
    physiological_score: Optional[float]
    explanation: Optional[str]
    heatmap_url: Optional[str]
    processing_time: float
    model_version: str
    file_type: str
