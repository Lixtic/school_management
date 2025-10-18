from datetime import datetime, timedelta
from django.db import transaction
from academics.models import Schedule, ClassSubject, Class
from typing import List, Dict, Any
import random


def create_time_slots(start_time_str: str, end_time_str: str, period_duration: int) -> List[Dict[str, Any]]:
    """Create time slots based on start time, end time and period duration"""
    start_time = datetime.strptime(start_time_str, '%H:%M').time()
    end_time = datetime.strptime(end_time_str, '%H:%M').time()
    
    # Convert times to datetime for easy arithmetic
    dt = datetime.now()
    current = datetime.combine(dt, start_time)
    end = datetime.combine(dt, end_time)
    
    slots = []
    period = 1
    
    while current + timedelta(minutes=period_duration) <= end:
        slot_end = current + timedelta(minutes=period_duration)
        slots.append({
            'period': period,
            'start_time': current.time(),
            'end_time': slot_end.time()
        })
        current = slot_end
        period += 1
    
    return slots


def check_teacher_conflict(schedule_data: Dict, existing_schedules: List[Schedule]) -> bool:
    """Check if a teacher is already scheduled at this time"""
    for existing in existing_schedules:
        if (existing.day == schedule_data['day'] and
            existing.class_subject.teacher == schedule_data['class_subject'].teacher and
            schedule_data['start_time'] < existing.end_time and
            schedule_data['end_time'] > existing.start_time):
            return True
    return False


def auto_schedule_class(class_obj: Class, time_slots: List[Dict], 
                       break_periods: List[int] = None) -> List[Schedule]:
    """Generate schedule for a single class"""
    if break_periods is None:
        break_periods = []
    
    # Get all subjects for this class
    class_subjects = ClassSubject.objects.filter(class_name=class_obj)
    if not class_subjects.exists():
        return []
    
    # Get existing schedules to check conflicts
    existing_schedules = Schedule.objects.filter(
        class_subject__class_name=class_obj
    )
    
    # Create schedule ensuring:
    # 1. No teacher teaches two classes at once
    # 2. Spread subjects across the week
    # 3. Respect break periods
    schedules = []
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    
    # Create a distribution of subjects based on their weekly frequency
    subject_distribution = []
    for class_subject in class_subjects:
        # Add each subject 4-5 times to ensure good distribution
        frequency = random.randint(4, 5)
        subject_distribution.extend([class_subject] * frequency)
    
    # Shuffle the distribution
    random.shuffle(subject_distribution)
    
    # Assign subjects to time slots
    subject_index = 0
    for day in days:
        for slot in time_slots:
            if slot['period'] in break_periods:
                continue
                
            if subject_index >= len(subject_distribution):
                subject_index = 0
                random.shuffle(subject_distribution)
            
            class_subject = subject_distribution[subject_index]
            
            # Check for teacher conflicts
            schedule_data = {
                'class_subject': class_subject,
                'day': day,
                'period': slot['period'],
                'start_time': slot['start_time'],
                'end_time': slot['end_time']
            }
            
            if not check_teacher_conflict(schedule_data, existing_schedules):
                schedule = Schedule(**schedule_data)
                schedules.append(schedule)
                subject_index += 1
    
    return schedules


def auto_schedule_all_classes(start_time: str, end_time: str, 
                            period_duration: int = 45,
                            break_periods: List[int] = None) -> bool:
    """
    Auto generate schedules for all classes.
    
    Args:
        start_time: School day start time in HH:MM format
        end_time: School day end time in HH:MM format
        period_duration: Duration of each period in minutes
        break_periods: List of period numbers that are breaks
    """
    if break_periods is None:
        break_periods = [3, 6]  # Default breaks after 2nd and 5th periods
    
    try:
        # Generate time slots
        time_slots = create_time_slots(start_time, end_time, period_duration)
        if not time_slots:
            raise ValueError("Could not create valid time slots with given parameters")
        
        # Get all classes
        classes = Class.objects.all()
        
        # Create schedules for each class
        with transaction.atomic():
            # Clear existing schedules
            Schedule.objects.all().delete()
            
            # Generate new schedules
            for class_obj in classes:
                schedules = auto_schedule_class(class_obj, time_slots, break_periods)
                if schedules:
                    Schedule.objects.bulk_create(schedules)
        
        return True
        
    except Exception as e:
        print(f"Error in auto scheduling: {str(e)}")
        return False