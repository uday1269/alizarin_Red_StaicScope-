import subprocess
import time
import pymysql

# Start XAMPP mysqld on port 3307
cmd = [r"C:\xampp\mysql\bin\mysqld.exe", "--port=3307", r"--datadir=C:\xampp\mysql\data", "--standalone"]
proc = subprocess.Popen(cmd)
print("Started XAMPP mysqld on port 3307, PID:", proc.pid)

time.sleep(2)

# Test connection to port 3307
try:
    conn = pymysql.connect(host="127.0.0.1", port=3307, user="root", password="", database="stainscope")
    print("SUCCESS: Connected to XAMPP MySQL on port 3307!")
    with conn.cursor() as c:
        c.execute("SHOW TABLES;")
        print("Tables in stainscope:", [t[0] for t in c.fetchall()])
    conn.close()
except Exception as e:
    print("Connection error on 3307:", e)
