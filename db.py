import sqlite3
import random

# Connect to the database (this will create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute('DROP TABLE IF EXISTS assignments')
cursor.execute('DROP TABLE IF EXISTS students')
cursor.execute('DROP TABLE IF EXISTS announcements')

# Create assignments table
cursor.execute('''
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    deadline DATE,
    question TEXT,
    professor TEXT NOT NULL
)
''')

# Create students table
cursor.execute('''
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    iwt_attendance INTEGER,
    toc_attendance INTEGER,
    cybersecurity_attendance INTEGER,
    dbms_attendance INTEGER,
    iwt_marks INTEGER,
    toc_marks INTEGER,
    cybersecurity_marks INTEGER,
    dbms_marks INTEGER
)
''')

# Create announcements table
cursor.execute('''
CREATE TABLE announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    professor TEXT NOT NULL,
    announcement TEXT NOT NULL,
    date DATE
)
''')

# Insert sample data for assignments
assignments_data = [
    ('Internet and Web Technology', '2024-11-01', 'Create a responsive website', 'Abhay Mundra'),
    ('Theory of Computation', '2024-11-05', 'Explain Turing machines', 'Shubhi Gupta'),
    ('Cybersecurity', '2024-11-10', 'Implement a basic encryption algorithm', 'Ranjan Thakur'),
    ('DBMS', '2024-11-15', 'Design a normalized database schema', 'Vijay Yadav')
]

cursor.executemany('''
INSERT INTO assignments (subject, deadline, question, professor)
VALUES (?, ?, ?, ?)
''', assignments_data)

# Insert sample data for students
student_names = ['Kshitij Kumrawat', 'Kunal Patil', 'Parth Pathak']
for name in student_names:
    cursor.execute('''
    INSERT INTO students (name, iwt_attendance, toc_attendance, cybersecurity_attendance, dbms_attendance,
                          iwt_marks, toc_marks, cybersecurity_marks, dbms_marks)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, 
          90, 90, 90, 90,
          90, 90, 90, 90))

# Insert sample announcements
announcements_data = [
    ('Internet and Web Technology', 'Abhay Mundra', 'Guest lecture on modern web frameworks next week', '2024-10-25'),
    ('Theory of Computation', 'Shubhi Gupta', 'Quiz on finite automata postponed to next Tuesday', '2024-10-26'),
    ('Cybersecurity', 'Ranjan Thakur', 'Cybersecurity workshop this Friday', '2024-10-27'),
    ('DBMS', 'Vijay Yadav', 'Project proposals due by end of the month', '2024-10-28')
]

cursor.executemany('''
INSERT INTO announcements (subject, professor, announcement, date)
VALUES (?, ?, ?, ?)
''', announcements_data)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database created successfully with sample data.")
