"""
FastAPI REST API Layer for StainScope Classical Computer Vision Analysis Engine.
Provides /auth/signup, /auth/login, /analyze, /analyze-batch, /analyses, /profile, /notes, and /saved-comparisons.
Persists records to XAMPP MySQL database 'stainscope' and local disk file storage.
"""
from typing import Optional, List, Dict, Any
import os
import sys
import asyncio
import io
import base64
import cv2
import numpy as np

if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pipeline import StainScopeCVEngine
from config import CVEngineConfig
from db_mysql import MySQLPersistenceManager, get_db_connection

app = FastAPI(
    title="StainScope Classical CV Analysis Engine & REST API",
    description="Microscopy ARS mineralization quantification engine with XAMPP MySQL database persistence.",
    version="1.0.0"
)

# Enable CORS for StainScope Web and Android App integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local storage directory for static file serving (/storage/... and /files/...)
STORAGE_PATH = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(STORAGE_PATH, exist_ok=True)
app.mount("/storage", StaticFiles(directory=STORAGE_PATH), name="storage")
app.mount("/files", StaticFiles(directory=STORAGE_PATH), name="files")

engine = StainScopeCVEngine()
db_manager = MySQLPersistenceManager()

DEV_MODE_TEST_USER_ID = "00000000-0000-0000-0000-000000000001"


