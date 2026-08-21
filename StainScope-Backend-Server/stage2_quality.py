"""
STAGE 2 — Microscopy / Image Quality Validation
Validates microscopy image quality before segmentation.
Detects blur, underexposure, overexposure, and severe illumination non-uniformity (vignetting).
Issues warnings separately from hard rejections.
"""
from typing import Dict, Any, List
import cv2
import numpy as np
from config import QualityConfig


def validate_image_quality(
    image: np.ndarray,
    cfg: QualityConfig = QualityConfig()
) -> Dict[str, Any]:
    """
    Evaluates image quality metrics and identifies potential quality issues.
    
    Returns:
        dict: {
            "usable": bool,
            "warnings": list of str,
            "metrics": dict
        }
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    h, w = gray.shape[:2]
    
    warnings: List[str] = []
    
    # 1. Blur evaluation (Laplacian variance)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < cfg.blur_laplacian_threshold:
        warnings.append(f"Image appears blurry or out-of-focus (Laplacian variance: {round(lap_var, 1)}).")

    # 2. Illumination / Brightness check
    mean_val = float(np.mean(gray))
    if mean_val < cfg.min_brightness_mean:
        warnings.append("Image is extremely dark / underexposed.")
    elif mean_val > cfg.max_brightness_mean:
        warnings.append("Image is extremely bright / overexposed.")
        
    # 3. Vignetting / Illumination gradient check (Corners vs Center)
    margin_h, margin_w = int(h * 0.2), int(w * 0.2)
    center = gray[margin_h:h-margin_h, margin_w:w-margin_w]
    
    c1 = np.mean(gray[0:margin_h, 0:margin_w])
    c2 = np.mean(gray[0:margin_h, w-margin_w:w])
    c3 = np.mean(gray[h-margin_h:h, 0:margin_w])
    c4 = np.mean(gray[h-margin_h:h, w-margin_w:w])
    corners_mean = float((c1 + c2 + c3 + c4) / 4.0)
    center_mean = float(np.mean(center))
    
    illum_ratio = center_mean / (corners_mean + 1e-5) if corners_mean > 0 else 1.0
    if illum_ratio > cfg.max_vignette_ratio or illum_ratio < (1.0 / cfg.max_vignette_ratio):
        warnings.append("Significant illumination variation or vignetting detected across field of view.")

    # Image is unusable only if extreme combination occurs (e.g. extremely dark AND blurry)
    usable = not (mean_val < 5.0 or mean_val > 252.0)
    
    metrics = {
        "blur_score": round(lap_var, 2),
        "mean_brightness": round(mean_val, 2),
        "vignette_illum_ratio": round(illum_ratio, 2)
    }

    return {
        "usable": usable,
        "warnings": warnings,
        "metrics": metrics
    }
