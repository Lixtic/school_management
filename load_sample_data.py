import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from accounts.models import User
from academics.models import AcademicYear, Class, Subject, ClassSubject
from students.models import Student, Attendance, Grade
from teachers.models import Teacher
from parents.models import Parent

print("🚀 Starting to load sample data...")

# Create Academic Year
print("\n📅 Creating Academic Year...")
ay, created = AcademicYear.objects.get_or_create(
    name="2024-2025",
    defaults={
        'start_date': date(2024, 9, 1),
        'end_date': date(2025, 6, 30),
        'is_current': True
    }
)
if created:
    print(f"✅ Created Academic Year: {ay.name}")
else:
    print(f"ℹ️  Academic Year already exists: {ay.name}")

# Create Subjects
print("\n📚 Creating Subjects...")
subjects_data = [
    ("MATH", "Mathematics"),
    ("ENG", "English Language"),
    ("SCI", "Integrated Science"),
    ("SOC", "Social Studies"),
    ("RME", "Religious & Moral Education"),
    ("CCA", "Creative Arts"),
    ("ICT", "ICT"),
    ("PHE", "Physical Education"),
]

subjects = {}
for code, name in subjects_data:
    subj, created = Subject.objects.get_or_create(
        code=code,
        defaults={'name': name}
    )
    subjects[code] = subj
    if created:
        print(f"✅ Created Subject: {name}")
    else:
        print(f"ℹ️  Subject already exists: {name}")

# Create Classes
print("\n🏫 Creating Classes...")
classes_data = [
    "JHS 1A",
    "JHS 1B",
    "JHS 2A",
    "JHS 2B",
    "JHS 3A",
]

classes = {}
for class_name in classes_data:
    cls, created = Class.objects.get_or_create(
        name=class_name,
        academic_year=ay
    )
    classes[class_name] = cls
    if created:
        print(f"✅ Created Class: {class_name}")
    else:
        print(f"ℹ️  Class already exists: {class_name}")

# Create Teachers
print("\n👨‍🏫 Creating Teachers...")
teachers_data = [
    ("teacher1", "Kwame", "Mensah", "kwame.mensah@school.com", "T001", "Mathematics & Science"),
    ("teacher2", "Akosua", "Boateng", "akosua.boateng@school.com", "T002", "English & Social Studies"),
    ("teacher3", "Kofi", "Asante", "kofi.asante@school.com", "T003", "ICT & Creative Arts"),
]

teachers = {}
for username, fname, lname, email, emp_id, qual in teachers_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': fname,
            'last_name': lname,
            'email': email,
            'user_type': 'teacher',
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"✅ Created Teacher User: {username}")
    
    teacher, created = Teacher.objects.get_or_create(
        user=user,
        defaults={
            'employee_id': emp_id,
            'date_of_birth': date(1985, 5, 15),
            'date_of_joining': date(2020, 8, 1),
            'qualification': qual
        }
    )
    teachers[username] = teacher
    if created:
        print(f"✅ Created Teacher Profile: {fname} {lname}")

# Assign subjects to teachers
teachers['teacher1'].subjects.add(subjects['MATH'], subjects['SCI'])
teachers['teacher2'].subjects.add(subjects['ENG'], subjects['SOC'])
teachers['teacher3'].subjects.add(subjects['ICT'], subjects['CCA'])

# Create Class Subjects (assign teachers to teach subjects in classes)
print("\n📖 Assigning Teachers to Classes...")
class_subject_assignments = [
    (classes['JHS 1A'], subjects['MATH'], teachers['teacher1']),
    (classes['JHS 1A'], subjects['ENG'], teachers['teacher2']),
    (classes['JHS 1A'], subjects['SCI'], teachers['teacher1']),
    (classes['JHS 1B'], subjects['MATH'], teachers['teacher1']),
    (classes['JHS 1B'], subjects['ENG'], teachers['teacher2']),
    (classes['JHS 2A'], subjects['ICT'], teachers['teacher3']),
]

for cls, subj, teacher in class_subject_assignments:
    cs, created = ClassSubject.objects.get_or_create(
        class_name=cls,
        subject=subj,
        defaults={'teacher': teacher}
    )
    if created:
        print(f"✅ Assigned {teacher.user.get_full_name()} to teach {subj.name} in {cls.name}")

