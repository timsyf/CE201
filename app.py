from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime, timedelta

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
    training_hours_graph = training_hours()
    get_newest_courses_1_week_graph = get_newest_courses_1_week()
    get_newest_courses_1_month_graph = get_newest_courses_1_month()
    get_newest_courses_1_year_graph = get_newest_courses_1_year()
    return render_template('Pages/dashboard.html', training_hours_graph=training_hours_graph,
                                                   get_newest_courses_1_week_graph=get_newest_courses_1_week_graph,
                                                   get_newest_courses_1_month_graph=get_newest_courses_1_month_graph,
                                                   get_newest_courses_1_year_graph=get_newest_courses_1_year_graph
    )

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
            session['user_department'] = user[5]
            
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
    session.pop('user_department', None)
    return redirect(url_for('index'))

# Profile Route
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT name, role, department_id FROM User WHERE id = %s', (session['user_id'],))
    user_data = cursor.fetchone()

    roles = {
        'staff': 'Staff',
        'hr_officer': 'HR Officer',
        'hr_supervisor': 'HR Supervisor'
    }
    display_role = roles.get(user_data['role'], 'Unknown Role')

    department_name = None
    hr_officers = []
    staff_list = []
    assigned_departments = []

    if user_data['role'] == 'staff':
        cursor.execute('SELECT name FROM Department WHERE id = %s', (user_data['department_id'],))
        department = cursor.fetchone()
        department_name = department['name'] if department else 'Not Assigned'

        cursor.execute('SELECT User.name FROM User JOIN DepartmentHR ON User.id = DepartmentHR.user_id WHERE DepartmentHR.department_id = %s AND User.role = "hr_officer"', (user_data['department_id'],))
        hr_officers = cursor.fetchall()

        cursor.execute('SELECT name FROM User WHERE department_id = %s AND role = "staff"', (user_data['department_id'],))
        staff_list = cursor.fetchall()

    elif user_data['role'] == 'hr_officer':
        cursor.execute('SELECT Department.name FROM DepartmentHR JOIN Department ON DepartmentHR.department_id = Department.id WHERE DepartmentHR.user_id = %s', (session['user_id'],))
        assigned_departments = cursor.fetchall()

    elif user_data['role'] == 'hr_supervisor':
        pass

    conn.close()

    return render_template('User/profile.html', 
                           username=user_data['name'], 
                           role=display_role, 
                           department_name=department_name, 
                           hr_officers=hr_officers, 
                           staff_list=staff_list, 
                           assigned_departments=assigned_departments)

