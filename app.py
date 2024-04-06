from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

import pandas as pd
import plotly.express as px

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'secret_key'

# Database connection function using environment variables
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv('DB_SERVER'),
        database=os.getenv('DB_DATABASE'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    return render_template('Pages/dashboard.html')  

# User Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE name = %s', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username already exists. Please choose another one.', 'error')
            return render_template('Auth/register.html')  

        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO User (name, password_hash, role) VALUES (%s, %s, %s)', (username, hashed_password, role))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('Auth/register.html')

# User Login Route
@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE name = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user is None:
            flash('User does not exist.', 'error')
        elif not check_password_hash(user[3], password):
            flash('Wrong password.', 'error')
        else:
            session['user_id'] = user[0]
            session['user_role'] = user[2]
            
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('index'))
    
    if 'user_id' in session:
        return render_template('Pages/dashboard.html')
    else:
        return render_template('Auth/login.html')

# User Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect(url_for('index'))

# Profile Route
@app.route('/profile')
def profile():
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT name, role FROM User WHERE id = %s', (session['user_id'],))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return render_template('User/profile.html', username=user_data[0], role=user_data[1])
        else:
            return 'User not found', 404
    else:
        return redirect(url_for('index'))
    
@app.route('/departmentexport', methods=['POST'])
def departmentexport():
    data = {
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Car A', 'Car B', 'Car C', 'Car D', 'Car E'],
        'Price': [25000, 30000, 35000, 40000, 45000]
    }

    df = pd.DataFrame(data)
    excel_file_path = "cars_data.xlsx"
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)

@app.route('/userexport', methods=['POST'])
def userexport():
    data = {
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Car A', 'Car B', 'Car C', 'Car D', 'Car E'],
        'Price': [25000, 30000, 35000, 40000, 45000]
    }

    df = pd.DataFrame(data)
    excel_file_path = "cars_data.xlsx"
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)

###Departments###
#View and edit Departments
@app.route('/departments')
def departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = 'SELECT Department.*, COUNT(User.department_id) AS user_count FROM Department LEFT JOIN User ON Department.id = User.department_id GROUP BY Department.id'
    cursor.execute(query)
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('Departments/departments.html', departments=departments)

#Add Department
@app.route('/department/add', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        name = request.form['name']
        default_total_hours = request.form['default_total_hours']
        core_skills_percentage = request.form['core_skills_percentage']
        soft_skills_percentage = request.form['soft_skills_percentage']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Department (name, default_total_hours, core_skills_percentage, soft_skills_percentage) VALUES (%s, %s, %s, %s)', (name, default_total_hours, core_skills_percentage, soft_skills_percentage))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Department added successfully.', 'success')
        return redirect(url_for('departments'))
    
    return render_template('Departments/add_department.html')

