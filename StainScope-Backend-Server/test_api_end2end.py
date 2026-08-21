"""
End-to-End API Integration Verification Test Script for StainScope Classical CV Engine.
Tests GET /health, POST /analyze with valid ARS image, invalid non-microscopy image,
incompatible DAPI blue image, and POST /analyze-batch.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import cv2
import numpy as np
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["engine"] == "StainScope Classical CV Engine"
    print("[OK] GET /health PASSED")


def test_analyze_valid_ars_image():
    img_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
    if not os.path.exists(img_path):
        pytest.skip(f"Test image not found at {img_path}")
        
    with open(img_path, "rb") as f:
        response = client.post("/analyze", files={"file": ("sample.tif", f, "image/tiff")})
        
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["stain"]["status"] == "ARS-compatible"
    assert data["mineralization"]["area_percent"] > 0
    assert data["nodules"]["count"] > 0
    assert "min" in data["nodules"]
    assert "max" in data["nodules"]
    assert "mean" in data["nodules"]
    assert "median" in data["nodules"]
    assert "pattern" in data
    assert "intensity" in data
    assert "overlay" in data
    assert data["overlay"].startswith("data:image/png;base64,")
    assert data["nodules"]["objects"][0]["id"] == "N1"
    
    print("[OK] POST /analyze (Valid ARS Image) PASSED")
    print(f"  -> Valid: {data['valid']}")
    print(f"  -> Mineralized Area %: {data['mineralization']['area_percent']}%")
    print(f"  -> Nodule Count: {data['nodules']['count']}")
    print(f"  -> Pattern: {data['pattern']}")
    print(f"  -> Overlay Base64 Len: {len(data['overlay'])} chars")


def test_analyze_invalid_blank_image():
    blank = np.ones((300, 400, 3), dtype=np.uint8) * 128
    _, buf = cv2.imencode(".png", blank)
    
    response = client.post("/analyze", files={"file": ("blank.png", buf.tobytes(), "image/png")})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "reason" in data
    print("[OK] POST /analyze (Invalid Blank Image Rejection) PASSED")
    print(f"  -> Rejection Reason: {data['reason']}")


def test_analyze_incompatible_blue_stain():
    blue_img = np.ones((300, 400, 3), dtype=np.uint8) * 20
    blue_img[:, :, 0] = 230 # High B channel in BGR
    _, buf = cv2.imencode(".png", blue_img)
    
    response = client.post("/analyze", files={"file": ("dapi_blue.png", buf.tobytes(), "image/png")})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "blue-dominant" in data["reason"] or "incompatible" in data["reason"]
    print("[OK] POST /analyze (Incompatible Blue Stain Rejection) PASSED")
    print(f"  -> Rejection Reason: {data['reason']}")


def test_analyze_batch():
    img1_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
    img2_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c5\C5_D28_4x_BF_01.tif"
    
    with open(img1_path, "rb") as f1, open(img2_path, "rb") as f2:
        files = [
            ("files", ("sample1.tif", f1, "image/tiff")),
            ("files", ("sample2.tif", f2, "image/tiff"))
        ]
        response = client.post("/analyze-batch", files=files)
        
    assert response.status_code == 200
    data = response.json()
    assert "comparison_summary" in data
    assert data["comparison_summary"]["total_samples"] == 2
    assert len(data["comparison_summary"]["ranked_by_mineralization"]) == 2
    print("[OK] POST /analyze-batch PASSED")
    print(f"  -> Ranked Samples: {data['comparison_summary']['ranked_by_mineralization']}")


if __name__ == "__main__":
    test_health_endpoint()
    test_analyze_valid_ars_image()
    test_analyze_invalid_blank_image()
    test_analyze_incompatible_blue_stain()
    test_analyze_batch()
    print("\nALL END-TO-END API INTEGRATION TESTS PASSED SUCCESSFULLY!")
