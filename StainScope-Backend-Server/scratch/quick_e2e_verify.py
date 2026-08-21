import os
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, r"c:\final_ppd\StainScope-Backend-Server")
from api import app

client = TestClient(app)

def main():
    real_image_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c2\C2_D28_4x_BF_01.tif"
    assert os.path.exists(real_image_path)
    
    with open(real_image_path, "rb") as f:
        resp = client.post("/analyze", files={"file": ("C2_D28_4x_BF_01.tif", f, "image/tiff")})
        
    assert resp.status_code == 200
    data = resp.json()
    
    print("=== FASTAPI + SUPABASE PERSISTENCE VERIFICATION RESULT ===")
    print("HTTP Status Code:", resp.status_code)
    print("Response Valid:", data["valid"])
    print("Stain Status:", data["stain"]["status"])
    print("Mineralized Area %:", data["mineralization"]["area_percent"])
    print("Total Image Pixels:", data["mineralization"]["total_pixels"])
    print("Optical Density Proxy:", data["intensity"]["optical_density"])
    print("Nodule Count:", data["nodules"]["count"])
    print("First 3 Nodule IDs:", [n["id"] for n in data["nodules"]["objects"][:3]])
    print("Overlays Present:", list(data["overlays"].keys()))
    print("=========================================================")

if __name__ == "__main__":
    main()
