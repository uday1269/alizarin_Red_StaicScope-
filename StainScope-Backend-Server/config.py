"""
Configurable parameters for StainScope Classical Computer Vision Pipeline.
All parameters can be tuned or overridden via dataclass configuration objects.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple, List


@dataclass
class RelevanceConfig:
    """Thresholds for Stage 0 — Conservative Relevance Gate."""
    min_resolution: Tuple[int, int] = (200, 200)
    max_channel_diff_std: float = 85.0     # Standard photograph check
    min_color_variance: float = 8.0        # Document / greyscale check
    max_text_edge_density: float = 0.35    # Screenshot / document check
    min_microscopy_texture: float = 2.0    # Texture variance expected in microscopy


@dataclass
class StainIDConfig:
    """Thresholds for Stage 1 — Stain Identification."""
    # Red/orange hue ranges in OpenCV HSV (H: 0-180, S: 0-255, V: 0-255)
    hue_lower_red1: Tuple[int, int, int] = (0, 30, 40)
    hue_upper_red1: Tuple[int, int, int] = (22, 255, 255)
    hue_lower_red2: Tuple[int, int, int] = (155, 30, 40)
    hue_upper_red2: Tuple[int, int, int] = (180, 255, 255)

    # Minimum red/brick ratio threshold
    min_red_pixel_ratio: float = 0.003     # At least 0.3% pixels should have ARS color signature
    blue_purple_max_dominance: float = 2.5  # Rejects strongly blue/purple dominant non-ARS stains


@dataclass
class QualityConfig:
    """Thresholds for Stage 2 — Microscopy & Image Quality Check."""
    blur_laplacian_threshold: float = 25.0 # Low variance = blurry
    min_brightness_mean: float = 15.0       # Dark image limit
    max_brightness_mean: float = 245.0      # Overexposed image limit
    max_vignette_ratio: float = 4.0        # Corner vs center illumination ratio warning threshold


@dataclass
class SegmentationConfig:
    """Thresholds for Stage 3 — Adaptive ARS Mineralization Segmentation."""
    clahe_clip_limit: float = 2.5
    clahe_tile_grid: Tuple[int, int] = (8, 8)
    
    # Adaptive thresholding block size & C
    adaptive_block_size: int = 31
    adaptive_c: float = 5.0
    
    # Lab a* channel dominance weight
    lab_a_weight: float = 0.6
    hsv_s_weight: float = 0.4
    
    # Morphological cleaning
    morph_kernel_size: int = 3


@dataclass
class NoduleDetectionConfig:
    """Thresholds for Stage 4 — Nodule & Dot Detection & Counting."""
    # Distance transform peak thresholding (fraction of max distance inside object)
    dist_threshold_ratio: float = 0.35
    min_nodule_distance: int = 3
    
    # Small dot preservation & noise filtering parameters
    # DO NOT use blind `area < X → delete`. Use local contrast + circularity.
    absolute_min_area: int = 2            # Only filter 1-pixel isolated noise
    min_local_contrast: float = 12.0      # Local background contrast delta (ΔI)
    min_circularity_for_tiny_dots: float = 0.25 # Circularity requirement for very small objects (2-8 px)
    

@dataclass
class QuantificationConfig:
    """Thresholds for Stage 5 — Mineralization Quantification."""
    # Pattern boundaries (mineralized area %)
    pattern_sparse_max: float = 2.0
    pattern_dispersed_max: float = 8.0
    pattern_clustered_max: float = 20.0
    pattern_dense_max: float = 50.0
    # > 50.0 is considered 'confluent'

    # Optional physical scale calibration (µm per pixel)
    pixel_size_um: Optional[float] = None  # Explicitly None by default! Never hardcoded.


@dataclass
class CVEngineConfig:
    """Root configuration object combining all stage configs."""
    relevance: RelevanceConfig = field(default_factory=RelevanceConfig)
    stain_id: StainIDConfig = field(default_factory=StainIDConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    segmentation: SegmentationConfig = field(default_factory=SegmentationConfig)
    nodule_detection: NoduleDetectionConfig = field(default_factory=NoduleDetectionConfig)
    quantification: QuantificationConfig = field(default_factory=QuantificationConfig)
