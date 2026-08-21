import os
import sys
import cv2
import json
import time
import requests
import datetime
import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline import StainScopeCVEngine
from db_mysql import JWT_SECRET, JWT_ALGORITHM

engine = StainScopeCVEngine()

print("=" * 70)
print("1. TEST REAL ARS DATASET IMAGE (StainScope-Ai-Model/ars)")
print("=" * 70)
ars_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_03.tif"
if not os.path.exists(ars_path):
    import glob
    tifs = glob.glob(r"c:\final_ppd\StainScope-Ai-Model\ars\*\*.tif")
    ars_path = tifs[0] if tifs else None

if ars_path and os.path.exists(ars_path):
    bgr_ars = cv2.imread(ars_path)
    t0 = time.time()
    res_ars = engine.analyze_image(bgr_ars)
    t_ars = time.time() - t0
    print("File:", os.path.basename(ars_path))
    print("Valid:", res_ars.get("valid"))
    print("Stain Status:", res_ars.get("stain", {}).get("status"))
    print("Mineralized Area %:", f"{res_ars.get('mineralization', {}).get('area_percent')}%")
    print("Mineralized Pixels:", res_ars.get("mineralization", {}).get("area_pixels"))
    print("Nodule Count:", res_ars.get("nodules", {}).get("count"))
    print("Mean Nodule Size:", f"{res_ars.get('nodules', {}).get('mean_size_pixels')} px")
    print("Median Nodule Size:", f"{res_ars.get('nodules', {}).get('median_size_pixels')} px")
    print("Spatial Pattern:", res_ars.get("mineralization", {}).get("spatial_pattern"))
    print("Optical Density:", res_ars.get("mineralization", {}).get("optical_density"))
    print("Visualizations Generated:", list(res_ars.get("visualizations", {}).keys()))
    print(f"Processing Time: {t_ars:.3f}s")

print("\n" + "=" * 70)
print("2. TEST PREVIOUSLY WORKING SAMPLE IMAGE")
print("=" * 70)
prev_path = r"c:\final_ppd\StainScope-Backend-Server\storage\micrographs\ddd21a1a-c3e9-4aa0-9027-fa4927b06b2e\b8a3ecc0-2da3-4053-ac3b-42e2cb1369b4\images.jpeg"
if not os.path.exists(prev_path):
    import glob
    imgs = glob.glob(r"c:\final_ppd\StainScope-Backend-Server\storage\micrographs\*\*\*.jpg") + glob.glob(r"c:\final_ppd\StainScope-Backend-Server\storage\micrographs\*\*\*.jpeg")
    prev_path = imgs[0] if imgs else None

if prev_path and os.path.exists(prev_path):
    bgr_prev = cv2.imread(prev_path)
    t0 = time.time()
    res_prev = engine.analyze_image(bgr_prev)
    t_prev = time.time() - t0
    print("File:", os.path.basename(prev_path))
    print("Valid:", res_prev.get("valid"))
    print("Stain Status:", res_prev.get("stain", {}).get("status"))
    print("Mineralized Area %:", f"{res_prev.get('mineralization', {}).get('area_percent')}%")
    print("Nodule Count:", res_prev.get("nodules", {}).get("count"))
    print("Mean Nodule Size:", f"{res_prev.get('nodules', {}).get('mean_size_pixels')} px")
    print("Spatial Pattern:", res_prev.get("mineralization", {}).get("spatial_pattern"))
    print("Visualizations:", list(res_prev.get("visualizations", {}).keys()))
    print(f"Processing Time: {t_prev:.3f}s")

print("\n" + "=" * 70)
print("3. TEST LIVE WEB ANALYSIS (API /analyze)")
print("=" * 70)
payload = {
    "sub": "ddd21a1a-c3e9-4aa0-9027-fa4927b06b2e",
    "email": "udaykiranbs9010@gmail.com",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
}
token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
headers = {"Authorization": f"Bearer {token}"}

test_web_img = r"c:\final_ppd\StainScope-Backend-Server\storage\micrographs\ddd21a1a-c3e9-4aa0-9027-fa4927b06b2e\b8a3ecc0-2da3-4053-ac3b-42e2cb1369b4\images.jpeg"
if os.path.exists(test_web_img):
    with open(test_web_img, "rb") as f:
        files = {"file": ("images.jpeg", f, "image/jpeg")}
        data = {"sample_title": "Web Verification Rollback Run"}
        t0 = time.time()
        resp = requests.post("http://127.0.0.1:8000/analyze", headers=headers, files=files, data=data)
        t_api = time.time() - t0
        print("HTTP Status Code:", resp.status_code)
        if resp.status_code == 200:
            res_json = resp.json()
            print("Analysis ID:", res_json.get("analysis_id") or res_json.get("id"))
            print("Valid:", res_json.get("is_valid", res_json.get("valid")))
            
            # Print both top-level and nested structure
            mineral = res_json.get("mineralization", {})
            nodules = res_json.get("nodules", {})
            area_pct = res_json.get("mineralized_area_percent") or mineral.get("area_percent")
            nod_cnt = res_json.get("nodule_count") or nodules.get("count")
            od = res_json.get("optical_density") or mineral.get("optical_density")
            pattern = res_json.get("pattern") or mineral.get("spatial_pattern")
            
            print("Mineralized Area %:", f"{area_pct}%")
            print("Nodule Count:", nod_cnt)
            print("Optical Density:", od)
            print("Spatial Pattern:", pattern)
            print("Overlay Path:", res_json.get("overlay"))
            print("Image URL:", res_json.get("image_url"))
            print(f"API Roundtrip Time: {t_api:.3f}s")
        else:
            print("Error:", resp.text)

print("\n" + "=" * 70)
print("4. TEST LIVE ANDROID ANALYSIS FLOW")
print("=" * 70)
if os.path.exists(test_web_img):
    with open(test_web_img, "rb") as f:
        files = {"file": ("android_sample.jpeg", f, "image/jpeg")}
        data = {
            "sample_title": "Android App Verification Run",
            "cell_line": "MC3T3-E1",
            "treatment": "Osteogenic Medium",
            "differentiation_day": "Day 21"
        }
        t0 = time.time()
        resp_android = requests.post("http://127.0.0.1:8000/analyze", headers=headers, files=files, data=data)
        t_android = time.time() - t0
        print("HTTP Status Code:", resp_android.status_code)
        if resp_android.status_code == 200:
            android_json = resp_android.json()
            mineral = android_json.get("mineralization", {})
            nodules = android_json.get("nodules", {})
            
            print("Analysis ID:", android_json.get("analysis_id") or android_json.get("id"))
            print("Sample Title:", android_json.get("sample_title"))
            print("Cell Line:", android_json.get("cell_line"))
            print("Treatment:", android_json.get("treatment"))
            print("Area %:", android_json.get("mineralized_area_percent") or mineral.get("area_percent"))
            print("Nodule Count:", android_json.get("nodule_count") or nodules.get("count"))
            print("Mean Nodule Size:", android_json.get("mean_nodule_size_pixels") or nodules.get("mean_size_pixels"))
            print("Overlay:", android_json.get("overlay"))
            print("Image URL:", android_json.get("image_url"))
            print(f"Android Request Time: {t_android:.3f}s")
        else:
            print("Error:", resp_android.text)
