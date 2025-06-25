from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
import logging, tempfile, os, asyncio
from pathlib import Path
from services.vision_service import VisionService
from services.lip_sync_service import LipSyncService
from services.rppg_service import RPPGService
from services.fusion_service import FusionService
from services.explain_service import ExplainService
from utils.frame_extractor import FrameExtractor
from api.deps import get_user
from models.schemas import DetectionResult

router = APIRouter(tags=["detect"])
logger = logging.getLogger(__name__)

@router.post("/detect/video", response_model=DetectionResult)
async def detect_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    explain: bool = False,
    user = Depends(get_user)
):
    ext = Path(file.filename).suffix.lower()
    vs = VisionService()
    if ext not in vs.allowed_video_ext:
        raise HTTPException(400, f"Invalid video type: {ext}")
    data = await file.read()
    if len(data) > vs.max_size:
        raise HTTPException(400, "Video too large")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(data); tmp.close()

    try:
        fe = FrameExtractor()
        frames_info = await fe.extract_frames(tmp.name)
        audio_path = await fe.extract_audio(tmp.name)

        vsvc, lsvc, rsvc = VisionService(), LipSyncService(), RPPGService()
        tasks = [
            vsvc.detect_video(frames_info["frames"]),
            lsvc.detect_sync(frames_info["frames"], audio_path),
            rsvc.detect_physiological(frames_info["frames"])
        ]
        vision, lip, rppg = await asyncio.gather(*tasks)
        fused = FusionService().fuse_scores({"vision": vision, "lip_sync": lip, "physiological": rppg})
        explain_data = await ExplainService().explain_video(tmp.name, {"vision": vision, "lip_sync": lip, "physiological": rppg}) if explain else {}

        background_tasks.add_task(lambda paths: [os.unlink(p) for p in paths], [tmp.name, audio_path] + frames_info["temp_files"])

        return DetectionResult(
            overall_score=fused["overall_score"],
            overall_prediction=fused["overall_prediction"],
            confidence=fused["confidence"],
            vision_score=vision["score"], vision_prediction=vision["prediction"],
            audio_sync_score=lip["score"], physiological_score=rppg["score"],
            explanation=explain_data.get("text_explanation", ""),
            heatmap_url=explain_data.get("heatmap_path"),
            processing_time=vision["processing_time"] + lip["processing_time"] + rppg["processing_time"],
            model_version="1.0.0", file_type="video"
        )
    finally:
        # cleanup in case of exception
        [os.unlink(p) for p in [tmp.name, audio_path] + frames_info.get("temp_files", []) if os.path.exists(p)]
