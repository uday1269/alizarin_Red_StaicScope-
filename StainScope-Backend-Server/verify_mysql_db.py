"""
Direct Database Verification Script for XAMPP MySQL 'stainscope'.
Checks table rows across:
- users
- profiles
- micrographs
- analyses
- nodules
- analysis_overlays
- research_notes
- batch_comparisons
"""
import pymysql
import pymysql.cursors

def verify_mysql_records():
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="",
        database="stainscope",
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("==================================================")
    print("XAMPP MYSQL 'STAINSCOPE' DIRECT DATABASE AUDIT")
    print("==================================================")
    
    tables = [
        "users",
        "profiles",
        "experiments",
        "micrographs",
        "analyses",
        "nodules",
        "analysis_overlays",
        "research_notes",
        "batch_comparisons",
        "batch_comparison_items"
    ]
    
    with conn.cursor() as cursor:
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {t}")
            cnt = cursor.fetchone()["cnt"]
            print(f"Table '{t}': {cnt} records")
            
        print("\n--- SAMPLE RECORD FROM 'analyses' TABLE ---")
        cursor.execute("SELECT id, user_id, model_type, model_version, analysis_method, analysis_version, mineralized_area_percent, nodule_count, optical_density_proxy, analyzed_at FROM analyses ORDER BY analyzed_at DESC LIMIT 1")
        an_sample = cursor.fetchone()
        if an_sample:
            for k, v in an_sample.items():
                print(f"  {k}: {v}")
        else:
            print("  (No analysis records found)")

        print("\n--- SAMPLE RECORD FROM 'analysis_overlays' TABLE ---")
        cursor.execute("SELECT id, analysis_id, overlay_type, storage_path FROM analysis_overlays ORDER BY created_at DESC LIMIT 2")
        ov_samples = cursor.fetchall()
        for ov in ov_samples:
            print(f"  Overlay: {ov['overlay_type']} -> {ov['storage_path']}")

    conn.close()
    print("==================================================")

if __name__ == "__main__":
    verify_mysql_records()
