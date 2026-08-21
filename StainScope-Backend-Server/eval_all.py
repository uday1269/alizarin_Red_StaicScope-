
import os, glob, json, cv2
import numpy as np
from pipeline import StainScopeCVEngine
from validation import compute_segmentation_metrics, compute_nodule_counting_metrics

engine = StainScopeCVEngine()
gt_files = sorted(glob.glob(r'c:\final_ppd\StainScope-Ai-Model\dataset_annotated\masks\*_mask.png'))
results = []
for gt_path in gt_files:
    base = os.path.basename(gt_path).replace('_mask.png', '')
    img_path = None
    for c in [f'c{i}' for i in range(1, 9)]:
        p = os.path.join(r'c:\final_ppd\StainScope-Ai-Model\ars', c, f'{base}.tif')
        if os.path.exists(p): img_path = p; break
    if not img_path: continue
    bgr = cv2.imread(img_path)
    gt_mask = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)
    res = engine.analyze_image(bgr, gt_mask=gt_mask, generate_images=False)
    if not res.get('valid', False): continue
    cv_mask = res['binary_mask_raw']
    cv_nodules = res['nodules']['objects']
    sm = compute_segmentation_metrics(gt_mask, cv_mask)
    cm = compute_nodule_counting_metrics(gt_mask, cv_nodules)
    gt_mineralized_px = int((gt_mask > 0).sum())
    gt_area_pct = round((gt_mineralized_px / gt_mask.size) * 100.0, 2)
    results.append({
        'sample_id': base,
        'gt_count': cm['gt_count'],
        'cv_count': cm['cv_count'],
        'abs_err': cm['abs_error'],
        'fp': cm['fp_nodules'],
        'fn': cm['fn_nodules'],
        'gt_area_pct': gt_area_pct,
        'cv_area_pct': res['mineralization']['area_percent'],
        'dice': sm['dice'],
        'iou': sm['iou']
    })

with open('eval_full.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'Done! Successfully evaluated {len(results)} samples.')
