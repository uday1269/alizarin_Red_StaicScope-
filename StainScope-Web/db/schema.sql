-- StainScope Relational Database Schema DDL
-- Compatible with MySQL 8.0+ / MariaDB (XAMPP) & SQLite

CREATE DATABASE IF NOT EXISTS stainscope_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE stainscope_db;

-- 1. Users & Researcher Profiles
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(150) NOT NULL,
  role VARCHAR(100) DEFAULT 'Bone Tissue Researcher',
  institution VARCHAR(255) DEFAULT 'BioMed Research Institute',
  lab_name VARCHAR(255) DEFAULT 'Regenerative Medicine & Osteogenesis Lab',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Experiments / Research Study Groups
CREATE TABLE IF NOT EXISTS experiments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Uploaded Micrographs Metadata Index
CREATE TABLE IF NOT EXISTS micrographs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  original_name VARCHAR(255) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  mime_type VARCHAR(50) NOT NULL,
  width_px INT NOT NULL,
  height_px INT NOT NULL,
  file_hash VARCHAR(64) NOT NULL,
  pixel_size_um DECIMAL(10, 4) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_file_hash (file_hash)
) ENGINE=InnoDB;

-- 4. Master Analysis Run Records (Source of Scientific Truth)
CREATE TABLE IF NOT EXISTS analyses (
  id VARCHAR(50) PRIMARY KEY,
  user_id INT NOT NULL,
  micrograph_id INT NOT NULL,
  experiment_id INT NULL,
  
  -- Engine & Algorithm Versioning
  engine_type ENUM('CLASSICAL_CV', 'UNET_AI') NOT NULL DEFAULT 'CLASSICAL_CV',
  engine_version VARCHAR(50) NOT NULL DEFAULT 'v1.0.0',
  
  -- Status & Gate Validation
  status ENUM('COMPLETED', 'REJECTED', 'FAILED') NOT NULL DEFAULT 'COMPLETED',
  is_valid BOOLEAN NOT NULL DEFAULT TRUE,
  rejection_reason TEXT NULL,
  
  -- Research Metadata (Entered by User)
  sample_title VARCHAR(255) NOT NULL,
  cell_line VARCHAR(150) NULL,
  treatment VARCHAR(255) NULL,
  differentiation_day VARCHAR(50) NULL,
  objective_magnification VARCHAR(50) DEFAULT '20x Objective',
  stain_name VARCHAR(100) DEFAULT 'Alizarin Red S (2%)',
  
  -- Scientific Quantification Results (Strictly from Backend Engine)
  mineralized_area_pixels BIGINT NOT NULL DEFAULT 0,
  mineralized_area_percent DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
  total_image_pixels BIGINT NOT NULL DEFAULT 0,
  optical_density_proxy DECIMAL(6, 3) NOT NULL DEFAULT 0.000,
  nodule_count INT NOT NULL DEFAULT 0,
  min_nodule_size_pixels INT NOT NULL DEFAULT 0,
  max_nodule_size_pixels INT NOT NULL DEFAULT 0,
  mean_nodule_size_pixels DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  median_nodule_size_pixels DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  nodule_size_distribution_json JSON NULL,
  spatial_pattern VARCHAR(50) NOT NULL DEFAULT 'dispersed',
  
  -- Quality & Confidence
  overall_confidence DECIMAL(4, 3) NOT NULL DEFAULT 0.980,
  quality_score DECIMAL(4, 3) NOT NULL DEFAULT 0.950,
  quality_warnings_json JSON NULL,
  processing_time_sec DECIMAL(6, 3) NOT NULL DEFAULT 0.000,
  
  analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (micrograph_id) REFERENCES micrographs(id) ON DELETE CASCADE,
  FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE SET NULL,
  INDEX idx_user_analyses (user_id, analyzed_at DESC),
  INDEX idx_engine (engine_type, engine_version)
) ENGINE=InnoDB;

-- 5. Granular Nodule Objects (N1, N2, N3...)
CREATE TABLE IF NOT EXISTS nodules (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  analysis_id VARCHAR(50) NOT NULL,
  nodule_index INT NOT NULL,
  label_id VARCHAR(20) NOT NULL,
  area_pixels INT NOT NULL,
  centroid_x DECIMAL(8, 2) NOT NULL,
  centroid_y DECIMAL(8, 2) NOT NULL,
  bbox_x INT NOT NULL,
  bbox_y INT NOT NULL,
  bbox_w INT NOT NULL,
  bbox_h INT NOT NULL,
  circularity DECIMAL(4, 3) NOT NULL,
  local_contrast DECIMAL(6, 2) NOT NULL,
  size_category ENUM('dot', 'small', 'medium', 'large', 'plaque') NOT NULL,
  confidence DECIMAL(4, 3) NOT NULL,
  FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
  INDEX idx_analysis_nodules (analysis_id, nodule_index)
) ENGINE=InnoDB;

-- 6. Generated Visual Overlay File References
CREATE TABLE IF NOT EXISTS analysis_overlays (
  id INT AUTO_INCREMENT PRIMARY KEY,
  analysis_id VARCHAR(50) NOT NULL,
  overlay_type ENUM('nodule_map', 'overlay', 'mask', 'validation_panel') NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  file_size_bytes INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
  UNIQUE KEY uk_analysis_overlay_type (analysis_id, overlay_type)
) ENGINE=InnoDB;

-- 7. Saved Multi-Sample Batch Comparisons
CREATE TABLE IF NOT EXISTS batch_comparisons (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  experiment_id INT NULL,
  title VARCHAR(255) NOT NULL,
  ranking_summary_json JSON NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. Comparison Session Items Junction Table
CREATE TABLE IF NOT EXISTS batch_comparison_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  batch_comparison_id INT NOT NULL,
  analysis_id VARCHAR(50) NOT NULL,
  rank_position INT NOT NULL,
  is_valid BOOLEAN NOT NULL DEFAULT TRUE,
  rejection_reason VARCHAR(255) NULL,
  FOREIGN KEY (batch_comparison_id) REFERENCES batch_comparisons(id) ON DELETE CASCADE,
  FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
) ENGINE=InnoDB;
