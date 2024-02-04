from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route("/")
def index():
    return render_template("index.html")

# Database connection 
def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

# User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        conn.execute('INSERT INTO User (name, password_hash, role) VALUES (?, ?, ?)', (username, hashed_password, role))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('Auth/register.html')

# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM User WHERE name = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_role'] = user[2]
            return redirect(url_for('index'))
        else:
            error = 'Wrong username or password'
    return render_template('Auth/login.html',error=error)

# User Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect(url_for('login'))

'''
#### USER ####

# SELECT ALL USER
@app.route('/user', methods=['GET'])
def user():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User')
    users = cursor.fetchall()
    conn.close()
    return render_template('User/index.html', users=users)

# SELECT ONE USER
@app.route('/user/update/<int:user_id>', methods=['GET'])
def user_update_view(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return render_template('User/update.html', user=user)

# INSERT USER
@app.route('/user/insert', methods=['POST'])
def user_insert():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO User (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
    return redirect(url_for('user'))

# DELETE USER
@app.route('/delete/<int:user_id>', methods=['POST'])
def user_delete(user_id):
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM User WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('user'))

# UPDATE USER
@app.route('/user/update_user/<int:user_id>', methods=['POST'])
def user_update(user_id):
    new_name = request.form.get('new_name')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE User SET name = ? WHERE id = ?', (new_name, user_id))
        conn.commit()
    return redirect(url_for('user'))
'''

#### COURSES ####

# INSERT Courses
@app.route('/courses/insert', methods=['POST'])
def courses_insert():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Courses (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
    return redirect(url_for('courses'))

# SELECT ALL courses
@app.route('/courses', methods=['GET'])
def courses():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses')
    courses = cursor.fetchall()
    conn.close()
    return render_template('Courses/courses.html', courses=courses)

# SELECT ONE course
@app.route('/courses/update/<int:courses_id>', methods=['GET'])
def courses_update_view(courses_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses WHERE id = ?', (courses_id,))
    courses = cursor.fetchone()
    conn.close()
    return render_template('Courses/coursesupdate.html', courses=courses)

# DELETE Course
@app.route('/courses/delete/<int:courses_id>', methods=['POST'])
def courses_delete(courses_id):
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Courses WHERE id = ?', (courses_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('courses'))

# UPDATE course
@app.route('/courses/update_courses/<int:courses_id>', methods=['POST'])
def courses_update(courses_id):
    new_name = request.form.get('new_name')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE Courses SET name = ? WHERE id = ?', (new_name, courses_id))
        conn.commit()
    return redirect(url_for('courses'))