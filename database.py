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
        except :
            print("Table already exists")
    
    def insert_data(self, tableName, data):
        try:
            cursor.execute(f"insert into {tableName} values ({data})")
            conn.commit()
        except Exception:
            print("error inserting data:" )
    
    def select_data(self, tableName, columns):
        try:
            cursor.execute(f"select {columns} from {tableName}")
            return cursor.fetchall() 
        except Exception:
            print("error selecting data:" )
    
    def update_data(self, tableName, data):
        try:
            cursor.execute(f"update {tableName} set {data}")
            conn.commit()
        except Exception:
            print("error updating data:" )
            
    def delete_data(self, tableName, data):
        try:
            cursor.execute(f"delete from {tableName} where {data}")
            conn.commit()
        except Exception:
            print("error deleting data:" )
    
   