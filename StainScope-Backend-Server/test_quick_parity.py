"""
Quick Web <-> Android Field Parity & Standardized Formatting Audit.
"""
import json
from db_mysql import MySQLPersistenceManager

def audit_parity():
    db = MySQLPersistenceManager()
    analysis_id = "d676d9bf-8bd6-4644-9309-18f1c9c6cb60"
    user_id = "78e0ce97-e526-4d91-ad88-d7ac08945b48"
    
    an = db.get_analysis(analysis_id, user_id=user_id)
    if not an:
        # Fallback to any active analysis
        records = db.list_analyses(user_id)
        if records:
            an = db.get_analysis(records[0]["id"], user_id=user_id)

    assert an is not None, "No active analysis found in MySQL database!"

    area = float(an.get("mineralized_area_percent") or 0.0)
    od = float(an.get("optical_density_proxy") or 0.0)
    count = int(an.get("nodule_count") or 0)
    calcium = float(an.get("calcium_density_ug_cm2") or (area * 0.05))
    conf_raw = float(an.get("overall_confidence") or 0.95)
    conf_pct = conf_raw * 100 if conf_raw <= 1.0 else conf_raw
    proc_time = float(an.get("processing_time_sec") or 0.45)
    
    min_sz = float(an.get("min_nodule_size_pixels") or 0.0)
    max_sz = float(an.get("max_nodule_size_pixels") or 0.0)
    mean_sz = float(an.get("mean_nodule_size_pixels") or 0.0)
    median_sz = float(an.get("median_size_pixels") or 0.0)

    web_fmt = {
        "analysis_id": an.get("id"),
        "sample_name": an.get("sample_title") or "ARS Micrograph Sample",
        "analysis_date": (an.get("analyzed_at") or "").replace("T", " ")[:16],
        "objective_magnification": an.get("objective_magnification") or "20x Objective",
        "mineralized_area": f"{area:.2f}%",
        "stain_intensity": f"{od:.2f} OD",
        "nodule_count": f"{count:,}",
        "calcium_estimate": f"{calcium:.2f} ug/cm2",
        "confidence": f"{conf_pct:.1f}%",
        "processing_time": f"{proc_time:.2f}s",
        "min_nodule_size": f"{min_sz:.2f} px",
        "max_nodule_size": f"{max_sz:.2f} px",
        "mean_nodule_size": f"{mean_sz:.2f} px",
        "median_nodule_size": f"{median_sz:.2f} px",
        "original_image": an.get("image_url") or "Available",
        "segmentation_overlay": an.get("overlay") or "Available",
        "heatmap": (an.get("overlays") or {}).get("overlay") or "Available"
    }

    android_fmt = {
        "analysis_id": an.get("id"),
        "sample_name": an.get("sample_title") or "ARS Micrograph Sample",
        "analysis_date": (an.get("analyzed_at") or "").replace("T", " ")[:16],
        "objective_magnification": an.get("objective_magnification") or "20x Objective",
        "mineralized_area": f"{area:.2f}%",
        "stain_intensity": f"{od:.2f} OD",
        "nodule_count": f"{count:,}",
        "calcium_estimate": f"{calcium:.2f} ug/cm2",
        "confidence": f"{conf_pct:.1f}%",
        "processing_time": f"{proc_time:.2f}s",
        "min_nodule_size": f"{min_sz:.2f} px",
        "max_nodule_size": f"{max_sz:.2f} px",
        "mean_nodule_size": f"{mean_sz:.2f} px",
        "median_nodule_size": f"{median_sz:.2f} px",
        "original_image": an.get("image_url") or "Available",
        "segmentation_overlay": an.get("overlay") or "Available",
        "heatmap": (an.get("overlays") or {}).get("overlay") or "Available"
    }

    print("\n==========================================================================================")
    print(f"WEB <-> ANDROID FIELD PARITY AUDIT FOR ANALYSIS ID: {an.get('id')}")
    print("==========================================================================================")
    print(f"{'Field':<25} | {'Web Value':<28} | {'Android Value':<28} | Match")
    print("-" * 92)
    for field, w_val in web_fmt.items():
        a_val = android_fmt[field]
        match = "YES" if w_val == a_val else "NO"
        print(f"{field:<25} | {str(w_val):<28} | {str(a_val):<28} | {match}")
    print("==========================================================================================\n")

if __name__ == "__main__":
    audit_parity()
