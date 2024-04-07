-- Connect to the database
CREATE DATABASE IF NOT EXISTS STRAITS;

-- Use the created database
USE STRAITS;

-- Department table
CREATE TABLE IF NOT EXISTS Department (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    default_total_hours INT DEFAULT 100,
    core_skills_percentage INT DEFAULT 50,
    soft_skills_percentage INT DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create User table
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    role TEXT,
    password_hash TEXT,
    duration INT,
    department_id INT, 
    FOREIGN KEY (department_id) REFERENCES Department(id)
);

-- Create manytomany rs between HR officers and Departments
CREATE TABLE IF NOT EXISTS DepartmentHR (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    department_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (department_id) REFERENCES Department(id)
);

-- Create Courses table
CREATE TABLE IF NOT EXISTS Courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    description TEXT,
    duration INTEGER,
    instructor TEXT,
    start_date DATE,
    course_type TEXT
);

-- Create UserCourses table
CREATE TABLE IF NOT EXISTS UserCourses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    duration INTEGER,
    course_id INTEGER,
    course_type TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE
);

-- Create Graph table
CREATE TABLE IF NOT EXISTS Graph (
    Category TEXT,
    Value INTEGER
);

-- TrainingRequirements table (for user)
CREATE TABLE IF NOT EXISTS TrainingRequirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    department_id INT,
    total_hours INT,
    core_skills_hours INT,
    soft_skills_hours INT,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (department_id) REFERENCES Department(id)
);

