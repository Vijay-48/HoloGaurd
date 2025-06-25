from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging, json, base64
from io import BytesIO
import cv2, numpy as np
from PIL import Image
from services.vision_service import VisionService

router = APIRouter(tags=["detect"])
logger = logging.getLogger(__name__)
vs = VisionService()

@router.websocket("/detect/stream")
async def stream_detect(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            if msg.get("type") == "frame":
                b64 = msg["data"].split(",")[1]
                img = Image.open(BytesIO(base64.b64decode(b64)))
                arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                res = await vs.detect_image_array(arr)
                await websocket.send_json({"frame_id": msg.get("frame_id"), **res})
    except WebSocketDisconnect:
        logger.info("Stream disconnected")
    except Exception as e:
        logger.error(f"Stream error: {e}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()
