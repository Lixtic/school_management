import os
import sys
import django
import random
from datetime import date, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.db import connection, transaction
from tenants.models import School

def populate_tenant(schema_name='school1'):
    print(f"🔄 Switching to tenant: {schema_name}")
    
    try:
        tenant = School.objects.get(schema_name=schema_name)
    except School.DoesNotExist:
        print(f"❌ Tenant '{schema_name}' not found!")
        return

    connection.set_tenant(tenant)
    print(f"✅ Context switched to {tenant.name} ({schema_name})")

    # Import models AFTER switching tenant (safer for some signals)
    from accounts.models import User
    from academics.models import AcademicYear, Class, Subject, ClassSubject, SchoolInfo, Timetable
    from students.models import Student, Attendance, Grade
    from teachers.models import Teacher
    from parents.models import Parent
    from finance.models import FeeHead, FeeStructure, StudentFee, Payment
    from announcements.models import Announcement

    print("🚀 Starting to load sample data...")

    # Create School Info
    print("\n🏫 Configuring School Info...")
    info, created = SchoolInfo.objects.get_or_create(
        id=1,
        defaults={
            'name': tenant.name, # Use tenant name
            'address': "P.O. Box 77, Kumasi, Ghana",
            'phone': "+233 24 000 0000",
            'email': f"info@{schema_name}.com",
            'motto': "Knowledge, Character & Service"
        }
    )

    # Create Academic Year
    print("\n📅 Creating Academic Year...")
    ay, created = AcademicYear.objects.get_or_create(
        name="2025-2026",
        defaults={
            'start_date': date(2025, 9, 2),
            'end_date': date(2026, 6, 30),
            'is_current': True
        }
    )

    # Create Classes
    print("\nclassroom Creating Classes...")
    classes = ['JHS 1', 'JHS 2', 'JHS 3']
    created_classes = []
    
    # Check if classes exist first
    if not Class.objects.exists():
        for i, c_name in enumerate(classes):
            c = Class.objects.create(name=c_name, order=i+1)
            created_classes.append(c)
        print(f"✅ Created {len(created_classes)} classes")
    else:
        created_classes = list(Class.objects.all())
        print(f"ℹ️  Using {len(created_classes)} existing classes")

    # Create Subjects
    print("\n📚 Creating Subjects...")
    subjects_list = [
        ('Mathematics', 'MATH'), ('English Language', 'ENG'), 
        ('Integrated Science', 'SCI'), ('Social Studies', 'SOC'),
        ('I.C.T', 'ICT'), ('R.M.E', 'RME'), ('French', 'FRE'),
        ('B.D.T', 'BDT')
    ]
    created_subjects = []
    if not Subject.objects.exists():
        for name, code in subjects_list:
            s_obj = Subject.objects.create(name=name, code=code)
            created_subjects.append(s_obj)
        print(f"✅ Created {len(created_subjects)} subjects")
    else:
        created_subjects = list(Subject.objects.all())

    # Create Teachers (Users + Profiles)
    print("\n👨‍🏫 Creating Teachers...")
    teachers = []
    if not Teacher.objects.exists():
        for i in range(1, 6):
            username = f'teacher{i}'
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(
                    username=username, password='password123', 
                    user_type='teacher', email=f'{username}@{schema_name}.com',
                    first_name=f"Teacher", last_name=f"{i}"
                )
                t = Teacher.objects.create(
                    user=u, 
                    staff_id=f"STF{202400+i}",
                    phone=f"024400000{i}"
                )
                teachers.append(t)
        print(f"✅ Created {len(teachers)} teachers")
    else:
        teachers = list(Teacher.objects.all())
    
    # Assign Subjects to Classes (Curriculum)
    print("\n🔗 Assigning Subjects to Class...")
    if not ClassSubject.objects.exists() and teachers:
        for c in created_classes:
            for s in created_subjects:
                # Random teacher assignment
                t = random.choice(teachers)
                ClassSubject.objects.create(
                    class_related=c,
                    subject=s,
                    teacher=t,
                    academic_year=ay
                )
        print("✅ Assigned subjects to classes")

    # Create Students
    print("\n🎓 Creating Students...")
    if not Student.objects.exists():
        for i, c in enumerate(created_classes):
            # Create 5 students per class
            for j in range(1, 6):
                s_num = (i * 5) + j
                username = f'student{s_num}'
                if not User.objects.filter(username=username).exists():
                    u = User.objects.create_user(
                        username=username, password='password123',
                        user_type='student', email=f'{username}@{schema_name}.com',
                        first_name=f"Student", last_name=f"{s_num}"
                    )
                    s = Student.objects.create(
                        user=u,
                        student_id=f"STD{202400+s_num}",
                        current_class=c,
                        date_of_birth=date(2010, 1, 1),
                        gender=random.choice(['Male', 'Female']),
                        father_name=f"Parent {s_num}", # Simplify parent logic for now
                        father_phone="0200000000"
                    )
        print("✅ Created sample students")

    print("\n✨ Tenant Population Complete!")

if __name__ == '__main__':
    # Default to school1 if no arg provided
    target_schema = sys.argv[1] if len(sys.argv) > 1 else 'school1'
    populate_tenant(target_schema)
