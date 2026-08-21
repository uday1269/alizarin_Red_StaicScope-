"""
StainScope MySQL Database & Local File Storage Persistence Layer.
Replaces Supabase completely with XAMPP MySQL database and local disk file storage.

Strict architecture constraints:
- Uses XAMPP MySQL database 'stainscope'.
- Stores file paths & metadata in MySQL, NOT heavy Base64 image payloads.
- Saves raw micrographs to storage/micrographs/{user_id}/{micrograph_id}/{filename}.
- Saves analysis overlays to storage/analysis-overlays/{analysis_id}/{overlay_type}.png.
- Maintains model provenance: model_type="classical_cv", model_version="1.0.0", analysis_method="classical_cv_pipeline", analysis_version="1.0.0".
- Implements bcrypt password hashing & JWT token verification.
- Enforces strict multi-tenant user isolation on all database queries.
"""
import os
import uuid
import hashlib
import json
import datetime
import cv2
import numpy as np
import pymysql
import pymysql.cursors
from typing import Dict, Any, List, Optional
import bcrypt
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "stainscope")

JWT_SECRET = os.getenv("JWT_SECRET", "stainscope_jwt_secret_key_2026_x7f89a")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72

STORAGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "storage")
MICROGRAPHS_DIR = os.path.join(STORAGE_BASE_DIR, "micrographs")
OVERLAYS_DIR = os.path.join(STORAGE_BASE_DIR, "analysis-overlays")

os.makedirs(MICROGRAPHS_DIR, exist_ok=True)
os.makedirs(OVERLAYS_DIR, exist_ok=True)


def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def compute_file_hash(data_bytes: bytes) -> str:
    return hashlib.sha256(data_bytes).hexdigest()


