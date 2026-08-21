import subprocess
import pymysql

res = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
for line in res.stdout.splitlines():
    if "5952" in line or "7064" in line or ":3306" in line or ":3307" in line or ":3308" in line:
        print("Port line:", line)

# Let's test connecting to 3306, 3307, 3308 with root and blank password
for port in [3306, 3307, 3308]:
    try:
        conn = pymysql.connect(host="127.0.0.1", port=port, user="root", password="")
        print(f"SUCCESS on port {port} with password ''!")
        with conn.cursor() as c:
            c.execute("SHOW DATABASES;")
            print("Databases:", c.fetchall())
        conn.close()
    except Exception as e:
        print(f"Port {port} error with '': {e}")
