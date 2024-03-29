import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('''
    CREATE TABLE User (
        id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT,
        password_hash TEXT,
        duration INTEGER
    )
''')
print("Created User successfully!")

conn.execute('''
    CREATE TABLE Courses (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        duration INTEGER,
        instructor TEXT,
        start_date DATE,
        course_type TEXT
    )
''')
print("Created Courses successfully!")

conn.execute('''
    CREATE TABLE UserCourses  (
       id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        duration INTEGER,
        course_id INTEGER,
        course_type TEXT,
        FOREIGN KEY (user_id) REFERENCES User (id),
        FOREIGN KEY (course_id) REFERENCES Courses (id)
    )
''')
print("Created UserCourses successfully!")

conn.execute('''
    CREATE TABLE Graph (
    Category TEXT,
    Value INTEGER
    )
''')
print("Created Graph successfully!")

conn.close()