# Create Students
print("\n👨‍🎓 Creating Students...")
students_data = [
    ("student1", "Ama", "Owusu", "ama.owusu@email.com", "S001", "JHS 1A", "101", "female"),
    ("student2", "Kwabena", "Osei", "kwabena.osei@email.com", "S002", "JHS 1A", "102", "male"),
    ("student3", "Abena", "Agyeman", "abena.agyeman@email.com", "S003", "JHS 1A", "103", "female"),
    ("student4", "Yaw", "Appiah", "yaw.appiah@email.com", "S004", "JHS 1A", "104", "male"),
    ("student5", "Efua", "Nkrumah", "efua.nkrumah@email.com", "S005", "JHS 1B", "105", "female"),
    ("student6", "Kofi", "Danquah", "kofi.danquah@email.com", "S006", "JHS 1B", "106", "male"),
    ("student7", "Adwoa", "Mensah", "adwoa.mensah@email.com", "S007", "JHS 2A", "201", "female"),
    ("student8", "Kwame", "Boakye", "kwame.boakye@email.com", "S008", "JHS 2A", "202", "male"),
]

students = {}
for username, fname, lname, email, adm_no, class_key, roll, gender in students_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': fname,
            'last_name': lname,
            'email': email,
            'user_type': 'student',
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"✅ Created Student User: {username}")
    
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            'admission_number': adm_no,
            'date_of_birth': date(2010, 3, 10),
            'gender': gender,
            'date_of_admission': date(2023, 9, 1),
            'current_class': classes[class_key],
            'roll_number': roll,
            'emergency_contact': "+233244567890"
        }
    )
    students[username] = student
    if created:
        print(f"✅ Created Student Profile: {fname} {lname} - {class_key}")

# Create Sample Grades
print("\n📊 Creating Sample Grades...")
sample_grades = [
    (students['student1'], subjects['MATH'], 25, 60),  # Class work, Exams
    (students['student1'], subjects['ENG'], 28, 65),
    (students['student1'], subjects['SCI'], 22, 55),
    (students['student2'], subjects['MATH'], 20, 50),
    (students['student2'], subjects['ENG'], 23, 58),
    (students['student3'], subjects['MATH'], 27, 68),
    (students['student3'], subjects['ENG'], 29, 70),
]

for student, subject, class_score, exam_score in sample_grades:
    grade, created = Grade.objects.get_or_create(
        student=student,
        subject=subject,
        academic_year=ay,
        term='first',
        defaults={
            'class_score': class_score,
            'exams_score': exam_score,
        }
    )
    if created:
        print(f"✅ Created Grade: {student.user.get_full_name()} - {subject.name} - Total: {grade.total_score}")

# Create Sample Attendance
print("\n📅 Creating Sample Attendance...")
today = date.today()
for i in range(10):
    attendance_date = today - timedelta(days=i)
    for student in [students['student1'], students['student2'], students['student3']]:
        status = 'present' if i < 8 else 'absent'  # 8 present, 2 absent
        att, created = Attendance.objects.get_or_create(
            student=student,
            date=attendance_date,
            defaults={
                'status': status,
                'marked_by': User.objects.filter(user_type='admin').first()
            }
        )
        if created and i == 0:  # Only print for first day
            print(f"✅ Created Attendance for {student.user.get_full_name()}")

# Create Parents
print("\n👨‍👩‍👧 Creating Parents...")
parents_data = [
    ("parent1", "Samuel", "Owusu", "samuel.owusu@email.com", "father", ["student1"]),
    ("parent2", "Grace", "Osei", "grace.osei@email.com", "mother", ["student2"]),
    ("parent3", "Joseph", "Agyeman", "joseph.agyeman@email.com", "father", ["student3"]),
]

for username, fname, lname, email, relation, child_usernames in parents_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': fname,
            'last_name': lname,
            'email': email,
            'user_type': 'parent',
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"✅ Created Parent User: {username}")
    
    parent, created = Parent.objects.get_or_create(
        user=user,
        defaults={
            'relation': relation,
            'occupation': 'Business Person'
        }
    )
    
    # Link children
    for child_username in child_usernames:
        if child_username in students:
            parent.children.add(students[child_username])
    
    if created:
        print(f"✅ Created Parent Profile: {fname} {lname}")

print("\n" + "="*60)
print("🎉 SAMPLE DATA LOADED SUCCESSFULLY!")
print("="*60)
print("\n📋 LOGIN CREDENTIALS:")
print("\n🔐 Admin:")
print("   Username: admin")
print("   Password: admin123")
print("\n👨‍🏫 Teachers:")
print("   Username: teacher1 / teacher2 / teacher3")
print("   Password: password123")
print("\n👨‍🎓 Students:")
print("   Username: student1 / student2 / student3 / etc.")
print("   Password: password123")
print("\n👨‍👩‍👧 Parents:")
print("   Username: parent1 / parent2 / parent3")
print("   Password: password123")
print("\n" + "="*60)
print("✅ You can now login and test the system!")
print("="*60)