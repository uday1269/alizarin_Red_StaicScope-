"""
Fast Recycle Bin Persistence, User Isolation, & Restoration Test.
"""
import requests
import time
import sys
from db_mysql import get_db_connection
import uuid

BASE_URL = "http://127.0.0.1:8000"

def run_fast_test():
    print("==========================================================================", flush=True)
    print("FAST RECYCLE BIN PERSISTENCE, USER ISOLATION & RESTORE TEST SUITE", flush=True)
    print("==========================================================================", flush=True)

    ts = int(time.time())

    # 1. Sign up User A
    email_a = f"usera_fast_recycle_{ts}@stainscope.org"
    pass_a = "Password123!"
    resp_reg_a = requests.post(f"{BASE_URL}/auth/signup", json={"email": email_a, "password": pass_a, "full_name": "User A Fast Recycle"})
    assert resp_reg_a.status_code == 200, f"Signup A failed: {resp_reg_a.text}"
    token_a = resp_reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Sign up User B
    email_b = f"userb_fast_recycle_{ts}@stainscope.org"
    pass_b = "Password123!"
    resp_reg_b = requests.post(f"{BASE_URL}/auth/signup", json={"email": email_b, "password": pass_b, "full_name": "User B Fast Recycle"})
    assert resp_reg_b.status_code == 200, f"Signup B failed: {resp_reg_b.text}"
    token_b = resp_reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Create mock analysis entry for User A directly in MySQL
    an_id = str(uuid.uuid4())
    user_a_id = resp_reg_a.json()["user_id"]

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO analyses (id, user_id, sample_title, mineralized_area_percent, optical_density_proxy, nodule_count, is_deleted)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
            """,
            (an_id, user_a_id, "Fast Recycle Micrograph Test", 45.76, 0.17, 1822)
        )
    conn.close()

    print(f"[OK] Test 1: Created analysis record {an_id} for User A in MySQL", flush=True)

    # 4. User A deletes analysis
    resp_del = requests.delete(f"{BASE_URL}/analyses/{an_id}", headers=headers_a)
    assert resp_del.status_code == 200, f"Delete failed: {resp_del.text}"
    print(f"[OK] Test 2: DELETE /analyses/{an_id} returned 200 OK", flush=True)

    # 5. Query GET /analyses/deleted as User A
    resp_list_a = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_a)
    assert resp_list_a.status_code == 200, f"Get deleted failed: {resp_list_a.text}"
    del_ids_a = [r["id"] for r in resp_list_a.json()]
    assert an_id in del_ids_a, "Deleted analysis missing from User A recycle bin!"
    print(f"[OK] Test 3: GET /analyses/deleted returns deleted analysis for User A from MySQL", flush=True)

    # 6. Query GET /analyses/deleted as User B (Isolation test)
    resp_list_b = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_b)
    assert resp_list_b.status_code == 200, f"Get deleted B failed: {resp_list_b.text}"
    del_ids_b = [r["id"] for r in resp_list_b.json()]
    assert an_id not in del_ids_b, "SECURITY VIOLATION: User B can see User A's deleted analysis!"
    print(f"[OK] Test 4: User B cannot see User A's deleted analysis (Strict User Isolation)", flush=True)

    # 7. Re-login User A and check persistence across login & F5 simulation
    resp_login_a = requests.post(f"{BASE_URL}/auth/login", json={"email": email_a, "password": pass_a})
    assert resp_login_a.status_code == 200, f"Login failed: {resp_login_a.text}"
    token_relog = resp_login_a.json()["access_token"]
    headers_relog = {"Authorization": f"Bearer {token_relog}"}

    resp_list_relog = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_relog)
    assert resp_list_relog.status_code == 200
    assert an_id in [r["id"] for r in resp_list_relog.json()], "Recycle bin item lost after re-login!"
    print(f"[OK] Test 5: Re-login & Page Refresh Persistence Verified (Item remains in Recycle Bin)", flush=True)

    # 8. Restore analysis
    resp_rest = requests.post(f"{BASE_URL}/analyses/{an_id}/restore", headers=headers_relog)
    assert resp_rest.status_code == 200, f"Restore failed: {resp_rest.text}"
    print(f"[OK] Test 6: POST /analyses/{an_id}/restore returned 200 OK", flush=True)

    # 9. Verify restored analysis is active and removed from recycle bin
    resp_act_after = requests.get(f"{BASE_URL}/analyses", headers=headers_relog)
    assert resp_act_after.status_code == 200
    assert an_id in [r["id"] for r in resp_act_after.json()], "Restored analysis missing from active history!"

    resp_del_after = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_relog)
    assert resp_del_after.status_code == 200
    assert an_id not in [r["id"] for r in resp_del_after.json()], "Restored analysis still present in recycle bin!"
    print(f"[OK] Test 7: Analysis restored to active history and removed from Recycle Bin", flush=True)

    print("==========================================================================", flush=True)
    print("ALL 7 RECYCLE BIN TESTS PASSED SUCCESSFULLY!", flush=True)
    print("==========================================================================", flush=True)

if __name__ == "__main__":
    try:
        run_fast_test()
    except Exception as err:
        import traceback
        print(f"[TEST EXCEPTION] {err}", flush=True)
        traceback.print_exc()

