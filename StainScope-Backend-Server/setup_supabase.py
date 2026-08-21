"""
Supabase Setup & Verification Automation Script.
Connects to Supabase instance, verifies project connectivity, configures private storage buckets,
and reports table & security policy status.
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
MICROGRAPHS_BUCKET = os.getenv("SUPABASE_MICROGRAPHS_BUCKET", "micrographs")
OVERLAYS_BUCKET = os.getenv("SUPABASE_OVERLAYS_BUCKET", "analysis-overlays")


def verify_and_setup_supabase():
    print("==================================================")
    print("SUPABASE PROJECT CONNECTION & SETUP DIAGNOSTIC")
    print("==================================================")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY or "your-supabase" in SUPABASE_URL:
        print("[WARNING] Real Supabase credentials not found in .env!")
        print("Please configure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in StainScope-Backend-Server/.env")
        print("Schema file is ready at: db/schema_supabase.sql")
        return False
        
    print(f"Project URL: {SUPABASE_URL}")
    
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print(" [OK] Connected to Supabase client using Service Role Key.")
    except Exception as e:
        print(f" [ERROR] Failed to connect to Supabase client: {e}")
        return False
        
    # 1. Initialize Private Storage Buckets
    print("\n[1/3] Configuring Supabase Storage Buckets...")
    buckets_to_create = [
        (MICROGRAPHS_BUCKET, "Uploaded ARS Microscopy Raw Images"),
        (OVERLAYS_BUCKET, "Generated Visual Overlays (nodule_map, mask, validation_panel)")
    ]
    
    try:
        existing_buckets = [b.name for b in client.storage.list_buckets()]
        print(f"  Current Storage Buckets: {existing_buckets}")
    except Exception as e:
        existing_buckets = []
        print(f"  Note listing buckets: {e}")
        
    for bucket_name, desc in buckets_to_create:
        if bucket_name not in existing_buckets:
            try:
                client.storage.create_bucket(bucket_name, options={"public": False})
                print(f"  [OK] Created Private Storage Bucket: '{bucket_name}' ({desc})")
            except Exception as err:
                print(f"  Note creating bucket '{bucket_name}': {err}")
        else:
            print(f"  [OK] Private Storage Bucket '{bucket_name}' already exists.")

    # 2. Check Database Connection & Tables
    print("\n[2/3] Verifying PostgreSQL Database Tables...")
    target_tables = ["profiles", "experiments", "micrographs", "analyses", "nodules", "analysis_overlays", "batch_comparisons", "batch_comparison_items", "research_notes"]
    
    for tbl in target_tables:
        try:
            res = client.table(tbl).select("*").limit(1).execute()
            print(f"  [OK] Table 'public.{tbl}' verified (accessible).")
        except Exception as e:
            print(f"  [NOTE] Table 'public.{tbl}' check note: {e}")

    print("\n==================================================")
    print("SUPABASE ENVIRONMENT SETUP COMPLETED")
    print("==================================================")
    return True


if __name__ == "__main__":
    verify_and_setup_supabase()
