from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import logging, tempfile, os
from pathlib import Path
from services.vision_service import VisionService
from services.fusion_service import FusionService
from services.explain_service import ExplainService
from api.deps import get_user
from models.schemas import DetectionResult

router = APIRouter(tags=["detect"])
logger = logging.getLogger(__name__)

@router.post("/detect/image", response_model=DetectionResult)
async def detect_image(
    file: UploadFile = File(...),
    explain: bool = False,
    user = Depends(get_user)
):
    ext = Path(file.filename).suffix.lower()
    vs = VisionService()
    if ext not in vs.allowed_image_ext:
        raise HTTPException(400, f"Invalid image type: {ext}")
    data = await file.read()
    if len(data) > vs.max_size:
        raise HTTPException(400, "File too large")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(data); tmp.close()
    try:
        vision = await vs.detect_image(tmp.name)
        fused = FusionService().fuse_scores({"vision": vision})
        explain_data = await ExplainService().explain_image(tmp.name, vision) if explain else {}
        return DetectionResult(
            overall_score=fused["overall_score"],
            overall_prediction=fused["overall_prediction"],
            confidence=fused["confidence"],
            vision_score=vision["score"],
            vision_prediction=vision["prediction"],
            audio_sync_score=None,
            physiological_score=None,
            explanation=explain_data.get("text_explanation", ""),
            heatmap_url=explain_data.get("heatmap_path"),
            processing_time=vision["processing_time"],
            model_version="1.0.0",
            file_type="image"
        )
    finally:
        os.unlink(tmp.name)
