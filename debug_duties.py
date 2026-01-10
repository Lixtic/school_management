
import os
import django
from datetime import date
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.utils import timezone
from teachers.models import Teacher, DutyAssignment
from academics.models import AcademicYear

def check_duties():
    print(f"Current Date: {timezone.now().date()}")
    
    # Check Current Academic Year
    ay = AcademicYear.objects.filter(is_current=True).first()
    print(f"Current Academic Year: {ay}")
    
    if not ay:
        print("No current academic year found!")
        return

    # Fetch a teacher (e.g., 'mahmed')
    teacher = Teacher.objects.filter(user__username='mahmed').first()
    if not teacher:
        print("Teacher 'mahmed' not found. Fetching first available teacher.")
        teacher = Teacher.objects.first()
        if not teacher:
            print("No teachers found in DB.")
            return

    print(f"Checking for teacher: {teacher.user.get_full_name()} ({teacher.user.username})")

    # Simulate logic from views.py
    today = timezone.now().date()
    
    next_duty = DutyAssignment.objects.filter(
        teacher=teacher,
        week__academic_year=ay,
        week__end_date__gte=today
    ).select_related('week').order_by('week__start_date').first()

    if next_duty:
        print(f"✅ Upcoming Duty Found: Week {next_duty.week.week_number} ({next_duty.week.start_date} - {next_duty.week.end_date}) as {next_duty.role}")
    else:
        print("❌ No upcoming duty found.")

    # List all future duties for debug
    future_duties = DutyAssignment.objects.filter(
        teacher=teacher,
        week__academic_year=ay
    ).select_related('week').order_by('week__start_date')
    
    print("\n--- All Duties for this teacher in Current AY ---")
    for duty in future_duties:
        status = "FUTURE" if duty.week.end_date >= today else "PAST"
        print(f"[{status}] Week {duty.week.week_number}: {duty.week.start_date} -> {duty.week.end_date} ({duty.role})")

if __name__ == "__main__":
    check_duties()
