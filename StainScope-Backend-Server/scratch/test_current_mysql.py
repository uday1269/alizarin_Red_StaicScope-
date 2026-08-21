import pymysql

print("Testing connection to 127.0.0.1:3306 with XAMPP root/empty password:")
try:
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
    print("SUCCESS: Connected to MySQL on port 3306 with root/empty password!")
    with conn.cursor() as c:
        c.execute("SHOW DATABASES;")
        dbs = [row[0] for row in c.fetchall()]
        print("Databases on port 3306:", dbs)
        if "stainscope" in dbs:
            print("stainscope DATABASE EXISTS ON PORT 3306!")
            c.execute("USE stainscope;")
            c.execute("SHOW TABLES;")
            print("Tables in stainscope:", [row[0] for row in c.fetchall()])
            c.execute("SELECT id, email, full_name FROM users;")
            print("Users in stainscope:", c.fetchall())
    conn.close()
except Exception as e:
    print("Failed on port 3306 root/empty:", e)

print("\nTesting connection to 127.0.0.1:3307 with XAMPP root/empty password:")
try:
    conn = pymysql.connect(host="127.0.0.1", port=3307, user="root", password="")
    print("SUCCESS: Connected to MySQL on port 3307!")
    conn.close()
except Exception as e:
    print("Failed on port 3307:", e)
