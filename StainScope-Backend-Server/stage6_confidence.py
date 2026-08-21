"""
STAGE 6 — Confidence / Quality Assessment
Evaluates overall confidence, segmentation reliability, and aggregates researcher warnings.
Never pretends every result is equally reliable; returns explicit warnings when appropriate.
"""
from typing import Dict, Any, List


def assess_confidence(
    relevance_res: Dict[str, Any],
    stain_res: Dict[str, Any],
    quality_res: Dict[str, Any],
    quantification_res: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes aggregated confidence score and compiles researcher warnings.
    
    Returns:
        dict: {
            "analysis_quality": "high" | "moderate" | "low",
            "overall_confidence": float (0.0 to 1.0),
            "warnings": list of str
        }
    """
    warnings: List[str] = []
    
    # Collect quality warnings
    warnings.extend(quality_res.get("warnings", []))
    warnings.extend(stain_res.get("reasons", []))
    
    stain_conf = stain_res.get("confidence", 0.8)
    stain_status = stain_res.get("status", "uncertain")
    
    if stain_status == "uncertain":
        warnings.append("Stain signal is faint or ambiguous. Quantification confidence is reduced.")
        
    count = quantification_res.get("nodule_count", 0)
    area_pct = quantification_res.get("mineralized_area_percent", 0.0)
    
    if count > 50 and area_pct > 30.0:
        warnings.append("High density confluent nodules detected. Some touching nodules may merge in classical analysis.")
        
    # Aggregate confidence score
    base_conf = stain_conf
    if len(warnings) == 0:
        overall_conf = min(0.98, base_conf + 0.1)
        quality_rating = "high"
    elif len(warnings) <= 2 and stain_status == "ARS-compatible":
        overall_conf = max(0.65, base_conf - 0.1)
        quality_rating = "moderate"
    else:
        overall_conf = max(0.30, base_conf - 0.25)
        quality_rating = "low"

    return {
        "analysis_quality": quality_rating,
        "overall_confidence": round(overall_conf, 2),
        "warnings": warnings
    }
