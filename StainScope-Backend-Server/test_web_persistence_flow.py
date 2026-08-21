"""
Web Persistence End-to-End Test: Upload/Analyze -> Fetch History -> Refresh Simulation
"""
import os
import sys
import unittest
import numpy as np
import cv2
import io
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))

from api import app

class TestWebPersistenceFlow(unittest.TestCase):
    def setUp(self):
        os.environ["STAINSCOPE_DEV_MODE"] = "true"
        self.client = TestClient(app)

    def test_upload_analyze_and_fetch_history_persistence(self):
        # 1. Create a dummy ARS microscopy test image
        img = np.zeros((300, 400, 3), dtype=np.uint8)
        # Draw red stained mineralized region
        cv2.circle(img, (200, 150), 60, (20, 20, 200), -1)
        
        success, encoded_png = cv2.imencode('.png', img)
        self.assertTrue(success)
        img_bytes = io.BytesIO(encoded_png.tobytes())

        # 2. Execute POST /analyze API call
        print("\n[Step 1] Uploading and analyzing test micrograph via POST /analyze...")
        response = self.client.post(
            "/analyze",
            files={"file": ("hMSC_Day21_BMP2_Test.png", img_bytes, "image/png")},
            data={
                "sample_title": "hMSC Day 21 BMP2 Persistence Test",
                "cell_line": "hMSC",
                "treatment": "100 ng/mL BMP-2",
                "differentiation_day": "Day 21"
            }
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data.get("valid"), f"Analysis failed: {res_data.get('reason')}")
        
        analysis_id = res_data.get("analysis_id")
        self.assertIsNotNone(analysis_id)
        print(f"  [PASS] Analysis completed with persistent Supabase ID: {analysis_id}")

        # 3. Simulate browser refresh by executing GET /analyses (fetching repository from Supabase)
        print("[Step 2] Simulating browser refresh -> GET /analyses from Supabase...")
        history_resp = self.client.get("/analyses")
        self.assertEqual(history_resp.status_code, 200)
        history_list = history_resp.json()
        self.assertIsInstance(history_list, list)

        # Check if created analysis appears in history
        found_in_history = any(rec.get("id") == analysis_id for rec in history_list)
        self.assertTrue(found_in_history, f"Created analysis {analysis_id} not found in Supabase history list!")
        print(f"  [PASS] Persistence verified! Analysis {analysis_id} appears in history after refresh.")

if __name__ == "__main__":
    unittest.main()
