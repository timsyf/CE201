import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

delete_query = "DELETE FROM Graph"
conn.execute(delete_query)
print("Deleted Graph successfully!")

conn.commit()

conn.close()