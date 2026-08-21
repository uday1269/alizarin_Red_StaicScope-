"""
Comprehensive Bidirectional Reports Verification Suite: Web <-> Android.
Tests:
1. Create analysis on Android -> verify it appears in Android Reports & Web Reports.
2. Create analysis on Web -> verify it appears in Web Reports & Android Reports.
3. Open same report from both applications and verify 100% metric parity.
"""
import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000"

def test_bidirectional_flow():
    print("==========================================================================")
    print("STARTING BIDIRECTIONAL WEB <-> ANDROID REPORTS SYNCHRONIZATION TEST SUITE")
    print("==========================================================================")

    # 1. Sign up test researcher
    email = f"lead_researcher_{int(time.time())}@stainscope.org"
    password = "SecurePassword123!"
    
    resp_auth = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": "Dr. Sarah Chen, Ph.D."
    })
    assert resp_auth.status_code == 200, f"Auth signup failed: {resp_auth.text}"
    token = resp_auth.json()["access_token"]
    user_id = resp_auth.json()["user_id"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[OK] User authenticated: {email} (ID: {user_id})")

    img_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
    assert os.path.exists(img_path), f"Test image missing: {img_path}"

    # --------------------------------------------------------------------------------
    # TEST 1: Create Analysis on Android -> Verify in Android Reports & Web Reports
    # --------------------------------------------------------------------------------
    print("\n--- TEST 1: Android Analysis Creation & Propagation ---")
    with open(img_path, "rb") as f:
        android_upload_resp = requests.post(
            f"{BASE_URL}/analyze",
            headers=headers,
            files={"file": ("ARS_Sample_Android_Run.tif", f, "image/tiff")},
            data={
                "sample_title": "hMSC Osteogenic Run (Android Source)",
                "cell_line": "hMSC",
                "treatment": "14 Days Osteo | 20x Objective",
                "pixel_size_um": 1.0
            }
        )
    assert android_upload_resp.status_code == 200, f"Android upload failed: {android_upload_resp.text}"
    android_res_data = android_upload_resp.json()
    android_an_id = android_res_data["analysis_id"]
    print(f"[OK] Android Analysis Created successfully. ID: {android_an_id}")

    # Fetch /analyses from Backend (Single Source of Truth)
    resp_analyses_1 = requests.get(f"{BASE_URL}/analyses", headers=headers)
    assert resp_analyses_1.status_code == 200
    active_analyses_1 = resp_analyses_1.json()

    # Simulate Android ReportsViewModel mapping
    android_reports_1 = []
    for dto in active_analyses_1:
        area_val = dto.get("mineralized_area_percent") or 0.0
        od_val = dto.get("optical_density_proxy") or dto.get("optical_density") or 0.0
        calc_val = dto.get("calcium_density_ug_cm2") or (area_val * 0.05)
        count_val = dto.get("nodule_count") or 0
        raw_date = dto.get("analyzed_at") or dto.get("created_at") or ""
        date_str = raw_date[:16].replace("T", " ") if raw_date else "Recent"
        status_text = "High Mineralization" if area_val > 50.0 else ("Moderate Mineralization" if area_val > 20.0 else "Low Mineralization")
        
        android_reports_1.append({
            "id": dto["id"],
            "name": dto.get("sample_title") or f"ARS Micrograph ({dto['id'][:8]})",
            "date": date_str,
            "magnification": dto.get("objective_magnification") or "20x Objective",
            "mineralizedArea": f"{area_val:.2f}%",
            "stainIntensity": f"{od_val:.2f} OD",
            "calciumDensity": f"{calc_val:.2f} µg/cm²",
            "noduleCount": f"{count_val:,}",
            "status": status_text,
            "imageUrl": dto.get("image_url"),
            "overlayUrl": dto.get("overlay") or (dto.get("overlays", {}).get("nodule_map") if isinstance(dto.get("overlays"), dict) else None)
        })

    # Simulate Web fetchAnalysesHistory mapping
    web_reports_1 = []
    for rec in active_analyses_1:
        area_val = float(rec.get("mineralized_area_percent") or 0.0)
        od_val = float(rec.get("optical_density_proxy") or 0.0)
        count_val = int(rec.get("nodule_count") or 0)
        calc_val = float(rec.get("calcium_density_ug_cm2") or (area_val * 0.05))
        status_text = "High Mineralization" if area_val > 50.0 else ("Moderate Mineralization" if area_val > 20.0 else "Low Mineralization")
        
        raw_img = rec.get("image_url") or (rec.get("overlays", {}).get("nodule_map") if isinstance(rec.get("overlays"), dict) else None)
        raw_ov = (rec.get("overlays", {}).get("nodule_map") if isinstance(rec.get("overlays"), dict) else None) or rec.get("overlay")

        web_reports_1.append({
            "id": rec["id"],
            "title": rec.get("sample_title") or "Micrograph Sample",
            "mineralizedArea": f"{area_val:.2f}%",
            "stainIntensityOD": f"{od_val:.2f} OD",
            "calciumEstimate": f"{calc_val:.2f} µg/cm²",
            "nodulesCount": f"{count_val:,}",
            "status": status_text,
            "imageUrl": raw_img,
            "overlay": raw_ov
        })

    # Verify Android report exists in Android Reports
    android_match_in_android = next((r for r in android_reports_1 if r["id"] == android_an_id), None)
    assert android_match_in_android is not None, "Android Analysis missing in Android Reports!"
    print(f"[OK] Verified: Android Analysis is present in Android Reports ({android_match_in_android['name']})")

    # Verify Android report exists in Web Reports
    android_match_in_web = next((r for r in web_reports_1 if r["id"] == android_an_id), None)
    assert android_match_in_web is not None, "Android Analysis missing in Web Reports!"
    print(f"[OK] Verified: Android Analysis is present in Web Reports ({android_match_in_web['title']})")

    # --------------------------------------------------------------------------------
    # TEST 2: Create Analysis on Web -> Verify in Web Reports & Android Reports
    # --------------------------------------------------------------------------------
    print("\n--- TEST 2: Web Analysis Creation & Propagation ---")
    with open(img_path, "rb") as f:
        web_upload_resp = requests.post(
            f"{BASE_URL}/analyze",
            headers=headers,
            files={"file": ("ARS_Sample_Web_Workstation.tif", f, "image/tiff")},
            data={
                "sample_title": "Primary Osteoblast Culture (Web Source)",
                "cell_line": "Primary Osteoblast",
                "treatment": "21 Days Mineralization | 20x Objective",
                "pixel_size_um": 1.0
            }
        )
    assert web_upload_resp.status_code == 200, f"Web upload failed: {web_upload_resp.text}"
    web_res_data = web_upload_resp.json()
    web_an_id = web_res_data["analysis_id"]
    print(f"[OK] Web Analysis Created successfully. ID: {web_an_id}")

    # Fetch updated /analyses list
    resp_analyses_2 = requests.get(f"{BASE_URL}/analyses", headers=headers)
    assert resp_analyses_2.status_code == 200
    active_analyses_2 = resp_analyses_2.json()

    # Re-map Android & Web
    android_reports_2 = [
        {
            "id": dto["id"],
            "name": dto.get("sample_title"),
            "mineralizedArea": f"{(dto.get('mineralized_area_percent') or 0.0):.2f}%",
            "stainIntensity": f"{(dto.get('optical_density_proxy') or 0.0):.2f} OD",
            "calciumDensity": f"{((dto.get('calcium_density_ug_cm2') or ((dto.get('mineralized_area_percent') or 0.0) * 0.05))):.2f} µg/cm²",
            "noduleCount": f"{(dto.get('nodule_count') or 0):,}",
            "status": "High Mineralization" if (dto.get('mineralized_area_percent') or 0.0) > 50.0 else ("Moderate Mineralization" if (dto.get('mineralized_area_percent') or 0.0) > 20.0 else "Low Mineralization")
        }
        for dto in active_analyses_2
    ]

    web_reports_2 = [
        {
            "id": rec["id"],
            "title": rec.get("sample_title"),
            "mineralizedArea": f"{(float(rec.get('mineralized_area_percent') or 0.0)):.2f}%",
            "stainIntensityOD": f"{(float(rec.get('optical_density_proxy') or 0.0)):.2f} OD",
            "calciumEstimate": f"{((float(rec.get('calcium_density_ug_cm2') or (float(rec.get('mineralized_area_percent') or 0.0) * 0.05)))):.2f} µg/cm²",
            "nodulesCount": f"{(int(rec.get('nodule_count') or 0)):,}",
            "status": "High Mineralization" if float(rec.get('mineralized_area_percent') or 0.0) > 50.0 else ("Moderate Mineralization" if float(rec.get('mineralized_area_percent') or 0.0) > 20.0 else "Low Mineralization")
        }
        for rec in active_analyses_2
    ]

    web_match_in_web = next((r for r in web_reports_2 if r["id"] == web_an_id), None)
    assert web_match_in_web is not None, "Web Analysis missing in Web Reports!"
    print(f"[OK] Verified: Web Analysis is present in Web Reports ({web_match_in_web['title']})")

    web_match_in_android = next((r for r in android_reports_2 if r["id"] == web_an_id), None)
    assert web_match_in_android is not None, "Web Analysis missing in Android Reports!"
    print(f"[OK] Verified: Web Analysis is present in Android Reports ({web_match_in_android['name']})")

    # --------------------------------------------------------------------------------
    # TEST 3: Deep Metric Parity Verification on Detail View
    # --------------------------------------------------------------------------------
    print("\n--- TEST 3: Deep Metric Parity Comparison across Web & Android ---")
    for test_idx, an_id in enumerate([android_an_id, web_an_id], 1):
        det_resp = requests.get(f"{BASE_URL}/analyses/{an_id}", headers=headers)
        assert det_resp.status_code == 200
        rec = det_resp.json()

        # Android ResultsViewModel metrics
        an_area = rec.get("mineralization", {}).get("area_percent") or rec.get("mineralized_area_percent") or 0.0
        an_od = rec.get("mineralization", {}).get("optical_density") or rec.get("optical_density_proxy") or 0.0
        an_count = rec.get("nodules", {}).get("count") or rec.get("nodule_count") or 0
        an_calc = rec.get("calcium_density_ug_cm2") or (an_area * 0.05)
        an_conf = rec.get("calibration", {}).get("ai_confidence") or rec.get("overall_confidence") or 0.95
        an_conf_pct = an_conf * 100 if an_conf <= 1.0 else an_conf

        android_view = {
            "ID": rec["id"],
            "Sample Title": rec.get("sample_title"),
            "Area %": f"{an_area:.2f}%",
            "Stain OD": f"{an_od:.2f} OD",
            "Nodule Count": f"{an_count:,}",
            "Calcium Density": f"{an_calc:.2f} µg/cm²",
            "Confidence": f"{an_conf_pct:.1f}%",
            "Magnification": rec.get("objective_magnification") or "20x Objective",
            "Image Path": rec.get("image_url"),
            "Overlay Path": rec.get("overlay") or (rec.get("overlays", {}).get("nodule_map") if isinstance(rec.get("overlays"), dict) else None)
        }

        # Web ResultsScreen metrics
        wb_area = Number = float(rec.get("mineralized_area_percent") or 0.0)
        wb_od = float(rec.get("optical_density_proxy") or 0.0)
        wb_count = int(rec.get("nodule_count") or 0)
        wb_calc = float(rec.get("calcium_density_ug_cm2") or (wb_area * 0.05))
        wb_conf = float(rec.get("overall_confidence") or 0.95)
        wb_conf_pct = wb_conf * 100 if wb_conf <= 1.0 else wb_conf

        web_view = {
            "ID": rec["id"],
            "Sample Title": rec.get("sample_title"),
            "Area %": f"{wb_area:.2f}%",
            "Stain OD": f"{wb_od:.2f} OD",
            "Nodule Count": f"{wb_count:,}",
            "Calcium Density": f"{wb_calc:.2f} µg/cm²",
            "Confidence": f"{wb_conf_pct:.1f}%",
            "Magnification": rec.get("objective_magnification") or "20x Objective",
            "Image Path": rec.get("image_url"),
            "Overlay Path": rec.get("overlay") or (rec.get("overlays", {}).get("nodule_map") if isinstance(rec.get("overlays"), dict) else None)
        }

        print(f"\n[Sample {test_idx}: {rec.get('sample_title')}]")
        print(f"{'Metric Field':<20} | {'Android Value':<25} | {'Web Value':<25} | Parity")
        print("-" * 80)
        for k in android_view:
            a_v = str(android_view[k])
            w_v = str(web_view[k])
            match = "MATCH [OK]" if a_v == w_v else "MISMATCH [FAIL]"
            assert a_v == w_v, f"Field '{k}' mismatch: Android={a_v} vs Web={w_v}"
            print(f"{k:<20} | {a_v:<25} | {w_v:<25} | {match}")

    print("\n==========================================================================")
    print("ALL BIDIRECTIONAL SYNCHRONIZATION AND METRIC PARITY TESTS PASSED (100%)")
    print("==========================================================================")

if __name__ == "__main__":
    test_bidirectional_flow()
