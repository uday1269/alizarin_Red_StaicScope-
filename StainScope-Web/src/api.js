/**
 * StainScope Web REST API Client Module
 * Connects to the StainScope Classical CV Analysis Engine & XAMPP MySQL backend.
 */

export const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || 
  (typeof window !== 'undefined' && window.location.hostname && window.location.hostname !== 'localhost'
    ? `http://${window.location.hostname}:8000`
    : 'http://localhost:8000');

export function getAuthToken() {
  return localStorage.getItem('stainscope_access_token');
}

export function setAuthSession(sessionData) {
  if (sessionData && sessionData.access_token) {
    localStorage.setItem('stainscope_access_token', sessionData.access_token);
    localStorage.setItem('stainscope_user', JSON.stringify({
      id: sessionData.user_id,
      email: sessionData.email,
      full_name: sessionData.full_name
    }));
  }
}

export function clearAuthSession() {
  localStorage.removeItem('stainscope_access_token');
  localStorage.removeItem('stainscope_user');
}

export async function getAuthHeaders(customHeaders = {}) {
  const headers = { ...customHeaders };
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Native FastAPI MySQL Auth API Helpers
 */
export async function signUpUser(email, password, fullName) {
  const resp = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName })
  });

  if (!resp.ok) {
    const errText = await resp.text();
    let detail = 'Signup failed.';
    try {
      const errJson = JSON.parse(errText);
      detail = errJson.detail || errText;
    } catch (e) {
      detail = errText;
    }
    throw new Error(detail);
  }

  const data = await resp.json();
  setAuthSession(data);
  return { session: { access_token: data.access_token, user: { id: data.user_id, email: data.email } }, user: data };
}

export async function signInUser(email, password) {
  const resp = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  if (!resp.ok) {
    const errText = await resp.text();
    let detail = 'Invalid email or password.';
    try {
      const errJson = JSON.parse(errText);
      detail = errJson.detail || errText;
    } catch (e) {
      detail = errText;
    }
    throw new Error(detail);
  }

  const data = await resp.json();
  setAuthSession(data);
  return { session: { access_token: data.access_token, user: { id: data.user_id, email: data.email } }, user: data };
}

export async function signOutUser() {
  clearAuthSession();
}

export async function getCurrentSession() {
  const token = getAuthToken();
  if (!token) return null;
  const userStr = localStorage.getItem('stainscope_user');
  let user = null;
  try {
    user = userStr ? JSON.parse(userStr) : null;
  } catch (e) {}
  return { access_token: token, user };
}

export async function checkHealth() {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers,
    });
    if (!response.ok) {
      throw new Error(`Health check failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API health check error:', error);
    throw error;
  }
}

/**
 * Analyzes a single ARS microscopy image file.
 */
export async function analyzeImage(file, pixelSizeUm = null, metadata = {}, signal = null) {
  if (!file) {
    throw new Error('No image file provided for analysis.');
  }

  const formData = new FormData();
  formData.append('file', file, file.name || 'micrograph.png');
  if (pixelSizeUm !== null && pixelSizeUm !== undefined && !isNaN(pixelSizeUm)) {
    formData.append('pixel_size_um', String(pixelSizeUm));
  }
  if (metadata.sampleTitle) formData.append('sample_title', metadata.sampleTitle);
  if (metadata.cellLineText) formData.append('cell_line', metadata.cellLineText);
  if (metadata.treatmentText) formData.append('treatment', metadata.treatmentText);
  if (metadata.dayText) formData.append('differentiation_day', metadata.dayText);

  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers,
      body: formData,
      signal: signal || undefined,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      throw new Error(`Server returned error ${response.status}: ${errorText || response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Analysis request timed out or was cancelled.');
    }
    console.error('Error analyzing image:', error);
    throw error;
  }
}

/**
 * Analyzes multiple ARS microscopy images in batch.
 */
