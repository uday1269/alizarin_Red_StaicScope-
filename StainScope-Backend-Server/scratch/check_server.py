import urllib.request
import json

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/docs") as resp:
        print("FastAPI /docs status:", resp.status)
except Exception as e:
    print("FastAPI not responding on 8000:", e)
