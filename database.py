import sqlite3
conn = sqlite3.connect('P2P.db')
cursor = conn.cursor()

def create_table(tableName, columns):
    try:
        cursor.execute(f"CREATE TABLE {tableName} ({columns})")
        conn.commit()
    except:
        print("Table already exists")
    