export async function analyzeBatch(files, pixelSizeUm = null, signal = null) {
  if (!files || files.length === 0) {
    throw new Error('No image files provided for batch analysis.');
  }

  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file, file.name || 'micrograph.png');
  });

  if (pixelSizeUm !== null && pixelSizeUm !== undefined && !isNaN(pixelSizeUm)) {
    formData.append('pixel_size_um', String(pixelSizeUm));
  }

  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/analyze-batch`, {
      method: 'POST',
      headers,
      body: formData,
      signal: signal || undefined,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      throw new Error(`Batch analysis failed with status ${response.status}: ${errorText || response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Batch analysis timed out or was cancelled.');
    }
    console.error('Error executing batch analysis:', error);
    throw error;
  }
}

export function resolveWebFileUrl(url) {
  if (!url) return null;
  if (url.startsWith('data:') || url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  const cleanBase = API_BASE_URL.replace(/\/$/, '');
  let cleanPath = url.startsWith('/') ? url : `/${url}`;
  if (!cleanPath.startsWith('/storage') && !cleanPath.startsWith('/files')) {
    cleanPath = `/storage${cleanPath}`;
  }
  let fullUrl = `${cleanBase}${cleanPath}`;
  const token = getAuthToken();
  if (token && !fullUrl.includes('token=')) {
    const connector = fullUrl.includes('?') ? '&' : '?';
    fullUrl = `${fullUrl}${connector}token=${encodeURIComponent(token)}`;
  }
  return fullUrl;
}

function parseJsonSafe(val, fallback = []) {
  if (val === null || val === undefined) return fallback;
  if (Array.isArray(val) || (typeof val === 'object' && val !== null)) return val;
  if (typeof val === 'string') {
    try {
      const parsed = JSON.parse(val);
      return parsed !== null && parsed !== undefined ? parsed : fallback;
    } catch (e) {
      return val.trim() ? [val] : fallback;
    }
  }
  return fallback;
}

/**
 * Retrieves the full list of active, persisted analysis records for the authenticated user from MySQL.
 */
export async function fetchAnalysesHistory() {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/analyses`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch analyses history (${response.status})`);
    }

    const dbRecords = await response.json();
    if (!Array.isArray(dbRecords)) return [];

    return dbRecords.map((rec) => {
      const areaVal = Number(rec.mineralized_area_percent) || 0;
      const odVal = Number(rec.optical_density_proxy) || 0;
      const countVal = rec.nodule_count !== undefined ? rec.nodule_count : 0;
      const analyzedDate = rec.analyzed_at ? new Date(rec.analyzed_at) : new Date();

      const rawImgUrl = rec.image_url || rec.overlays?.nodule_map || rec.overlays?.overlay || rec.overlay || null;
      const imageUrl = resolveWebFileUrl(rawImgUrl);

      const overlaysObj = rec.overlays || {};
      const resolvedOverlay = resolveWebFileUrl(overlaysObj.nodule_map || overlaysObj.overlay || rec.overlay || rawImgUrl);

      const confVal = rec.overall_confidence != null ? Number(rec.overall_confidence) : (rec.ai_confidence != null ? Number(rec.ai_confidence) : 0.95);
      const confPct = confVal <= 1.0 ? confVal * 100 : confVal;
      const calciumVal = rec.calcium_density_ug_cm2 != null ? Number(rec.calcium_density_ug_cm2) : (areaVal * 0.05);
      const procTimeVal = rec.processing_time_sec != null ? Number(rec.processing_time_sec) : 0.45;

      const parsedWarnings = parseJsonSafe(rec.quality_warnings, []);
      const parsedSizeDist = parseJsonSafe(rec.nodule_size_distribution, {});

      return {
        id: rec.id || `STAIN-${Math.floor(8000 + Math.random() * 1000)}`,
        dbId: rec.id,
        micrographId: rec.micrograph_id,
        title: rec.sample_title || rec.original_name || 'Micrograph Sample',
        date: analyzedDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
        time: analyzedDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
        
        mineralizedArea: `${areaVal.toFixed(2)}%`,
        mineralizedAreaValue: areaVal,
        stainIntensityOD: `${odVal.toFixed(2)} OD`,
        stainIntensityValue: odVal,
        nodulesCount: countVal,
        calciumEstimate: `${calciumVal.toFixed(2)} μg/cm²`,
        calciumValue: Number(calciumVal.toFixed(2)),
        
        minNoduleSize: `${(Number(rec.min_nodule_size_pixels) || 0).toFixed(2)} px`,
        maxNoduleSize: `${(Number(rec.max_nodule_size_pixels) || 0).toFixed(2)} px`,
        avgNoduleSize: `${(Number(rec.mean_nodule_size_pixels) || 0).toFixed(2)} px`,
        medianNoduleSize: `${(Number(rec.median_size_pixels) || 0).toFixed(2)} px`,
        sizeDistribution: parsedSizeDist,
        warnings: Array.isArray(parsedWarnings) ? parsedWarnings : [],
        
        coveragePercentage: `${areaVal.toFixed(2)}%`,
        aiConfidence: `${confPct.toFixed(1)}%`,
        processingTime: `${procTimeVal.toFixed(2)}s`,
        treatment: rec.treatment || 'Unspecified Treatment',
        day: rec.differentiation_day || 'Not specified',
        cellLine: rec.cell_line || 'Not specified',
        status: areaVal > 50 ? 'High Mineralization' : areaVal > 20 ? 'Moderate Mineralization' : 'Low Mineralization',
        statusColor: areaVal > 50 ? '#059669' : areaVal > 20 ? '#D97706' : '#64748B',
        stainType: rec.stain_name || 'Alizarin Red S (2%)',
        magnification: rec.objective_magnification || '20x Objective',
        resolution: '2048 × 1536 px',
        pattern: rec.spatial_pattern || 'Cluster Nodule Network',
        thumbnailUrl: imageUrl,
        imageUrl: imageUrl,
        overlay: resolvedOverlay,
        overlays: overlaysObj,
        rawDbRecord: rec
      };
    });
  } catch (error) {
    console.error('Error fetching analyses history from backend:', error);
    return [];
  }
}