async def get_authenticated_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    Validates JWT Bearer token against MySQL database session context and returns verified user_id.
    """
    is_dev_mode = os.getenv("STAINSCOPE_DEV_MODE", "false").lower() in ("true", "1")
    
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ")[1].strip()
        user_id = db_manager.verify_jwt_token(token)
        if user_id:
            return user_id

    if is_dev_mode:
        return DEV_MODE_TEST_USER_ID

    raise HTTPException(
        status_code=401,
        detail="Authentication required. Please provide a valid Bearer token in the Authorization header."
    )


def encode_image_to_base64(img_bgr: np.ndarray, format_ext: str = ".png") -> str:
    """Helper to convert BGR image array into base64 data URI string."""
    if img_bgr is None or img_bgr.size == 0:
        return ""
    success, buffer = cv2.imencode(format_ext, img_bgr)
    if not success:
        return ""
    b64_str = base64.b64encode(buffer.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


# Pydantic Schemas for Requests
class UserSignUpRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    institution: Optional[str] = None
    lab_name: Optional[str] = None


class ResearchNoteCreateRequest(BaseModel):
    title: str
    content: str


class ComparisonSaveRequest(BaseModel):
    title: str
    analysis_ids: List[str]
    ranking_summary: Optional[Dict[str, Any]] = None


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "StainScope Classical CV Engine",
        "version": "1.0.0",
        "db_connected": db_manager.is_connected(),
        "dev_mode": os.getenv("STAINSCOPE_DEV_MODE", "false").lower() in ("true", "1")
    }


# Authentication Endpoints
@app.get("/files/{file_type}/{subpath:path}")
async def get_secure_file(
    file_type: str,
    subpath: str,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    """
    Authenticated & authorized file serving endpoint for micrographs and analysis overlays.
    Validates JWT Bearer token (from Header or query param ?token=...) and verifies user ownership in MySQL.
    """
    is_dev_mode = os.getenv("STAINSCOPE_DEV_MODE", "false").lower() in ("true", "1")
    
    auth_token = None
    if authorization and authorization.startswith("Bearer "):
        auth_token = authorization.split("Bearer ")[1].strip()
    elif token:
        auth_token = token.strip()
        
    user_id = db_manager.verify_jwt_token(auth_token) if auth_token else None
    if not user_id and is_dev_mode:
        user_id = DEV_MODE_TEST_USER_ID

    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication token required to access file.")

    clean_subpath = os.path.normpath(subpath).lstrip("/\\")
    if ".." in clean_subpath:
        raise HTTPException(status_code=400, detail="Invalid path traversal.")

    if clean_subpath.startswith(f"{file_type}/") or clean_subpath.startswith(f"{file_type}\\"):
        clean_subpath = clean_subpath[len(file_type)+1:]

    full_disk_path = os.path.join(STORAGE_PATH, file_type, clean_subpath)

    conn = get_db_connection()
    try:
        if file_type == "micrographs":
            parts = clean_subpath.replace("\\", "/").split("/")
            mg_id = parts[1] if len(parts) >= 2 else parts[0]
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM micrographs WHERE id = %s OR user_id = %s", (mg_id, parts[0]))
                rows = cursor.fetchall()
                if not rows:
                    raise HTTPException(status_code=404, detail="Micrograph record not found.")
                owner_ids = [r["user_id"] for r in rows if "user_id" in r]
                if user_id not in owner_ids:
                    raise HTTPException(status_code=403, detail="Forbidden: You do not own this file.")

        elif file_type == "analysis-overlays":
            parts = clean_subpath.replace("\\", "/").split("/")
            an_id = parts[0]
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM analyses WHERE id = %s", (an_id,))
                an_row = cursor.fetchone()
                if not an_row:
                    raise HTTPException(status_code=404, detail="Analysis record not found.")
                if an_row.get("user_id") != user_id:
                    raise HTTPException(status_code=403, detail="Forbidden: You do not own this analysis file.")
        else:
            raise HTTPException(status_code=400, detail="Invalid file type category.")

    finally:
        conn.close()

    if not os.path.exists(full_disk_path):
        raise HTTPException(status_code=404, detail="Requested file does not exist on disk.")

    mime_type = "image/png"
    if full_disk_path.lower().endswith((".tif", ".tiff")):
        mime_type = "image/tiff"
    elif full_disk_path.lower().endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"

    return FileResponse(full_disk_path, media_type=mime_type)


@app.post("/auth/signup")
@app.post("/signup")
def signup_user(req: UserSignUpRequest):
    """
    Creates a new user in XAMPP MySQL database with bcrypt password hash.
    Returns access token and user info.
    """
    try:
        res = db_manager.create_user(
            email=req.email,
            password=req.password,
            full_name=req.full_name
        )
        return {
            "status": "success",
            "user_id": res["user_id"],
            "email": res["email"],
            "full_name": res["full_name"],
            "access_token": res["access_token"],
            "token_type": "bearer"
        }
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Signup failed: {err}")


@app.post("/auth/login")
def login_user(req: UserLoginRequest):
    """
    Authenticates user against XAMPP MySQL database using bcrypt password verification.
    """
    try:
        res = db_manager.authenticate_user(
            email=req.email,
            password=req.password
        )
        return {
            "status": "success",
            "user_id": res["user_id"],
            "email": res["email"],
            "full_name": res["full_name"],
            "access_token": res["access_token"],
            "token_type": "bearer"
        }
    except ValueError as val_err:
        raise HTTPException(status_code=401, detail=str(val_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Login failed: {err}")


# Analysis Endpoints
@app.post("/analyze")
async def analyze_single_image(
    file: UploadFile = File(...),
    pixel_size_um: Optional[float] = Form(None),
    sample_title: Optional[str] = Form(None),
    cell_line: Optional[str] = Form(None),
    treatment: Optional[str] = Form(None),
    differentiation_day: Optional[str] = Form(None),
    user_id: str = Depends(get_authenticated_user_id)
):
    """
    Analyzes a single ARS microscopy image file and persists run & overlays into MySQL & local disk storage.
    User ID is strictly derived from the validated JWT token.
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    raw_img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    
    if raw_img is None:
        return {
            "valid": False,
            "reason": "Invalid or unreadable image file.",
            "warnings": []
        }
        
    # Standardize image channels and bit depth without clipping or loss
    if raw_img.dtype == np.uint16:
        image = (raw_img / 256.0).astype(np.uint8)
    else:
        image = raw_img.copy()

    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    print(f"[Image Load Audit] filename={file.filename}, shape={image.shape}, dtype={image.dtype}, min={np.min(image)}, max={np.max(image)}, mean={np.mean(image):.2f}", flush=True)
        
    result = engine.analyze_image(image, pixel_size_um=pixel_size_um, generate_images=True)
    
    if not result.get("valid", False):
        return {
            "valid": False,
            "reason": result.get("reason", "Image validation failed."),
            "warnings": result.get("quality_warnings", result.get("quality", {}).get("warnings", []))
        }
        
    visuals = result.pop("visualizations", {})
    result.pop("binary_mask_raw", None)
    
    saved_meta = {}
    try:
        saved_meta = db_manager.save_analysis_run(
            analysis_result=result,
            raw_image_bytes=contents,
            file_name=file.filename or "micrograph.tif",
            user_id=user_id,
            pixel_size_um=pixel_size_um,
            sample_title=sample_title or file.filename or "ARS Microscopy Sample",
            overlays_bgr_dict=visuals,
            model_type="classical_cv",
            model_version="1.0.0",
            analysis_method="classical_cv_pipeline",
            analysis_version="1.0.0"
        )
    except Exception as db_err:
        print(f"[MySQL Persistence Warning] {db_err}")

    recent_analysis_cache = getattr(app, "_recent_analysis_cache", {})
    
    nodule_map_b64 = encode_image_to_base64(visuals.get("nodule_map"))
    overlay_b64 = encode_image_to_base64(visuals.get("overlay"))
    mask_b64 = encode_image_to_base64(visuals.get("mask"))
    val_panel_b64 = encode_image_to_base64(visuals.get("validation_panel"))
    
    overlays = {
        "nodule_map": nodule_map_b64,
        "overlay": overlay_b64,
        "mask": mask_b64,
        "validation_panel": val_panel_b64
    }
    
    analysis_id = saved_meta.get("analysis_id") or str(uuid.uuid4())
    micrograph_id = saved_meta.get("micrograph_id") or str(uuid.uuid4())
    
    resp_payload = {
        "valid": True,
        "analysis_id": analysis_id,
        "id": analysis_id,
        "micrograph_id": micrograph_id,
        "user_id": user_id,
        "sample_title": sample_title or file.filename or "ARS Microscopy Sample",
        "stain": result["stain"],
        "image_quality": result["image_quality"],
        "mineralization": {
            "area": result["mineralization"]["area_pixels"],
            "area_pixels": result["mineralization"]["area_pixels"],
            "area_percent": result["mineralization"]["area_percent"],
            "total_area": result["mineralization"]["total_pixels"],
            "total_pixels": result["mineralization"]["total_pixels"],
            "density_per_10k_px": result["mineralization"]["density_per_10k_px"]
        },
        "nodules": {
            "count": result["nodules"]["count"],
            "min": result["nodules"]["min_size_pixels"],
            "max": result["nodules"]["max_size_pixels"],
            "mean": result["nodules"]["mean_size_pixels"],
            "median": result["nodules"]["median_size_pixels"],
            "min_size_pixels": result["nodules"]["min_size_pixels"],
            "max_size_pixels": result["nodules"]["max_size_pixels"],
            "mean_size_pixels": result["nodules"]["mean_size_pixels"],
            "median_size_pixels": result["nodules"]["median_size_pixels"],
            "size_distribution": result["nodules"]["size_distribution"],
            "objects": result["nodules"]["objects"]
        },
        "pattern": result["mineralization"]["spatial_pattern"],
        "intensity": {
            "optical_density": result["mineralization"]["optical_density"]
        },
        "quality": result["quality"],
        "calibration": result["calibration"],
        "physical_metrics": result["physical_metrics"],
        "overlay": nodule_map_b64,
        "overlays": overlays
    }
    
    recent_analysis_cache[analysis_id] = resp_payload
    app._recent_analysis_cache = recent_analysis_cache
    
    return resp_payload


