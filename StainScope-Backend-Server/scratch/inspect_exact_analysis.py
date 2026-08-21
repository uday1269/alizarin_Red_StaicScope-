import requests
import json

BASE_URL = "http://127.0.0.1:8000"
an_id = "a7c117d5-6a18-4afb-8361-0d37427a757e"
user_id = "ddd21a1a-c3e9-4aa0-9027-fa4927b06b2e"

# 1. Login as udaykiranbs9010@gmail.com
# Let's generate a token or login
import jwt
JWT_SECRET = "stainscope_jwt_secret_key_2026_x7f89a"
token = jwt.encode({"sub": user_id, "email": "udaykiranbs9010@gmail.com"}, JWT_SECRET, algorithm="HS256")
if isinstance(token, bytes):
    token = token.decode()

headers = {"Authorization": f"Bearer {token}"}

print(f"Calling GET /analyses/{an_id} with user token...")
resp = requests.get(f"{BASE_URL}/analyses/{an_id}", headers=headers)
print("Status code:", resp.status_code)

if resp.status_code == 200:
    data = resp.json()
    print("KEYS in response:")
    print(list(data.keys()))
    print("\nFULL JSON (truncated nodules list):")
    data_copy = dict(data)
    if "nodules_list" in data_copy:
        data_copy["nodules_list"] = f"[{len(data_copy['nodules_list'])} nodule objects]"
    if "nodules" in data_copy and isinstance(data_copy["nodules"], dict) and "objects" in data_copy["nodules"]:
        data_copy["nodules"] = dict(data_copy["nodules"])
        data_copy["nodules"]["objects"] = f"[{len(data_copy['nodules']['objects'])} objects]"
    print(json.dumps(data_copy, indent=2))
else:
    print("ERROR:", resp.text)