/**
 * Retrieves a single detailed analysis record by ID from MySQL.
 */
export async function fetchAnalysisById(analysisId) {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/analyses/${analysisId}`, {
      method: 'GET',
      headers,
    });
    if (!response.ok) return null;
    const rec = await response.json();
    if (!rec) return null;

    const areaVal = Number(rec.mineralized_area_percent) || 0;
    const odVal = Number(rec.optical_density_proxy) || 0;
    const countVal = rec.nodule_count !== undefined ? rec.nodule_count : 0;
    const analyzedDate = rec.analyzed_at ? new Date(rec.analyzed_at) : new Date();

    const rawImgUrl = rec.image_url || rec.overlays?.nodule_map || rec.overlays?.overlay || rec.overlay || null;
    const imageUrl = resolveWebFileUrl(rawImgUrl);

    const overlaysObj = rec.overlays || {};
    const resolvedOverlay = resolveWebFileUrl(overlaysObj.nodule_map || overlaysObj.overlay || rec.overlay || rawImgUrl);

    const confVal = rec.overall_confidence != null ? Number(rec.overall_confidence) : (rec.ai_confidence != null ? Number(rec.ai_confidence) : 0.95);
    const confPct = confVal <= 1.0 ? confVal * 100 : confVal;
    const calciumVal = rec.calcium_density_ug_cm2 != null ? Number(rec.calcium_density_ug_cm2) : (areaVal * 0.05);
    const procTimeVal = rec.processing_time_sec != null ? Number(rec.processing_time_sec) : 0.45;

    const parsedWarnings = parseJsonSafe(rec.quality_warnings, []);
    const parsedSizeDist = parseJsonSafe(rec.nodule_size_distribution, {});

    return {
      id: rec.id || analysisId,
      dbId: rec.id || analysisId,
      micrographId: rec.micrograph_id,
      title: rec.sample_title || rec.original_name || 'Micrograph Sample',
      date: analyzedDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
      time: analyzedDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
      
      mineralizedArea: `${areaVal.toFixed(2)}%`,
      mineralizedAreaValue: areaVal,
      stainIntensityOD: `${odVal.toFixed(2)} OD`,
      stainIntensityValue: odVal,
      nodulesCount: countVal,
      calciumEstimate: `${calciumVal.toFixed(2)} μg/cm²`,
      calciumValue: Number(calciumVal.toFixed(2)),
      
      minNoduleSize: `${(Number(rec.min_nodule_size_pixels) || 0).toFixed(2)} px`,
      maxNoduleSize: `${(Number(rec.max_nodule_size_pixels) || 0).toFixed(2)} px`,
      avgNoduleSize: `${(Number(rec.mean_nodule_size_pixels) || 0).toFixed(2)} px`,
      medianNoduleSize: `${(Number(rec.median_size_pixels) || 0).toFixed(2)} px`,
      sizeDistribution: parsedSizeDist,
      warnings: Array.isArray(parsedWarnings) ? parsedWarnings : [],
      
      coveragePercentage: `${areaVal.toFixed(2)}%`,
      aiConfidence: `${confPct.toFixed(1)}%`,
      processingTime: `${procTimeVal.toFixed(2)}s`,
      treatment: rec.treatment || 'Unspecified Treatment',
      day: rec.differentiation_day || 'Not specified',
      cellLine: rec.cell_line || 'Not specified',
      status: areaVal > 50 ? 'High Mineralization' : areaVal > 20 ? 'Moderate Mineralization' : 'Low Mineralization',
      statusColor: areaVal > 50 ? '#059669' : areaVal > 20 ? '#D97706' : '#64748B',
      stainType: rec.stain_name || 'Alizarin Red S (2%)',
      magnification: rec.objective_magnification || '20x Objective',
      resolution: '2048 × 1536 px',
      pattern: rec.spatial_pattern || 'Cluster Nodule Network',
      thumbnailUrl: imageUrl,
      imageUrl: imageUrl,
      overlay: resolvedOverlay,
      overlays: overlaysObj,
      nodules: rec.nodules || {},
      rawDbRecord: rec
    };
  } catch (error) {
    console.error(`Error fetching analysis ${analysisId}:`, error);
    return null;
  }
}

/**
 * Soft-deletes an analysis record in MySQL.
 */
export async function deleteAnalysis(analysisId) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/analyses/${analysisId}`, {
      method: 'DELETE',
      headers,
    });
    return response.ok;
  } catch (error) {
    console.error(`Error deleting analysis ${analysisId}:`, error);
    return false;
  }
}