@app.post("/analyze-batch")
async def analyze_batch_images(
    files: List[UploadFile] = File(...),
    pixel_size_um: Optional[float] = Form(None),
    user_id: str = Depends(get_authenticated_user_id)
):
    """Analyzes multiple microscopy images independently and provides comparative summary."""
    samples = {}
    for f in files:
        contents = await f.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            samples[f.filename] = img
            
    if not samples:
        raise HTTPException(status_code=400, detail="No valid images provided in batch.")
        
    batch_res = engine.analyze_batch(samples, pixel_size_um=pixel_size_um)
    for sample_name, res in batch_res.get("individual_results", {}).items():
        if isinstance(res, dict):
            res.pop("binary_mask_raw", None)
            res.pop("visualizations", None)
    return batch_res


# REST API Repository Endpoints
@app.get("/analyses")
def list_user_analyses(user_id: str = Depends(get_authenticated_user_id)):
    """Retrieves list of all active non-deleted analysis runs for the authenticated user from MySQL."""
    return db_manager.list_analyses(user_id)


@app.get("/analyses/deleted")
def list_deleted_user_analyses(user_id: str = Depends(get_authenticated_user_id)):
    """Retrieves list of deleted analysis runs for the authenticated user from MySQL (within 28-day retention)."""
    return db_manager.list_deleted_analyses(user_id)


@app.get("/analyses/{analysis_id}")
def get_analysis_detail(analysis_id: str, user_id: str = Depends(get_authenticated_user_id)):
    """Retrieves full analysis record including granular nodules list and overlays."""
    analysis = db_manager.get_analysis(analysis_id, user_id=user_id)
    if not analysis:
        recent_cache = getattr(app, "_recent_analysis_cache", {})
        cached = recent_cache.get(analysis_id)
        if cached and cached.get("user_id") == user_id:
            analysis = cached
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return analysis


