"""
STAGE 5 — Mineralization Quantification
Calculates area, area %, nodule count, size metrics, spatial patterns, and optical density.
Strictly reports pixel-based measurements (pixels²) by default. Converts to µm² ONLY if explicit
calibration parameters are provided. Never invents scale calibration.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import cv2
from config import QuantificationConfig


def quantify_mineralization(
    image: np.ndarray,
    binary_mask: np.ndarray,
    nodule_data: Dict[str, Any],
    cfg: QuantificationConfig = QuantificationConfig()
) -> Dict[str, Any]:
    """
    Quantifies mineralization metrics and spatial distribution.
    
    Args:
        image: Original BGR image (for optical density computation).
        binary_mask: Binary mask of mineralized regions.
        nodule_data: Output dict from stage4_nodule_detection.
        cfg: QuantificationConfig object.
        
    Returns:
        dict: Mineralization quantification metrics.
    """
    total_pixels = int(binary_mask.shape[0] * binary_mask.shape[1])
    mineralized_pixels = int(np.count_nonzero(binary_mask))
    area_percent = float((mineralized_pixels / (total_pixels + 1e-5)) * 100.0)
    
    nodules: List[Dict[str, Any]] = nodule_data.get("objects", [])
    count = nodule_data.get("count", 0)
    
    if count > 0:
        areas = [n["area_pixels"] for n in nodules]
        min_size = int(np.min(areas))
        max_size = int(np.max(areas))
        mean_size = float(np.mean(areas))
        median_size = float(np.median(areas))
    else:
        min_size, max_size, mean_size, median_size = 0, 0, 0.0, 0.0

    # Size distribution breakdown
    size_dist = {
        "dot": 0,       # 1 - 10 px
        "small": 0,     # 11 - 50 px
        "medium": 0,    # 51 - 200 px
        "large": 0,     # 201 - 1000 px
        "plaque": 0     # > 1000 px
    }
    for n in nodules:
        cat = n.get("size_category", "small")
        size_dist[cat] = size_dist.get(cat, 0) + 1
        
    # Nodule density (Nodules per 10,000 pixels²)
    density = float((count / (total_pixels + 1e-5)) * 10000.0)
    
    # Spatial pattern categorization based on area % and nodule density
    if area_percent <= cfg.pattern_sparse_max:
        pattern = "sparse"
    elif area_percent <= cfg.pattern_dispersed_max:
        pattern = "dispersed"
    elif area_percent <= cfg.pattern_clustered_max:
        pattern = "clustered" if count > 15 else "dispersed"
    elif area_percent <= cfg.pattern_dense_max:
        pattern = "dense"
    else:
        pattern = "confluent"

    # Optical density proxy (mean RGB intensity contrast between background and mineralized regions)
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    if mineralized_pixels > 0:
        mean_mineral_intensity = float(np.mean(gray[binary_mask > 0]))
        bg_mask = (binary_mask == 0)
        mean_bg_intensity = float(np.mean(gray[bg_mask])) if np.any(bg_mask) else 255.0
        optical_density = max(0.0, float(np.log10((mean_bg_intensity + 1.0) / (mean_mineral_intensity + 1.0))))
    else:
        optical_density = 0.0

    # Physical micrometer scale calibration (Strictly optional!)
    calibration_info: Dict[str, Any] = {
        "calibrated": False,
        "pixel_size_um": None,
        "unit": "pixels²"
    }
    
    physical_metrics: Dict[str, Any] = {}
    
    if cfg.pixel_size_um is not None and cfg.pixel_size_um > 0:
        px_um2 = cfg.pixel_size_um ** 2
        calibration_info = {
            "calibrated": True,
            "pixel_size_um": cfg.pixel_size_um,
            "unit": "µm²"
        }
        physical_metrics = {
            "mineralized_area_um2": round(mineralized_pixels * px_um2, 2),
            "mean_nodule_size_um2": round(mean_size * px_um2, 2),
            "median_nodule_size_um2": round(median_size * px_um2, 2),
            "min_nodule_size_um2": round(min_size * px_um2, 2),
            "max_nodule_size_um2": round(max_size * px_um2, 2)
        }

    return {
        "mineralized_area_pixels": mineralized_pixels,
        "mineralized_area_percent": round(area_percent, 2),
        "total_image_pixels": total_pixels,
        "nodule_count": count,
        "min_nodule_size_pixels": min_size,
        "max_nodule_size_pixels": max_size,
        "mean_nodule_size_pixels": round(mean_size, 1),
        "median_nodule_size_pixels": round(median_size, 1),
        "nodule_size_distribution": size_dist,
        "mineralization_density_per_10k_px": round(density, 2),
        "spatial_pattern": pattern,
        "optical_density_proxy": round(optical_density, 3),
        "calibration": calibration_info,
        "physical_metrics": physical_metrics
    }
