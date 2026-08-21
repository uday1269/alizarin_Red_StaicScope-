"""
API Integration-Readiness Test Suite for StainScope Classical CV Engine.
Verifies:
1. POST /analyze with real valid ARS microscopy image
2. POST /analyze with invalid photograph
3. POST /analyze with non-ARS blue stain image
4. POST /analyze with blank image
5. Base64 overlay image decoding & PNG format validity
6. Nodule object structure (N1, N2, N3... IDs, centroids, bboxes, areas)
7. POST /analyze-batch comparative sample ranking
"""
import os
import io
import base64
import cv2
import numpy as np
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def verify_base64_decoding(b64_str: str, name: str) -> bool:
    """Verifies that a base64 data URI decodes into a valid openable image array."""
    assert b64_str.startswith("data:image/png;base64,"), f"{name} does not have standard data URI prefix"
    header, encoded = b64_str.split(",", 1)
    img_data = base64.b64decode(encoded)
    assert len(img_data) > 0, f"{name} decoded buffer is empty"
    
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    assert img is not None and img.size > 0, f"{name} failed to decode into valid OpenCV image"
    print(f"  ✓ {name} successfully decoded to image array shape {img.shape}")
    return True


def run_integration_readiness_test():
    print("==================================================")
    print("STARTING API INTEGRATION-READINESS VERIFICATION")
    print("==================================================")
    
    # -------------------------------------------------------------
    # Test 1: Real Valid ARS Microscopy Image
    # -------------------------------------------------------------
    ars_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
    assert os.path.exists(ars_path), f"Sample image not found at {ars_path}"
    
    with open(ars_path, "rb") as f:
        resp = client.post("/analyze", files={"file": ("ars_sample.tif", f, "image/tiff")})
        
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    
    assert data["valid"] is True, "Valid ARS image was incorrectly rejected"
    assert data["stain"]["status"] == "ARS-compatible"
    assert data["mineralization"]["area_percent"] > 0
    assert data["nodules"]["count"] == 8
    
    # Check nodule objects structure
    nodules = data["nodules"]["objects"]
    assert len(nodules) == 8
    for idx, n in enumerate(nodules, 1):
        assert n["id"] == f"N{idx}", f"Expected ID N{idx}, got {n['id']}"
        assert "centroid" in n and len(n["centroid"]) == 2
        assert "bbox" in n and len(n["bbox"]) == 4
        assert "area_pixels" in n and n["area_pixels"] > 0
        assert "confidence" in n
        
    print(f"\n1. Valid ARS Microscopy Image Test: PASSED")
    print(f"   - Valid: {data['valid']}")
    print(f"   - Stain Status: {data['stain']['status']}")
    print(f"   - Nodule Count: {data['nodules']['count']} (IDs: {[n['id'] for n in nodules]})")
    print(f"   - Area %: {data['mineralization']['area_percent']}%")
    print(f"   - Spatial Pattern: {data['pattern']}")
    
    # Verify base64 overlays decode back to valid images
    verify_base64_decoding(data["overlay"], "data.overlay")
    verify_base64_decoding(data["overlays"]["nodule_map"], "data.overlays.nodule_map")
    verify_base64_decoding(data["overlays"]["overlay"], "data.overlays.overlay")
    verify_base64_decoding(data["overlays"]["mask"], "data.overlays.mask")
    verify_base64_decoding(data["overlays"]["validation_panel"], "data.overlays.validation_panel")

    # -------------------------------------------------------------
    # Test 2: Invalid Normal Photograph (High channel std dev / non-microscopy)
    # -------------------------------------------------------------
    photo = np.zeros((400, 400, 3), dtype=np.uint8)
    photo[:, :, 0] = np.tile(np.linspace(0, 255, 400, dtype=np.uint8), (400, 1)) # B gradient
    photo[:, :, 2] = np.tile(np.linspace(255, 0, 400, dtype=np.uint8).reshape(400, 1), (1, 400)) # R gradient
    _, buf = cv2.imencode(".png", photo)
    
    resp_photo = client.post("/analyze", files={"file": ("photo.png", buf.tobytes(), "image/png")})
    assert resp_photo.status_code == 200
    data_photo = resp_photo.json()
    assert data_photo["valid"] is False, "Standard photo should be rejected"
    assert "mineralization" not in data_photo, "Rejection response must not contain mineralization keys"
    assert "nodules" not in data_photo, "Rejection response must not contain nodules keys"
    print(f"\n2. Invalid Normal Photograph Gate Test: PASSED")
    print(f"   - Valid: {data_photo['valid']}")
    print(f"   - Rejection Reason: {data_photo['reason']}")

    # -------------------------------------------------------------
    # Test 3: Non-ARS / Blue-Dominant Stain Image (e.g. DAPI)
    # -------------------------------------------------------------
    blue_img = np.ones((400, 400, 3), dtype=np.uint8) * 15
    blue_img[:, :, 0] = 220 # Strong Blue channel in BGR
    _, buf_blue = cv2.imencode(".png", blue_img)
    
    resp_blue = client.post("/analyze", files={"file": ("dapi.png", buf_blue.tobytes(), "image/png")})
    assert resp_blue.status_code == 200
    data_blue = resp_blue.json()
    assert data_blue["valid"] is False, "Blue dominant stain should be rejected"
    print(f"\n3. Incompatible Blue Stain Test: PASSED")
    print(f"   - Valid: {data_blue['valid']}")
    print(f"   - Rejection Reason: {data_blue['reason']}")

    # -------------------------------------------------------------
    # Test 4: Blank / Unusable Image
    # -------------------------------------------------------------
    blank = np.ones((400, 400, 3), dtype=np.uint8) * 128
    _, buf_blank = cv2.imencode(".png", blank)
    
    resp_blank = client.post("/analyze", files={"file": ("blank.png", buf_blank.tobytes(), "image/png")})
    assert resp_blank.status_code == 200
    data_blank = resp_blank.json()
    assert data_blank["valid"] is False, "Blank image should be rejected"
    print(f"\n4. Blank Image Gate Test: PASSED")
    print(f"   - Valid: {data_blank['valid']}")
    print(f"   - Rejection Reason: {data_blank['reason']}")

    # -------------------------------------------------------------
    # Test 5: POST /analyze-batch with Multiple Real ARS Images
    # -------------------------------------------------------------
    img1_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
    img2_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c5\C5_D28_4x_BF_01.tif"
    
    with open(img1_path, "rb") as f1, open(img2_path, "rb") as f2:
        files = [
            ("files", ("sample_c1.tif", f1, "image/tiff")),
            ("files", ("sample_c5.tif", f2, "image/tiff"))
        ]
        resp_batch = client.post("/analyze-batch", files=files)
        
    assert resp_batch.status_code == 200
    data_batch = resp_batch.json()
    assert "comparison_summary" in data_batch
    summary = data_batch["comparison_summary"]
    assert summary["total_samples"] == 2
    assert summary["valid_samples_count"] == 2
    ranked = summary["ranked_by_mineralization"]
    assert len(ranked) == 2
    assert ranked[0]["mineralized_area_percent"] >= ranked[1]["mineralized_area_percent"]
    
    print(f"\n5. Multi-Image Batch Analysis Test: PASSED")
    print(f"   - Total Samples: {summary['total_samples']}")
    print(f"   - Valid Samples: {summary['valid_samples_count']}")
    print(f"   - Ranked Samples Summary:")
    for s in ranked:
        print(f"     * {s['sample_id']}: Area % = {s['mineralized_area_percent']}%, Nodules = {s['nodule_count']}, Pattern = {s['spatial_pattern']}")

    print("\n==================================================")
    print("ALL API READINESS TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_integration_readiness_test()
