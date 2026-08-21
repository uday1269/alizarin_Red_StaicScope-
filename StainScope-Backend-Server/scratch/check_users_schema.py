import pymysql

conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="", database="stainscope")
with conn.cursor() as c:
    c.execute("DESCRIBE users;")
    print("Users table schema:")
    for col in c.fetchall():
        print(" ", col)
    c.execute("SELECT * FROM users;")
    users = c.fetchall()
    print("\nExisting users count:", len(users))
    for u in users:
        print("  User:", u)
conn.close()
