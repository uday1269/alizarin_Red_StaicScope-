"""
Script to inspect benchmark validation results and print worst-case sample breakdown.
"""
import os
import json

report_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "output", "validation", "benchmark_report.json"))
with open(report_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("==================================================")
print("BASELINE BENCHMARK SUMMARY (72 SAMPLES)")
print("==================================================")
print(f"Total Validated Samples: {data['total_validated_samples']}")
print(f"Mean Dice Score:         {data['mean_dice']}")
print(f"Mean IoU:                {data['mean_iou']}")
print(f"Mean Nodule Count Error: {data['mean_nodule_count_abs_error']} nodules")
print(f"Mean False Positives:    {data['mean_fp_nodules']} nodules")
print(f"Mean False Negatives:    {data['mean_fn_nodules']} nodules")
print("==================================================")
print("TOP 10 WORST-CASE SAMPLES BY NODULE COUNT ERROR:")
print("==================================================")

for idx, s in enumerate(data['worst_case_samples'], 1):
    sid = s['sample_id']
    gt = s['gt_nodule_count']
    cv = s['cv_nodule_count']
    err = s['count_abs_error']
    fp = s['fp_nodules']
    fn = s['fn_nodules']
    dice = s['metrics']['dice']
    print(f"{idx:2d}. {sid:<25} | GT: {gt:3d} | CV: {cv:3d} | Err: {err:3d} | FP: {fp:2d} | FN: {fn:2d} | Dice: {dice:.4f}")
