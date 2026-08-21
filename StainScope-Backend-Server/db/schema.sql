-- StainScope XAMPP MySQL Database Schema
-- Database Name: stainscope

CREATE DATABASE IF NOT EXISTS stainscope CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stainscope;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) DEFAULT NULL,
    role VARCHAR(100) DEFAULT 'Bone Tissue Researcher',
    institution VARCHAR(255) DEFAULT 'BioMed Research Institute',
    lab_name VARCHAR(255) DEFAULT 'Regenerative Medicine & Osteogenesis Lab',
    total_scans INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Experiments Table
CREATE TABLE IF NOT EXISTS experiments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    cell_line VARCHAR(255) DEFAULT NULL,
    incubation_period VARCHAR(100) DEFAULT NULL,
    magnification VARCHAR(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Micrographs Table
CREATE TABLE IF NOT EXISTS micrographs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    experiment_id VARCHAR(36) DEFAULT NULL,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) DEFAULT NULL,
    storage_bucket VARCHAR(100) DEFAULT 'micrographs',
    storage_path VARCHAR(512) NOT NULL,
    file_size_bytes BIGINT DEFAULT 0,
    mime_type VARCHAR(100) DEFAULT 'image/png',
    width_px INT DEFAULT 0,
    height_px INT DEFAULT 0,
    file_hash VARCHAR(64) DEFAULT NULL,
    pixel_size_um DOUBLE DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Analyses Table
CREATE TABLE IF NOT EXISTS analyses (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    micrograph_id VARCHAR(36) DEFAULT NULL,
    experiment_id VARCHAR(36) DEFAULT NULL,
    model_type VARCHAR(100) NOT NULL DEFAULT 'classical_cv',
    model_version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    analysis_method VARCHAR(100) NOT NULL DEFAULT 'classical_cv_pipeline',
    analysis_version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    status VARCHAR(50) DEFAULT 'COMPLETED',
    is_valid BOOLEAN DEFAULT TRUE,
    rejection_reason TEXT DEFAULT NULL,
    sample_title VARCHAR(255) DEFAULT NULL,
    objective_magnification VARCHAR(100) DEFAULT '20x Objective',
    stain_name VARCHAR(100) DEFAULT 'Alizarin Red S (2%)',
    mineralized_area_pixels BIGINT DEFAULT 0,
    mineralized_area_percent DOUBLE DEFAULT 0.0,
    total_image_pixels BIGINT DEFAULT 0,
    optical_density_proxy DOUBLE DEFAULT 0.0,
    nodule_count INT DEFAULT 0,
    min_nodule_size_pixels DOUBLE DEFAULT 0.0,
    max_nodule_size_pixels DOUBLE DEFAULT 0.0,
    mean_nodule_size_pixels DOUBLE DEFAULT 0.0,
    median_nodule_size_pixels DOUBLE DEFAULT 0.0,
    nodule_size_distribution JSON DEFAULT NULL,
    spatial_pattern VARCHAR(100) DEFAULT 'dispersed',
    overall_confidence DOUBLE DEFAULT 0.95,
    quality_score DOUBLE DEFAULT 0.95,
    quality_warnings JSON DEFAULT NULL,
    processing_time_sec DOUBLE DEFAULT 0.0,
    is_deleted BOOLEAN DEFAULT FALSE,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (micrograph_id) REFERENCES micrographs(id) ON DELETE SET NULL,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Nodules Table
CREATE TABLE IF NOT EXISTS nodules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(36) NOT NULL,
    nodule_index INT NOT NULL,
    label_id VARCHAR(50) DEFAULT NULL,
    area_pixels INT DEFAULT 0,
    centroid_x DOUBLE DEFAULT 0.0,
    centroid_y DOUBLE DEFAULT 0.0,
    bbox_x INT DEFAULT 0,
    bbox_y INT DEFAULT 0,
    bbox_w INT DEFAULT 0,
    bbox_h INT DEFAULT 0,
    circularity DOUBLE DEFAULT 0.0,
    local_contrast DOUBLE DEFAULT 0.0,
    size_category VARCHAR(50) DEFAULT 'small',
    confidence DOUBLE DEFAULT 0.95,
    contour_json JSON DEFAULT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Analysis Overlays Table
CREATE TABLE IF NOT EXISTS analysis_overlays (
    id VARCHAR(36) PRIMARY KEY,
    analysis_id VARCHAR(36) NOT NULL,
    overlay_type VARCHAR(100) NOT NULL,
    storage_bucket VARCHAR(100) DEFAULT 'analysis-overlays',
    storage_path VARCHAR(512) NOT NULL,
    file_size_bytes BIGINT DEFAULT 0,
    mime_type VARCHAR(100) DEFAULT 'image/png',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Research Notes Table
CREATE TABLE IF NOT EXISTS research_notes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Batch Comparisons Table
CREATE TABLE IF NOT EXISTS batch_comparisons (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    ranking_summary JSON DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Batch Comparison Items Table
CREATE TABLE IF NOT EXISTS batch_comparison_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comparison_id VARCHAR(36) NOT NULL,
    analysis_id VARCHAR(36) NOT NULL,
    item_order INT DEFAULT 0,
    FOREIGN KEY (comparison_id) REFERENCES batch_comparisons(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
