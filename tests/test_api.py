# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def token():
    # sign up & get token
    resp = client.post("/auth/signup", json={"username":"test","password":"test123"})
    assert resp.status_code == 200
    resp = client.post("/auth/token", data={"username":"test","password":"test123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_image_detect(token):
    with open("tests/sample_real.jpg", "rb") as f:
        resp = client.post("/detect/image", files={"file":("sample.jpg",f,"image/jpeg")}, headers={"Authorization":f"Bearer {token}"})
    assert resp.status_code == 200
    j = resp.json()
    assert "overall_score" in j

def test_history(token):
    resp = client.get("/history/", headers={"Authorization":f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
