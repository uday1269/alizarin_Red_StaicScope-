"""
Validation & Evaluation Benchmark Suite for StainScope Classical CV Engine.
Evaluates classical CV segmentation & nodule counting against all ground-truth ARS masks.
Computes Dice, IoU, Nodule Count Error, False Positives, False Negatives, and generates 4-panel visual comparison sheets.
"""
from typing import Dict, Any, List, Optional, Tuple
import os
import glob
import json
import cv2
import numpy as np

from pipeline import StainScopeCVEngine


def compute_segmentation_metrics(gt_mask: np.ndarray, cv_mask: np.ndarray) -> Dict[str, float]:
    """
    Computes Dice, IoU, Precision, and Recall between binary ground-truth and CV masks.
    """
    gt_bin = (gt_mask > 0).astype(np.uint8)
    cv_bin = (cv_mask > 0).astype(np.uint8)
    
    intersection = float(np.sum(gt_bin & cv_bin))
    total_gt = float(np.sum(gt_bin))
    total_cv = float(np.sum(cv_bin))
    
    dice = (2.0 * intersection) / (total_gt + total_cv + 1e-5)
    iou = intersection / (total_gt + total_cv - intersection + 1e-5)
    precision = intersection / (total_cv + 1e-5)
    recall = intersection / (total_gt + 1e-5)
    
    return {
        "dice": round(float(dice), 4),
        "iou": round(float(iou), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4)
    }


