import pymysql
import os

# Check if there are any config files in C:\ProgramData\MySQL or C:\Program Files\MySQL or C:\xampp\mysql
print("Checking MySQL configs:")
for d in [r"C:\ProgramData\MySQL", r"C:\xampp\mysql\bin\my.ini", r"C:\xampp\mysql\my.ini"]:
    if os.path.exists(d):
        print("Found:", d)

# Common passwords list
common_passwords = [
    "root", "admin", "123456", "12345678", "1234", "mysql", "Password123!", "stainscope", 
    "root123", "Admin@123", "Root@123", "uday", "udayk", "uday123", "password", "Password@123",
    "stainscope123", "simats", "simats123", "SIMATS", "Simats@123"
]

for pwd in common_passwords:
    try:
        conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password=pwd)
        print(f"SUCCESS on port 3306 with password: '{pwd}'")
        with conn.cursor() as c:
            c.execute("SHOW DATABASES;")
            print("Databases:", c.fetchall())
        conn.close()
        break
    except Exception as e:
        pass
else:
    print("None of the common passwords worked.")
