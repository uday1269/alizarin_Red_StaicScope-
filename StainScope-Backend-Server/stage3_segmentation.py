"""
STAGE 3 — ARS Mineralization Segmentation
Classical CV segmentation engine with adaptive thresholding & color space transformations.
Designed with a modular interface `segment_ars(image, method="classical")` allowing seamless
future replacement with U-Net without modifying downstream quantification or API layers.
"""
from typing import Optional
import cv2
import numpy as np
from config import SegmentationConfig


def segment_ars(
    image: np.ndarray,
    method: str = "classical",
    cfg: SegmentationConfig = SegmentationConfig()
) -> np.ndarray:
    """
    Segments ARS-positive mineralization regions in a microscopy image.
    
    Args:
        image: BGR numpy image array.
        method: Segmentation method ("classical" or "unet").
        cfg: SegmentationConfig object with tuning parameters.
        
    Returns:
        np.ndarray: Binary mask (255 for mineralized pixels, 0 for background).
    """
    if method == "unet":
        # Interface placeholder for future Deep Learning U-Net replacement
        raise NotImplementedError("U-Net model mode will be activated in future StainScope-Ai-Model integration.")
        
    if len(image.shape) == 2:
        bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    else:
        bgr = image.copy()

    # Step 1: Illumination Normalization in Lab color space
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=cfg.clahe_clip_limit, tileGridSize=cfg.clahe_tile_grid)
    cl_channel = clahe.apply(l_channel)
    lab_norm = cv2.merge([cl_channel, a_channel, b_channel])
    bgr_norm = cv2.cvtColor(lab_norm, cv2.COLOR_LAB2BGR)
    
    # Step 2: Color Space Transformations
    hsv = cv2.cvtColor(bgr_norm, cv2.COLOR_BGR2HSV)
    
    # Red/Orange Hue Masking in HSV (handling 0-180 wrap-around)
    lower_red1 = np.array([0, 25, 30])
    upper_red1 = np.array([24, 255, 255])
    lower_red2 = np.array([150, 25, 30])
    upper_red2 = np.array([180, 255, 255])
    
    hsv_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    hsv_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    hsv_red_mask = cv2.bitwise_or(hsv_mask1, hsv_mask2)
    
    # Step 3: Lab a* Channel Dominance Analysis
    # In Lab, high positive a* indicates strong red/magenta saturation
    a_mean = float(np.mean(a_channel))
    a_std = float(np.std(a_channel))
    
    # Adaptive threshold on a* channel based on image statistics
    a_thresh_val = max(130.0, a_mean + 0.4 * a_std)
    _, lab_a_mask = cv2.threshold(a_channel, int(a_thresh_val), 255, cv2.THRESH_BINARY)
    
    # Step 4: Adaptive Otsu / Local Thresholding on Gray Intensity Contrast
    gray_norm = cv2.cvtColor(bgr_norm, cv2.COLOR_BGR2GRAY)
    inverted_gray = cv2.bitwise_not(gray_norm) # Mineralized dots are typically darker than light background
    
    # Otsu thresholding on contrast-inverted image
    _, otsu_mask = cv2.threshold(inverted_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Step 5: Adaptive Fusion of HSV, Lab, and Contrast Features
    # Red hue + strong a* dominance OR (strong red hue + Otsu contrast)
    color_fusion = cv2.bitwise_and(hsv_red_mask, lab_a_mask)
    adaptive_mineral_mask = cv2.bitwise_or(color_fusion, cv2.bitwise_and(hsv_red_mask, otsu_mask))
    
    # Step 6: Morphological Refining (Fill minor pinholes, smooth edges slightly without shrinking dots)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (cfg.morph_kernel_size, cfg.morph_kernel_size))
    cleaned_mask = cv2.morphologyEx(adaptive_mineral_mask, cv2.MORPH_CLOSE, kernel)
    
    return cleaned_mask
