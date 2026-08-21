-- =============================================================
-- StainScope Supabase PostgreSQL Schema DDL (Production Ready)
-- Project: StainScope (Region: South Asia / Mumbai)
-- Includes: Tables, FKs, Indexes, RLS Policies & Auth Trigger
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -------------------------------------------------------------
-- 1. PROFILES / USERS
-- Integrates with Supabase Auth (auth.users)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  role TEXT DEFAULT 'Bone Tissue Researcher',
  institution TEXT DEFAULT 'BioMed Research Institute',
  lab_name TEXT DEFAULT 'Regenerative Medicine & Osteogenesis Lab',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -------------------------------------------------------------
-- 2. EXPERIMENTS / STUDY GROUPS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT NULL,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -------------------------------------------------------------
-- 3. MICROGRAPHS (Uploaded Image Metadata & Private Storage Refs)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.micrographs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  experiment_id UUID NULL REFERENCES public.experiments(id) ON DELETE SET NULL,
  file_name TEXT NOT NULL,
  original_name TEXT NOT NULL,
  storage_bucket TEXT NOT NULL DEFAULT 'micrographs',
  storage_path TEXT NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  mime_type TEXT NOT NULL,
  width_px INT NOT NULL,
  height_px INT NOT NULL,
  file_hash TEXT NOT NULL,
  pixel_size_um NUMERIC(10, 4) NULL,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_micrographs_user ON public.micrographs(user_id);
CREATE INDEX IF NOT EXISTS idx_micrographs_hash ON public.micrographs(file_hash);