def compute_nodule_counting_metrics(
    gt_mask: np.ndarray,
    cv_nodules: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes Ground Truth nodule count, CV nodule count, False Positives, and False Negatives.
    Uses connected components on GT mask as GT nodule entities and checks spatial overlap.
    """
    gt_bin = (gt_mask > 0).astype(np.uint8)
    num_gt_labels, gt_labels = cv2.connectedComponents(gt_bin)
    gt_count = max(0, num_gt_labels - 1)
    cv_count = len(cv_nodules)
    
    if gt_count == 0:
        return {
            "gt_count": 0,
            "cv_count": cv_count,
            "fp_nodules": cv_count,
            "fn_nodules": 0,
            "abs_error": cv_count
        }

    # Track which GT nodules are matched by at least one detected CV nodule
    matched_gt = set()
    matched_cv = set()
    
    for idx, nodule in enumerate(cv_nodules):
        cx, cy = int(nodule["centroid"][0]), int(nodule["centroid"][1])
        # Ensure centroid is inside bounds
        cy_clamped = min(gt_labels.shape[0] - 1, max(0, cy))
        cx_clamped = min(gt_labels.shape[1] - 1, max(0, cx))
        
        gt_label_val = gt_labels[cy_clamped, cx_clamped]
        if gt_label_val > 0:
            matched_gt.add(gt_label_val)
            matched_cv.add(idx)
        else:
            # Check bounding box region for overlap with GT
            x, y, w, h = nodule["bbox"]
            sub_gt = gt_labels[max(0, y):min(gt_labels.shape[0], y+h), max(0, x):min(gt_labels.shape[1], x+w)]
            vals = sub_gt[sub_gt > 0]
            if vals.size > 0:
                # Assign to most frequent GT label in bbox
                most_freq = int(np.bincount(vals).argmax())
                matched_gt.add(most_freq)
                matched_cv.add(idx)

    fp_nodules = cv_count - len(matched_cv) # Detected nodules that don't match GT nodules
    fn_nodules = gt_count - len(matched_gt) # GT nodules missed by CV detector
    abs_error = abs(cv_count - gt_count)

    return {
        "gt_count": gt_count,
        "cv_count": cv_count,
        "fp_nodules": fp_nodules,
        "fn_nodules": fn_nodules,
        "abs_error": abs_error
    }


def run_benchmark(
    ars_dataset_dir: str = r"c:\final_ppd\StainScope-Ai-Model\ars",
    gt_masks_dir: str = r"c:\final_ppd\StainScope-Ai-Model\dataset_annotated\masks",
    output_dir: Optional[str] = None,
    max_samples: Optional[int] = None
) -> Dict[str, Any]:
    """
    Runs full evaluation benchmark across all ground truth samples.
    """
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "output", "validation"))
    else:
        output_dir = os.path.abspath(output_dir)
        
    os.makedirs(output_dir, exist_ok=True)
    engine = StainScopeCVEngine()
    
    gt_mask_files = sorted(glob.glob(os.path.join(gt_masks_dir, "*_mask.png")))
    if not gt_mask_files:
        raise FileNotFoundError(f"No ground truth mask files found in {gt_masks_dir}")

    results: List[Dict[str, Any]] = []
    processed = 0
    
    print(f"Starting full benchmark on {len(gt_mask_files)} ground-truth samples...")
    
    for gt_path in gt_mask_files:
        if max_samples and processed >= max_samples:
            break
            
        base_name = os.path.basename(gt_path).replace("_mask.png", "")
        img_path = None
        for category in [f"c{i}" for i in range(1, 9)]:
            candidate = os.path.join(ars_dataset_dir, category, f"{base_name}.tif")
            if os.path.exists(candidate):
                img_path = candidate
                break
                
        if img_path is None or not os.path.exists(img_path):
            continue

        bgr = cv2.imread(img_path)
        gt_mask = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)
        
        if bgr is None or gt_mask is None:
            continue
            
        analysis = engine.analyze_image(bgr, gt_mask=gt_mask, generate_images=True)
        if not analysis.get("valid", False):
            continue
            
        cv_mask = analysis["binary_mask_raw"]
        cv_nodules = analysis["nodules"]["objects"]
        
        seg_metrics = compute_segmentation_metrics(gt_mask, cv_mask)
        count_metrics = compute_nodule_counting_metrics(gt_mask, cv_nodules)
        
        sample_res = {
            "sample_id": base_name,
            "metrics": seg_metrics,
            "gt_nodule_count": count_metrics["gt_count"],
            "cv_nodule_count": count_metrics["cv_count"],
            "count_abs_error": count_metrics["abs_error"],
            "fp_nodules": count_metrics["fp_nodules"],
            "fn_nodules": count_metrics["fn_nodules"],
            "mineralized_area_percent": analysis["mineralization"]["area_percent"],
            "quality_warnings": analysis["image_quality"]["warnings"]
        }
        results.append(sample_res)
        
        # Save visual 4-panel comparison sheet
        vis_panel = analysis["visualizations"]["validation_panel"]
        panel_out_path = os.path.normpath(os.path.join(output_dir, f"{base_name}_val_panel.png"))
        success = cv2.imwrite(panel_out_path, vis_panel)
        if not success:
            print(f"Warning: Failed to write image panel to {panel_out_path}")
        
        processed += 1

    if not results:
        return {"error": "No matching image-mask pairs processed."}

    # Sort results by nodule count error descending (worst-case first)
    results.sort(key=lambda x: x["count_abs_error"], reverse=True)

    avg_dice = float(np.mean([r["metrics"]["dice"] for r in results]))
    avg_iou = float(np.mean([r["metrics"]["iou"] for r in results]))
    avg_precision = float(np.mean([r["metrics"]["precision"] for r in results]))
    avg_recall = float(np.mean([r["metrics"]["recall"] for r in results]))
    avg_count_error = float(np.mean([r["count_abs_error"] for r in results]))
    avg_fp = float(np.mean([r["fp_nodules"] for r in results]))
    avg_fn = float(np.mean([r["fn_nodules"] for r in results]))
    
    summary = {
        "total_validated_samples": len(results),
        "mean_dice": round(avg_dice, 4),
        "mean_iou": round(avg_iou, 4),
        "mean_precision": round(avg_precision, 4),
        "mean_recall": round(avg_recall, 4),
        "mean_nodule_count_abs_error": round(avg_count_error, 2),
        "mean_fp_nodules": round(avg_fp, 2),
        "mean_fn_nodules": round(avg_fn, 2),
        "worst_case_samples": results[:10],
        "all_samples": results
    }
    
    report_path = os.path.normpath(os.path.join(output_dir, "benchmark_report.json"))
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print(f"\nFull Benchmark Completed! Validated {len(results)} samples.")
    print(f"Report written to: {report_path}")
    print(f"Mean Dice: {round(avg_dice, 4)} | Mean IoU: {round(avg_iou, 4)}")
    print(f"Mean Nodule Count Error: {round(avg_count_error, 2)} nodules")
    print(f"Mean False Positives: {round(avg_fp, 2)} | Mean False Negatives: {round(avg_fn, 2)}")
    
    return summary


if __name__ == "__main__":
    run_benchmark()
