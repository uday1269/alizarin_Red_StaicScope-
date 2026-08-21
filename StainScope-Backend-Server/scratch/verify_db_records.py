import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, r"c:\final_ppd\StainScope-Backend-Server")
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from db_supabase import supabase_client, DEMO_USER_ID

def check_db_records():
    print("==================================================")
    print("SUPABASE LIVE DATABASE PERSISTENCE VERIFICATION")
    print("==================================================")
    if not supabase_client:
        print("Supabase client not initialized.")
        return

    # 1. Check profiles
    prof_res = supabase_client.table("profiles").select("*").eq("id", DEMO_USER_ID).execute()
    print("1. PROFILES Table Record:")
    print("   Data:", prof_res.data)

    # 2. Check micrographs
    mic_res = supabase_client.table("micrographs").select("*").order("created_at", desc=True).limit(1).execute()
    print("\n2. MICROGRAPHS Table Latest Record:")
    if mic_res.data:
        m = mic_res.data[0]
        print(f"   ID: {m['id']}")
        print(f"   File Name: {m['file_name']}")
        print(f"   Storage Bucket: {m['storage_bucket']}")
        print(f"   Storage Path: {m['storage_path']}")
        print(f"   File Size: {m['file_size_bytes']} bytes")
        print(f"   File Hash: {m['file_hash']}")

    # 3. Check analyses
    an_res = supabase_client.table("analyses").select("*").order("analyzed_at", desc=True).limit(1).execute()
    print("\n3. ANALYSES Table Latest Record:")
    if an_res.data:
        a = an_res.data[0]
        print(f"   ID: {a['id']}")
        print(f"   Model Type: {a['model_type']}")
        print(f"   Model Version: {a['model_version']}")
        print(f"   Analysis Method: {a['analysis_method']}")
        print(f"   Analysis Version: {a['analysis_version']}")
        print(f"   Status: {a['status']}")
        print(f"   Mineralization %: {a['mineralized_area_percent']}%")
        print(f"   Nodule Count: {a['nodule_count']}")

        analysis_id = a['id']
        # 4. Check nodules for this analysis
        nod_res = supabase_client.table("nodules").select("id, label_id, area_pixels, centroid_x, centroid_y, size_category, confidence").eq("analysis_id", analysis_id).limit(5).execute()
        print(f"\n4. NODULES Table Records (Sample for Analysis {analysis_id}):")
        print(f"   Total Nodules Sampled: {len(nod_res.data)}")
        for n in nod_res.data:
            print(f"   - {n['label_id']}: Area={n['area_pixels']}px, Centroid=({n['centroid_x']}, {n['centroid_y']}), Category={n['size_category']}, Conf={n['confidence']}")

        # 5. Check overlays for this analysis
        ov_res = supabase_client.table("analysis_overlays").select("*").eq("analysis_id", analysis_id).execute()
        print(f"\n5. ANALYSIS_OVERLAYS Table Records (For Analysis {analysis_id}):")
        for ov in ov_res.data:
            print(f"   - {ov['overlay_type']}: Bucket={ov['storage_bucket']}, Path={ov['storage_path']}, Size={ov['file_size_bytes']} bytes")

    print("\n==================================================")

if __name__ == "__main__":
    check_db_records()
