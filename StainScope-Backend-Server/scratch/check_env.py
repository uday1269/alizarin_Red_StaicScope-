import subprocess
import os

print("Checking XAMPP / MySQL installation paths:")
for p in [r"C:\xampp\mysql\bin\mysql.exe", r"C:\Program Files\MySQL", r"C:\xampp"]:
    print(p, "exists:", os.path.exists(p))

try:
    res = subprocess.run(["tasklist"], capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if any(x in line.lower() for x in ["mysql", "mariadb", "httpd", "apache", "python", "node"]):
            print("Running process:", line)
except Exception as e:
    print("Error:", e)
