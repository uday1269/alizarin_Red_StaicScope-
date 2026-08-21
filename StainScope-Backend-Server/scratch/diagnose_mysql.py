import subprocess
import socket
import os

print("=== 1. Checking open ports 3306, 3307, 3308 ===")
for port in [3306, 3307, 3308]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    res = s.connect_ex(('127.0.0.1', port))
    s.close()
    if res == 0:
        print(f"Port {port} is OPEN / LISTENING")
    else:
        print(f"Port {port} is CLOSED ({res})")

print("\n=== 2. Tasklist for mysql ===")
try:
    out = subprocess.check_output('tasklist /V /FO LIST /FI "IMAGENAME eq mysqld*"', shell=True).decode(errors="ignore")
    print(out)
except Exception as e:
    print("Error querying tasklist:", e)

print("\n=== 3. Netstat for 3306 and 3307 ===")
try:
    out = subprocess.check_output('netstat -ano | findstr ":330"', shell=True).decode(errors="ignore")
    print(out)
except Exception as e:
    print("Netstat findstr:", e)

print("\n=== 4. Checking XAMPP my.ini ===")
my_ini_path = r"C:\xampp\mysql\bin\my.ini"
if os.path.exists(my_ini_path):
    print(f"Found {my_ini_path}:")
    with open(my_ini_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "port" in line.lower() and not line.strip().startswith("#"):
                print("  ", line.strip())
else:
    print("XAMPP my.ini not found at", my_ini_path)
