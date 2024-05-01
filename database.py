import sqlite3
conn = sqlite3.connect('P2P.db', check_same_thread=False)
cursor = conn.cursor()

class database:
    def __init__(self):
        print("Database")

    def create_table(self, tableName, columns):
        try:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {tableName} ({columns})")
            conn.commit()
        except :
            print("Table creation error")
    
    def insert_data(self, tableName, data):
        #try:
            cursor.execute(f"insert into {tableName} values ({data})")
            conn.commit()
        #except Exception:
        #    print("error inserting data:" )
    
    def select_data(self, tableName, columns):
        #try:
            cursor.execute(f"select {columns} from {tableName}")
            return cursor.fetchall() 
        #except Exception:
        #    print("error selecting data:" )
    
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

    def execute_select(self, command):
        #try:
        cursor.execute(command)
        return cursor.fetchall() 
        #except Exception:
        #    print("Error in custom select command")

    def execute_insert(self, command):
        try:
            result = cursor.execute(command)
            conn.commit()
        except Exception:
            print("Error in custom insert command")

   