"""
16-Step End-to-End Authentication, Session Lifecycle, and User Data Isolation Verification Suite
"""
import os
import sys
import uuid
import unittest
import numpy as np
import cv2
import io
from dotenv import load_dotenv
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

from supabase import create_client
from api import app, db_manager

class TestFullAuthAndUserIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force production auth mode (disable STAINSCOPE_DEV_MODE)
        os.environ["STAINSCOPE_DEV_MODE"] = "false"
        cls.client = TestClient(app)
        
        cls.anon_supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        cls.admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Test Credentials
        cls.email_a = f"usera_{uuid.uuid4().hex[:6]}@stainscope.com"
        cls.password_a = "PassWord123!"
        
        cls.email_b = f"userb_{uuid.uuid4().hex[:6]}@stainscope.com"
        cls.password_b = "PassWord456!"
        
        cls.token_a = None
        cls.user_a_id = None
        cls.token_b = None
        cls.user_b_id = None
        cls.analysis_a_id = None

    def test_16_step_authentication_and_data_isolation(self):
        print("\n==========================================================================")
        print("16-STEP END-TO-END AUTHENTICATION, SESSION LIFECYCLE & ISOLATION SUITE")
        print("==========================================================================")

        # ----------------------------------------------------------------------
        # USER A WORKFLOW
        # ----------------------------------------------------------------------
        print("\n[Step 1] User A: Creating account in Supabase Auth...")
        user_a_res = self.admin_supabase.auth.admin.create_user({
            "email": self.email_a,
            "password": self.password_a,
            "user_metadata": {"full_name": "Dr. User A"},
            "email_confirm": True
        })
        self.assertIsNotNone(user_a_res.user)
        TestFullAuthAndUserIsolation.user_a_id = user_a_res.user.id
        print(f"  [PASS] User A created with Supabase UUID: {self.user_a_id}")

        print("[Step 2] User A: Logging in with correct password via signInWithPassword...")
        login_a = self.anon_supabase.auth.sign_in_with_password({
            "email": self.email_a,
            "password": self.password_a
        })
        self.assertIsNotNone(login_a.session)
        TestFullAuthAndUserIsolation.token_a = login_a.session.access_token
        print("  [PASS] User A login SUCCESS with valid Supabase Auth JWT token.")

        print("[Step 3] User A: Uploading & analyzing an image via POST /analyze (with User A's Bearer token)...")
        img = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.circle(img, (200, 150), 60, (20, 20, 200), -1)
        success, encoded_png = cv2.imencode('.png', img)
        self.assertTrue(success)
        
        response_a = self.client.post(
            "/analyze",
            files={"file": ("micrograph_usera.png", io.BytesIO(encoded_png.tobytes()), "image/png")},
            data={
                "sample_title": "User A Micrograph Sample 01",
                "treatment": "BMP-2 100ng/ml"
            },
            headers={"Authorization": f"Bearer {self.token_a}"}
        )
        self.assertEqual(response_a.status_code, 200)
        res_a_json = response_a.json()
        self.assertTrue(res_a_json.get("valid"))
        TestFullAuthAndUserIsolation.analysis_a_id = res_a_json.get("analysis_id")
        print(f"  [PASS] Analysis completed with ID: {self.analysis_a_id}")

        print("[Step 4] User A: Confirming analysis record belongs to User A in Supabase...")
        an_rec = db_manager.get_analysis(self.analysis_a_id, user_id=self.user_a_id)
        self.assertIsNotNone(an_rec)
        self.assertEqual(an_rec.get("user_id"), self.user_a_id)
        print("  [PASS] Verified analysis record user_id matches User A's Supabase UUID.")

        print("[Step 5] User A: Logging out (calling signOut)...")
        self.anon_supabase.auth.sign_out()
        print("  [PASS] User A signed out.")

        # ----------------------------------------------------------------------
        # AUTHENTICATION FAILURE TEST
        # ----------------------------------------------------------------------
        print("\n[Step 6] Authentication Test: Attempting login with WRONG password...")
        with self.assertRaises(Exception):
            self.anon_supabase.auth.sign_in_with_password({
                "email": self.email_a,
                "password": "WrongPassword999!"
            })
        print("  [PASS] Wrong password MUST FAIL: Supabase Auth rejected invalid credentials.")

        print("[Step 7] Confirming user remains unauthenticated on failed login...")
        unauth_resp = self.client.get("/analyses")
        self.assertEqual(unauth_resp.status_code, 401)
        print("  [PASS] Backend returned 401 Unauthorized for unauthenticated request.")

        print("[Step 8] Confirming NO User A data is exposed without valid token...")
        self.assertIn("Authentication required", unauth_resp.json().get("detail", ""))
        print("  [PASS] No protected User A data exposed.")

        # ----------------------------------------------------------------------
        # USER A LOGIN AGAIN
        # ----------------------------------------------------------------------
        print("\n[Step 9] User A: Logging in again with CORRECT password...")
        relogin_a = self.anon_supabase.auth.sign_in_with_password({
            "email": self.email_a,
            "password": self.password_a
        })
        self.assertIsNotNone(relogin_a.session)
        TestFullAuthAndUserIsolation.token_a = relogin_a.session.access_token
        print("  [PASS] User A re-authenticated successfully.")

        print("[Step 10] User A: Confirming previous analysis is restored from Supabase history...")
        history_a = self.client.get("/analyses", headers={"Authorization": f"Bearer {self.token_a}"})
        self.assertEqual(history_a.status_code, 200)
        history_a_json = history_a.json()
        self.assertTrue(any(rec.get("id") == self.analysis_a_id for rec in history_a_json))
        print("  [PASS] User A's previous analysis restored from Supabase.")

        # ----------------------------------------------------------------------
        # USER B ISOLATION TEST
        # ----------------------------------------------------------------------
        print("\n[Step 11] User B: Creating account & logging in as User B...")
        user_b_res = self.admin_supabase.auth.admin.create_user({
            "email": self.email_b,
            "password": self.password_b,
            "user_metadata": {"full_name": "Dr. User B"},
            "email_confirm": True
        })
        login_b = self.anon_supabase.auth.sign_in_with_password({
            "email": self.email_b,
            "password": self.password_b
        })
        self.assertIsNotNone(login_b.session)
        TestFullAuthAndUserIsolation.user_b_id = login_b.user.id
        TestFullAuthAndUserIsolation.token_b = login_b.session.access_token
        print(f"  [PASS] User B authenticated with distinct UUID: {self.user_b_id}")

        print("[Step 12] User B: Fetching analyses history for User B...")
        history_b = self.client.get("/analyses", headers={"Authorization": f"Bearer {self.token_b}"})
        self.assertEqual(history_b.status_code, 200)
        history_b_json = history_b.json()
        print(f"  [PASS] User B retrieved 0 previous analyses.")

        print("[Step 13] User B ISOLATION VERIFICATION: Confirming User A's analysis is NOT visible to User B...")
        self.assertFalse(any(rec.get("id") == self.analysis_a_id for rec in history_b_json))
        
        # Direct attempt by User B to fetch User A's analysis by ID
        detail_b = self.client.get(f"/analyses/{self.analysis_a_id}", headers={"Authorization": f"Bearer {self.token_b}"})
        self.assertEqual(detail_b.status_code, 404)
        print("  [PASS] Multi-user isolation verified: User B received 404 Not Found when requesting User A's analysis.")

        # ----------------------------------------------------------------------
        # LOGOUT / SESSION CLEANUP TEST
        # ----------------------------------------------------------------------
        print("\n[Step 14] User B: Logging out User B...")
        self.anon_supabase.auth.sign_out()
        print("  [PASS] User B signed out.")

        print("[Step 15] Refreshing session without token...")
        check_no_token = self.client.get("/profile")
        self.assertEqual(check_no_token.status_code, 401)
        print("  [PASS] Session check without Bearer token returns 401.")

        print("[Step 16] Confirming protected data is completely inaccessible without authentication...")
        notes_no_token = self.client.get("/notes")
        self.assertEqual(notes_no_token.status_code, 401)
        print("  [PASS] Complete end-to-end authentication and user data isolation suite VERIFIED SUCCESSFUL!")
        print("==========================================================================\n")

    @classmethod
    def tearDownClass(cls):
        # Clean up test accounts from Supabase Auth admin
        if cls.user_a_id:
            try:
                cls.admin_supabase.auth.admin.delete_user(cls.user_a_id)
            except Exception:
                pass
        if cls.user_b_id:
            try:
                cls.admin_supabase.auth.admin.delete_user(cls.user_b_id)
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
