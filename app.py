from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

import pandas as pd
import plotly.express as px

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route("/")
def index():
    line_graph_html = create_line_graph_courses()
    pie_graph_html = create_pie_graph_courses()
    return render_template("index.html", line_graph_html=line_graph_html, pie_graph_html=pie_graph_html)

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

#Profile Route
@app.route('/profile')
def profile():
    if 'user_id' in session:  
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT name, role FROM User WHERE id = ?', (session['user_id'],))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return render_template('User/profile.html', username=user_data[0], role=user_data[1])
        else:
            return 'User not found', 404
    else:
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
        course_type = request.form['course_type']
        duration = request.form['duration']
        start_date = request.form['start_date']
        instructor = request.form['instructor']
        description = request.form['description']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Use a single INSERT statement with multiple columns
        cursor.execute('''
            INSERT INTO Courses (name, course_type, duration, start_date, instructor, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, course_type, duration, start_date, instructor, description))

        conn.commit()
        conn.close()

    return redirect(url_for('courses'))


# SELECT ALL courses
@app.route('/courses', methods=['GET'])
def courses():
    user_id = session.get('user_id')
  
    applied_course_id = get_applied_course_id(user_id)
    print(applied_course_id)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses')
    courses = cursor.fetchall()
    conn.close()
    return render_template('Courses/courses.html', courses=courses,applied_course_id=applied_course_id)

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

# Apply course
@app.route('/apply_course/<int:courses_id>', methods=['POST'])
def apply_course(courses_id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO UserCourses (user_id, course_id) VALUES (?, ?)', (user_id, courses_id))
        conn.commit()
        conn.close()

  
    #applied_courses = get_applied_courses(user_id)  
    applied_courses_data = get_applied_courses(user_id)

    total_duration_core = 0
    total_duration_soft = 0
    
    for course in applied_courses_data:
       
        if course[6] == 'Core':
            total_duration_core += course[3]
            
        elif course[6] == 'Soft':
            total_duration_soft += course[3]
    

    return render_template('TrainingHours/training.html', applied_courses=applied_courses_data, total_duration_core=total_duration_core, total_duration_soft=total_duration_soft)
    
    
    #return render_template('TrainingHours/training.html', applied_courses=applied_courses)

#Get applied course
def get_applied_courses(user_id):
    user_id = session.get('user_id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT course_id FROM UserCourses WHERE user_id = ?', (user_id,))
    
    # Fetch all the results and create a list of course IDs
    applied_courses_ids = cursor.fetchall()
    
    # Retrieve the course details for the applied course IDs
    applied_courses = []
    
    for course_id in applied_courses_ids:
        cursor.execute('SELECT * FROM Courses WHERE id = ?', (course_id[0],))
        course_details = cursor.fetchone()
        applied_courses.append(course_details)

    conn.close()
    return applied_courses

# Get applied course IDs for a user
def get_applied_course_id(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT course_id FROM UserCourses WHERE user_id = ?', (user_id,))
    
    applied_course_id = [course_id[0] for course_id in cursor.fetchall()]

    conn.close()
    return applied_course_id

@app.route('/delete_applied_course/<int:course_id>', methods=['POST'])
def delete_applied_course(course_id):
    # Add logic to delete the course from the UserCourses table
    user_id = session.get('user_id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM UserCourses WHERE user_id = ? AND course_id = ?', (user_id, course_id))
    conn.commit()
    conn.close()

    # Refresh the applied courses list
    applied_courses = get_applied_courses(user_id)
    applied_courses_data = get_applied_courses(user_id)

    total_duration_core = 0
    total_duration_soft = 0
    
    for course in applied_courses_data:
       
        if course[6] == 'Core':
            total_duration_core += course[3]
            
        elif course[6] == 'Soft':
            total_duration_soft += course[3]
    return render_template('TrainingHours/training.html', applied_courses=applied_courses,total_duration_core=total_duration_core, total_duration_soft=total_duration_soft)

@app.route('/traininghours', methods=['GET'])
def training_hours():
    user_id = session.get('user_id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT course_id FROM UserCourses WHERE user_id = ?', (user_id,))
    
    # Fetch all the results and create a list of course IDs
    applied_courses_ids = cursor.fetchall()
    
    # Retrieve the course details for the applied course IDs
    applied_courses = []
    
    for course_id in applied_courses_ids:
        cursor.execute('SELECT * FROM Courses WHERE id = ?', (course_id[0],))
        course_details = cursor.fetchone()
        applied_courses.append(course_details)

    conn.close()
    applied_courses_data = get_applied_courses(user_id)

    total_duration_core = 0
    total_duration_soft = 0
    
    for course in applied_courses_data:
       
        if course[6] == 'Core':
            total_duration_core += course[3]
            
        elif course[6] == 'Soft':
            total_duration_soft += course[3]
    return render_template('TrainingHours/training.html',applied_courses= applied_courses,total_duration_core=total_duration_core, total_duration_soft=total_duration_soft)

#### GRAPHS ####
def create_line_graph_courses():
    conn = sqlite3.connect('database.db')
    query = "SELECT course_type, duration FROM Courses"
    df = pd.read_sql_query(query, conn)
    conn.close()
    fig = px.bar(df, x='course_type', y='duration', title='Courses Bar Graph')
    graph_html = fig.to_html(full_html=False)
    return graph_html

def create_pie_graph_courses():
    conn = sqlite3.connect('database.db')
    query = "SELECT course_type, duration FROM Courses"
    df = pd.read_sql_query(query, conn)
    conn.close()
    fig = px.pie(df, names='course_type', values='duration', title='Courses Pie Graph')
    graph_html = fig.to_html(full_html=False)
    return graph_html