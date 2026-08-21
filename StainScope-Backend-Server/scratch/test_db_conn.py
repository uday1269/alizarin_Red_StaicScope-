import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_mysql import MySQLPersistenceManager, get_db_connection

db_manager = MySQLPersistenceManager()
print("DB connected:", db_manager.is_connected())
conn = get_db_connection()
with conn.cursor() as c:
    c.execute("SELECT COUNT(*) as count FROM analyses")
    print("Analyses in MySQL:", c.fetchone())
conn.close()
