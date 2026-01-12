from django.core.management.base import BaseCommand
from django.utils import timezone
from academics.models import Timetable
from announcements.models import Notification
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Check for upcoming classes and notify teachers (45 min and 10 min warnings)'

    def handle(self, *args, **options):
        # Get current time
        now = timezone.now()
        current_date = now.date()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday

        self.stdout.write(f"Checking schedule for day {current_weekday} at {now.time()}...")

        # Get all timetable slots for today
        slots = Timetable.objects.filter(day=current_weekday).select_related('class_subject', 'class_subject__teacher', 'class_subject__subject', 'class_subject__class_name')

        for slot in slots:
            teacher = slot.class_subject.teacher
            # If no teacher assigned to this subject, skip
            if not teacher or not teacher.email:
                continue

            # Calculate start datetime for this slot today
            start_dt = datetime.combine(current_date, slot.start_time)
            
            # Make timezone aware if needed
            if timezone.is_aware(now):
                start_dt = timezone.make_aware(start_dt)

            # Calculate time difference
            # diff > 0 means the class is in the future
            diff = start_dt - now
            minutes_diff = diff.total_seconds() / 60

            # Logic for 45 minute warning (allow window of 40-50 mins)
            # This assumes the script runs at least every 10 minutes
            if 40 <= minutes_diff <= 50:
                self.send_notification(teacher, slot, '45_min', 
                    f"Reminder: You have {slot.class_subject.subject.name} with {slot.class_subject.class_name.name} in 45 minutes ({slot.start_time.strftime('%H:%M')}).")
            
            # Logic for 10 minute warning (allow window of 5-15 mins)
            elif 5 <= minutes_diff <= 15:
                self.send_notification(teacher, slot, '10_min', 
                    f"Hurry up! Your class {slot.class_subject.subject.name} with {slot.class_subject.class_name.name} starts in 10 minutes ({slot.start_time.strftime('%H:%M')}).")

    def send_notification(self, user, slot, alert_type, message):
        # Check if we already sent this specific alert TYPE for this SLOT TODAY
        # We filter by created_at__date to ensure we only look at today's notifications
        already_sent = Notification.objects.filter(
            recipient=user,
            timetable_slot=slot,
            alert_type=alert_type,
            created_at__date=timezone.now().date()
        ).exists()

        if not already_sent:
            Notification.objects.create(
                recipient=user,
                timetable_slot=slot,
                alert_type=alert_type,
                message=message
            )
            self.stdout.write(self.style.SUCCESS(f"Sent {alert_type} alert to {user.get_full_name()}"))
        else:
            # self.stdout.write(f"Skipping {alert_type} for {user} - already sent.")
            pass
