"""
Evaluation benchmark runner.
Executes classical CV engine over all 72 ground-truth images, computes detailed error metrics,
identifies worst-case images, and saves visual comparison panels.
"""
import os
import glob
import json
import cv2
import numpy as np

from pipeline import StainScopeCVEngine
from validation import compute_segmentation_metrics, compute_nodule_counting_metrics

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    ars_dir = r"c:\final_ppd\StainScope-Ai-Model\ars"
    gt_dir = r"c:\final_ppd\StainScope-Ai-Model\dataset_annotated\masks"
    out_dir = os.path.join(root_dir, "output_eval")
    os.makedirs(out_dir, exist_ok=True)
    
    gt_files = sorted(glob.glob(os.path.join(gt_dir, "*_mask.png")))
    print(f"Loaded {len(gt_files)} ground truth mask files.")
    
    engine = StainScopeCVEngine()
    results = []
    
    for gt_path in gt_files:
        base_name = os.path.basename(gt_path).replace("_mask.png", "")
        img_path = None
        for category in [f"c{i}" for i in range(1, 9)]:
            cand = os.path.join(ars_dir, category, f"{base_name}.tif")
            if os.path.exists(cand):
                img_path = cand
                break
        if not img_path:
            continue
            
        bgr = cv2.imread(img_path)
        gt_mask = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)
        if bgr is None or gt_mask is None:
            continue
            
        res = engine.analyze_image(bgr, gt_mask=gt_mask, generate_images=True)
        if not res.get("valid", False):
            continue
            
        cv_mask = res["binary_mask_raw"]
        cv_nodules = res["nodules"]["objects"]
        
        seg_m = compute_segmentation_metrics(gt_mask, cv_mask)
        cnt_m = compute_nodule_counting_metrics(gt_mask, cv_nodules)
        
        item = {
            "sample_id": base_name,
            "metrics": seg_m,
            "gt_nodule_count": cnt_m["gt_count"],
            "cv_nodule_count": cnt_m["cv_count"],
            "count_abs_error": cnt_m["abs_error"],
            "fp_nodules": cnt_m["fp_nodules"],
            "fn_nodules": cnt_m["fn_nodules"],
            "area_percent": res["mineralization"]["area_percent"]
        }
        results.append(item)
        
        vis_panel = res["visualizations"]["validation_panel"]
        cv2.imwrite(os.path.join(out_dir, f"{base_name}_val_panel.png"), vis_panel)

    results.sort(key=lambda x: x["count_abs_error"], reverse=True)
    
    summary = {
        "total_samples": len(results),
        "mean_dice": round(float(np.mean([r["metrics"]["dice"] for r in results])), 4),
        "mean_iou": round(float(np.mean([r["metrics"]["iou"] for r in results])), 4),
        "mean_count_error": round(float(np.mean([r["count_abs_error"] for r in results])), 2),
        "mean_fp": round(float(np.mean([r["fp_nodules"] for r in results])), 2),
        "mean_fn": round(float(np.mean([r["fn_nodules"] for r in results])), 2),
        "worst_case_samples": results[:10],
        "all_samples": results
    }
    
    with open(os.path.join(out_dir, "eval_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print("\n==================================================")
    print("EVALUATION BENCHMARK COMPLETED SUCCESSFULLY!")
    print(f"Total Samples:       {summary['total_samples']}")
    print(f"Mean Dice Score:     {summary['mean_dice']}")
    print(f"Mean IoU Score:      {summary['mean_iou']}")
    print(f"Mean Nodule Error:   {summary['mean_count_error']} nodules")
    print(f"Mean False Positives:{summary['mean_fp']} nodules")
    print(f"Mean False Negatives:{summary['mean_fn']} nodules")
    print("==================================================")
    print("TOP 10 WORST-CASE SAMPLES BY NODULE COUNT ERROR:")
    for idx, s in enumerate(summary['worst_case_samples'], 1):
        print(f"{idx:2d}. {s['sample_id']:<22} | GT: {s['gt_nodule_count']:3d} | CV: {s['cv_nodule_count']:3d} | Err: {s['count_abs_error']:3d} | FP: {s['fp_nodules']:2d} | FN: {s['fn_nodules']:2d} | Dice: {s['metrics']['dice']:.4f}")

if __name__ == "__main__":
    main()