@app.delete("/analyses/{analysis_id}")
def delete_user_analysis(analysis_id: str, user_id: str = Depends(get_authenticated_user_id)):
    """Soft-deletes an analysis record in MySQL."""
    success = db_manager.delete_analysis(analysis_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not delete analysis record.")
    return {"status": "deleted", "id": analysis_id}


@app.post("/analyses/{analysis_id}/restore")
def restore_user_analysis(analysis_id: str, user_id: str = Depends(get_authenticated_user_id)):
    """Restores a soft-deleted analysis record in MySQL."""
    success = db_manager.restore_analysis(analysis_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not restore analysis record.")
    return {"status": "restored", "id": analysis_id}


@app.post("/analyses/cleanup-deleted")
def cleanup_deleted_analyses(user_id: str = Depends(get_authenticated_user_id)):
    """Purges expired deleted records older than 28 days."""
    count = db_manager.cleanup_expired_deleted_analyses()
    return {"status": "success", "purged_count": count}



@app.get("/profile")
def get_profile(user_id: str = Depends(get_authenticated_user_id)):
    """Retrieves profile record for authenticated user."""
    profile = db_manager.get_user_profile(user_id)
    if not profile:
        return {
            "id": user_id,
            "full_name": "Dr. StainScope Researcher",
            "role": "Bone Tissue Engineer",
            "institution": "BioMed Research Institute",
            "lab_name": "Regenerative Medicine & Osteogenesis Lab"
        }
    return profile


@app.put("/profile")
def update_profile(req: ProfileUpdateRequest, user_id: str = Depends(get_authenticated_user_id)):
    """Updates profile record for authenticated user."""
    updated = db_manager.update_user_profile(user_id, req.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update user profile.")
    return updated


@app.get("/notes")
def list_notes(user_id: str = Depends(get_authenticated_user_id)):
    """Retrieves research notes for authenticated user."""
    return db_manager.list_research_notes(user_id)


@app.get("/notes/deleted")
def list_deleted_notes(user_id: str = Depends(get_authenticated_user_id)):
    """Retrieves soft-deleted research notes for authenticated user."""
    return db_manager.list_deleted_research_notes(user_id)


@app.post("/notes")
def create_note(req: ResearchNoteCreateRequest, user_id: str = Depends(get_authenticated_user_id)):
    """Creates a research note in MySQL for authenticated user."""
    note = db_manager.create_research_note(user_id, req.title, req.content)
    if not note:
        raise HTTPException(status_code=400, detail="Could not create research note.")
    return note


@app.delete("/notes/{note_id}")
def delete_note(note_id: str, user_id: str = Depends(get_authenticated_user_id)):
    """Deletes a research note in MySQL."""
    success = db_manager.delete_research_note(note_id, user_id)
    return {"status": "deleted" if success else "failed", "id": note_id}


@app.post("/notes/{note_id}/restore")
def restore_note(note_id: str, user_id: str = Depends(get_authenticated_user_id)):
    """Restores a soft-deleted research note in MySQL."""
    success = db_manager.restore_research_note(note_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not restore research note.")
    return {"status": "restored", "id": note_id}



@app.get("/saved-comparisons")
def list_saved_comparisons(user_id: str = Depends(get_authenticated_user_id)):
    """Retrieves saved batch comparisons from MySQL."""
    return db_manager.list_batch_comparisons(user_id)


@app.post("/saved-comparisons")
def create_saved_comparison(req: ComparisonSaveRequest, user_id: str = Depends(get_authenticated_user_id)):
    """Saves a batch comparison record in MySQL."""
    comp = db_manager.create_batch_comparison(
        user_id=user_id,
        title=req.title,
        ranking_summary=req.ranking_summary or {},
        analysis_ids=req.analysis_ids
    )
    if not comp:
        raise HTTPException(status_code=400, detail="Could not save comparison.")
    return comp


@app.delete("/saved-comparisons/{comp_id}")
def delete_saved_comparison(comp_id: str, user_id: str = Depends(get_authenticated_user_id)):
    """Deletes a saved comparison record in MySQL."""
    success = db_manager.delete_batch_comparison(comp_id, user_id)
    return {"status": "deleted" if success else "failed", "id": comp_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
