#!/usr/bin/env python
"""
Create comprehensive test data for the school management system.
This script creates users, classes, subjects, grades, and other necessary data.
"""
import os
import sys
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from academics.models import AcademicYear, Class, Subject, ClassSubject
from students.models import Student, Grade, Attendance
from teachers.models import Teacher
from parents.models import Parent
from communications.models import Message

User = get_user_model()

def create_academic_year():
    """Create an academic year"""
    from datetime import datetime
    year, created = AcademicYear.objects.get_or_create(
        name='2024/2025',
        defaults={
            'is_current': True,
            'start_date': datetime(2024, 9, 1).date(),
            'end_date': datetime(2025, 7, 31).date()
        }
    )
    if created:
        print(f"✓ Created academic year: {year.name}")
    return year

def create_admin_user():
    """Create admin user"""
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@school.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✓ Created admin user: admin")
    else:
        user.set_password('admin123')
        user.save()
        print(f"✓ Updated admin user password")
    return user

def create_classes(academic_year):
    """Create class entries"""
    classes_data = [
        {'name': 'Primary 4', 'level': 4},
        {'name': 'Primary 5', 'level': 5},
        {'name': 'Primary 6', 'level': 6},
    ]
    
    classes = []
    for class_data in classes_data:
        klass, created = Class.objects.get_or_create(
            name=class_data['name'],
            academic_year=academic_year
        )
        classes.append(klass)
        if created:
            print(f"✓ Created class: {class_data['name']}")
    return classes

def create_subjects():
    """Create subjects"""
    subjects_data = [
        {'code': 'ENG', 'name': 'English Language'},
        {'code': 'MAT', 'name': 'Mathematics'},
        {'code': 'SCI', 'name': 'Science'},
        {'code': 'SST', 'name': 'Social Studies'},
    ]
    
    subjects = []
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults={'name': subject_data['name']}
        )
        subjects.append(subject)
        if created:
            print(f"✓ Created subject: {subject_data['name']}")
    return subjects

def create_teachers(academic_year):
    """Create teacher users and records"""
    teachers_data = [
        {'username': 'teacher1', 'first_name': 'John', 'last_name': 'Smith'},
        {'username': 'teacher2', 'first_name': 'Jane', 'last_name': 'Doe'},
    ]
    
    teachers = []
    for idx, teacher_data in enumerate(teachers_data):
        user, created = User.objects.get_or_create(
            username=teacher_data['username'],
            defaults={
                'email': f"{teacher_data['username']}@school.com",
                'first_name': teacher_data['first_name'],
                'last_name': teacher_data['last_name'],
                'user_type': 'teacher',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✓ Created teacher user: {teacher_data['username']}")
        
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': f"EMP{1001+idx}",
                'date_of_birth': datetime(1990, 1, 1).date(),
                'date_of_joining': datetime(2020, 1, 1).date(),
                'qualification': 'Bachelor of Education'
            }
        )
        teachers.append(teacher)
        if created:
            print(f"✓ Created teacher record: {teacher_data['first_name']} {teacher_data['last_name']}")
    
    return teachers

def assign_teachers_to_classes(teachers, classes, subjects):
    """Assign teachers to classes and subjects"""
    for idx, teacher in enumerate(teachers):
        klass = classes[idx % len(classes)]
        subject = subjects[idx % len(subjects)]
        
        cs, created = ClassSubject.objects.get_or_create(
            class_name=klass,
            subject=subject,
            defaults={'teacher': teacher}
        )
        if created:
            print(f"✓ Assigned {teacher.user.first_name} to teach {subject.name} in {klass.name}")

def create_students(classes):
    """Create student users and records"""
    students_data = [
        {'username': 'student1', 'first_name': 'Alice', 'last_name': 'Johnson', 'admission': 'ADM001'},
        {'username': 'student2', 'first_name': 'Bob', 'last_name': 'Williams', 'admission': 'ADM002'},
        {'username': 'student3', 'first_name': 'Charlie', 'last_name': 'Brown', 'admission': 'ADM003'},
        {'username': 'student4', 'first_name': 'Diana', 'last_name': 'Davis', 'admission': 'ADM004'},
    ]
    
    students = []
    for idx, student_data in enumerate(students_data):
        user, created = User.objects.get_or_create(
            username=student_data['username'],
            defaults={
                'email': f"{student_data['username']}@school.com",
                'first_name': student_data['first_name'],
                'last_name': student_data['last_name'],
                'user_type': 'student',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✓ Created student user: {student_data['username']}")
        
        klass = classes[idx % len(classes)]
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'admission_number': student_data['admission'],
                'current_class': klass,
                'date_of_birth': datetime(2015, 1, 1).date(),
                'date_of_admission': datetime(2023, 9, 1).date(),
                'gender': 'male' if idx % 2 == 0 else 'female',
                'emergency_contact': '+233123456789'
            }
        )
        students.append(student)
        if created:
            print(f"✓ Created student: {student_data['first_name']} {student_data['last_name']} in {klass.name}")
    
    return students

