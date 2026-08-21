import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"

# 1. Login or Signup test user
email = "researcher@stainscope.org"
password = "Password123!"

resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
if resp.status_code != 200:
    resp = requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password, "full_name": "Dr. Lead Researcher"})

print("Auth status:", resp.status_code)
auth_data = resp.json()
token = auth_data["access_token"]
user_id = auth_data["user_id"]
print("User ID:", user_id)

headers = {"Authorization": f"Bearer {token}"}

# 2. Upload an image for analysis
img_path = r"c:\final_ppd\StainScope-Ai-Model\ars\c1\C1_D28_4x_BF_01.tif"
with open(img_path, "rb") as f:
    files = {"file": ("C1_D28_4x_BF_01.tif", f, "image/tiff")}
    data = {
        "sample_title": "Android Run Test Sample",
        "cell_line": "hMSC",
        "treatment": "14 Days | 20x"
    }
    an_resp = requests.post(f"{BASE_URL}/analyze", headers=headers, files=files, data=data)

print("Analyze status:", an_resp.status_code)
an_data = an_resp.json()
an_id = an_data["analysis_id"]
print("Analysis ID created:", an_id)

# 3. Call GET /analyses
list_resp = requests.get(f"{BASE_URL}/analyses", headers=headers)
print("GET /analyses status:", list_resp.status_code)
list_data = list_resp.json()
print("Total records returned by GET /analyses:", len(list_data))

# Find our newly created analysis
match = next((item for item in list_data if item["id"] == an_id), None)
print("\n--- NEW RECORD IN GET /analyses ---")
print(json.dumps(match, indent=2))

# 4. Call GET /analyses/{an_id}
detail_resp = requests.get(f"{BASE_URL}/analyses/{an_id}", headers=headers)
print("\nGET /analyses/{an_id} status:", detail_resp.status_code)
detail_data = detail_resp.json()
print("Detail id:", detail_data.get("id"))
