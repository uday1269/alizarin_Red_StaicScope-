import pymysql

passwords = ['', 'root', 'admin', '123456', '1234', 'mysql', 'Password123!', 'stainscope', 'root123']
for pwd in passwords:
    try:
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password=pwd)
        print(f'SUCCESS with password: "{pwd}"')
        with conn.cursor() as c:
            c.execute('SHOW DATABASES;')
            print('Databases:', c.fetchall())
        conn.close()
        break
    except Exception as e:
        print(f'Failed with "{pwd}": {e}')
