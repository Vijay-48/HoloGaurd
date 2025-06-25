# tests/test_services.py
import pytest
import numpy as np
from services.vision_service import VisionService

vs = VisionService()

def test_detect_image_array():
    arr = np.zeros((224,224,3), dtype=np.uint8)
    res = pytest.run(asyncio.ensure_future(vs.detect_image_array(arr)))
    assert res["prediction"] in ("real","fake")
    assert 0.0 <= res["score"] <= 1.0