/**
 * Restores a soft-deleted analysis record in MySQL.
 */
export async function restoreAnalysis(analysisId) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/analyses/${analysisId}/restore`, {
      method: 'POST',
      headers,
    });
    return response.ok;
  } catch (error) {
    console.error(`Error restoring analysis ${analysisId}:`, error);
    return false;
  }
}

/**
 * Restores a soft-deleted research note in MySQL.
 */
export async function restoreNote(noteId) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/notes/${noteId}/restore`, {
      method: 'POST',
      headers,
    });
    return response.ok;
  } catch (error) {
    console.error(`Error restoring note ${noteId}:`, error);
    return false;
  }
}

/**
 * Retrieves list of soft-deleted research notes for the authenticated user from MySQL.
 */
export async function fetchDeletedNotes() {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/notes/deleted`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) return [];

    const dbRecords = await response.json();
    if (!Array.isArray(dbRecords)) return [];

    return dbRecords.map((rec) => {
      const deletedDate = rec.deleted_at ? new Date(rec.deleted_at) : new Date();
      return {
        id: 'del-note-' + rec.id,
        dbId: rec.id,
        originalId: rec.id,
        name: rec.title || 'Research Note',
        title: rec.title || 'Research Note',
        type: 'Note',
        deletedAt: rec.deleted_at || rec.created_at,
        deletedDate: deletedDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
        deletedDateStr: deletedDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
        itemData: rec
      };
    });
  } catch (error) {
    console.error('Error fetching deleted notes from backend:', error);
    return [];
  }
}

/**
 * Retrieves list of soft-deleted analyses for the authenticated user from MySQL.
 */
export async function fetchDeletedAnalyses() {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/analyses/deleted`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch deleted analyses (${response.status})`);
    }

    const dbRecords = await response.json();
    if (!Array.isArray(dbRecords)) return [];

    return dbRecords.map((rec) => {
      const areaVal = Number(rec.mineralized_area_percent) || 0;
      const odVal = Number(rec.optical_density_proxy) || 0;
      const countVal = rec.nodule_count !== undefined ? rec.nodule_count : 0;
      const analyzedDate = rec.analyzed_at ? new Date(rec.analyzed_at) : new Date();
      const deletedDate = rec.deleted_at ? new Date(rec.deleted_at) : new Date();

      const rawImgUrl = rec.image_url || rec.overlays?.nodule_map || rec.overlays?.overlay || rec.overlay || null;
      const imageUrl = resolveWebFileUrl(rawImgUrl);

      const overlaysObj = rec.overlays || {};
      const resolvedOverlay = resolveWebFileUrl(overlaysObj.nodule_map || overlaysObj.overlay || rec.overlay || rawImgUrl);

      return {
        id: rec.id,
        dbId: rec.id,
        type: 'Result',
        micrographId: rec.micrograph_id,
        name: rec.sample_title || rec.original_name || 'ARS Micrograph Sample',
        title: rec.sample_title || rec.original_name || 'ARS Micrograph Sample',
        sampleId: rec.id,
        subtitle: `ID: ${rec.id.slice(0, 8)} • Area: ${areaVal.toFixed(2)}%`,
        date: analyzedDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
        deletedAt: rec.deleted_at || rec.analyzed_at,
        deletedDate: deletedDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
        deletedDateStr: deletedDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
        
        mineralizedArea: `${areaVal.toFixed(2)}%`,
        stainIntensityOD: `${odVal.toFixed(2)} OD`,
        nodulesCount: countVal,
        imageUrl: imageUrl,
        overlay: resolvedOverlay,
        rawDbRecord: rec
      };
    });
  } catch (error) {
    console.error('Error fetching deleted analyses from backend:', error);
    return [];
  }
}



/**
 * Retrieves researcher profile from MySQL.
 */
export async function fetchProfile() {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'GET',
      headers,
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error('Error fetching profile:', error);
    return null;
  }
}

/**
 * Updates researcher profile details in MySQL.
 */
export async function updateProfile(profileData) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(profileData),
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error('Error updating profile:', error);
    return null;
  }
}

/**
 * Retrieves research notes from MySQL.
 */
export async function fetchNotes() {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/notes`, {
      method: 'GET',
      headers,
    });
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.error('Error fetching notes:', error);
    return [];
  }
}