-- -------------------------------------------------------------
-- 4. ANALYSES (Master Run Records — Model Agnostic)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  micrograph_id UUID NOT NULL REFERENCES public.micrographs(id) ON DELETE CASCADE,
  experiment_id UUID NULL REFERENCES public.experiments(id) ON DELETE SET NULL,
  
  -- Model & Engine Provenance (Classical CV / U-Net AI)
  model_type TEXT NOT NULL DEFAULT 'classical_cv',
  model_version TEXT NOT NULL DEFAULT '1.0.0',
  analysis_method TEXT NOT NULL DEFAULT 'classical_cv_pipeline',
  analysis_version TEXT NOT NULL DEFAULT '1.0.0',
  
  -- Status & Gate Validation
  status TEXT NOT NULL DEFAULT 'COMPLETED',
  is_valid BOOLEAN NOT NULL DEFAULT TRUE,
  rejection_reason TEXT NULL,
  
  -- Research Sample Context
  sample_title TEXT NOT NULL,
  cell_line TEXT NULL,
  treatment TEXT NULL,
  differentiation_day TEXT NULL,
  objective_magnification TEXT DEFAULT '20x Objective',
  stain_name TEXT DEFAULT 'Alizarin Red S (2%)',
  
  -- Quantitative Analysis Results
  mineralized_area_pixels BIGINT NOT NULL DEFAULT 0,
  mineralized_area_percent NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
  total_image_pixels BIGINT NOT NULL DEFAULT 0,
  optical_density_proxy NUMERIC(6, 3) NOT NULL DEFAULT 0.000,
  nodule_count INT NOT NULL DEFAULT 0,
  min_nodule_size_pixels INT NOT NULL DEFAULT 0,
  max_nodule_size_pixels INT NOT NULL DEFAULT 0,
  mean_nodule_size_pixels NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
  median_nodule_size_pixels NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
  nodule_size_distribution JSONB NULL,
  spatial_pattern TEXT NOT NULL DEFAULT 'dispersed',
  
  -- Quality & Confidence Metrics
  overall_confidence NUMERIC(4, 3) NOT NULL DEFAULT 0.980,
  quality_score NUMERIC(4, 3) NOT NULL DEFAULT 0.950,
  quality_warnings JSONB NULL,
  processing_time_sec NUMERIC(6, 3) NOT NULL DEFAULT 0.000,
  
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_date ON public.analyses(user_id, analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_model ON public.analyses(model_type, model_version);

-- -------------------------------------------------------------
-- 5. NODULES (Individual Nodule Objects N1, N2, N3...)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.nodules (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
  nodule_index INT NOT NULL,
  label_id TEXT NOT NULL,
  area_pixels INT NOT NULL,
  centroid_x NUMERIC(8, 2) NOT NULL,
  centroid_y NUMERIC(8, 2) NOT NULL,
  bbox_x INT NOT NULL,
  bbox_y INT NOT NULL,
  bbox_w INT NOT NULL,
  bbox_h INT NOT NULL,
  circularity NUMERIC(4, 3) NOT NULL,
  local_contrast NUMERIC(6, 2) NOT NULL,
  size_category TEXT NOT NULL,
  confidence NUMERIC(4, 3) NOT NULL,
  contour_json JSONB NULL
);

CREATE INDEX IF NOT EXISTS idx_nodules_analysis ON public.nodules(analysis_id, nodule_index);

-- -------------------------------------------------------------
-- 6. ANALYSIS_OVERLAYS (Private Storage References for Overlays)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.analysis_overlays (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
  overlay_type TEXT NOT NULL, -- 'nodule_map', 'overlay', 'mask', 'validation_panel'
  storage_bucket TEXT NOT NULL DEFAULT 'analysis-overlays',
  storage_path TEXT NOT NULL,
  file_size_bytes INT NOT NULL DEFAULT 0,
  mime_type TEXT NOT NULL DEFAULT 'image/png',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uk_analysis_overlay_type UNIQUE (analysis_id, overlay_type)
);

-- -------------------------------------------------------------
-- 7. BATCH_COMPARISONS & ITEMS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.batch_comparisons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  experiment_id UUID NULL REFERENCES public.experiments(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  ranking_summary JSONB NULL,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.batch_comparison_items (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  batch_comparison_id UUID NOT NULL REFERENCES public.batch_comparisons(id) ON DELETE CASCADE,
  analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
  rank_position INT NOT NULL,
  is_valid BOOLEAN NOT NULL DEFAULT TRUE,
  rejection_reason TEXT NULL
);

-- -------------------------------------------------------------
-- 8. RESEARCH_NOTES (User Lab Observations & Research Notes)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.research_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_research_notes_user ON public.research_notes(user_id, created_at DESC);

-- =============================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.micrographs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nodules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_overlays ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.batch_comparisons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.batch_comparison_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_notes ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can view and update their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Experiments: Users can manage their own non-deleted experiments
DROP POLICY IF EXISTS "Users can access own experiments" ON public.experiments;
CREATE POLICY "Users can access own experiments" ON public.experiments FOR ALL USING (auth.uid() = user_id AND is_deleted = FALSE);

-- Micrographs: Users can access their own micrographs
DROP POLICY IF EXISTS "Users can access own micrographs" ON public.micrographs;
CREATE POLICY "Users can access own micrographs" ON public.micrographs FOR ALL USING (auth.uid() = user_id AND is_deleted = FALSE);

-- Analyses: Users can access their own analyses
DROP POLICY IF EXISTS "Users can access own analyses" ON public.analyses;
CREATE POLICY "Users can access own analyses" ON public.analyses FOR ALL USING (auth.uid() = user_id AND is_deleted = FALSE);

-- Research Notes: Access notes owned by user_id
DROP POLICY IF EXISTS "Users can access own research notes" ON public.research_notes;
CREATE POLICY "Users can access own research notes" ON public.research_notes FOR ALL USING (auth.uid() = user_id);

-- Nodules: Access nodules owned via analysis->user_id
DROP POLICY IF EXISTS "Users can access own nodules" ON public.nodules;
CREATE POLICY "Users can access own nodules" ON public.nodules FOR ALL USING (
  EXISTS (
    SELECT 1 FROM public.analyses a
    WHERE a.id = nodules.analysis_id AND a.user_id = auth.uid() AND a.is_deleted = FALSE
  )
);

-- Overlays: Access overlays owned via analysis->user_id
DROP POLICY IF EXISTS "Users can access own overlays" ON public.analysis_overlays;
CREATE POLICY "Users can access own overlays" ON public.analysis_overlays FOR ALL USING (
  EXISTS (
    SELECT 1 FROM public.analyses a
    WHERE a.id = analysis_overlays.analysis_id AND a.user_id = auth.uid() AND a.is_deleted = FALSE
  )
);

-- Research Notes: Users can access their own research notes
DROP POLICY IF EXISTS "Users can access own research notes" ON public.research_notes;
CREATE POLICY "Users can access own research notes" ON public.research_notes FOR ALL USING (auth.uid() = user_id);


-- =============================================================
-- SUPABASE AUTH INTEGRATION TRIGGER
-- Automatically creates a public.profiles record on auth.users signup
-- =============================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role, institution, lab_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', SPLIT_PART(NEW.email, '@', 1)),
    COALESCE(NEW.raw_user_meta_data->>'role', 'Bone Tissue Researcher'),
    COALESCE(NEW.raw_user_meta_data->>'institution', 'BioMed Research Institute'),
    COALESCE(NEW.raw_user_meta_data->>'lab_name', 'Regenerative Medicine & Osteogenesis Lab')
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =============================================================
-- ROLE PRIVILEGES & SERVICE ROLE PERMISSIONS
-- =============================================================
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres, anon, authenticated, service_role;
