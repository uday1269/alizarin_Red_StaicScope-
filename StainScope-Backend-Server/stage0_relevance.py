"""
STAGE 0 — Conservative Image Relevance Gate
Determines whether an uploaded image is a valid microscopy image suitable for analysis.
Rejects non-microscopy images, normal photographs, screenshots, documents, and corrupt files.
"""
from typing import Dict, Any, Tuple
import cv2
import numpy as np
from config import RelevanceConfig


def check_image_relevance(
    image: np.ndarray,
    cfg: RelevanceConfig = RelevanceConfig()
) -> Dict[str, Any]:
    """
    Evaluates an input BGR image array against conservative relevance heuristics.
    
    Returns:
        dict: {
            "valid": bool,
            "reason": str (empty if valid),
            "metrics": dict
        }
    """
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        return {
            "valid": False,
            "reason": "Invalid or corrupt image data.",
            "metrics": {}
        }
        
    h, w = image.shape[:2]
    if h < cfg.min_resolution[0] or w < cfg.min_resolution[1]:
        return {
            "valid": False,
            "reason": f"Image dimensions ({w}x{h}) are below minimum requirement ({cfg.min_resolution[1]}x{cfg.min_resolution[0]}).",
            "metrics": {"width": w, "height": h}
        }
        
    # Standardize to 3-channel BGR
    if len(image.shape) == 2:
        bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    else:
        bgr = image.copy()

    # Convert to grayscale for texture and edge analysis
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Check for blank / near-zero variance images
    std_dev = float(np.std(gray))
    if std_dev < cfg.min_color_variance:
        return {
            "valid": False,
            "reason": "Image has almost no contrast/variance (blank or solid color image).",
            "metrics": {"std_dev": std_dev}
        }
        
    # 2. Document / Screenshot check (high edge density with sharp text features)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0) / (h * w))
    
    # Check for text document features: very bright background (>230 mean) with sharp text edges
    mean_val = float(np.mean(gray))
    if mean_val > 225.0 and edge_density > cfg.max_text_edge_density:
        return {
            "valid": False,
            "reason": "Image appears to be a text document or document screenshot.",
            "metrics": {"mean_brightness": mean_val, "edge_density": edge_density}
        }
        
    # 3. Check channel statistics (Standard photograph vs microscopy)
    b, g, r = cv2.split(bgr)
    std_b, std_g, std_r = float(np.std(b)), float(np.std(g)), float(np.std(r))
    channel_std_diff = max(abs(std_r - std_g), abs(std_g - std_b), abs(std_r - std_b))
    
    # Texture variance (Laplacian variance)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < cfg.min_microscopy_texture:
        return {
            "valid": False,
            "reason": "Image lacks granular microscopy texture details.",
            "metrics": {"laplacian_variance": lap_var}
        }
        
    metrics = {
        "width": w,
        "height": h,
        "std_dev": round(std_dev, 2),
        "edge_density": round(edge_density, 4),
        "mean_brightness": round(mean_val, 2),
        "laplacian_variance": round(lap_var, 2),
        "channel_std_diff": round(channel_std_diff, 2)
    }

    return {
        "valid": True,
        "reason": "",
        "metrics": metrics
    }
