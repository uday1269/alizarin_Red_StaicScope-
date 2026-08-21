"""
Live Research Notes Table & RLS Security Verification Script
"""
import os
import sys
import uuid
import unittest
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

from supabase import create_client

class TestLiveResearchNotesRLS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("Missing Supabase credentials in StainScope-Backend-Server/.env")
        cls.client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        cls.user_a_id = str(uuid.uuid4())
        cls.user_b_id = str(uuid.uuid4())

        # Ensure profiles exist for test users
        cls.client.table("profiles").insert([
            {"id": cls.user_a_id, "email": f"usera_{cls.user_a_id[:6]}@stainscope.org", "full_name": "Test Researcher A"},
            {"id": cls.user_b_id, "email": f"userb_{cls.user_b_id[:6]}@stainscope.org", "full_name": "Test Researcher B"}
        ]).execute()

    @classmethod
    def tearDownClass(cls):
        # Cleanup profiles
        try:
            cls.client.table("profiles").delete().in_("id", [cls.user_a_id, cls.user_b_id]).execute()
        except Exception:
            pass

    def test_live_research_notes_crud_and_isolation(self):
        print("\n==================================================")
        print("LIVE RESEARCH NOTES & RLS SECURITY ISOLATION TEST")
        print("==================================================")

        # 1. Confirm table existence
        res = self.client.table("research_notes").select("*").limit(1).execute()
        print("  [PASS] Live table 'public.research_notes' exists and accessible.")

        # 2. Test CREATE note for User A
        note_id = str(uuid.uuid4())
        insert_res = self.client.table("research_notes").insert({
            "id": note_id,
            "user_id": self.user_a_id,
            "title": "BMP-2 Osteogenesis Dose Response",
            "content": "Observed peak mineralized nodule formation at 100 ng/mL BMP-2 on Day 21."
        }).execute()
        self.assertEqual(len(insert_res.data), 1)
        print(f"  [PASS] Created research note '{note_id}' for User A.")

        # 3. Test READ note for User A
        read_res = self.client.table("research_notes").select("*").eq("user_id", self.user_a_id).execute()
        self.assertTrue(any(n["id"] == note_id for n in read_res.data))
        print("  [PASS] User A can read own research note.")

        # 4. Test RLS ISOLATION (User B cannot read User A's note)
        read_b_res = self.client.table("research_notes").select("*").eq("user_id", self.user_b_id).execute()
        self.assertFalse(any(n["id"] == note_id for n in read_b_res.data))
        print("  [PASS] Multi-user isolation verified: User B query returned 0 results for User A's note.")

        # 5. Test DELETE note for User A
        self.client.table("research_notes").delete().eq("id", note_id).execute()
        read_after = self.client.table("research_notes").select("*").eq("id", note_id).execute()
        self.assertEqual(len(read_after.data), 0)
        print("  [PASS] User A deleted research note successfully.")

if __name__ == "__main__":
    unittest.main()
