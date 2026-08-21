import requests
import json

BASE_URL = "http://127.0.0.1:8000"
an_id = "a7c117d5-6a18-4afb-8361-0d37427a757e"
user_id = "ddd21a1a-c3e9-4aa0-9027-fa4927b06b2e"

import jwt
JWT_SECRET = "stainscope_jwt_secret_key_2026_x7f89a"
token = jwt.encode({"sub": user_id, "email": "udaykiranbs9010@gmail.com"}, JWT_SECRET, algorithm="HS256")
if isinstance(token, bytes):
    token = token.decode()

headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(f"{BASE_URL}/analyses/{an_id}", headers=headers)
data = resp.json()

print("Field types in API response:")
for k, v in data.items():
    if k not in ["nodules_list", "nodules"]:
        print(f"  {k} ({type(v).__name__}): {repr(v)[:80]}")
    else:
        print(f"  {k} ({type(v).__name__}): [complex structure]")
