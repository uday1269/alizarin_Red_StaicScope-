"""
StainScope Classical Computer Vision Pipeline Orchestrator.
Links Stage 0 through Stage 7 into a single unified analysis workflow.
Supports single image processing and multi-image comparative sample analysis.
"""
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np

from config import CVEngineConfig
from stage0_relevance import check_image_relevance
from stage1_stain_id import identify_stain
from stage2_quality import validate_image_quality
from stage3_segmentation import segment_ars
from stage4_nodule_detection import detect_nodules
from stage5_quantification import quantify_mineralization
from stage6_confidence import assess_confidence
from stage7_visualizer import generate_visualizations


class StainScopeCVEngine:
    """
    Standalone ARS Microscopy Analysis Engine.
    """
    def __init__(self, config: Optional[CVEngineConfig] = None):
        self.cfg = config or CVEngineConfig()
        
    def analyze_image(
        self,
        image: np.ndarray,
        pixel_size_um: Optional[float] = None,
        gt_mask: Optional[np.ndarray] = None,
        generate_images: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete Stage 0 to Stage 7 pipeline on a single microscopy image.
        
        Args:
            image: BGR numpy image array.
            pixel_size_um: Optional physical scale calibration (µm per pixel).
            gt_mask: Optional ground truth binary mask array for validation benchmark.
            generate_images: Whether to include generated visualization image arrays.
            
        Returns:
            dict: Comprehensive structured analysis result.
        """
        # Override scale calibration if provided
        if pixel_size_um is not None:
            self.cfg.quantification.pixel_size_um = pixel_size_um
            
        # STAGE 0 — Relevance Gate
        rel_res = check_image_relevance(image, self.cfg.relevance)
        if not rel_res["valid"]:
            return {
                "valid": False,
                "reason": rel_res["reason"],
                "relevance_metrics": rel_res["metrics"]
            }

        # STAGE 1 — Stain Identification
        stain_res = identify_stain(image, self.cfg.stain_id)
        if stain_res["status"] == "likely_incompatible":
            return {
                "valid": False,
                "reason": stain_res["reasons"][0] if stain_res["reasons"] else "Image is incompatible with ARS staining.",
                "stain": stain_res
            }

        # STAGE 2 — Quality Validation
        quality_res = validate_image_quality(image, self.cfg.quality)
        if not quality_res["usable"]:
            return {
                "valid": False,
                "reason": "Image quality is too severely degraded for reliable quantification.",
                "quality_warnings": quality_res["warnings"]
            }

        # STAGE 3 — ARS Mineralization Segmentation
        binary_mask = segment_ars(image, method="classical", cfg=self.cfg.segmentation)

        # STAGE 4 — Nodule & Dot Detection & Counting
        nodule_data = detect_nodules(image, binary_mask, cfg=self.cfg.nodule_detection)

        # STAGE 5 — Mineralization Quantification
        quant_res = quantify_mineralization(image, binary_mask, nodule_data, cfg=self.cfg.quantification)

        # STAGE 6 — Confidence & Quality Assessment
        conf_res = assess_confidence(rel_res, stain_res, quality_res, quant_res)

        # STAGE 7 — Visual Output Generation
        visuals = {}
        if generate_images:
            visuals = generate_visualizations(image, binary_mask, nodule_data, gt_mask=gt_mask)

        # Assemble final researcher-oriented response contract
        return {
            "valid": True,
            "stain": stain_res,
            "image_quality": quality_res,
            "mineralization": {
                "area_pixels": quant_res["mineralized_area_pixels"],
                "area_percent": quant_res["mineralized_area_percent"],
                "total_pixels": quant_res["total_image_pixels"],
                "density_per_10k_px": quant_res["mineralization_density_per_10k_px"],
                "spatial_pattern": quant_res["spatial_pattern"],
                "optical_density": quant_res["optical_density_proxy"]
            },
            "nodules": {
                "count": quant_res["nodule_count"],
                "min_size_pixels": quant_res["min_nodule_size_pixels"],
                "max_size_pixels": quant_res["max_nodule_size_pixels"],
                "mean_size_pixels": quant_res["mean_nodule_size_pixels"],
                "median_size_pixels": quant_res["median_nodule_size_pixels"],
                "size_distribution": quant_res["nodule_size_distribution"],
                "objects": nodule_data["objects"]
            },
            "calibration": quant_res["calibration"],
            "physical_metrics": quant_res["physical_metrics"],
            "quality": conf_res,
            "visualizations": visuals,
            "binary_mask_raw": binary_mask
        }

    def analyze_batch(
        self,
        samples: Dict[str, np.ndarray],
        pixel_size_um: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyzes multiple microscopy images independently and generates comparative summary.
        
        Args:
            samples: dict of {sample_id: BGR image array}
            pixel_size_um: Optional calibration factor.
            
        Returns:
            dict: {
                "individual_results": dict,
                "comparison_summary": dict
            }
        """
        individual: Dict[str, Any] = {}
        valid_summary: List[Dict[str, Any]] = []
        
        for name, img in samples.items():
            res = self.analyze_image(img, pixel_size_um=pixel_size_um, generate_images=False)
            individual[name] = res
            
            if res.get("valid", False):
                valid_summary.append({
                    "sample_id": name,
                    "mineralized_area_percent": res["mineralization"]["area_percent"],
                    "nodule_count": res["nodules"]["count"],
                    "mean_nodule_size_pixels": res["nodules"]["mean_size_pixels"],
                    "spatial_pattern": res["mineralization"]["spatial_pattern"],
                    "quality_rating": res["quality"]["analysis_quality"]
                })
                
        # Rank samples by mineralization area %
        valid_summary.sort(key=lambda x: x["mineralized_area_percent"], reverse=True)
        
        return {
            "individual_results": individual,
            "comparison_summary": {
                "total_samples": len(samples),
                "valid_samples_count": len(valid_summary),
                "ranked_by_mineralization": valid_summary
            }
        }
