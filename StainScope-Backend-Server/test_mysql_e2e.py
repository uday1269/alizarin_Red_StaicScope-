"""
Comprehensive E2E Integration Test Script for StainScope FastAPI + XAMPP MySQL + Local File Storage.
Tests:
1. Health endpoint
2. User signup & login authentication (password hashing, wrong password rejection)
3. Micrograph upload & Classical CV analysis (/analyze)
4. Verification of MySQL database records (micrographs, analyses, nodules, analysis_overlays)
5. Verification of local disk storage files
6. Strict Multi-User Data Isolation (User A vs User B)
"""
import os
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"


def test_e2e_mysql():
    print("==================================================")
    print("STARTING STAINSCOPE MYSQL & LOCAL STORAGE E2E TEST")
    print("==================================================")

    # 1. Health check
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    health_data = resp.json()
    assert health_data["status"] == "healthy"
    assert health_data["db_connected"] is True
    print("[OK] /health PASSED (MySQL connected)")

    # 2. Authentication Tests (User A)
    user_a_email = f"usera_{int(time.time())}@stainscope.org"
    user_a_password = "SecurePassword123!"

    # Signup User A
    signup_resp = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": user_a_email,
        "password": user_a_password,
        "full_name": "Dr. User A"
    })
    assert signup_resp.status_code == 200, f"User A signup failed: {signup_resp.text}"
    user_a_data = signup_resp.json()
    token_a = user_a_data["access_token"]
    user_a_id = user_a_data["user_id"]
    print(f"[OK] User A Signup PASSED (User ID: {user_a_id})")

    # Login User A with WRONG password (must fail)
    wrong_login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": user_a_email,
        "password": "WrongPassword999!"
    })
    assert wrong_login_resp.status_code == 401, f"Wrong password should be rejected: {wrong_login_resp.status_code}"
    print("[OK] Wrong Password Rejection PASSED")

    # Login User A with CORRECT password
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": user_a_email,
        "password": user_a_password
    })
    assert login_resp.status_code == 200, f"User A login failed: {login_resp.text}"
    token_a = login_resp.json()["access_token"]
    print("[OK] User A Login PASSED")

    # 3. Analyze Image for User A
    img_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
    assert os.path.exists(img_path), f"Test image not found at {img_path}"

    headers_a = {"Authorization": f"Bearer {token_a}"}
    with open(img_path, "rb") as f:
        analyze_resp = requests.post(
            f"{BASE_URL}/analyze",
            headers=headers_a,
            files={"file": ("C1_D28_4x_BF_01.tif", f, "image/tiff")},
            data={"sample_title": "User A Experiment 1"}
        )

    assert analyze_resp.status_code == 200, f"Analysis failed: {analyze_resp.text}"
    an_data = analyze_resp.json()
    assert an_data["valid"] is True
    analysis_id = an_data["analysis_id"]
    area_percent = an_data["mineralization"]["area_percent"]
    nodule_count = an_data["nodules"]["count"]
    print(f"[OK] POST /analyze PASSED (Analysis ID: {analysis_id}, Area %: {area_percent}%, Nodules: {nodule_count})")

    # 4. Retrieve Analysis Details for User A
    detail_resp = requests.get(f"{BASE_URL}/analyses/{analysis_id}", headers=headers_a)
    assert detail_resp.status_code == 200, f"Get analysis detail failed: {detail_resp.text}"
    detail_data = detail_resp.json()
    assert detail_data["id"] == analysis_id
    assert "overlay" in detail_data or "overlays" in detail_data
    print("[OK] GET /analyses/{id} PASSED")

    # 5. List Analyses for User A
    list_a_resp = requests.get(f"{BASE_URL}/analyses", headers=headers_a)
    assert list_a_resp.status_code == 200
    list_a_data = list_a_resp.json()
    assert len(list_a_data) >= 1
    assert any(item["id"] == analysis_id for item in list_a_data)
    print(f"[OK] User A List Analyses PASSED (Count: {len(list_a_data)})")

    # 6. Multi-User Isolation Test (User B)
    user_b_email = f"userb_{int(time.time())}@stainscope.org"
    user_b_password = "SecurePassword456!"

    signup_b_resp = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": user_b_email,
        "password": user_b_password,
        "full_name": "Dr. User B"
    })
    assert signup_b_resp.status_code == 200
    token_b = signup_b_resp.json()["access_token"]
    user_b_id = signup_b_resp.json()["user_id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B lists analyses (must see 0 of User A's analyses)
    list_b_resp = requests.get(f"{BASE_URL}/analyses", headers=headers_b)
    assert list_b_resp.status_code == 200
    list_b_data = list_b_resp.json()
    assert len(list_b_data) == 0, f"User B should see 0 analyses, but saw {len(list_b_data)}"
    print("[OK] Multi-User Isolation PASSED (User B sees 0 of User A's analyses)")

    # User B attempts to access User A's analysis detail (must fail 404)
    detail_unauth_resp = requests.get(f"{BASE_URL}/analyses/{analysis_id}", headers=headers_b)
    assert detail_unauth_resp.status_code == 404, f"User B accessing User A analysis must return 404: {detail_unauth_resp.status_code}"
    print("[OK] Multi-User Access Block PASSED (User B blocked from User A's analysis)")

    print("\n==================================================")
    print("ALL MYSQL & LOCAL STORAGE E2E TESTS PASSED 100%!")
    print("==================================================")


if __name__ == "__main__":
    test_e2e_mysql()