#Edit Department
@app.route('/department/edit/<int:department_id>', methods=['GET', 'POST'])
def edit_department(department_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        default_total_hours = request.form['default_total_hours']
        core_skills_percentage = request.form['core_skills_percentage']
        soft_skills_percentage = request.form['soft_skills_percentage']
        
        cursor.execute('UPDATE Department SET name = %s, default_total_hours = %s, core_skills_percentage = %s, soft_skills_percentage = %s WHERE id = %s', (name, default_total_hours, core_skills_percentage, soft_skills_percentage, department_id))
        conn.commit()
        flash('Department updated successfully.', 'success')
        return redirect(url_for('departments'))
    
    cursor.execute('SELECT * FROM Department WHERE id = %s', (department_id,))
    department = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if department:
        return render_template('Departments/edit_department.html', department=department)
    else:
        flash('Department not found.', 'error')
        return redirect(url_for('departments'))

#Delete Department
@app.route('/department/delete/<int:department_id>', methods=['POST'])
def delete_department(department_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the department exists
    cursor.execute('SELECT id FROM Department WHERE id = %s', (department_id,))
    department = cursor.fetchone()
    if not department:
        flash('Department does not exist.', 'error')
        return redirect(url_for('departments'))
    
    # Check if there are any users assigned to this department
    cursor.execute('SELECT id FROM User WHERE department_id = %s', (department_id,))
    if cursor.fetchone():
        flash('Cannot delete a department with assigned users. Please reassign or remove users first.', 'error')
        return redirect(url_for('departments'))
    
    # Proceed with deletion since validations passed
    cursor.execute('DELETE FROM Department WHERE id = %s', (department_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Department deleted successfully.', 'success')
    return redirect(url_for('departments'))

#View and Edit Department Users List
@app.route('/department/users/<int:department_id>')
def edit_department_users(department_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT name FROM Department WHERE id = %s', (department_id,))
    department = cursor.fetchone()

    cursor.execute('SELECT * FROM User WHERE department_id = %s AND role = %s', (department_id, 'staff',))
    department_users = cursor.fetchall()

    cursor.execute('SELECT * FROM User WHERE (department_id IS NULL OR department_id = 0) AND role = %s', ('staff',))
    users_without_department = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('Departments/edit_department_users.html', department_users=department_users, users_without_department=users_without_department, department_id=department_id, department_name=department['name'])

#Add Department User
@app.route('/department/add_user_to_department', methods=['POST'])
def add_user_to_department():
    user_id = request.form.get('user_id')
    department_id = request.form.get('department_id')

    if not user_id or not department_id:
        flash('Missing user or department information.', 'error')
        return redirect(url_for('departments'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE User SET department_id = %s WHERE id = %s', (department_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User added to department successfully.', 'success')
    return redirect(url_for('edit_department_users', department_id=department_id))

#Remove Department User
@app.route('/department/remove_user_from_department', methods=['POST'])
def remove_user_from_department():
    user_id = request.form.get('user_id')
    department_id = request.form.get('department_id')  
    if not user_id:
        flash('Missing user information.', 'error')
        return redirect(url_for('departments'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE User SET department_id = NULL WHERE id = %s', (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User removed from department successfully.', 'success')
    return redirect(url_for('edit_department_users', department_id=department_id))

    
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

        conn = get_db_connection()
        cursor = conn.cursor()

        # Use a single INSERT statement with multiple columns
        cursor.execute('''
            INSERT INTO Courses (name, course_type, duration, start_date, instructor, description)
            VALUES (%s, %s, %s, %s, %s, %s)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses')
    courses = cursor.fetchall()
    conn.close()
    return render_template('Courses/courses.html', courses=courses, applied_course_id=applied_course_id)

# SELECT ONE course
@app.route('/courses/update/<int:courses_id>', methods=['GET'])
def courses_update_view(courses_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses WHERE id = %s', (courses_id,))
    courses = cursor.fetchone()
    conn.close()
    return render_template('Courses/coursesupdate.html', courses=courses)

# DELETE Course
@app.route('/courses/delete/<int:courses_id>', methods=['POST'])
def courses_delete(courses_id):
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Courses WHERE id = %s', (courses_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('courses'))

# UPDATE course
@app.route('/courses/update_courses/<int:courses_id>', methods=['POST'])
def courses_update(courses_id):
    new_name = request.form.get('new_name')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Courses SET name = %s WHERE id = %s', (new_name, courses_id))
    conn.commit()
    conn.close()
    return redirect(url_for('courses'))

# Apply course
@app.route('/apply_course/<int:courses_id>', methods=['POST'])
def apply_course(courses_id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO UserCourses (user_id, course_id) VALUES (%s, %s)', (user_id, courses_id))
        conn.commit()
        conn.close()
  
    applied_courses_data = get_applied_courses(user_id)

    total_duration_core = 0
    total_duration_soft = 0
    
    for course in applied_courses_data:
       
        if course[6] == 'Core':
            total_duration_core += course[3]
            
        elif course[6] == 'Soft':
            total_duration_soft += course[3]

    return render_template('TrainingHours/training.html', applied_courses=applied_courses_data, total_duration_core=total_duration_core, total_duration_soft=total_duration_soft)
    
#Get applied course
def get_applied_courses(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT course_id FROM UserCourses WHERE user_id = %s', (user_id,))
    
    # Fetch all the results and create a list of course IDs
    applied_courses_ids = cursor.fetchall()
    
    # Retrieve the course details for the applied course IDs
    applied_courses = []
    
    for course_id in applied_courses_ids:
        cursor.execute('SELECT * FROM Courses WHERE id = %s', (course_id[0],))
        course_details = cursor.fetchone()
        applied_courses.append(course_details)

    conn.close()
    return applied_courses

# Get applied course IDs for a user
def get_applied_course_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT course_id FROM usercourses WHERE user_id = %s', (user_id,))
    
    applied_course_id = [course_id[0] for course_id in cursor.fetchall()]

    conn.close()
    return applied_course_id

@app.route('/delete_applied_course/<int:course_id>', methods=['POST'])
def delete_applied_course(course_id):
    # Add logic to delete the course from the UserCourses table
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usercourses WHERE user_id = %s AND course_id = %s', (user_id, course_id))
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
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT course_id FROM UserCourses WHERE user_id = %s', (user_id,))
    
    # Fetch all the results and create a list of course IDs
    applied_courses_ids = cursor.fetchall()
    
    # Retrieve the course details for the applied course IDs
    applied_courses = []
    
    for course_id in applied_courses_ids:
        cursor.execute('SELECT * FROM Courses WHERE id = %s', (course_id[0],))
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

    return render_template('TrainingHours/training.html', applied_courses=applied_courses, total_duration_core=total_duration_core, total_duration_soft=total_duration_soft)

#### GRAPHS ####
def create_line_graph_courses():
    conn = get_db_connection()
    query = "SELECT course_type, duration FROM Courses"
    df = pd.read_sql(query, conn)
    conn.close()
    fig = px.bar(df, x='course_type', y='duration', title='Courses Bar Graph')
    graph_html = fig.to_html(full_html=False)
    return graph_html

def create_pie_graph_courses():
    conn = get_db_connection()
    query = "SELECT course_type, duration FROM Courses"
    df = pd.read_sql(query, conn)
    conn.close()
    fig = px.pie(df, names='course_type', values='duration', title='Courses Pie Graph')
    graph_html = fig.to_html(full_html=False)
    return graph_html