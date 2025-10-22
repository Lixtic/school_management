"""
Load mock data for Riverside School for testing purposes
Run this script with: python load_riverside_data.py
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from schools.models import School
from students.models import Student, Grade, Attendance
from teachers.models import Teacher
from parents.models import Parent
from academics.models import AcademicYear, Class, Subject

User = get_user_model()

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKBLUE}ℹ {msg}{Colors.ENDC}")

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{Colors.ENDC}\n")

def get_or_create_riverside_school():
    """Get or create Riverside School"""
    print_info("Setting up Riverside School...")
    
    # Try to find existing school by slug or name
    try:
        school = School.objects.get(slug='riverside')
        print_success(f"Found existing school: {school.name}")
        
        # Update some fields if needed
        school.email = 'admin@riverside.edu.gh'
        school.phone = '+233244123456'
        school.subscription_status = 'active'
        school.is_active = True
        school.save()
        
        return school
    except School.DoesNotExist:
        pass
    
    # Try by name
    try:
        school = School.objects.get(name__iexact='riverside')
        print_success(f"Found existing school by name: {school.name}")
        return school
    except School.DoesNotExist:
        pass
    
    # Create new school
    school = School.objects.create(
        name="Riverside School",
        slug='riverside-school',  # Different slug to avoid conflict
        email='admin@riverside.edu.gh',
        phone='+233244123456',
        website='https://riverside.edu.gh',
        address='123 Education Road, East Legon',
        city='Accra',
        state='Greater Accra',
        country='Ghana',
        postal_code='GA-123-4567',
        primary_color='#1e40af',
        secondary_color='#7c3aed',
        subscription_status='active',
        is_active=True,
        max_students=1000,
        max_teachers=100,
    )
    print_success(f"Created school: {school.name}")
    
    return school

def create_admin_user(school):
    """Create admin user for Riverside School"""
    print_info("Creating admin user...")
    
    # Check if admin user exists
    username = 'riverside_admin'
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.school = school
        user.save()
        print_success(f"Updated existing admin: {username}")
    else:
        user = User.objects.create_user(
            username=username,
            password='admin123',
            email='admin@riverside.edu.gh',
            first_name='Riverside',
            last_name='Administrator',
            user_type='admin',
            phone='+233244123456',
            school=school
        )
        print_success(f"Created admin: {username} (password: admin123)")
    
    # Set as school admin
    school.admin_user = user
    school.save()
    
    return user

def create_academic_year(school):
    """Create current academic year"""
    print_info("Creating academic year...")
    
    current_year = date.today().year
    
    year, created = AcademicYear.objects.get_or_create(
        school=school,
        name=f"{current_year}/{current_year + 1}",
        defaults={
            'start_date': date(current_year, 9, 1),
            'end_date': date(current_year + 1, 6, 30),
            'is_current': True
        }
    )
    
    if created:
        print_success(f"Created academic year: {year.name}")
    else:
        print_success(f"Found existing academic year: {year.name}")
    
    return year

def create_subjects(school):
    """Create subjects for the school"""
    print_info("Creating subjects...")
    
    subjects_data = [
        {'name': 'Mathematics', 'code': 'MATH'},
        {'name': 'English Language', 'code': 'ENG'},
        {'name': 'Science', 'code': 'SCI'},
        {'name': 'Social Studies', 'code': 'SOC'},
        {'name': 'Integrated Science', 'code': 'ISCI'},
        {'name': 'Information Technology', 'code': 'ICT'},
        {'name': 'French', 'code': 'FRE'},
        {'name': 'Religious & Moral Education', 'code': 'RME'},
        {'name': 'Physical Education', 'code': 'PE'},
        {'name': 'Creative Arts', 'code': 'CA'},
    ]
    
    subjects = []
    for subject_data in subjects_data:
        # Try to find existing subject by code
        try:
            subject = Subject.objects.get(code=subject_data['code'])
            # Update school if needed
            if not subject.school:
                subject.school = school
                subject.save()
            subjects.append(subject)
            print_success(f"  Found existing subject: {subject.name}")
        except Subject.DoesNotExist:
            # Create new with school-specific code if needed
            try:
                subject = Subject.objects.create(
                    school=school,
                    code=subject_data['code'],
                    name=subject_data['name']
                )
                subjects.append(subject)
                print_success(f"  Created subject: {subject.name}")
            except Exception as e:
                # If code conflict, try with school prefix
                code_with_prefix = f"RS_{subject_data['code']}"
                subject, created = Subject.objects.get_or_create(
                    code=code_with_prefix,
                    defaults={
                        'school': school,
                        'name': subject_data['name']
                    }
                )
                subjects.append(subject)
                if created:
                    print_success(f"  Created subject with prefix: {subject.name} ({code_with_prefix})")
    
    return subjects

def create_classes(school, academic_year):
    """Create classes for the school"""
    print_info("Creating classes...")
    
    class_names = [
        'Primary 1', 'Primary 2', 'Primary 3',
        'Primary 4', 'Primary 5', 'Primary 6',
        'JHS 1', 'JHS 2', 'JHS 3'
    ]
    
    classes = []
    for class_name in class_names:
        cls, created = Class.objects.get_or_create(
            school=school,
            name=class_name,
            academic_year=academic_year
        )
        classes.append(cls)
        if created:
            print_success(f"  Created class: {class_name}")
    
    return classes

def create_teachers(school, subjects):
    """Create teachers for the school"""
    print_info("Creating teachers...")
    
    teachers_data = [
        {'first': 'Kwame', 'last': 'Mensah', 'emp_id': 'T001', 'subjects': ['MATH', 'ISCI']},
        {'first': 'Akua', 'last': 'Asante', 'emp_id': 'T002', 'subjects': ['ENG', 'FRE']},
        {'first': 'Kofi', 'last': 'Boateng', 'emp_id': 'T003', 'subjects': ['SCI', 'ISCI']},
        {'first': 'Ama', 'last': 'Adjei', 'emp_id': 'T004', 'subjects': ['SOC', 'RME']},
        {'first': 'Yaw', 'last': 'Owusu', 'emp_id': 'T005', 'subjects': ['ICT']},
        {'first': 'Efua', 'last': 'Osei', 'emp_id': 'T006', 'subjects': ['PE', 'CA']},
        {'first': 'Kwabena', 'last': 'Amponsah', 'emp_id': 'T007', 'subjects': ['MATH']},
        {'first': 'Abena', 'last': 'Darko', 'emp_id': 'T008', 'subjects': ['ENG', 'RME']},
    ]
    
    teachers = []
    for i, teacher_data in enumerate(teachers_data):
        username = f"teacher{i+1}"
        
        # Create or get user
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.school = school
            user.save()
        else:
            user = User.objects.create_user(
                username=username,
                password='password123',
                email=f"{username}@riverside.edu.gh",
                first_name=teacher_data['first'],
                last_name=teacher_data['last'],
                user_type='teacher',
                phone=f'+23324412{3000+i}',
                school=school
            )
        
        # Create or get teacher
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                'school': school,
                'employee_id': teacher_data['emp_id'],
                'date_of_birth': date(1985 + i, 1 + i % 12, 15),
                'date_of_joining': date(2015 + i % 5, 9, 1),
                'qualification': 'B.Ed in Education'
            }
        )
        
        # Assign subjects
        teacher_subjects = Subject.objects.filter(
            school=school,
            code__in=teacher_data['subjects']
        )
        teacher.subjects.set(teacher_subjects)
        
        teachers.append(teacher)
        if created:
            print_success(f"  Created teacher: {user.get_full_name()} ({username})")
    
    return teachers

def create_students(school, classes):
    """Create students for the school"""
    print_info("Creating students...")
    
    first_names = [
        'Kwame', 'Kofi', 'Kwabena', 'Yaw', 'Akwasi',
        'Akua', 'Ama', 'Abena', 'Yaa', 'Afua',
        'Kwesi', 'Kwadwo', 'Esi', 'Efua', 'Adwoa'
    ]
    
    last_names = [
        'Mensah', 'Asante', 'Boateng', 'Osei', 'Adjei',
        'Owusu', 'Amponsah', 'Darko', 'Appiah', 'Agyeman'
    ]
    
    students = []
    student_num = 1
    
    for cls in classes:
        # Create 8-12 students per class
        num_students = random.randint(8, 12)
        
        for i in range(num_students):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"student{student_num}"
            admission_number = f"RS{date.today().year}{student_num:04d}"
            
            # Create or get user
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.school = school
                user.save()
            else:
                user = User.objects.create_user(
                    username=username,
                    password='password123',
                    email=f"{username}@student.riverside.edu.gh",
                    first_name=first_name,
                    last_name=last_name,
                    user_type='student',
                    phone=f'+23324450{student_num:04d}',
                    school=school
                )
            
            # Create or get student
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'school': school,
                    'admission_number': admission_number,
                    'date_of_birth': date(2010 + random.randint(0, 8), random.randint(1, 12), random.randint(1, 28)),
                    'gender': random.choice(['male', 'female']),
                    'date_of_admission': date(2020 + random.randint(0, 4), 9, 1),
                    'current_class': cls,
                    'roll_number': str(i + 1),
                    'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+']),
                    'emergency_contact': f'+23324460{student_num:04d}'
                }
            )
            
            if not created:
                student.current_class = cls
                student.school = school
                student.save()
            
            students.append(student)
            student_num += 1
    
    print_success(f"  Created {len(students)} students across {len(classes)} classes")
    return students

def create_parents(school, students):
    """Create parents for students"""
    print_info("Creating parents...")
    
    parents_created = 0
    
    # Create parents for first 20 students
    for i, student in enumerate(students[:20]):
        username = f"parent{i+1}"
        
        # Create or get user
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.school = school
            user.save()
        else:
            # Use student's last name for parent
            user = User.objects.create_user(
                username=username,
                password='password123',
                email=f"{username}@riverside.edu.gh",
                first_name=student.user.first_name if i % 2 == 0 else 'Parent',
                last_name=student.user.last_name,
                user_type='parent',
                phone=f'+23324470{i:04d}',
                school=school
            )
        
        # Create or get parent
        parent, created = Parent.objects.get_or_create(
            user=user,
            defaults={
                'school': school,
                'relation': random.choice(['father', 'mother', 'guardian']),
                'occupation': random.choice(['Teacher', 'Doctor', 'Engineer', 'Businessman', 'Nurse'])
            }
        )
        
        # Link to child
        parent.children.add(student)
        
        if created:
            parents_created += 1
    
    print_success(f"  Created {parents_created} parents")
    return parents_created

def create_attendance(school, students, days=30):
    """Create attendance records for the last 30 days"""
    print_info(f"Creating attendance records for last {days} days...")
    
    today = date.today()
    attendance_count = 0
    
    for day_offset in range(days):
        current_date = today - timedelta(days=day_offset)
        
        # Skip weekends
        if current_date.weekday() >= 5:
            continue
        
        for student in students:
            # 90% present, 5% absent, 3% late, 2% excused
            status_choice = random.choices(
                ['present', 'absent', 'late', 'excused'],
                weights=[90, 5, 3, 2]
            )[0]
            
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                date=current_date,
                defaults={
                    'school': school,
                    'status': status_choice,
                    'remarks': '' if status_choice == 'present' else 'Auto-generated test data'
                }
            )
            
            if created:
                attendance_count += 1
    
    print_success(f"  Created {attendance_count} attendance records")
    return attendance_count

def create_grades(school, students, subjects, academic_year):
    """Create grades for students"""
    print_info("Creating grades...")
    
    grades_count = 0
    terms = ['first', 'second', 'third']
    
    for student in students:
        # Select 5-7 random subjects for each student
        student_subjects = random.sample(subjects, random.randint(5, 7))
        
        for subject in student_subjects:
            # Create grades for first and second terms
            for term in terms[:2]:
                # Random scores
                class_score = Decimal(random.uniform(15, 30))  # Out of 30
                exams_score = Decimal(random.uniform(35, 70))  # Out of 70
                
                grade, created = Grade.objects.get_or_create(
                    school=school,
                    student=student,
                    subject=subject,
                    academic_year=academic_year,
                    term=term,
                    defaults={
                        'class_score': class_score,
                        'exams_score': exams_score,
                    }
                )
                
                if created:
                    grades_count += 1
    
    print_success(f"  Created {grades_count} grade records")
    return grades_count

def assign_class_teachers(classes, teachers):
    """Assign class teachers to classes"""
    print_info("Assigning class teachers...")
    
    for i, cls in enumerate(classes):
        if i < len(teachers):
            cls.class_teacher = teachers[i]
            cls.save()
            print_success(f"  Assigned {teachers[i].user.get_full_name()} to {cls.name}")

def main():
    """Main function to load all mock data"""
    print_header("RIVERSIDE SCHOOL MOCK DATA LOADER")
    
    try:
        # 1. Create school
        school = get_or_create_riverside_school()
        
        # 2. Create admin user
        admin_user = create_admin_user(school)
        
        # 3. Create academic year
        academic_year = create_academic_year(school)
        
        # 4. Create subjects
        subjects = create_subjects(school)
        
        # 5. Create classes
        classes = create_classes(school, academic_year)
        
        # 6. Create teachers
        teachers = create_teachers(school, subjects)
        
        # 7. Assign class teachers
        assign_class_teachers(classes, teachers)
        
        # 8. Create students
        students = create_students(school, classes)
        
        # 9. Create parents
        create_parents(school, students)
        
        # 10. Create attendance records
        create_attendance(school, students, days=30)
        
        # 11. Create grades
        create_grades(school, students, subjects, academic_year)
        
        # Print summary
        print_header("SUMMARY")
        print_success(f"School: {school.name}")
        print_success(f"Admin: riverside_admin (password: admin123)")
        print_success(f"Teachers: {len(teachers)} (teacher1-teacher{len(teachers)}, password: password123)")
        print_success(f"Students: {len(students)} (student1-student{len(students)}, password: password123)")
        print_success(f"Parents: ~20 (parent1-parent20, password: password123)")
        print_success(f"Classes: {len(classes)}")
        print_success(f"Subjects: {len(subjects)}")
        print_success(f"Academic Year: {academic_year.name}")
        
        print_header("DONE! You can now login and test the system.")
        print_info("Login URLs:")
        print_info("  Admin Dashboard: http://127.0.0.1:8000/school/admin/")
        print_info("  Django Admin: http://127.0.0.1:8000/admin/")
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
