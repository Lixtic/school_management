import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from accounts.models import User
from academics.models import Timetable, ClassSubject, Class

def debug_schedules():
    print("--- DEBUGGING TEACHER SCHEDULES ---")
    teachers = User.objects.filter(user_type='teacher')
    print(f"Found {teachers.count()} teachers.")
    
    for teacher in teachers:
        print(f"\nTeacher: {teacher.get_full_name()} (username: {teacher.username})")
        
        # Check assigned subjects
        subjects = ClassSubject.objects.filter(teacher__user=teacher)
        print(f"  Assigned ClassSubjects: {subjects.count()}")
        
        # Check Timetable entries
        entries = Timetable.objects.filter(
            class_subject__teacher__user=teacher,
            class_subject__class_name__academic_year__is_current=True
        ).order_by('day', 'start_time')
        
        print(f"  Timetable Entries: {entries.count()}")
        if entries.exists():
            for entry in entries:
                print(f"    - {entry.get_day_display()} {entry.start_time}: {entry.class_subject.subject.name} ({entry.class_subject.class_name.name})")
        else:
             print("    [NO ENTRIES]")

    print("\n--- CHECKING FOR UNASSIGNED SUBJECTS IN TIMETABLE ---")
    # Find timetable entries where the class_subject has no teacher
    orphan_entries = Timetable.objects.filter(class_subject__teacher__isnull=True)
    print(f"Timetable entries pointing to Subject with NO TEACHER: {orphan_entries.count()}")
    for entry in orphan_entries[:5]: 
        print(f"  - {entry.get_day_display()} {entry.start_time} - {entry.class_subject} (No Teacher Assigned)")

if __name__ == '__main__':
    debug_schedules()