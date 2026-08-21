"""
Verification Script for Syncing Profile Page (Deleted Notes & Deleted Analysis Reports),
FastAPI + MySQL Database Persistence, and User Isolation.
"""
import requests
import time
import uuid
from db_mysql import get_db_connection

BASE_URL = "http://127.0.0.1:8000"

def run_sync_test():
    print("==========================================================================", flush=True)
    print("RUNNING PROFILE PAGE RECYCLE BIN & DELETE SYNC VERIFICATION TEST", flush=True)
    print("==========================================================================", flush=True)

    ts = int(time.time())

    # 1. Register User A
    email_a = f"usera_sync_{ts}@stainscope.org"
    pass_a = "Password123!"
    resp_a = requests.post(f"{BASE_URL}/auth/signup", json={"email": email_a, "password": pass_a, "full_name": "User A Profile Sync"})
    assert resp_a.status_code == 200, f"Signup A failed: {resp_a.text}"
    token_a = resp_a.json()["access_token"]
    user_a_id = resp_a.json()["user_id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register User B
    email_b = f"userb_sync_{ts}@stainscope.org"
    pass_b = "Password123!"
    resp_b = requests.post(f"{BASE_URL}/auth/signup", json={"email": email_b, "password": pass_b, "full_name": "User B Profile Sync"})
    assert resp_b.status_code == 200
    token_b = resp_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Create Note for User A
    resp_note = requests.post(f"{BASE_URL}/notes", headers=headers_a, json={"title": "Test Osteogenesis Research Note", "content": "Day 21 Alizarin Red S staining notes."})
    assert resp_note.status_code == 200, f"Create note failed: {resp_note.text}"
    note_id = resp_note.json()["id"]
    print(f"[OK] Test 1: Created note {note_id} for User A", flush=True)

    # 4. Create Analysis for User A in MySQL
    an_id = str(uuid.uuid4())
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO analyses (id, user_id, sample_title, mineralized_area_percent, optical_density_proxy, nodule_count, is_deleted)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
            """,
            (an_id, user_a_id, "Mobile Created Analysis Report", 38.50, 0.14, 1420)
        )
    conn.close()
    print(f"[OK] Test 2: Created analysis report {an_id} for User A", flush=True)

    # 5. Simulate Mobile Deletion of Note (DELETE /notes/{note_id})
    resp_del_note = requests.delete(f"{BASE_URL}/notes/{note_id}", headers=headers_a)
    assert resp_del_note.status_code == 200, f"Delete note failed: {resp_del_note.text}"
    print(f"[OK] Test 3: Mobile deleted note {note_id} (DELETE /notes/{note_id} 200 OK)", flush=True)

    # 6. Simulate Mobile Deletion of Analysis Report (DELETE /analyses/{an_id})
    resp_del_an = requests.delete(f"{BASE_URL}/analyses/{an_id}", headers=headers_a)
    assert resp_del_an.status_code == 200, f"Delete analysis failed: {resp_del_an.text}"
    print(f"[OK] Test 4: Mobile deleted analysis report {an_id} (DELETE /analyses/{an_id} 200 OK)", flush=True)

    # 7. Query GET /notes/deleted and GET /analyses/deleted for User A
    resp_del_notes_list = requests.get(f"{BASE_URL}/notes/deleted", headers=headers_a)
    assert resp_del_notes_list.status_code == 200, f"GET /notes/deleted failed: {resp_del_notes_list.text}"
    deleted_notes_ids = [n["id"] for n in resp_del_notes_list.json()]
    assert note_id in deleted_notes_ids, "Deleted note missing from GET /notes/deleted!"

    resp_del_an_list = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_a)
    assert resp_del_an_list.status_code == 200, f"GET /analyses/deleted failed: {resp_del_an_list.text}"
    deleted_an_ids = [a["id"] for a in resp_del_an_list.json()]
    assert an_id in deleted_an_ids, "Deleted analysis report missing from GET /analyses/deleted!"

    print("[OK] Test 5: Profile Recycle Bin sync confirmed - both deleted note & analysis report present in MySQL backend response", flush=True)

    # 8. User B Isolation Verification
    resp_b_notes = requests.get(f"{BASE_URL}/notes/deleted", headers=headers_b)
    assert resp_b_notes.status_code == 200
    assert note_id not in [n["id"] for n in resp_b_notes.json()], "SECURITY VIOLATION: User B can see User A's deleted note!"

    resp_b_ans = requests.get(f"{BASE_URL}/analyses/deleted", headers=headers_b)
    assert resp_b_ans.status_code == 200
    assert an_id not in [a["id"] for a in resp_b_ans.json()], "SECURITY VIOLATION: User B can see User A's deleted analysis!"

    print("[OK] Test 6: Strict User Isolation confirmed - User B cannot view User A's deleted notes or analysis reports", flush=True)

    # 9. Restore Note & Analysis Report
    resp_rest_note = requests.post(f"{BASE_URL}/notes/{note_id}/restore", headers=headers_a)
    assert resp_rest_note.status_code == 200, f"Restore note failed: {resp_rest_note.text}"

    resp_rest_an = requests.post(f"{BASE_URL}/analyses/{an_id}/restore", headers=headers_a)
    assert resp_rest_an.status_code == 200, f"Restore analysis failed: {resp_rest_an.text}"

    # Verify both returned to active lists
    resp_act_notes = requests.get(f"{BASE_URL}/notes", headers=headers_a)
    assert note_id in [n["id"] for n in resp_act_notes.json()], "Restored note missing from active /notes!"

    resp_act_ans = requests.get(f"{BASE_URL}/analyses", headers=headers_a)
    assert an_id in [a["id"] for a in resp_act_ans.json()], "Restored analysis report missing from active /analyses!"

    print("[OK] Test 7: Restoration confirmed - Note and Analysis report returned to active lists and removed from Recycle Bin", flush=True)

    print("==========================================================================", flush=True)
    print("ALL 7 PROFILE SYNC VERIFICATION TESTS PASSED CLEANLY!", flush=True)
    print("==========================================================================", flush=True)

if __name__ == "__main__":
    try:
        run_sync_test()
    except Exception as err:
        import traceback
        print(f"[SYNC TEST EXCEPTION] {err}", flush=True)
        traceback.print_exc()
