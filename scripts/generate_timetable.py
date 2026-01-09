import os
import django
import random
import sys
from datetime import time

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from academics.models import ClassSubject, Timetable

def run():
    print("Generating timetable data...")
    
    # Clear existing timetable entries to avoid duplicates
    Timetable.objects.all().delete()
    
    # Time slots
    slots = [
        (time(8, 0), time(9, 0)),
        (time(9, 0), time(10, 0)),
        (time(10, 30), time(11, 30)), # Break between 10-10:30
        (time(11, 30), time(12, 30)),
        (time(13, 30), time(14, 30)), # Lunch between 12:30-1:30
    ]
    
    rooms = ['Room 101', 'Room 102', 'Science Lab', 'Room 103', 'Room 104', 'Library']
    days = [0, 1, 2, 3, 4] # Mon-Fri
    
    class_subjects = ClassSubject.objects.all()
    
    if not class_subjects.exists():
        print("No ClassSubjects found. Please run 'assign_class_subjects.py' first.")
        return

    count = 0
    # Process by class to ensure no clashes for the class
    classes = set(cs.class_name for cs in class_subjects)
    
    for cls in classes:
        # Get subjects for this class
        cs_list = list(ClassSubject.objects.filter(class_name=cls))
        if not cs_list:
            continue
            
        print(f"Generating schedule for {cls}...")
        
        # Simple algorithm: assign subjects to random slots
        # In a real app, this would be complex constraint satisfaction
        
        for day in days:
            daily_slots = list(slots) # 5 slots per day
            random.shuffle(daily_slots)
            
            # Pick 4-5 subjects per day
            daily_subjects = random.sample(cs_list, k=min(len(cs_list), len(daily_slots)))
            
            for i, cs in enumerate(daily_subjects):
                start, end = daily_slots[i]
                
                Timetable.objects.create(
                    class_subject=cs,
                    day=day,
                    start_time=start,
                    end_time=end,
                    room=random.choice(rooms)
                )
                count += 1
                
    print(f"Successfully created {count} timetable entries.")

if __name__ == '__main__':
    run()
