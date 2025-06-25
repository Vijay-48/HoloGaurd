# tests/test_utils.py
import pytest
from utils.frame_extractor import FrameExtractor

@pytest.mark.asyncio
async def test_frame_extraction(tmp_path):
    # create a tiny video
    import cv2, numpy as np
    path = tmp_path/"vid.mp4"
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 1, (100,100))
    for _ in range(3):
        out.write(np.zeros((100,100,3), np.uint8))
    out.release()
    fe = FrameExtractor()
    data = await fe.extract_frames(str(path))
    assert len(data["frames"]) == 3
