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

ars_dir = r"c:\final_ppd\StainScope-Ai-Model\ars"
gt_dir = r"c:\final_ppd\StainScope-Ai-Model\dataset_annotated\masks"
gt_files = sorted(glob.glob(os.path.join(gt_dir, "*_mask.png")))

def detect_nodules_candidate(image, binary_mask, cfg=NoduleDetectionConfig(), mode="cand_a"):
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
    
    # 1. Distance transform peaks
    coords_dist = peak_local_max(
        dist_transform,
        min_distance=cfg.min_nodule_distance,
        labels=mask_bool,
        threshold_rel=0.12
    )
    
    # 2. Local intensity minima inside mineralized mask (dark nodule cores)
    inverted_gray = 255 - gray_blur
    
    if mode == "baseline":
        coords_int = peak_local_max(
            inverted_gray,
            min_distance=cfg.min_nodule_distance,
            labels=mask_bool,
            threshold_rel=0.16
        )
    elif mode == "cand_a":
        # Filter intensity peaks by requiring relative intensity threshold of 0.45 inside mineralized regions
        coords_int = peak_local_max(
            inverted_gray,
            min_distance=cfg.min_nodule_distance,
            labels=mask_bool,
            threshold_rel=0.45
        )
    elif mode == "cand_b":
        # Require intensity peaks to have absolute intensity value > mean(inverted_gray[mask_bool]) + 0.2*std
        mean_val = np.mean(inverted_gray[mask_bool])
        std_val = np.std(inverted_gray[mask_bool])
        thresh_abs = mean_val + 0.2 * std_val
        coords_int = peak_local_max(
            inverted_gray,
            min_distance=cfg.min_nodule_distance,
            labels=mask_bool,
            threshold_abs=thresh_abs
        )
    elif mode == "cand_c":
        # Scale min_distance for intensity peaks dynamically in deep plaque interiors (dist_transform > 6)
        # For dist_transform <= 6 (normal/small nodules), min_distance = 3
        # For dist_transform > 6 (deep inside giant plaques), min_distance = 8
        coords_int_raw = peak_local_max(
            inverted_gray,
            min_distance=cfg.min_nodule_distance,
            labels=mask_bool,
            threshold_rel=0.35
        )
        if coords_int_raw.size > 0:
            d_vals = dist_transform[coords_int_raw[:, 0], coords_int_raw[:, 1]]
            # Prune intensity peaks inside deep plaque interiors if too close to another peak
            keep_mask = d_vals <= 8.0 # Keep all peaks near borders/nodules
            deep_coords = coords_int_raw[d_vals > 8.0]
            if deep_coords.size > 0:
                # Subsample deep plaque peaks
                sub_indices = np.linspace(0, len(deep_coords)-1, num=min(len(deep_coords), 200), dtype=int)
                keep_deep = np.zeros(len(deep_coords), dtype=bool)
                if len(deep_coords) > 0:
                    keep_deep[sub_indices] = True
                keep_mask = np.concatenate([keep_mask[d_vals <= 8.0], keep_deep])
            coords_int = coords_int_raw[keep_mask] if len(keep_mask) == len(coords_int_raw) else coords_int_raw
        else:
            coords_int = coords_int_raw

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
    from stage3_segmentation import segment_ars
    
    modes = ["baseline", "cand_a", "cand_b"]
    
    for mode in modes:
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
            nodules = detect_nodules_candidate(bgr, bin_mask, mode=mode)
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
        
        print(f"\n=== MODE: {mode.upper()} ===")
        print(f"Total time: {tot_time:.2f}s | Mean per image: {m_dt:.3f}s")
        print(f"Mean Count Error: {m_err:.2f} | Median: {med_err:.2f} | FP: {m_fp:.2f} | FN: {m_fn:.2f}")
        print(f"Mean Dice: {m_dice:.4f} | Mean IoU: {m_iou:.4f}")
        print(f"Category C7 Mean Time: {c7_dt:.3f}s | Category C8 Mean Time: {c8_dt:.3f}s")
