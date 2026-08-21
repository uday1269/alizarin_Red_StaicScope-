"""
Phase 2 Backend Integration & Security Validation Tests
"""
import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))

# Import app from api
from api import app, db_manager

class TestBackendPhase2Auth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_unauthenticated_request_rejected_when_dev_mode_off(self):
        os.environ["STAINSCOPE_DEV_MODE"] = "false"
        response = self.client.get("/analyses")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authentication required", response.json().get("detail", ""))

    def test_dev_mode_fallback_when_dev_mode_on(self):
        os.environ["STAINSCOPE_DEV_MODE"] = "true"
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("dev_mode"))

        response_profile = self.client.get("/profile")
        self.assertEqual(response_profile.status_code, 200)
        self.assertEqual(response_profile.json().get("id"), "00000000-0000-0000-0000-000000000001")

    def test_notes_and_analyses_endpoints_in_dev_mode(self):
        os.environ["STAINSCOPE_DEV_MODE"] = "true"
        res_notes = self.client.get("/notes")
        self.assertEqual(res_notes.status_code, 200)
        self.assertIsInstance(res_notes.json(), list)

        res_analyses = self.client.get("/analyses")
        self.assertEqual(res_analyses.status_code, 200)
        self.assertIsInstance(res_analyses.json(), list)

if __name__ == "__main__":
    unittest.main()