/**
 * Creates a research note in MySQL.
 */
export async function createNote(title, content) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/notes`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ title, content }),
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error('Error creating note:', error);
    return null;
  }
}

/**
 * Deletes a research note from MySQL.
 */
export async function deleteNote(noteId) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/notes/${noteId}`, {
      method: 'DELETE',
      headers,
    });
    return response.ok;
  } catch (error) {
    console.error(`Error deleting note ${noteId}:`, error);
    return false;
  }
}

/**
 * Retrieves saved comparisons from MySQL.
 */
export async function fetchSavedComparisons() {
  try {
    const headers = await getAuthHeaders({ 'Accept': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/saved-comparisons`, {
      method: 'GET',
      headers,
    });
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.error('Error fetching comparisons:', error);
    return [];
  }
}

/**
 * Saves a comparison in MySQL.
 */
export async function saveComparison(title, analysisIds, rankingSummary = {}) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/saved-comparisons`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ title, analysis_ids: analysisIds, ranking_summary: rankingSummary }),
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error('Error saving comparison:', error);
    return null;
  }
}

/**
 * Deletes a saved comparison record from MySQL.
 */
export async function deleteComparison(compId) {
  try {
    const headers = await getAuthHeaders({ 'Content-Type': 'application/json' });
    const response = await fetch(`${API_BASE_URL}/saved-comparisons/${compId}`, {
      method: 'DELETE',
      headers,
    });
    return response.ok;
  } catch (error) {
    console.error(`Error deleting comparison ${compId}:`, error);
    return false;
  }
}
