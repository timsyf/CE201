import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('''
    CREATE TABLE User (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')
print("Created table successfully!")

conn.close()