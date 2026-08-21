import os
import glob
import time
import json
import cv2
import numpy as np

from pipeline import StainScopeCVEngine
from stage0_relevance import check_image_relevance
from stage1_stain_id import identify_stain
from stage2_quality import validate_image_quality

ars_dir = r"C:\final_ppd\StainScope-Ai-Model\ars"
engine = StainScopeCVEngine()
cfg = engine.cfg

files = []
for root, dirs, filenames in os.walk(ars_dir):
    for f in filenames:
        files.append(os.path.join(root, f))

files.sort()

results = []

for filepath in files:
    rel = os.path.relpath(filepath, ars_dir)
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in ['.tif', '.tiff', '.jpg', '.jpeg', '.png']:
        results.append({'file': rel, 'type': 'non_image', 'valid': False, 'stage': 'File Type Gate', 'reason': 'Non-image file format (.ini or .txt)'})
        continue

    bgr = cv2.imread(filepath)
    if bgr is None:
        results.append({'file': rel, 'type': 'image', 'valid': False, 'stage': 'Image Decoder', 'reason': 'cv2.imread decoding error'})
        continue

    h, w = bgr.shape[:2]
    
    r0 = check_image_relevance(bgr, cfg.relevance)
    if not r0['valid']:
        results.append({'file': rel, 'dims': f"{w}x{h}", 'valid': False, 'stage': 'Stage 0 Relevance', 'reason': r0['reason'], 'metrics': r0['metrics']})
        continue

    r1 = identify_stain(bgr, cfg.stain_id)
    if r1['status'] == 'likely_incompatible':
        reason = r1['reasons'][0] if r1['reasons'] else 'Incompatible stain'
        results.append({'file': rel, 'dims': f"{w}x{h}", 'valid': False, 'stage': 'Stage 1 Stain ID', 'reason': reason, 'red_ratio': r1['red_pixel_ratio'], 'blue_ratio': r1['blue_dominance_ratio']})
        continue

    r2 = validate_image_quality(bgr, cfg.quality)
    if not r2['usable']:
        results.append({'file': rel, 'dims': f"{w}x{h}", 'valid': False, 'stage': 'Stage 2 Quality', 'reason': 'Image quality severely degraded', 'warnings': r2['warnings']})
        continue

    results.append({'file': rel, 'dims': f"{w}x{h}", 'valid': True, 'stage': 'Passed Stages 0-2', 'reason': 'Valid ARS microscopy image', 'stain_status': r1['status'], 'confidence': r1['confidence'], 'warnings': r2['warnings']})

with open('ars_stages0_2_diagnostic.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

valid_list = [r for r in results if r.get('valid')]
invalid_list = [r for r in results if not r.get('valid')]

print('Total files scanned:', len(results))
print('Valid images passing Stages 0-2:', len(valid_list))
print('Invalid / Rejected files:', len(invalid_list))
print('\nRejected Breakdown:')
rejection_map = {}
for r in invalid_list:
    key = f"[{r.get('stage', 'File Read')}] {r['reason']}"
    rejection_map[key] = rejection_map.get(key, 0) + 1

for k, v in rejection_map.items():
    print(f" - ({v} files) {k}")
