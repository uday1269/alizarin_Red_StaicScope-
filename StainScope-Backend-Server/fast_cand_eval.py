import os
import glob
import time
import json
import cv2
import numpy as np
import scipy.ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed

from config import NoduleDetectionConfig
from validation import compute_segmentation_metrics, compute_nodule_counting_metrics
from stage3_segmentation import segment_ars

ars_dir = r"c:\final_ppd\StainScope-Ai-Model\ars"
gt_dir = r"c:\final_ppd\StainScope-Ai-Model\dataset_annotated\masks"
gt_files = sorted(glob.glob(os.path.join(gt_dir, "*_mask.png")))

def detect_nodules_opt(image, binary_mask, cfg=NoduleDetectionConfig(), threshold_rel_int=0.45):
    if binary_mask is None or np.count_nonzero(binary_mask) == 0:
        return {"count": 0, "objects": [], "labeled_mask": np.zeros(binary_mask.shape if binary_mask is not None else (100, 100), dtype=np.int32)}

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    mask_bin = (binary_mask > 0).astype(np.uint8) * 255
    mask_bool = binary_mask > 0
    h_img, w_img = gray.shape

    gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
    dist_transform = cv2.distanceTransform(mask_bin, cv2.DIST_L2, 5)
    
    # 1. Distance transform peaks (geometrical centers of blobs/nodules)
    coords_dist = peak_local_max(
        dist_transform,
        min_distance=cfg.min_nodule_distance,
        labels=mask_bool,
        threshold_rel=0.12
    )
    
    # 2. Local intensity minima inside mineralized mask (dark nodule cores)
    # Raising threshold_rel_int to 0.45 filters out 99%+ of noisy micro-peaks in flat plaque interiors!
    inverted_gray = 255 - gray_blur
    coords_int = peak_local_max(
        inverted_gray,
        min_distance=cfg.min_nodule_distance,
        labels=mask_bool,
        threshold_rel=threshold_rel_int
    )

    # Combine peak coordinate markers
    combined_mask = np.zeros(dist_transform.shape, dtype=bool)
    if coords_dist.size > 0:
        combined_mask[coords_dist[:, 0], coords_dist[:, 1]] = True
    if coords_int.size > 0:
        combined_mask[coords_int[:, 0], coords_int[:, 1]] = True

    markers, num_features = ndi.label(combined_mask)
    if num_features == 0:
        num_labels, labels = cv2.connectedComponents(mask_bin)
    else:
        dist_norm = cv2.normalize(dist_transform, None, 0, 255, cv2.NORM_MINMAX).astype(np.float32)
        inv_gray_norm = cv2.normalize(inverted_gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.float32)
        energy_field = -(0.65 * dist_norm + 0.35 * inv_gray_norm)
        labels = watershed(energy_field, markers, mask=mask_bin > 0)

    # Component Filtering & Small Dot Preservation
    nodules = []
    final_labeled_mask = np.zeros_like(labels, dtype=np.int32)
    max_label = int(np.max(labels))
    if max_label == 0:
        return {"count": 0, "objects": [], "labeled_mask": final_labeled_mask}

    label_objects = ndi.find_objects(labels)
    valid_count = 0
    
    for label_idx, obj_slice in enumerate(label_objects, start=1):
        if obj_slice is None: continue
        slice_y, slice_x = obj_slice
        sub_labels = labels[slice_y, slice_x]
        component_mask_sub = (sub_labels == label_idx).astype(np.uint8)
        area = int(np.count_nonzero(component_mask_sub))
        if area < cfg.absolute_min_area: continue
            
        contours, _ = cv2.findContours(component_mask_sub, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: continue
        cnt_sub = contours[0]
        cnt = cnt_sub + np.array([[[slice_x.start, slice_y.start]]], dtype=cnt_sub.dtype)

        M = cv2.moments(cnt_sub)
        if M["m00"] > 0:
            cx = float(M["m10"] / M["m00"]) + slice_x.start
            cy = float(M["m01"] / M["m00"]) + slice_y.start
        else:
            cx = float(cnt_sub[0][0][0] + slice_x.start)
            cy = float(cnt_sub[0][0][1] + slice_y.start)
            
        x, y = slice_x.start, slice_y.start
        w, h = slice_x.stop - slice_x.start, slice_y.stop - slice_y.start

        perimeter = float(cv2.arcLength(cnt_sub, True))
        circularity = float((4.0 * np.pi * area) / (perimeter ** 2 + 1e-5))
        
        y1, y2 = max(0, y - 4), min(h_img, y + h + 4)
        x1, x2 = max(0, x - 4), min(w_img, x + w + 4)
        
        crop_gray = gray[y1:y2, x1:x2]
        crop_mask = (labels[y1:y2, x1:x2] == label_idx)
        nodule_intensity = float(np.mean(crop_gray[crop_mask]))
        bg_pixels = crop_gray[~crop_mask]
        bg_intensity = float(np.mean(bg_pixels)) if bg_pixels.size > 0 else nodule_intensity
        local_contrast = abs(nodule_intensity - bg_intensity)

        if area <= 15:
            is_genuine = (local_contrast >= 7.5) or (circularity >= 0.25)
            if not is_genuine: continue
                
        valid_count += 1
        final_labeled_mask[slice_y, slice_x][sub_labels == label_idx] = valid_count
        nodules.append({
            "id": f"N{valid_count}",
            "label_index": valid_count,
            "area_pixels": area,
            "centroid": (round(cx, 1), round(cy, 1)),
            "bbox": [x, y, w, h],
            "circularity": round(circularity, 3),
            "local_contrast": round(local_contrast, 1),
            "contour": cnt.tolist()
        })

    return {"count": valid_count, "objects": nodules, "labeled_mask": final_labeled_mask}

if __name__ == "__main__":
    t_start = time.time()
    results = []
    for gt_path in gt_files:
        base_name = os.path.basename(gt_path).replace("_mask.png", "")
        cat = base_name.split("_")[0].lower()
        img_path = os.path.join(ars_dir, cat, f"{base_name}.tif")
        if not os.path.exists(img_path): continue
        
        bgr = cv2.imread(img_path)
        gt_mask = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)
        if bgr is None or gt_mask is None: continue
        
        t0 = time.time()
        bin_mask = segment_ars(bgr)
        nodules = detect_nodules_opt(bgr, bin_mask, threshold_rel_int=0.45)
        dt = time.time() - t0
        
        cnt_m = compute_nodule_counting_metrics(gt_mask, nodules["objects"])
        seg_m = compute_segmentation_metrics(gt_mask, bin_mask)
        
        results.append({
            "sample_id": base_name,
            "cat": cat,
            "dice": seg_m["dice"],
            "iou": seg_m["iou"],
            "gt_count": cnt_m["gt_count"],
            "cv_count": cnt_m["cv_count"],
            "abs_err": cnt_m["abs_error"],
            "fp": cnt_m["fp_nodules"],
            "fn": cnt_m["fn_nodules"],
            "dt": dt
        })
        
    tot_time = time.time() - t_start
    m_err = np.mean([r["abs_err"] for r in results])
    med_err = np.median([r["abs_err"] for r in results])
    m_fp = np.mean([r["fp"] for r in results])
    m_fn = np.mean([r["fn"] for r in results])
    m_dice = np.mean([r["dice"] for r in results])
    m_iou = np.mean([r["iou"] for r in results])
    m_dt = np.mean([r["dt"] for r in results])
    
    c7_dt = np.mean([r["dt"] for r in results if r["cat"] == "c7"])
    c8_dt = np.mean([r["dt"] for r in results if r["cat"] == "c8"])
    
    print("\n==================================================")
    print("OPTIMIZED CANDIDATE EVALUATION (72 Ground Truth Images)")
    print(f"Total Benchmark Time: {tot_time:.2f}s")
    print(f"Mean Time per Image:  {m_dt:.3f}s")
    print(f"Mean Nodule Error:    {m_err:.2f} nodules")
    print(f"Median Nodule Error:  {med_err:.2f} nodules")
    print(f"Mean False Positives: {m_fp:.2f} nodules")
    print(f"Mean False Negatives: {m_fn:.2f} nodules")
    print(f"Mean Dice Score:      {m_dice:.4f}")
    print(f"Mean IoU Score:       {m_iou:.4f}")
    print(f"C7 Mean Image Time:   {c7_dt:.3f}s")
    print(f"C8 Mean Image Time:   {c8_dt:.3f}s")
    print("==================================================")
    
    with open("opt_candidate_72_results.json", "w") as f:
        json.dump({"summary": {
            "total_samples": len(results),
            "mean_count_error": round(float(m_err), 2),
            "median_count_error": round(float(med_err), 2),
            "mean_fp": round(float(m_fp), 2),
            "mean_fn": round(float(m_fn), 2),
            "mean_dice": round(float(m_dice), 4),
            "mean_iou": round(float(m_iou), 4),
            "mean_time_sec": round(float(m_dt), 3),
            "c7_mean_time": round(float(c7_dt), 3),
            "c8_mean_time": round(float(c8_dt), 3),
            "total_time_sec": round(float(tot_time), 2)
        }, "samples": results}, f, indent=2)