#Change Username
@app.route('/change_username', methods=['GET', 'POST'])
def change_username():
    if 'user_id' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        if not new_username:
            flash('Please enter a new username.', 'error')
            return redirect(url_for('change_username'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id FROM User WHERE name = %s', (new_username,))
        if cursor.fetchone():
            flash('This username is already taken. Please choose a different one.', 'error')
            conn.close()
            return redirect(url_for('change_username'))

        cursor.execute('UPDATE User SET name = %s WHERE id = %s', (new_username, session['user_id']))
        conn.commit()
        conn.close()
        flash('Your username has been updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('Changes/change_username.html')

#Change password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT password_hash FROM User WHERE id = %s', (session['user_id'],))
        user = cursor.fetchone()

        if not check_password_hash(user['password_hash'], current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('change_password'))

        if new_password != confirm_new_password:
            flash("New passwords don't match", 'error')
            return redirect(url_for('change_password'))

        new_password_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE User SET password_hash = %s WHERE id = %s', (new_password_hash, session['user_id']))
        conn.commit()

        flash('Password successfully updated', 'success')
        return redirect(url_for('profile'))

    return render_template('Changes/change_password.html')

###Departments###
#View and edit Departments
@app.route('/departments')
def departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['user_role'] == 'hr_supervisor':
        query = '''
        SELECT Department.*,
               COUNT(DISTINCT u1.id) AS user_count,
               COUNT(DISTINCT DepartmentHR.user_id) AS hr_officer_count
        FROM Department
        LEFT JOIN User AS u1 ON Department.id = u1.department_id AND u1.role = "staff"
        LEFT JOIN DepartmentHR ON Department.id = DepartmentHR.department_id
        GROUP BY Department.id;
        '''
    elif session['user_role'] == 'hr_officer':
        query = '''
        SELECT Department.*,
               COUNT(DISTINCT u1.id) AS user_count
        FROM Department
        INNER JOIN DepartmentHR ON Department.id = DepartmentHR.department_id
        LEFT JOIN User AS u1 ON Department.id = u1.department_id AND u1.role = "staff"
        WHERE DepartmentHR.user_id = %s
        GROUP BY Department.id;
        ''' % session['user_id']
    else:
        pass

    cursor.execute(query)
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('Departments/departments.html', departments=departments, user_role=session['user_role'])

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

    cursor.execute('SELECT id FROM Department WHERE id = %s', (department_id,))
    department = cursor.fetchone()
    if not department:
        flash('Department does not exist.', 'error')
        return redirect(url_for('departments'))
    
    cursor.execute('SELECT id FROM DepartmentHR WHERE department_id = %s', (department_id,))
    if cursor.fetchone():
        flash('Cannot delete a department with assigned HR officers. Please reassign or remove HR officers first.', 'error')
        return redirect(url_for('departments'))

    cursor.execute('SELECT id FROM User WHERE department_id = %s', (department_id,))
    if cursor.fetchone():
        flash('Cannot delete a department with assigned Staff. Please reassign or remove Staff first.', 'error')
        return redirect(url_for('departments'))
    
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

#View and edit HR officers 
@app.route('/department/officers/<int:department_id>')
def department_officers(department_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT name FROM Department WHERE id = %s', (department_id,))
    department = cursor.fetchone()

    cursor.execute('''
        SELECT User.* FROM DepartmentHR
        JOIN User ON DepartmentHR.user_id = User.id
        WHERE DepartmentHR.department_id = %s AND User.role = "hr_officer"
    ''', (department_id,))
    department_officers = cursor.fetchall()

    cursor.execute('''
        SELECT * FROM User
        WHERE id NOT IN (
            SELECT user_id FROM DepartmentHR WHERE department_id = %s
        ) AND role = "hr_officer"
    ''', (department_id,))
    available_officers = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('Departments/department_officers.html', 
                           department_officers=department_officers, 
                           available_officers=available_officers, 
                           department_id=department_id, 
                           department_name=department['name'])

#Add HR officers to department
@app.route('/department/add_officer_to_department', methods=['POST'])
def add_officer_to_department():
    department_id = request.form.get('department_id')
    user_id = request.form.get('user_id')
    
    if not department_id or not user_id:
        flash('Missing department or HR officer information.', 'error')
        return redirect(url_for('departments'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO DepartmentHR (user_id, department_id) VALUES (%s, %s)', (user_id, department_id))
    
    conn.commit()
    cursor.close()
    conn.close()

    flash('HR officer added to the department successfully.', 'success')
    return redirect(url_for('department_officers', department_id=department_id))

#Delete HR officers from Department
@app.route('/department/remove_officer_from_department', methods=['POST'])
def remove_officer_from_department():
    user_id = request.form.get('user_id')
    department_id = request.form.get('department_id')

    if not user_id or not department_id:
        flash('Missing HR officer or department information.', 'error')
        return redirect(url_for('departments'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM DepartmentHR WHERE user_id = %s AND department_id = %s', (user_id, department_id))
    
    conn.commit()
    cursor.close()
    conn.close()

    flash('HR officer removed from the department successfully.', 'success')
    return redirect(url_for('department_officers', department_id=department_id))


#### COURSES ####
# Insert Courses Page
@app.route('/addcourse', methods=['GET'])
def render_course_form():
    return render_template('Courses/addcourse.html')

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
    new_date = request.form.get('new_date')
    new_duration = request.form.get('new_duration')
    new_type= request.form.get('new_type')
    new_instructor = request.form.get('new_instructor')
    new_description = request.form.get('new_description')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Courses 
    SET name = %s, 
        start_date = %s, 
        duration = %s, 
        course_type = %s, 
        instructor = %s, 
        description = %s 
    WHERE id = %s
''', (new_name, new_date, new_duration, new_type, new_instructor, new_description, courses_id))

    conn.commit()
    conn.close()
    return redirect(url_for('courses'))

# Apply course
@app.route('/apply_course/<int:courses_id>/<string:name>/<int:duration>/<string:course_type>', methods=['POST'])
def apply_course(courses_id, name, duration, course_type):
    if request.method == 'POST':
        user_id = session.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO UserCourses (user_id, course_id, name, duration, course_type) VALUES (%s, %s, %s, %s, %s)', (user_id, courses_id, name, duration, course_type))
        conn.commit()
        conn.close()

        flash('Course applied successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to dashboard or any other appropriate page
  
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

    # Retrieve the applied courses data
    applied_courses_data = get_applied_courses(user_id)

    #Fetch department Id and the required hours
    department_id = session.get('user_department')
    print(department_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT default_total_hours, core_skills_percentage, soft_skills_percentage FROM Department WHERE id = %s', (department_id,))
    department_info = cursor.fetchone()

    if department_info:
        default_total_hours, core_skills_percentage, soft_skills_percentage = department_info

        total_duration_core = 0
        total_duration_soft = 0
        total_required_core = (core_skills_percentage/100) * default_total_hours
        total_required_soft = (soft_skills_percentage/100) * default_total_hours

        for course in applied_courses_data:
            if course[6] == 'Core':
                total_duration_core += course[3]
            elif course[6] == 'Soft':
                total_duration_soft += course[3]

        required_core = total_required_core - total_duration_core
        required_soft = total_required_soft - total_duration_soft 
    else:
        # Handle the case where department info is not available
        required_core = 0
        required_soft = 0
        total_duration_core = 0
        total_duration_soft = 0
        for course in applied_courses_data:
            if course[6] == 'Core':
                total_duration_core += course[3]
            elif course[6] == 'Soft':
                total_duration_soft += course[3]
    



    # Retrieve the course details for the applied course IDs
    applied_courses = []
    
    for course_id in applied_courses_ids:
        cursor.execute('SELECT * FROM Courses WHERE id = %s', (course_id[0],))
        course_details = cursor.fetchone()
        applied_courses.append(course_details)

    conn.close()

    return render_template('TrainingHours/training.html', applied_courses=applied_courses, total_duration_core=total_duration_core, total_duration_soft=total_duration_soft, required_core=required_core,
                       required_soft=required_soft)



#### GRAPHS && DASHBOARD ####
#### FOR STAFF - VIEW OWN TRAINING COURSES ####
def training_hours():
    conn = get_db_connection()
    query = "SELECT name AS Name, course_type AS CourseType, duration AS Duration FROM UserCourses WHERE user_id = %s"
    df = pd.read_sql(query, conn, params=(session['user_id'],))
    conn.close()
    fig = px.bar(df, x='CourseType', y='Duration', color='Name', title='Total duration of courses applied', labels={'Duration': 'Duration (hours)'})
    graph_html = fig.to_html(full_html=False)
    return graph_html

def get_newest_courses_1_week():
    one_week_ago = datetime.now() - timedelta(weeks=1)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses WHERE start_date >= %s ORDER BY start_date DESC', (one_week_ago,))
    newest_courses_1_week = cursor.fetchall()
    conn.close()
    return newest_courses_1_week

def get_newest_courses_1_month():
    one_month_ago = datetime.now() - timedelta(weeks=4)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses WHERE start_date >= %s ORDER BY start_date DESC', (one_month_ago,))
    newest_courses_1_month = cursor.fetchall()
    conn.close()
    return newest_courses_1_month

def get_newest_courses_1_year():
    one_year_ago = datetime.now() - timedelta(days=365)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Courses WHERE start_date >= %s ORDER BY start_date DESC', (one_year_ago,))
    newest_courses_1_year = cursor.fetchall()
    conn.close()
    return newest_courses_1_year

def get_single_staff_department(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trainingrequirements WHERE user_id = %s', (user_id,))
    single_staff_department = cursor.fetchall()
    conn.close()
    return single_staff_department

#### REPORT ####
@app.route('/reports')
def reports():
    user_reports = get_users_reports()
    department_reports = get_departments_reports()
    
    return render_template('Pages/reports.html',
                           dropdown_options_users=user_reports,
                           dropdown_options_departments=department_reports,
                           )

def get_users_reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User')
    users = cursor.fetchall()
    conn.close()
    dropdown_options = [{'id': user[0], 'name': user[1]} for user in users]
    return dropdown_options

def get_departments_reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Department')
    departments = cursor.fetchall()
    conn.close()
    dropdown_options = [{'id': department[0], 'name': department[1]} for department in departments]
    return dropdown_options

@app.route('/staffexport', methods=['POST'])
def staffexport():
    user_id = request.form.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT uc.id AS user_course_id, uc.user_id, uc.name AS user_course_name, uc.duration AS user_course_duration, 
           uc.course_type AS user_course_type, c.id AS course_id, c.name AS course_name, c.description, c.duration AS course_duration,
           c.instructor, c.start_date, c.course_type AS course_course_type,
           u.name AS user_name, u.role, u.duration AS user_duration, u.department_id,
           d.name AS department_name, d.default_total_hours, d.core_skills_percentage, d.soft_skills_percentage
    FROM UserCourses uc
    JOIN Courses c ON uc.course_id = c.id
    JOIN User u ON uc.user_id = u.id
    JOIN Department d ON u.department_id = d.id
    WHERE uc.user_id = %s
    ''', (user_id,))
    fetched_data = cursor.fetchall()
    conn.close()

    formatted_data = {
        'User ID': [],
        'User Name': [],
        'User Role': [],
        'User Course ID': [],
        'User Course Name': [],
        'User Course Duration': [],
        'User Course Type': [],
        'Course ID': [],
        'Course Name': [],
        'Description': [],
        'Course Duration': [],
        'Instructor': [],
        'Start Date': [],
        'Course Course Type': [],
        'User Duration': [],
        'Department ID': [],
        'Department Name': [],
        'Default Total Hours': [],
        'Core Skills Percentage': [],
        'Soft Skills Percentage': []
    }

    for row in fetched_data:
        formatted_data['User ID'].append(row[1])
        formatted_data['User Name'].append(row[12])
        formatted_data['User Role'].append(row[13])
        formatted_data['User Course ID'].append(row[0])
        formatted_data['User Course Name'].append(row[2])
        formatted_data['User Course Duration'].append(row[3])
        formatted_data['User Course Type'].append(row[4])
        formatted_data['Course ID'].append(row[5])
        formatted_data['Course Name'].append(row[6])
        formatted_data['Description'].append(row[7])
        formatted_data['Course Duration'].append(row[8])
        formatted_data['Instructor'].append(row[9])
        formatted_data['Start Date'].append(row[10])
        formatted_data['Course Course Type'].append(row[11])
        formatted_data['User Duration'].append(row[14])
        formatted_data['Department ID'].append(row[15])
        formatted_data['Department Name'].append(row[16])
        formatted_data['Default Total Hours'].append(row[17])
        formatted_data['Core Skills Percentage'].append(row[18])
        formatted_data['Soft Skills Percentage'].append(row[19])
    
    df = pd.DataFrame(formatted_data)
    excel_file_path = "STAFF_REPORT.xlsx"
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)

@app.route('/departmentexport', methods=['POST'])
def departmentexport():
    department_year = request.form.get('department_date')
    conn = get_db_connection()
    cursor = conn.cursor()

    sql_query = """
    SELECT id, name, default_total_hours, core_skills_percentage, soft_skills_percentage, created_at 
    FROM Department 
    WHERE YEAR(created_at) = %s
    """

    cursor.execute(sql_query, (department_year,))
    
    fetched_data = cursor.fetchall()

    conn.close()

    formatted_data = {
        'ID': [],
        'Name': [],
        'Default Total Hours': [],
        'Core Skills Percentage': [],
        'Soft Skills Percentage': [],
        'Created At': []
    }

    for row in fetched_data:
        formatted_data['ID'].append(row[0])
        formatted_data['Name'].append(row[1])
        formatted_data['Default Total Hours'].append(row[2])
        formatted_data['Core Skills Percentage'].append(row[3])
        formatted_data['Soft Skills Percentage'].append(row[4])
        formatted_data['Created At'].append(row[5])
    
    df = pd.DataFrame(formatted_data)
    excel_file_path = "DEPARTMENT_REPORT.xlsx"
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)

@app.route('/completedexport', methods=['POST'])
def completedexport():
    department_id = request.form.get('department_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    sql_query = """SELECT 
        u.id AS user_id,
        u.name AS user_name,
        u.department_id,
        uc.course_type,
        COALESCE(SUM(uc.duration), 0) AS total_duration,
        d.default_total_hours,
        d.core_skills_percentage,
        d.soft_skills_percentage,
        CASE 
            WHEN uc.course_type = 'Core' AND COALESCE(SUM(uc.duration), 0) >= d.default_total_hours * d.core_skills_percentage / 100 THEN TRUE 
            WHEN uc.course_type = 'Soft' AND COALESCE(SUM(uc.duration), 0) >= d.default_total_hours * d.soft_skills_percentage / 100 THEN TRUE 
            ELSE FALSE 
        END AS "Skills requirement met"
    FROM 
        User u
    LEFT JOIN 
        UserCourses uc ON u.id = uc.user_id
    LEFT JOIN 
        Department d ON u.department_id = d.id
    WHERE
        u.department_id = %s
    GROUP BY 
        u.id, u.name, u.department_id, uc.course_type, d.default_total_hours, d.core_skills_percentage, d.soft_skills_percentage;
    """
    
    cursor.execute(sql_query, (department_id,))
    
    fetched_data = cursor.fetchall()

    conn.close()

    formatted_data = {
        'User ID': [],
        'Name': [],
        'Department ID': [],
        'Course Type': [],
        'Total Duration': [],
        'Default Total Hours': [],
        'Core Skills Percentage': [],
        'Soft Skills Percentage': [],
        'Skills Requirement Met': []
    }

    for row in fetched_data:
        formatted_data['User ID'].append(row[0])
        formatted_data['Name'].append(row[1])
        formatted_data['Department ID'].append(row[2])
        formatted_data['Course Type'].append(row[3])
        formatted_data['Total Duration'].append(row[4])
        formatted_data['Default Total Hours'].append(row[5])
        formatted_data['Core Skills Percentage'].append(row[6])
        formatted_data['Soft Skills Percentage'].append(row[7])
        formatted_data['Skills Requirement Met'].append(row[8])
    
    df = pd.DataFrame(formatted_data)
    excel_file_path = "COMPLETEDDEPARTMENT_REPORT.xlsx"
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)


# review route
@app.route('/review', methods=['GET'])
def review():
    user_id = session.get('user_id')

    applied_course_id = get_applied_course_id(user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.name, c.description, c.duration, c.instructor, c.start_date, c.course_type, r.review
        FROM straits.courses c
        LEFT JOIN usercourses u ON c.name = u.name
        LEFT JOIN review r ON c.id = r.course_name AND r.user_id = u.user_id
        WHERE u.user_id = %s
    ''', (session['user_id'],))
    courses = cursor.fetchall()
    
    conn.close()
    return render_template('Courses/review.html', courses=courses, applied_course_id=applied_course_id)



# add review
@app.route('/review/insert', methods=['POST'])
def review_insert():
    print(request.form)  # Add this line to inspect the form data
    user_id = session.get('user_id')
    review = request.form['review']
    course_name = request.form['course_name']  # Retrieve the course name from the form data
   
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Use a single INSERT statement with multiple columns
    cursor.execute('''
        INSERT INTO review (user_id, course_name, review)  -- Include course_name in the INSERT statement
        VALUES (%s, %s, %s)
    ''', (user_id, course_name, review))

    conn.commit()
    conn.close()

    return redirect(url_for('review'))
