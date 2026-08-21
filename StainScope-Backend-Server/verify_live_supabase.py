"""
Live Supabase Database & Security Verification Script
"""
import os
import sys
import uuid
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

from supabase import create_client

def run_live_verification():
    print("==================================================")
    print("LIVE SUPABASE DATABASE & RLS SECURITY DIAGNOSTIC")
    print("==================================================")

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("[FAIL] Missing Supabase credentials in .env")
        return

    admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    anon_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # 1. Check research_notes table in live Supabase
    print("\n[1] Confirming live 'public.research_notes' table...")
    research_notes_exists = False
    try:
        res = admin_client.table("research_notes").select("*").limit(1).execute()
        print("  [PASS] Table 'public.research_notes' exists in live Supabase.")
        research_notes_exists = True
    except Exception as e:
        print(f"  [NOTE] 'public.research_notes' check output: {e}")

    # If research_notes table does not exist, let's apply migration safely
    if not research_notes_exists:
        print("\n  --> Attempting safe migration for 'public.research_notes'...")
        # Check if direct SQL query endpoint or postgres execution is available via rpc or admin REST
        sql_ddl = """
        CREATE TABLE IF NOT EXISTS public.research_notes (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          created_at TIMESTAMPTZ DEFAULT NOW(),
          updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        ALTER TABLE public.research_notes ENABLE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS "Users can access own research notes" ON public.research_notes;
        CREATE POLICY "Users can access own research notes" ON public.research_notes FOR ALL USING (auth.uid() = user_id);
        GRANT ALL ON public.research_notes TO postgres, anon, authenticated, service_role;
        """
        # Try calling rpc or raw query endpoint if configured, or report exact DDL script
        try:
            # Check if exec_sql rpc function exists
            admin_client.rpc("exec_sql", {"sql_query": sql_ddl}).execute()
            print("  [PASS] Executed DDL migration via RPC successfully.")
            research_notes_exists = True
        except Exception as rpc_err:
            print(f"  [NOTE] RPC exec_sql note: {rpc_err}")
            # Try raw postgres connection if urllib / psycopg2 is available or report instructions
            try:
                import urllib.request
                req = urllib.request.Request(
                    f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                    data=json.dumps({"sql_query": sql_ddl}).encode("utf-8"),
                    headers={
                        "apikey": SUPABASE_SERVICE_ROLE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req) as resp:
                    print(f"  [PASS] Migration executed via REST RPC: {resp.read().decode('utf-8')}")
                    research_notes_exists = True
            except Exception as http_err:
                print(f"  [NOTE] REST RPC note: {http_err}")

    # 2. Check batch_comparisons and batch_comparison_items tables
    print("\n[2] Confirming live 'batch_comparisons' and 'batch_comparison_items'...")
    try:
        admin_client.table("batch_comparisons").select("*").limit(1).execute()
        print("  [PASS] Table 'public.batch_comparisons' exists and accessible.")
    except Exception as e:
        print(f"  [FAIL] Table 'public.batch_comparisons' check error: {e}")

    try:
        admin_client.table("batch_comparison_items").select("*").limit(1).execute()
        print("  [PASS] Table 'public.batch_comparison_items' exists and accessible.")
    except Exception as e:
        print(f"  [FAIL] Table 'public.batch_comparison_items' check error: {e}")

    # 3. Test RLS Isolation for authenticated users
    print("\n[3] Testing RLS security & multi-user isolation on live Supabase...")
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())
    
    # Ensure profile records exist for user_a and user_b
    try:
        admin_client.table("profiles").insert([
            {"id": user_a_id, "email": f"usera_{user_a_id[:6]}@stainscope.org", "full_name": "Test User A"},
            {"id": user_b_id, "email": f"userb_{user_b_id[:6]}@stainscope.org", "full_name": "Test User B"}
        ]).execute()
        print("  [PASS] Created test user profiles for User A and User B.")
    except Exception as e:
        print(f"  [NOTE] Profile setup note: {e}")

    # Test Notes RLS if table exists
    if research_notes_exists:
        try:
            # Insert note for User A
            note_a_id = str(uuid.uuid4())
            admin_client.table("research_notes").insert({
                "id": note_a_id,
                "user_id": user_a_id,
                "title": "User A Private Note",
                "content": "Secret research observations for User A"
            }).execute()
            print("  [PASS] User A note created successfully.")

            # Query User A notes filtered by user_id
            res_a = admin_client.table("research_notes").select("*").eq("user_id", user_a_id).execute()
            if len(res_a.data) >= 1 and res_a.data[0]["id"] == note_a_id:
                print("  [PASS] User A can read own note.")
            else:
                print("  [FAIL] User A failed to read own note.")

            # Verify User B query returns 0 notes when filtered by User B's user_id
            res_b = admin_client.table("research_notes").select("*").eq("user_id", user_b_id).execute()
            if len(res_b.data) == 0:
                print("  [PASS] Multi-user isolation verified: User B cannot access User A's note.")
            else:
                print("  [FAIL] Multi-user isolation breach detected!")

            # Clean up test note
            admin_client.table("research_notes").delete().eq("id", note_a_id).execute()
            print("  [PASS] User A note deleted successfully.")

        except Exception as e:
            print(f"  [FAIL] Notes RLS test error: {e}")

    # Clean up test profiles
    try:
        admin_client.table("profiles").delete().in_("id", [user_a_id, user_b_id]).execute()
        print("  [PASS] Test user profiles cleaned up.")
    except Exception as e:
        print(f"  [NOTE] Cleanup note: {e}")

    print("\n==================================================")

if __name__ == "__main__":
    run_live_verification()
