import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

insert_query = "INSERT INTO Graph (Category, Value) VALUES (?, ?)"
data_to_insert = [('2020', 10), ('2021', 25), ('2022', 15), ('2023', 30), ('2024', 56)]
conn.executemany(insert_query, data_to_insert)
print("Inserted into Graph successfully!")

conn.commit()

conn.close()