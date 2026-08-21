"""
Comprehensive E2E Verification Script for Recycle Bin / Recently Deleted Persistence,
User Isolation, F5 Refresh Session Simulation, & Restoration in StainScope FastAPI + MySQL Backend.
"""
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==========================================================================", flush=True)
    print("STARTING RECYCLE BIN PERSISTENCE, USER ISOLATION & RESTORE TEST SUITE", flush=True)
    print("==========================================================================", flush=True)

    ts = int(time.time())
    img_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"

    # ------------------------------------------------------------------
    # TEST 1: User A Registration & Analysis Creation
    # ------------------------------------------------------------------
    email_a = f"usera_recycle_{ts}@stainscope.org"
    pass_a = "Password123!"
    resp_reg_a = requests.post(f"{BASE_URL}/auth/signup", json={"email": email_a, "password": pass_a, "full_name": "Dr. User A Recycle"})
    assert resp_reg_a.status_code == 200, f"User A signup failed: {resp_reg_a.text}"
    token_a = resp_reg_a.json()["access_token"]
    user_a_id = resp_reg_a.json()["user_id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"[OK] Test 1: User A created: {email_a} (ID: {user_a_id})", flush=True)

    # User A creates Analysis A
    with open(img_path, "rb") as f:
        resp_an_a = requests.post(
            f"{BASE_URL}/analyze",
            headers=headers_a,
            files={"file": ("c1_sample_a.tif", f, "image/tiff")},
            data={"sample_title": "User A Sample Micrograph"}
        )
    assert resp_an_a.status_code == 200, f"Analysis A creation failed: {resp_an_a.text}"
    an_a_id = resp_an_a.json()["analysis_id"]
    print(f"[OK] Test 2: User A created Analysis A (ID: {an_a_id})", flush=True)

    # Verify Analysis A is initially active in GET /analyses
    resp_act_1 = requests.get(f"{BASE_URL}/analyses", headers=headers_a)
    assert resp_act_1.status_code == 200
    active_ids_1 = [rec["id"] for rec in resp_act_1.json()]
    assert an_a_id in active_ids_1, "Analysis A missing from active list"
    print("[OK] Test 3: Analysis A is present in active /analyses list", flush=True)

    # ------------------------------------------------------------------
    # TEST 2: User A Deletes Analysis A (DELETE /analyses/{an_a_id})
    # ------------------------------------------------------------------
    resp_del_a = requests.delete(f"{BASE_URL}/analyses/{an_a_id}", headers=headers_a)
    assert resp_del_a.status_code == 200, f"Delete Analysis A failed: {resp_del_a.text}"
    print(f"[OK] Test 4: DELETE /analyses/{an_a_id} executed successfully", flush=True)

    # Verify Analysis A is removed from active GET /analyses
    resp_act_2 = requests.get(f"{BASE_URL}/analyses", headers=headers_a)
    assert resp_act_2.status_code == 200
    active_ids_2 = [rec["id"] for rec in resp_act_2.json()]
    assert an_a_id not in active_ids_2, "Analysis A still in active list after soft-delete!"
    print("[OK] Test 5: Analysis A removed from active /analyses list", flush=True)

    # Verify Analysis A is present in GET /analyses/deleted
    resp_del_list_a = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_a)
    assert resp_del_list_a.status_code == 200, f"GET /analyses/deleted failed: {resp_del_list_a.text}"
    deleted_recs_a = resp_del_list_a.json()
    deleted_ids_a = [rec["id"] for rec in deleted_recs_a]
    assert an_a_id in deleted_ids_a, "Analysis A missing from GET /analyses/deleted list!"
    print(f"[OK] Test 6: GET /analyses/deleted returns Analysis A for User A (Recycle Bin Persisted in MySQL)", flush=True)

    # ------------------------------------------------------------------
    # TEST 3: User B Isolation Check
    # ------------------------------------------------------------------
    email_b = f"userb_recycle_{ts}@stainscope.org"
    pass_b = "Password123!"
    resp_reg_b = requests.post(f"{BASE_URL}/auth/signup", json={"email": email_b, "password": pass_b, "full_name": "Dr. User B Recycle"})
    assert resp_reg_b.status_code == 200
    token_b = resp_reg_b.json()["access_token"]
    user_b_id = resp_reg_b.json()["user_id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B queries GET /analyses/deleted
    resp_del_list_b = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_b)
    assert resp_del_list_b.status_code == 200
    deleted_ids_b = [rec["id"] for rec in resp_del_list_b.json()]
    assert an_a_id not in deleted_ids_b, "SECURITY VIOLATION: User B can see User A's deleted analysis!"
    print("[OK] Test 7: Strict User Isolation Verified - User B cannot see User A's deleted analysis in Recycle Bin", flush=True)

    # ------------------------------------------------------------------
    # TEST 4: Refresh / Re-login Simulation for User A
    # ------------------------------------------------------------------
    # User A re-logs in
    resp_login_a = requests.post(f"{BASE_URL}/auth/login", json={"email": email_a, "password": pass_a})
    assert resp_login_a.status_code == 200
    token_a_new = resp_login_a.json()["access_token"]
    headers_a_new = {"Authorization": f"Bearer {token_a_new}"}

    resp_del_relog = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_a_new)
    assert resp_del_relog.status_code == 200
    deleted_ids_relog = [rec["id"] for rec in resp_del_relog.json()]
    assert an_a_id in deleted_ids_relog, "Analysis A disappeared after re-login!"
    print("[OK] Test 8: Logout -> Login Persistence Verified - Analysis A remains in Recycle Bin from MySQL", flush=True)

    # ------------------------------------------------------------------
    # TEST 5: Restore Analysis A (POST /analyses/{an_a_id}/restore)
    # ------------------------------------------------------------------
    resp_rest = requests.post(f"{BASE_URL}/analyses/{an_a_id}/restore", headers=headers_a_new)
    assert resp_rest.status_code == 200, f"Restore failed: {resp_rest.text}"
    print(f"[OK] Test 9: POST /analyses/{an_a_id}/restore executed successfully", flush=True)

    # Verify Analysis A is back in active list and removed from deleted list
    resp_act_rest = requests.get(f"{BASE_URL}/analyses", headers=headers_a_new)
    assert resp_act_rest.status_code == 200
    active_ids_rest = [rec["id"] for rec in resp_act_rest.json()]
    assert an_a_id in active_ids_rest, "Restored Analysis A missing from active list!"

    resp_del_rest = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_a_new)
    assert resp_del_rest.status_code == 200
    deleted_ids_rest = [rec["id"] for rec in resp_del_rest.json()]
    assert an_a_id not in deleted_ids_rest, "Restored Analysis A still in deleted list!"
    print("[OK] Test 10: Restoration Complete - Analysis A returned to active History/Reports and removed from Recycle Bin", flush=True)

    print("==========================================================================", flush=True)
    print("SUCCESS: ALL 10 RECYCLE BIN E2E VERIFICATION TESTS PASSED CLEANLY", flush=True)
    print("==========================================================================", flush=True)

if __name__ == "__main__":
    run_tests()
