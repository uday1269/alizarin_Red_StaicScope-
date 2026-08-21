import requests
import json
import pymysql

# Connect to MySQL and find the analysis with mineralized_area_percent ~ 50.22%
conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="", database="stainscope")
with conn.cursor() as c:
    c.execute("SELECT id, user_id, sample_title, mineralized_area_percent, optical_density_proxy, nodule_count, analyzed_at FROM analyses ORDER BY created_at DESC LIMIT 10;")
    rows = c.fetchall()
    print("Latest 10 analyses in MySQL:")
    for r in rows:
        print(" ", r)
conn.close()
