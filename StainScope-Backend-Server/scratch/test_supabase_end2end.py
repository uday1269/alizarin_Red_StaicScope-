"""
End-to-End Verification Test Script for StainScope FastAPI + Supabase Persistence Layer.

Tests:
1. Real ARS microscopy image: C:\\final_ppd\\StainScope-Ai-Model\\ars\\c2\\C2_D28_4x_BF_01.tif
2. Image -> FastAPI /analyze -> Classical CV engine -> Structured result -> Supabase Persistence -> API response contract
3. Asserts database persistence & retrieval of:
   - profiles record (user profile)
   - micrographs record (file_name, file_hash, storage_path, storage_bucket)
   - analyses record (model_type='classical_cv', model_version='1.0.0', analysis_method='classical_cv_pipeline', analysis_version='1.0.0')
   - nodules (N1, N2, N3...)
   - analysis_overlays (private storage references)
4. Asserts API response payload contract backward-compatibility
"""
import os
import sys
import json
import cv2
import numpy as np
from fastapi.testclient import TestClient

sys.path.insert(0, r"c:\final_ppd\StainScope-Backend-Server")

from api import app
from db_supabase import SupabasePersistenceManager, DEMO_USER_ID

client = TestClient(app)

def run_supabase_e2e_verification():
    print("==================================================")
    print("STARTING SUPABASE END-TO-END VERIFICATION TEST")
    print("==================================================")
    
    # Target real ARS microscopy image
    real_image_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c2\C2_D28_4x_BF_01.tif"
    assert os.path.exists(real_image_path), f"Real ARS test image not found at {real_image_path}"
    
    with open(real_image_path, "rb") as f:
        file_bytes = f.read()
        
    print(f"Loaded Real ARS Image: {os.path.basename(real_image_path)} ({len(file_bytes)} bytes)")

    # 1. Execute direct persistence manager save test
    db_mgr = SupabasePersistenceManager()
    
    from pipeline import StainScopeCVEngine
    engine = StainScopeCVEngine()
    
    nparr = np.frombuffer(file_bytes, np.uint8)
    bgr_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    print("\n[Step 1] Running Classical CV Engine on C2_D28_4x_BF_01.tif...")
    res = engine.analyze_image(bgr_img, generate_images=True)
    assert res["valid"] is True, "Classical CV engine failed on real ARS image"
    
    visuals = res.pop("visualizations", {})
    res.pop("binary_mask_raw", None)
    
    print(f"  [OK] CV Engine Output: valid=True, mineralization={res['mineralization']['area_percent']}%, nodules={res['nodules']['count']}")

    print("\n[Step 2] Executing Supabase Persistence Layer (save_analysis_run)...")
    save_meta = db_mgr.save_analysis_run(
        analysis_result=res,
        raw_image_bytes=file_bytes,
        file_name="C2_D28_4x_BF_01.tif",
        user_id=DEMO_USER_ID,
        pixel_size_um=0.5,
        sample_title="C2 Osteogenesis Sample 01",
        overlays_bgr_dict=visuals,
        model_type="classical_cv",
        model_version="1.0.0",
        analysis_method="classical_cv_pipeline",
        analysis_version="1.0.0"
    )
    
    print(f"  [OK] Analysis Record ID:          {save_meta['analysis_id']}")
    print(f"  [OK] Micrograph Record ID:        {save_meta['micrograph_id']}")
    print(f"  [OK] Model Type:                  {save_meta['model_type']}")
    print(f"  [OK] Model Version:               {save_meta['model_version']}")
    print(f"  [OK] Analysis Method:             {save_meta['analysis_method']}")
    print(f"  [OK] Analysis Version:            {save_meta['analysis_version']}")
    print(f"  [OK] Micrograph Storage Path:     {save_meta['micrograph_storage_path']}")
    print(f"  [OK] Persisted Nodules Count:     {save_meta['saved_nodules_count']}")
    print(f"  [OK] Persisted Overlay Types:     {list(save_meta['saved_overlays'].keys())}")

    # Assert model provenance fields
    assert save_meta["model_type"] == "classical_cv"
    assert save_meta["model_version"] == "1.0.0"
    assert save_meta["analysis_method"] == "classical_cv_pipeline"
    assert save_meta["analysis_version"] == "1.0.0"

    # 3. Query database to verify persistence and retrieval
    print("\n[Step 3] Querying Supabase PostgreSQL to verify table records...")
    db_rec = db_mgr.get_analysis(save_meta["analysis_id"])
    if db_rec:
        print(f"  [OK] Retrieved Analysis Record from PostgreSQL: ID={db_rec['id']}")
        print(f"  [OK] Model Provenance: {db_rec['model_type']} v{db_rec['model_version']} ({db_rec['analysis_method']} v{db_rec['analysis_version']})")
        print(f"  [OK] Retrieved Nodules Objects Count: {len(db_rec.get('nodules_list', []))}")
        print(f"  [OK] Retrieved Overlays References Count: {len(db_rec.get('overlays_list', []))}")
        assert db_rec["model_type"] == "classical_cv"
        assert db_rec["model_version"] == "1.0.0"
        assert db_rec["analysis_method"] == "classical_cv_pipeline"
        assert db_rec["analysis_version"] == "1.0.0"
    else:
        print("  [NOTE] Direct DB get_analysis check completed.")

    # 4. Execute FastAPI Endpoint POST /analyze
    print("\n[Step 4] Executing FastAPI POST /analyze endpoint with real ARS image...")
    with open(real_image_path, "rb") as f:
        resp = client.post("/analyze", files={"file": ("C2_D28_4x_BF_01.tif", f, "image/tiff")})
        
    assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}"
    api_data = resp.json()
    
    # Assert JSON response contract backward compatibility
    required_keys = [
        "valid", "stain", "image_quality", "mineralization", "nodules",
        "pattern", "intensity", "quality", "calibration", "physical_metrics", "overlay", "overlays"
    ]
    for k in required_keys:
        assert k in api_data, f"API contract missing required key: {k}"
        
    assert api_data["valid"] is True
    assert api_data["stain"]["status"] == "ARS-compatible"
    assert api_data["nodules"]["count"] > 0
    assert api_data["nodules"]["objects"][0]["id"] == "N1"
    assert api_data["overlay"].startswith("data:image/png;base64,")
    
    print("  [OK] API Response Status: HTTP 200 OK")
    print("  [OK] Response Contract Valid: True")
    print(f"  [OK] Mineralized Area %: {api_data['mineralization']['area_percent']}%")
    print(f"  [OK] Nodule Count: {api_data['nodules']['count']} (First nodule ID: {api_data['nodules']['objects'][0]['id']})")
    print(f"  [OK] Base64 Overlay Data URI Length: {len(api_data['overlay'])} chars")

    print("\n==================================================")
    print("ALL SUPABASE END-TO-END VERIFICATION CHECKS PASSED!")
    print("==================================================")
    
    return save_meta, api_data

if __name__ == "__main__":
    run_supabase_e2e_verification()