def create_grades(students, subjects):
    """Create grades for students"""
    terms = ['first', 'second', 'third']
    year = AcademicYear.objects.filter(is_current=True).first()
    if not year:
        year = AcademicYear.objects.order_by('-name').first()
    
    for student in students:
        for term in terms:
            for subject in subjects:
                # Create a grade with realistic scores
                grade, created = Grade.objects.get_or_create(
                    student=student,
                    subject=subject,
                    term=term,
                    academic_year=year,
                    defaults={
                        'class_score': 20,
                        'exams_score': 65,
                        'total_score': 85.0
                    }
                )
                if created:
                    print(f"✓ Created grade: {student.user.first_name} - {subject.name} ({term}): {grade.total_score}")

def create_attendance(students):
    """Create attendance records"""
    today = datetime.now().date()
    
    for student in students:
        for days_ago in range(1, 11):  # Last 10 days
            attendance_date = today - timedelta(days=days_ago)
            
            att, created = Attendance.objects.get_or_create(
                student=student,
                date=attendance_date,
                defaults={'status': 'present' if days_ago % 3 != 0 else 'absent'}
            )
            if created and days_ago == 1:
                print(f"✓ Created attendance records for {student.user.first_name}")

def create_parents(students):
    """Create parent users and link to students"""
    parents_data = [
        {'username': 'parent1', 'first_name': 'Mary', 'last_name': 'Johnson'},
        {'username': 'parent2', 'first_name': 'Robert', 'last_name': 'Williams'},
    ]
    
    for idx, parent_data in enumerate(parents_data):
        user, created = User.objects.get_or_create(
            username=parent_data['username'],
            defaults={
                'email': f"{parent_data['username']}@school.com",
                'first_name': parent_data['first_name'],
                'last_name': parent_data['last_name'],
                'user_type': 'parent',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✓ Created parent user: {parent_data['username']}")
        
        # Create or get parent record
        parent, created = Parent.objects.get_or_create(
            user=user,
            defaults={'relation': 'mother' if idx % 2 == 0 else 'father'}
        )
        if created:
            print(f"✓ Created parent: {parent_data['first_name']} {parent_data['last_name']}")
        
        # Assign students to parent
        student = students[idx % len(students)]
        parent.children.add(student)
        print(f"✓ Linked parent {parent_data['first_name']} to student {student.user.first_name}")

def create_messages(users):
    """Create sample messages for testing messaging system"""
    admin_user = User.objects.get(username='admin')
    teacher_user = User.objects.filter(user_type='teacher').first()
    parent_user = User.objects.filter(user_type='parent').first()
    
    if teacher_user and parent_user:
        message, created = Message.objects.get_or_create(
            sender=teacher_user,
            recipient=parent_user,
            defaults={
                'subject': 'Update on Student Progress',
                'body': 'Your child is doing well in class. Please keep up with the homework assignments.',
                'is_read': False
            }
        )
        if created:
            print(f"✓ Created sample message from teacher to parent")

def main():
    print("\n" + "="*60)
    print("CREATING TEST DATA FOR SCHOOL MANAGEMENT SYSTEM")
    print("="*60 + "\n")
    
    try:
        # Create foundational data
        academic_year = create_academic_year()
        admin_user = create_admin_user()
        classes = create_classes(academic_year)
        subjects = create_subjects()
        
        # Create users and assignments
        teachers = create_teachers(academic_year)
        assign_teachers_to_classes(teachers, classes, subjects)
        students = create_students(classes)
        
        # Create records
        create_grades(students, subjects)
        create_attendance(students)
        create_parents(students)
        create_messages(User.objects.all())
        
        print("\n" + "="*60)
        print("TEST DATA CREATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nLOGIN CREDENTIALS:")
        print("-" * 60)
        print("Admin:     admin / admin123")
        print("Teacher:   teacher1 / password123")
        print("Teacher:   teacher2 / password123")
        print("Student:   student1 / password123")
        print("Student:   student2 / password123")
        print("Parent:    parent1 / password123")
        print("Parent:    parent2 / password123")
        print("-" * 60 + "\n")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
