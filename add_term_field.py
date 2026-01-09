import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Add term column
    try:
        cursor.execute("ALTER TABLE students_grade ADD COLUMN term VARCHAR(20) DEFAULT 'first';")
        print("Added term column")
    except:
        print("term column already exists")
    
    # Add class_score column
    try:
        cursor.execute("ALTER TABLE students_grade ADD COLUMN class_score DECIMAL(5,2) DEFAULT 0;")
        print("Added class_score column")
    except:
        print("class_score column already exists")
    
    # Add exams_score column
    try:
        cursor.execute("ALTER TABLE students_grade ADD COLUMN exams_score DECIMAL(5,2) DEFAULT 0;")
        print("Added exams_score column")
    except:
        print("exams_score column already exists")
    
    # Add subject_position column
    try:
        cursor.execute("ALTER TABLE students_grade ADD COLUMN subject_position INTEGER DEFAULT 0;")
        print("Added subject_position column")
    except:
        print("subject_position column already exists")

print("Database updated successfully!")