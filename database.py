import sqlite3
conn = sqlite3.connect('P2P.db')
cursor = conn.cursor()

class database:
    def __init__(self):
        print("Database")

    def create_table(self, tableName, columns):
        try:
            cursor.execute(f"CREATE TABLE {tableName} ({columns})")
            conn.commit()
        except:
            print("Table already exists")
    