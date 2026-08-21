"""
Unit & Integration Test Suite for StainScope Classical CV Engine.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import numpy as np
import cv2

from config import CVEngineConfig

from stage0_relevance import check_image_relevance
from stage1_stain_id import identify_stain
from stage2_quality import validate_image_quality
from stage3_segmentation import segment_ars
from stage4_nodule_detection import detect_nodules
from stage5_quantification import quantify_mineralization
from pipeline import StainScopeCVEngine


@pytest.fixture
def sample_ars_image():
    """Generates a synthetic ARS microscopy image with background and red nodules."""
    img = np.ones((300, 400, 3), dtype=np.uint8) * 220 # Light background
    
    # Add a few distinct red mineralization nodules (BGR format: low B, low G, high R)
    cv2.circle(img, (100, 100), 12, (20, 30, 210), -1) # Nodule 1
    cv2.circle(img, (250, 150), 8, (15, 25, 200), -1)  # Nodule 2
    cv2.circle(img, (260, 150), 7, (15, 25, 200), -1)  # Touching Nodule 3
    cv2.circle(img, (180, 220), 2, (10, 20, 190), -1)  # Tiny dot 4
    
    return img


@pytest.fixture
def non_ars_blue_image():
    """Generates a synthetic blue DAPI stained image."""
    img = np.ones((300, 400, 3), dtype=np.uint8) * 20
    # High blue channel
    img[:, :, 0] = 230
    return img


def test_stage0_relevance_gate(sample_ars_image):
    # Valid microscopy image
    res = check_image_relevance(sample_ars_image)
    assert res["valid"] is True
    
    # Invalid low resolution
    tiny_img = np.ones((50, 50, 3), dtype=np.uint8)
    res_tiny = check_image_relevance(tiny_img)
    assert res_tiny["valid"] is False
    assert "dimensions" in res_tiny["reason"]

    # Blank image
    blank = np.ones((300, 400, 3), dtype=np.uint8) * 128
    res_blank = check_image_relevance(blank)
    assert res_blank["valid"] is False


def test_stage1_stain_identification(sample_ars_image, non_ars_blue_image):
    res_ars = identify_stain(sample_ars_image)
    assert res_ars["status"] == "ARS-compatible"
    
    res_blue = identify_stain(non_ars_blue_image)
    assert res_blue["status"] == "likely_incompatible"


def test_stage3_and_4_nodule_detection(sample_ars_image):
    mask = segment_ars(sample_ars_image)
    assert np.count_nonzero(mask) > 0
    
    nodule_res = detect_nodules(sample_ars_image, mask)
    assert nodule_res["count"] >= 3 # Should detect isolated nodules, touching nodules, and tiny dot
    assert len(nodule_res["objects"]) == nodule_res["count"]
    assert nodule_res["objects"][0]["id"].startswith("N")


def test_stage5_quantification_uncalibrated_vs_calibrated(sample_ars_image):
    mask = segment_ars(sample_ars_image)
    nodules = detect_nodules(sample_ars_image, mask)
    
    # Default uncalibrated -> pixels²
    quant = quantify_mineralization(sample_ars_image, mask, nodules)
    assert quant["calibration"]["calibrated"] is False
    assert quant["calibration"]["unit"] == "pixels²"
    assert "mineralized_area_um2" not in quant["physical_metrics"]

    # Explicit calibration -> µm²
    cfg = CVEngineConfig()
    cfg.quantification.pixel_size_um = 0.5
    quant_cal = quantify_mineralization(sample_ars_image, mask, nodules, cfg=cfg.quantification)
    assert quant_cal["calibration"]["calibrated"] is True
    assert quant_cal["calibration"]["unit"] == "µm²"
    assert quant_cal["physical_metrics"]["mineralized_area_um2"] > 0


def test_full_pipeline_orchestration(sample_ars_image, non_ars_blue_image):
    engine = StainScopeCVEngine()
    
    # Valid ARS image
    res = engine.analyze_image(sample_ars_image)
    assert res["valid"] is True
    assert "mineralization" in res
    assert "nodules" in res
    assert res["nodules"]["count"] > 0
    assert "overlays" not in res # visualizations present before API formatting
    assert "validation_panel" in res["visualizations"]
    
    # Incompatible image rejection
    res_invalid = engine.analyze_image(non_ars_blue_image)
    assert res_invalid["valid"] is False
    assert "reason" in res_invalid