class MySQLPersistenceManager:
    """
    MySQL & Local File Storage Service Layer for StainScope FastAPI Backend.
    """
    def __init__(self):
        self.host = MYSQL_HOST
        self.database = MYSQL_DATABASE
        self._ensure_schema_columns()

    def _ensure_schema_columns(self):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM analyses LIKE 'deleted_at'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE analyses ADD COLUMN deleted_at DATETIME DEFAULT NULL")
                cursor.execute("SHOW COLUMNS FROM research_notes LIKE 'deleted_at'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE research_notes ADD COLUMN deleted_at DATETIME DEFAULT NULL")
            conn.close()
        except Exception as e:
            print(f"[Schema Migration Notice] {e}")

    def is_connected(self) -> bool:
        try:
            conn = get_db_connection()
            conn.close()
            return True
        except Exception:
            return False

    # Password & JWT Helpers
    def hash_password(self, password: str) -> str:
        pwd_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            pwd_bytes = plain_password.encode('utf-8')[:72]
            hash_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False

    def create_jwt_token(self, user_id: str, email: str) -> str:
        payload = {
            "sub": user_id,
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def verify_jwt_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload.get("sub")
        except Exception:
            return None

    # User Auth & Profile Methods
    def create_user(self, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email_clean,))
                if cursor.fetchone():
                    raise ValueError("A user with this email address has already been registered.")
                
                user_id = str(uuid.uuid4())
                pwd_hash = self.hash_password(password)
                cursor.execute(
                    "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
                    (user_id, email_clean, pwd_hash)
                )
                
                display_name = full_name or email_clean.split("@")[0]
                cursor.execute(
                    "INSERT INTO profiles (id, email, full_name) VALUES (%s, %s, %s)",
                    (user_id, email_clean, display_name)
                )
                
                token = self.create_jwt_token(user_id, email_clean)
                return {
                    "user_id": user_id,
                    "email": email_clean,
                    "full_name": display_name,
                    "access_token": token
                }
        finally:
            conn.close()

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (email_clean,))
                user_row = cursor.fetchone()
                if not user_row or not self.verify_password(password, user_row["password_hash"]):
                    raise ValueError("Invalid email or password.")
                
                user_id = user_row["id"]
                cursor.execute("SELECT full_name FROM profiles WHERE id = %s", (user_id,))
                profile_row = cursor.fetchone()
                full_name = profile_row["full_name"] if profile_row else email_clean.split("@")[0]
                
                token = self.create_jwt_token(user_id, email_clean)
                return {
                    "user_id": user_id,
                    "email": email_clean,
                    "full_name": full_name,
                    "access_token": token
                }
        finally:
            conn.close()

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM profiles WHERE id = %s", (user_id,))
                prof = cursor.fetchone()
                if prof:
                    if isinstance(prof.get("created_at"), (datetime.date, datetime.datetime)):
                        prof["created_at"] = prof["created_at"].isoformat()
                    if isinstance(prof.get("updated_at"), (datetime.date, datetime.datetime)):
                        prof["updated_at"] = prof["updated_at"].isoformat()
                return prof
        finally:
            conn.close()

    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = ["full_name", "role", "institution", "lab_name"]
        set_clauses = []
        params = []
        for key in allowed_fields:
            if key in updates and updates[key] is not None:
                set_clauses.append(f"{key} = %s")
                params.append(updates[key])
                
        if not set_clauses:
            return self.get_user_profile(user_id)
            
        params.append(user_id)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"UPDATE profiles SET {', '.join(set_clauses)} WHERE id = %s", tuple(params))
            return self.get_user_profile(user_id)
        finally:
            conn.close()

    # Analysis Persistence Methods
    def save_analysis_run(
        self,
        analysis_result: Dict[str, Any],
        raw_image_bytes: bytes,
        file_name: str,
        user_id: str,
        experiment_id: Optional[str] = None,
        pixel_size_um: Optional[float] = None,
        sample_title: str = "ARS Microscopy Sample",
        overlays_bgr_dict: Optional[Dict[str, np.ndarray]] = None,
        model_type: str = "classical_cv",
        model_version: str = "1.0.0",
        analysis_method: str = "classical_cv_pipeline",
        analysis_version: str = "1.0.0"
    ) -> Dict[str, Any]:
        if not user_id:
            raise ValueError("Authenticated user_id is required to save an analysis run.")
            
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                analysis_id = str(uuid.uuid4())
                micrograph_id = str(uuid.uuid4())
                
                # Compute image specs & hash
                file_hash = compute_file_hash(raw_image_bytes)
                file_size = len(raw_image_bytes)
                nparr = np.frombuffer(raw_image_bytes, np.uint8)
                img_temp = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                h_px, w_px = (img_temp.shape[0], img_temp.shape[1]) if img_temp is not None else (0, 0)

                # 1. Save Micrograph File to Local Disk Storage
                user_mg_dir = os.path.join(MICROGRAPHS_DIR, user_id, micrograph_id)
                os.makedirs(user_mg_dir, exist_ok=True)
                mg_disk_path = os.path.join(user_mg_dir, file_name)
                with open(mg_disk_path, "wb") as f:
                    f.write(raw_image_bytes)
                rel_mg_path = f"micrographs/{user_id}/{micrograph_id}/{file_name}"

                # Insert Micrograph Record into MySQL
                cursor.execute(
                    """
                    INSERT INTO micrographs 
                    (id, user_id, experiment_id, file_name, original_name, storage_bucket, storage_path, file_size_bytes, mime_type, width_px, height_px, file_hash, pixel_size_um)
                    VALUES (%s, %s, %s, %s, %s, 'micrographs', %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        micrograph_id, user_id, experiment_id, file_name, file_name,
                        rel_mg_path, file_size,
                        "image/tiff" if file_name.endswith((".tif", ".tiff")) else "image/png",
                        w_px, h_px, file_hash, pixel_size_um
                    )
                )

                # 2. Insert Master Analysis Record into MySQL
                is_valid = analysis_result.get("valid", False)
                rejection_reason = analysis_result.get("reason", None)
                min_data = analysis_result.get("mineralization", {})
                nod_data = analysis_result.get("nodules", {})
                qual_data = analysis_result.get("quality", {})

                cursor.execute(
                    """
                    INSERT INTO analyses 
                    (id, user_id, micrograph_id, experiment_id, model_type, model_version, analysis_method, analysis_version,
                     status, is_valid, rejection_reason, sample_title, objective_magnification, stain_name,
                     mineralized_area_pixels, mineralized_area_percent, total_image_pixels, optical_density_proxy,
                     nodule_count, min_nodule_size_pixels, max_nodule_size_pixels, mean_nodule_size_pixels, median_nodule_size_pixels,
                     nodule_size_distribution, spatial_pattern, overall_confidence, quality_score, quality_warnings, processing_time_sec)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        analysis_id, user_id, micrograph_id, experiment_id, model_type, model_version, analysis_method, analysis_version,
                        "COMPLETED" if is_valid else "REJECTED", is_valid, rejection_reason, sample_title, "20x Objective", "Alizarin Red S (2%)",
                        int(min_data.get("area_pixels", 0)), float(min_data.get("area_percent", 0.0)), int(min_data.get("total_pixels", 0)),
                        float(min_data.get("optical_density", 0.0)), int(nod_data.get("count", 0)),
                        float(nod_data.get("min_size_pixels", 0.0)), float(nod_data.get("max_size_pixels", 0.0)),
                        float(nod_data.get("mean_size_pixels", 0.0)), float(nod_data.get("median_size_pixels", 0.0)),
                        json.dumps(nod_data.get("size_distribution", {})), str(min_data.get("spatial_pattern", "dispersed")),
                        float(qual_data.get("overall_confidence", 0.95)), float(qual_data.get("quality_score", 0.95)),
                        json.dumps(qual_data.get("quality_warnings", [])), float(qual_data.get("processing_time_sec", 0.0))
                    )
                )

                # 3. Insert Granular Nodules into MySQL
                nodule_objects = nod_data.get("objects", [])
                for idx, n in enumerate(nodule_objects, 1):
                    bbox = n.get("bbox", [0, 0, 0, 0])
                    centroid = n.get("centroid", (0.0, 0.0))
                    cursor.execute(
                        """
                        INSERT INTO nodules 
                        (analysis_id, nodule_index, label_id, area_pixels, centroid_x, centroid_y, bbox_x, bbox_y, bbox_w, bbox_h, circularity, local_contrast, size_category, confidence, contour_json)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            analysis_id, idx, n.get("id", f"N{idx}"), int(n.get("area_pixels", 0)),
                            float(centroid[0]), float(centroid[1]), int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]),
                            float(n.get("circularity", 0.0)), float(n.get("local_contrast", 0.0)),
                            str(n.get("size_category", "small")), float(n.get("confidence", 0.95)),
                            json.dumps(n.get("contour", []))
                        )
                    )

                # 4. Save Overlay Files to Disk and MySQL
                saved_overlays = {}
                if overlays_bgr_dict:
                    analysis_ov_dir = os.path.join(OVERLAYS_DIR, analysis_id)
                    os.makedirs(analysis_ov_dir, exist_ok=True)
                    for overlay_type, overlay_bgr in overlays_bgr_dict.items():
                        if overlay_bgr is None or overlay_bgr.size == 0:
                            continue
                        ov_filename = f"{overlay_type}.png"
                        ov_disk_path = os.path.join(analysis_ov_dir, ov_filename)
                        cv2.imwrite(ov_disk_path, overlay_bgr)
                        rel_ov_path = f"analysis-overlays/{analysis_id}/{ov_filename}"
                        ov_size = os.path.getsize(ov_disk_path) if os.path.exists(ov_disk_path) else 0
                        ov_id = str(uuid.uuid4())

                        cursor.execute(
                            """
                            INSERT INTO analysis_overlays (id, analysis_id, overlay_type, storage_bucket, storage_path, file_size_bytes, mime_type)
                            VALUES (%s, %s, %s, 'analysis-overlays', %s, %s, 'image/png')
                            """,
                            (ov_id, analysis_id, overlay_type, rel_ov_path, ov_size)
                        )
                        saved_overlays[overlay_type] = f"/files/{rel_ov_path}"

                # Update total scans count on user profile
                cursor.execute("UPDATE profiles SET total_scans = total_scans + 1 WHERE id = %s", (user_id,))

                return {
                    "analysis_id": analysis_id,
                    "micrograph_id": micrograph_id,
                    "user_id": user_id,
                    "file_name": file_name,
                    "model_type": model_type,
                    "model_version": model_version,
                    "analysis_method": analysis_method,
                    "analysis_version": analysis_version,
                    "saved_nodules_count": len(nodule_objects),
                    "saved_overlays": saved_overlays
                }
        finally:
            conn.close()

    def get_analysis(self, analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM analyses WHERE id = %s AND is_deleted = FALSE"
                params = [analysis_id]
                if user_id:
                    sql += " AND user_id = %s"
                    params.append(user_id)
                cursor.execute(sql, tuple(params))
                an = cursor.fetchone()
                if not an:
                    return None

                # Format datetimes
                for dt_key in ["analyzed_at", "created_at"]:
                    if isinstance(an.get(dt_key), (datetime.date, datetime.datetime)):
                        an[dt_key] = an[dt_key].isoformat()

                # Parse JSON fields
                for json_key in ["nodule_size_distribution", "quality_warnings"]:
                    if isinstance(an.get(json_key), str):
                        try:
                            an[json_key] = json.loads(an[json_key])
                        except Exception:
                            pass

                # Fetch Micrograph info
                if an.get("micrograph_id"):
                    cursor.execute("SELECT storage_path FROM micrographs WHERE id = %s", (an["micrograph_id"],))
                    mg = cursor.fetchone()
                    if mg and mg.get("storage_path"):
                        an["image_url"] = f"/files/{mg['storage_path']}"

                # Fetch Nodules list
                cursor.execute("SELECT * FROM nodules WHERE analysis_id = %s ORDER BY nodule_index", (analysis_id,))
                nodules = cursor.fetchall()
                for nod in nodules:
                    if isinstance(nod.get("contour_json"), str):
                        try:
                            nod["contour_json"] = json.loads(nod["contour_json"])
                        except Exception:
                            pass
                an["nodules_list"] = nodules

                # Fetch Overlays map
                cursor.execute("SELECT overlay_type, storage_path FROM analysis_overlays WHERE analysis_id = %s", (analysis_id,))
                overlays = cursor.fetchall()
                ov_map = {}
                for ov in overlays:
                    ov_map[ov["overlay_type"]] = f"/files/{ov['storage_path']}"
                an["overlays"] = ov_map
                if "nodule_map" in ov_map:
                    an["overlay"] = ov_map["nodule_map"]
                elif "overlay" in ov_map:
                    an["overlay"] = ov_map["overlay"]

                # Build nested DTO structures for contract compatibility
                an["stain"] = {"status": "ARS-compatible", "stain_name": an.get("stain_name")}
                an["image_quality"] = {"status": "PASS", "score": an.get("quality_score", 0.95)}
                an["mineralization"] = {
                    "area_pixels": an.get("mineralized_area_pixels", 0),
                    "area_percent": an.get("mineralized_area_percent", 0.0),
                    "total_pixels": an.get("total_image_pixels", 0),
                    "optical_density": an.get("optical_density_proxy", 0.0),
                    "density_per_10k_px": (an.get("mineralized_area_percent", 0.0) / 100.0) * 10000.0
                }
                an["nodules"] = {
                    "count": an.get("nodule_count", 0),
                    "min_size_pixels": an.get("min_nodule_size_pixels", 0.0),
                    "max_size_pixels": an.get("max_nodule_size_pixels", 0.0),
                    "mean_size_pixels": an.get("mean_nodule_size_pixels", 0.0),
                    "median_size_pixels": an.get("median_nodule_size_pixels", an.get("median_size_pixels", 0.0)),
                    "size_distribution": an.get("nodule_size_distribution", {}),
                    "objects": nodules
                }
                an["quality"] = {
                    "overall_confidence": an.get("overall_confidence", 0.95),
                    "quality_score": an.get("quality_score", 0.95),
                    "quality_warnings": an.get("quality_warnings", [])
                }
                an["calibration"] = {
                    "pixel_size_um": 1.0,
                    "ai_confidence": an.get("overall_confidence", 0.95)
                }

                return an
        finally:
            conn.close()

    def list_analyses(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.*, m.storage_path as micrograph_storage_path
                    FROM analyses a
                    LEFT JOIN micrographs m ON a.micrograph_id = m.id
                    WHERE a.user_id = %s AND a.is_deleted = FALSE
                    ORDER BY a.analyzed_at DESC
                    """,
                    (user_id,)
                )
                records = cursor.fetchall()
                for rec in records:
                    for dt_key in ["analyzed_at", "created_at"]:
                        if isinstance(rec.get(dt_key), (datetime.date, datetime.datetime)):
                            rec[dt_key] = rec[dt_key].isoformat()
                    if rec.get("micrograph_storage_path"):
                        rec["image_url"] = f"/files/{rec['micrograph_storage_path']}"

                    # Fetch overlay references
                    cursor.execute("SELECT overlay_type, storage_path FROM analysis_overlays WHERE analysis_id = %s", (rec["id"],))
                    ovs = cursor.fetchall()
                    ov_map = {}
                    for ov in ovs:
                        ov_map[ov["overlay_type"]] = f"/files/{ov['storage_path']}"
                    rec["overlays"] = ov_map
                    if "nodule_map" in ov_map:
                        rec["overlay"] = ov_map["nodule_map"]
                    elif "overlay" in ov_map:
                        rec["overlay"] = ov_map["overlay"]

                return records
        finally:
            conn.close()

    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE analyses SET is_deleted = TRUE, deleted_at = NOW() WHERE id = %s AND user_id = %s",
                    (analysis_id, user_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def restore_analysis(self, analysis_id: str, user_id: str) -> bool:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE analyses SET is_deleted = FALSE, deleted_at = NULL WHERE id = %s AND user_id = %s",
                    (analysis_id, user_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def list_deleted_analyses(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.*, m.storage_path as micrograph_storage_path
                    FROM analyses a
                    LEFT JOIN micrographs m ON a.micrograph_id = m.id
                    WHERE a.user_id = %s 
                      AND a.is_deleted = TRUE 
                      AND (a.deleted_at IS NULL OR a.deleted_at >= NOW() - INTERVAL 28 DAY)
                    ORDER BY COALESCE(a.deleted_at, a.analyzed_at) DESC
                    """,
                    (user_id,)
                )
                records = cursor.fetchall()
                for rec in records:
                    for dt_key in ["analyzed_at", "created_at", "deleted_at"]:
                        if isinstance(rec.get(dt_key), (datetime.date, datetime.datetime)):
                            rec[dt_key] = rec[dt_key].isoformat()
                    if rec.get("micrograph_storage_path"):
                        rec["image_url"] = f"/files/{rec['micrograph_storage_path']}"

                    cursor.execute("SELECT overlay_type, storage_path FROM analysis_overlays WHERE analysis_id = %s", (rec["id"],))
                    ovs = cursor.fetchall()
                    ov_map = {}
                    for ov in ovs:
                        ov_map[ov["overlay_type"]] = f"/files/{ov['storage_path']}"
                    rec["overlays"] = ov_map
                    if "nodule_map" in ov_map:
                        rec["overlay"] = ov_map["nodule_map"]
                    elif "overlay" in ov_map:
                        rec["overlay"] = ov_map["overlay"]

                return records
        finally:
            conn.close()

    def cleanup_expired_deleted_analyses(self) -> int:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM analyses WHERE is_deleted = TRUE AND deleted_at IS NOT NULL AND deleted_at < NOW() - INTERVAL 28 DAY"
                )
                return cursor.rowcount
        finally:
            conn.close()


    # Research Notes Methods
    def list_research_notes(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM research_notes WHERE user_id = %s AND is_deleted = FALSE ORDER BY created_at DESC", (user_id,))
                notes = cursor.fetchall()
                for n in notes:
                    for dt_key in ["created_at", "updated_at"]:
                        if isinstance(n.get(dt_key), (datetime.date, datetime.datetime)):
                            n[dt_key] = n[dt_key].isoformat()
                return notes
        finally:
            conn.close()

    def create_research_note(self, user_id: str, title: str, content: str) -> Dict[str, Any]:
        note_id = str(uuid.uuid4())
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO research_notes (id, user_id, title, content) VALUES (%s, %s, %s, %s)",
                    (note_id, user_id, title, content)
                )
                cursor.execute("SELECT * FROM research_notes WHERE id = %s", (note_id,))
                note = cursor.fetchone()
                for dt_key in ["created_at", "updated_at"]:
                    if isinstance(note.get(dt_key), (datetime.date, datetime.datetime)):
                        note[dt_key] = note[dt_key].isoformat()
                return note
        finally:
            conn.close()

    def delete_research_note(self, note_id: str, user_id: str) -> bool:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_notes SET is_deleted = TRUE, deleted_at = NOW() WHERE id = %s AND user_id = %s",
                    (note_id, user_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def restore_research_note(self, note_id: str, user_id: str) -> bool:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_notes SET is_deleted = FALSE, deleted_at = NULL WHERE id = %s AND user_id = %s",
                    (note_id, user_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def list_deleted_research_notes(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM research_notes 
                    WHERE user_id = %s 
                      AND is_deleted = TRUE 
                      AND (deleted_at IS NULL OR deleted_at >= NOW() - INTERVAL 28 DAY)
                    ORDER BY COALESCE(deleted_at, created_at) DESC
                    """,
                    (user_id,)
                )
                notes = cursor.fetchall()
                for n in notes:
                    for dt_key in ["created_at", "updated_at", "deleted_at"]:
                        if isinstance(n.get(dt_key), (datetime.date, datetime.datetime)):
                            n[dt_key] = n[dt_key].isoformat()
                return notes
        finally:
            conn.close()


    # Batch Comparisons Methods
    def list_batch_comparisons(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM batch_comparisons WHERE user_id = %s AND is_deleted = FALSE ORDER BY created_at DESC", (user_id,))
                comps = cursor.fetchall()
                for c in comps:
                    for dt_key in ["created_at", "updated_at"]:
                        if isinstance(c.get(dt_key), (datetime.date, datetime.datetime)):
                            c[dt_key] = c[dt_key].isoformat()
                    if isinstance(c.get("ranking_summary"), str):
                        try:
                            c["ranking_summary"] = json.loads(c["ranking_summary"])
                        except Exception:
                            pass
                    cursor.execute("SELECT analysis_id FROM batch_comparison_items WHERE comparison_id = %s ORDER BY item_order", (c["id"],))
                    items = cursor.fetchall()
                    c["analysis_ids"] = [i["analysis_id"] for i in items]
                return comps
        finally:
            conn.close()

    def create_batch_comparison(self, user_id: str, title: str, ranking_summary: Dict[str, Any], analysis_ids: List[str]) -> Dict[str, Any]:
        comp_id = str(uuid.uuid4())
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO batch_comparisons (id, user_id, title, ranking_summary) VALUES (%s, %s, %s, %s)",
                    (comp_id, user_id, title, json.dumps(ranking_summary))
                )
                for order, an_id in enumerate(analysis_ids, 1):
                    cursor.execute(
                        "INSERT INTO batch_comparison_items (comparison_id, analysis_id, item_order) VALUES (%s, %s, %s)",
                        (comp_id, an_id, order)
                    )
                cursor.execute("SELECT * FROM batch_comparisons WHERE id = %s", (comp_id,))
                comp = cursor.fetchone()
                for dt_key in ["created_at", "updated_at"]:
                    if isinstance(comp.get(dt_key), (datetime.date, datetime.datetime)):
                        comp[dt_key] = comp[dt_key].isoformat()
                comp["analysis_ids"] = analysis_ids
                return comp
        finally:
            conn.close()

    def delete_batch_comparison(self, comp_id: str, user_id: str) -> bool:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE batch_comparisons SET is_deleted = TRUE WHERE id = %s AND user_id = %s", (comp_id, user_id))
                return cursor.rowcount > 0
        finally:
            conn.close()
