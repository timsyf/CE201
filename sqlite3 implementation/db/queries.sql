-- Connect to the database
CREATE DATABASE IF NOT EXISTS STRAITS;

-- Use the created database
USE STRAITS;

-- Create User table
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY,
    name TEXT,
    role TEXT,
    password_hash TEXT,
    duration INTEGER
);

-- Create Courses table
CREATE TABLE IF NOT EXISTS Courses (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    duration INTEGER,
    instructor TEXT,
    start_date DATE,
    course_type TEXT
);

-- Create UserCourses table
CREATE TABLE IF NOT EXISTS UserCourses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    duration INTEGER,
    course_id INTEGER,
    course_type TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (course_id) REFERENCES Courses(id)
);

-- Create Graph table
CREATE TABLE IF NOT EXISTS Graph (
    Category TEXT,
    Value INTEGER
);