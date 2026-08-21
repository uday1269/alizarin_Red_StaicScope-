import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("--- 1. Testing FastAPI /health endpoint ---")
try:
    resp = requests.get(f"{BASE_URL}/health")
    print("Status:", resp.status_code)
    print("Health response:", resp.json())
    assert resp.status_code == 200
    assert resp.json().get("db_connected") == True
    print("SUCCESS: /health returns db_connected: true")
except Exception as e:
    print("Health check failed:", e)

print("\n--- 2. Testing Web / Android Login with Existing Accounts ---")

# Try known existing accounts in DB
test_accounts = [
    ("udaykiran.creator@gmail.com", "Password123!"),
    ("udaykiranbs9010@gmail.com", "Password123!"),
    ("researcher@stainscope.org", "Password123!"),
    ("test@example.com", "Password123!")
]

for email, password in test_accounts:
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    print(f"Login attempt for '{email}': Status {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  -> SUCCESS! Token: {data.get('access_token')[:20]}..., User ID: {data.get('user_id')}")
    else:
        print(f"  -> Detail: {resp.text}")

print("\n--- 3. Testing User Registration & Immediate Login ---")
new_email = "verified_researcher@stainscope.org"
new_pwd = "SecureResearch2026!"
resp_signup = requests.post(f"{BASE_URL}/auth/signup", json={"email": new_email, "password": new_pwd, "full_name": "Dr. Verification"})
print(f"Signup for '{new_email}': Status {resp_signup.status_code}")
if resp_signup.status_code in [200, 400]:
    resp_login = requests.post(f"{BASE_URL}/auth/login", json={"email": new_email, "password": new_pwd})
    print(f"Login for '{new_email}': Status {resp_login.status_code}")
    assert resp_login.status_code == 200
    print("  -> SUCCESS: Registered user logged in cleanly!")

print("\n--- 4. Testing Analyses & Profile with Token ---")
auth_token = resp_login.json()["access_token"]
headers = {"Authorization": f"Bearer {auth_token}"}
prof_resp = requests.get(f"{BASE_URL}/profile", headers=headers)
print("Profile status:", prof_resp.status_code, "->", prof_resp.json().get("email"))
an_resp = requests.get(f"{BASE_URL}/analyses", headers=headers)
print("Analyses list status:", an_resp.status_code, "-> items:", len(an_resp.json()))
