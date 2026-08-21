"""
STAGE 1 — Stain Identification
Determines whether an uploaded image is compatible with Alizarin Red S (ARS) staining.
Uses HSV color distribution, red/orange hue signatures, saturation, and RGB channel ratios.
"""
from typing import Dict, Any
import cv2
import numpy as np
from config import StainIDConfig


def identify_stain(
    image: np.ndarray,
    cfg: StainIDConfig = StainIDConfig()
) -> Dict[str, Any]:
    """
    Evaluates BGR image for Alizarin Red S (ARS) color characteristics.
    
    Returns:
        dict: {
            "status": "ARS-compatible" | "likely_incompatible" | "uncertain",
            "confidence": float (0.0 to 1.0),
            "red_pixel_ratio": float,
            "blue_dominance_ratio": float,
            "reasons": list of str
        }
    """
    if len(image.shape) == 2:
        bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    else:
        bgr = image.copy()
        
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    
    # 1. Mask red/orange/brick-red hues in HSV
    mask1 = cv2.inRange(hsv, np.array(cfg.hue_lower_red1), np.array(cfg.hue_upper_red1))
    mask2 = cv2.inRange(hsv, np.array(cfg.hue_lower_red2), np.array(cfg.hue_upper_red2))
    ars_mask = cv2.bitwise_or(mask1, mask2)
    
    total_pixels = image.shape[0] * image.shape[1]
    red_pixel_count = int(np.count_nonzero(ars_mask))
    red_pixel_ratio = float(red_pixel_count / total_pixels)
    
    # 2. Check Blue vs Red dominance (e.g., DAPI / Trypan Blue / Giemsa checks)
    b, g, r = cv2.split(bgr.astype(np.float32))
    mean_r, mean_g, mean_b = float(np.mean(r)), float(np.mean(g)), float(np.mean(b))
    
    blue_dominance_ratio = mean_b / (mean_r + 1e-5)
    
    reasons = []
    
    # Rejection check for blue-dominant non-ARS stains (e.g. DAPI)
    if blue_dominance_ratio > cfg.blue_purple_max_dominance or (mean_b > mean_r * 1.8 and red_pixel_ratio < 0.02):
        return {
            "status": "likely_incompatible",
            "confidence": 0.95,
            "red_pixel_ratio": round(red_pixel_ratio, 4),
            "blue_dominance_ratio": round(blue_dominance_ratio, 2),
            "reasons": ["Image is strongly blue-dominant (likely DAPI or nuclear blue stain, not ARS)."]
        }

    # Evaluate compatibility score
    if red_pixel_ratio >= cfg.min_red_pixel_ratio:
        if mean_r >= mean_b:
            status = "ARS-compatible"
            confidence = min(0.95, 0.6 + red_pixel_ratio * 2.5)
            reasons.append("Characteristic ARS red/orange hue signature detected.")
        else:
            status = "uncertain"
            confidence = 0.55
            reasons.append("Red hue detected, but image has elevated blue background.")
    else:
        if red_pixel_ratio < 0.002:
            status = "likely_incompatible"
            confidence = 0.85
            reasons.append("Absence of characteristic ARS red/orange hue signature.")
        else:
            status = "uncertain"
            confidence = 0.50
            reasons.append("Very low ARS red hue signal (possibly unstained baseline or extremely weak ARS).")

    return {
        "status": status,
        "confidence": round(confidence, 2),
        "red_pixel_ratio": round(red_pixel_ratio, 4),
        "blue_dominance_ratio": round(blue_dominance_ratio, 2),
        "reasons": reasons
    }
