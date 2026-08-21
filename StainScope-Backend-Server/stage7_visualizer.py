"""
STAGE 7 — Visual Output & Nodule Validation Panel Generator
Generates:
1. Binary Mineralization Mask
2. Mineralization Overlay
3. Nodule Detection Map with explicit ID labels (N1, N2, N3...)
4. Multi-panel Ground Truth vs CV comparison sheets for manual count verification
"""
from typing import Dict, Any, Optional
import cv2
import numpy as np


def generate_visualizations(
    image: np.ndarray,
    binary_mask: np.ndarray,
    nodule_data: Dict[str, Any],
    gt_mask: Optional[np.ndarray] = None
) -> Dict[str, np.ndarray]:
    """
    Generates annotated visualization graphics for researchers.
    
    Returns:
        dict: {
            "mask": np.ndarray (uint8),
            "overlay": np.ndarray (BGR uint8),
            "nodule_map": np.ndarray (BGR uint8),
            "contour_map": np.ndarray (BGR uint8),
            "validation_panel": np.ndarray (BGR uint8 - 4-panel image)
        }
    """
    if len(image.shape) == 2:
        bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        bgr = image.copy()
        
    h, w = bgr.shape[:2]
    
    # 1. Binary Mask (3-channel uint8 for display consistency)
    mask_3ch = cv2.cvtColor((binary_mask > 0).astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
    
    # 2. Mineralization Red Overlay
    overlay = bgr.copy()
    red_tint = np.zeros_like(bgr)
    red_tint[:, :] = (0, 0, 230) # Bright red in BGR
    
    mineral_pixels = binary_mask > 0
    overlay[mineral_pixels] = cv2.addWeighted(bgr[mineral_pixels], 0.5, red_tint[mineral_pixels], 0.5, 0)

    # 3. Nodule Detection Map with IDs (N1, N2, N3...)
    nodule_map = bgr.copy()
    nodules = nodule_data.get("objects", [])
    count = nodule_data.get("count", 0)
    
    # Draw header banner at top
    banner_height = 40
    banner = np.zeros((banner_height, w, 3), dtype=np.uint8)
    cv2.putText(
        banner,
        f"Detected Nodules: {count}  |  Objects Labeled: N1..N{count}",
        (15, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )
    
    # Draw centroids, bounding boxes, and ID labels
    font_scale = max(0.35, min(0.65, w / 1000.0))
    for n in nodules:
        nid = n["id"]
        cx, cy = int(n["centroid"][0]), int(n["centroid"][1])
        x, y, bw, bh = n["bbox"]
        
        # Bounding box in yellow/green
        cv2.rectangle(nodule_map, (x, y), (x + bw, y + bh), (0, 220, 255), 1)
        # Centroid dot in red
        cv2.circle(nodule_map, (cx, cy), 2, (0, 0, 255), -1)
        # Text label (N1, N2, N3...) in white with dark background offset
        label_pos = (max(2, x - 2), max(12, y - 4))
        cv2.putText(nodule_map, nid, label_pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(nodule_map, nid, label_pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1, cv2.LINE_AA)

    # 4. Contour Map
    contour_map = bgr.copy()
    contours, _ = cv2.findContours((binary_mask > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(contour_map, contours, -1, (0, 255, 0), 2)

    # 5. Build 4-Panel Validation Graphic for manual inspection
    # Resize components to uniform tile size
    tile_w, tile_h = 480, 360
    
    p1 = cv2.resize(bgr, (tile_w, tile_h))
    cv2.putText(p1, "1. Original Image", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    if gt_mask is not None:
        gt_disp = cv2.cvtColor((gt_mask > 0).astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
        p2 = cv2.resize(gt_disp, (tile_w, tile_h))
        cv2.putText(p2, "2. Ground Truth Mask", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        p2 = cv2.resize(overlay, (tile_w, tile_h))
        cv2.putText(p2, "2. ARS Red Overlay", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

    p3 = cv2.resize(mask_3ch, (tile_w, tile_h))
    cv2.putText(p3, "3. Classical CV Mask", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    p4 = cv2.resize(nodule_map, (tile_w, tile_h))
    cv2.putText(p4, f"4. Detected Nodules (Count={count})", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Combine 2x2 grid
    top_row = np.hstack([p1, p2])
    bot_row = np.hstack([p3, p4])
    validation_panel = np.vstack([top_row, bot_row])

    return {
        "mask": mask_3ch,
        "overlay": overlay,
        "nodule_map": nodule_map,
        "contour_map": contour_map,
        "validation_panel": validation_panel
    }
