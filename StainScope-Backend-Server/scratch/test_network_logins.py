import requests

# Test Localhost (Web access)
url_local = "http://127.0.0.1:8000"
resp_web = requests.post(f"{url_local}/auth/login", json={"email": "researcher@stainscope.org", "password": "Password123!"})
print("Web Localhost Login Test (http://127.0.0.1:8000):", resp_web.status_code)
assert resp_web.status_code == 200, "Web Localhost Login failed"

# Test LAN IP (Android access)
url_lan = "http://10.131.43.110:8000"
resp_android = requests.post(f"{url_lan}/auth/login", json={"email": "researcher@stainscope.org", "password": "Password123!"})
print("Android LAN Login Test (http://10.131.43.110:8000):", resp_android.status_code)
assert resp_android.status_code == 200, "Android LAN Login failed"

# Test Health on both
h_web = requests.get(f"{url_local}/health").json()
h_android = requests.get(f"{url_lan}/health").json()
print("Web /health db_connected:", h_web.get("db_connected"))
print("Android /health db_connected:", h_android.get("db_connected"))
assert h_web.get("db_connected") == True
assert h_android.get("db_connected") == True

print("\nALL WEB AND ANDROID AUTHENTICATION AND DATABASE CHECKS PASSED 100%!")
