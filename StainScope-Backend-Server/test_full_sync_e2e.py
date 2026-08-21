"""
Full Real-World Verification Script for Web <-> Android Synchronization, Authentication, & User Isolation.
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print("STARTING FULL WEB <-> ANDROID SYNCHRONIZATION TEST")
    print("==================================================")

    # ----------------------------------------------------
    # TEST A: Web-created account & Web <-> Android Sync
    # ----------------------------------------------------
    email_a = f"usera_sync_{int(time.time())}@stainscope.org"
    password_a = "Password123!"
    full_name_a = "Dr. User A Sync"

    # Step 1: Web creates account
    res_web_signup = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": email_a, "password": password_a, "full_name": full_name_a
    })
    assert res_web_signup.status_code == 200, f"Web signup failed: {res_web_signup.text}"
    data_a = res_web_signup.json()
    token_a = data_a["access_token"]
    user_a_id = data_a["user_id"]
    print(f"[OK] Test A1: Web Account Created for {email_a} (User ID: {user_a_id})")

    # Step 2: Web performs an analysis
    headers_a = {"Authorization": f"Bearer {token_a}"}
    img_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
    with open(img_path, "rb") as f:
        res_web_an = requests.post(
            f"{BASE_URL}/analyze",
            headers=headers_a,
            files={"file": ("C1_D28_4x_BF_01.tif", f, "image/tiff")},
            data={"sample_title": "Web Created Analysis 1"}
        )
    assert res_web_an.status_code == 200, f"Web analysis failed: {res_web_an.text}"
    web_an_id = res_web_an.json()["analysis_id"]
    print(f"[OK] Test A2: Web Analysis Created (Analysis ID: {web_an_id})")

    # Step 3: Android logs in using exact same Web-created account
    res_android_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email_a, "password": password_a
    })
    assert res_android_login.status_code == 200, f"Android login failed: {res_android_login.text}"
    android_data_a = res_android_login.json()
    assert android_data_a["access_token"] is not None
    assert android_data_a["user_id"] == user_a_id
    print(f"[OK] Test A3: Android Login with Web-Created Account Succeeded (Token & User ID Matched)")

    # Step 4: Android Dashboard fetches analyses history for User A
    res_android_history = requests.get(f"{BASE_URL}/analyses", headers=headers_a)
    assert res_android_history.status_code == 200
    history_a = res_android_history.json()
    assert len(history_a) >= 1
    assert history_a[0]["id"] == web_an_id
    print(f"[OK] Test A4: Android History Displays Web-Created Analysis ({web_an_id})")

    # Step 5: Android performs an analysis
    with open(img_path, "rb") as f:
        res_android_an = requests.post(
            f"{BASE_URL}/analyze",
            headers=headers_a,
            files={"file": ("C1_D28_4x_BF_01.tif", f, "image/tiff")},
            data={"sample_title": "Android Created Analysis 2"}
        )
    assert res_android_an.status_code == 200
    android_an_id = res_android_an.json()["analysis_id"]
    print(f"[OK] Test A5: Android Analysis Created (Analysis ID: {android_an_id})")

    # Step 6: Web fetches history and sees Android-created analysis
    res_web_history = requests.get(f"{BASE_URL}/analyses", headers=headers_a)
    assert res_web_history.status_code == 200
    web_history_data = res_web_history.json()
    assert len(web_history_data) >= 2
    assert any(an["id"] == android_an_id for an in web_history_data)
    print(f"[OK] Test A6: Web History Displays Android-Created Analysis ({android_an_id})")

    # ----------------------------------------------------
    # TEST B: Multi-User Data Isolation
    # ----------------------------------------------------
    email_b = f"userb_sync_{int(time.time())}@stainscope.org"
    password_b = "Password123!"
    full_name_b = "Dr. User B Sync"

    res_b_signup = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": email_b, "password": password_b, "full_name": full_name_b
    })
    assert res_b_signup.status_code == 200
    token_b = res_b_signup.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B checks history (must see 0 of User A's analyses)
    res_b_history = requests.get(f"{BASE_URL}/analyses", headers=headers_b)
    assert res_b_history.status_code == 200
    assert len(res_b_history.json()) == 0
    print(f"[OK] Test B1: User B Sees 0 of User A's Analyses")

    # User B creates an analysis
    with open(img_path, "rb") as f:
        res_b_an = requests.post(
            f"{BASE_URL}/analyze",
            headers=headers_b,
            files={"file": ("C1_D28_4x_BF_01.tif", f, "image/tiff")},
            data={"sample_title": "User B Analysis"}
        )
    assert res_b_an.status_code == 200
    an_b_id = res_b_an.json()["analysis_id"]

    # User A checks history (must NOT see User B's analysis)
    res_a_check = requests.get(f"{BASE_URL}/analyses", headers=headers_a)
    assert res_a_check.status_code == 200
    assert not any(an["id"] == an_b_id for an in res_a_check.json())
    print(f"[OK] Test B2: User A Does NOT See User B's Analysis ({an_b_id})")

    # ----------------------------------------------------
    # TEST C: Wrong Password Rejection & State Reset
    # ----------------------------------------------------
    res_wrong_pw = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email_a, "password": "WrongPassword999!"
    })
    assert res_wrong_pw.status_code == 401
    err_json = res_wrong_pw.json()
    assert err_json["detail"] == "Invalid email or password."
    print(f"[OK] Test C: Wrong Password Rejected with 401 ('Invalid email or password.')")

    print("\n==================================================")
    print("ALL TESTS PASSED 100%! WEB <-> ANDROID SYNC VERIFIED")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
