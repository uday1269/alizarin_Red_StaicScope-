import os
import glob
import time
import json
import cv2
import numpy as np
import scipy.ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed

from pipeline import StainScopeCVEngine
from validation import compute_segmentation_metrics, compute_nodule_counting_metrics

ars_dir = r"c:\final_ppd\StainScope-Ai-Model\ars"
gt_dir = r"c:\final_ppd\StainScope-Ai-Model\dataset_annotated\masks"
gt_files = sorted(glob.glob(os.path.join(gt_dir, "*_mask.png")))

print(f"Loaded {len(gt_files)} ground truth files for benchmarking.")

# Test image list: 1 image from each category + full 72 run
sample_cases = ["C1_D28_4x_BF_01", "C2_D28_4x_BF_01", "C3_D28_4x_BF_01", "C4_D28_4x_BF_01", 
                "C5_D28_4x_BF_01", "C6_D28_4x_BF_01", "C7_D28_4x_BF_01", "C8_D28_4x_BF_01"]

for name in sample_cases:
    gt_path = os.path.join(gt_dir, f"{name}_mask.png")
    cat = name.split("_")[0].lower()
    img_path = os.path.join(ars_dir, cat, f"{name}.tif")
    if not os.path.exists(img_path) or not os.path.exists(gt_path):
        continue
    
    bgr = cv2.imread(img_path)
    gt_mask = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)
    
    # Baseline
    engine = StainScopeCVEngine()
    t0 = time.time()
    res = engine.analyze_image(bgr, generate_images=False)
    dt = time.time() - t0
    
    cnt_m = compute_nodule_counting_metrics(gt_mask, res["nodules"]["objects"])
    seg_m = compute_segmentation_metrics(gt_mask, res["binary_mask_raw"])
    
    print(f"[{name}] Base Time: {dt:.2f}s | GT: {cnt_m['gt_count']} | CV: {cnt_m['cv_count']} | Err: {cnt_m['abs_error']} | Dice: {seg_m['dice']:.4f}")
