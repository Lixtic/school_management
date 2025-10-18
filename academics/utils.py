from datetime import datetime
from django.conf import settings

_DEFAULT_TIMETABLE_SLOTS = [
    ("07:00", "08:30"),
    ("08:30", "09:45"),
    ("09:45", "10:30"),
    ("10:30", "11:30"),
    ("11:30", "13:00"),
]


def get_timetable_slots():
    """Return configured time slots parsed into time objects."""
    configured_slots = getattr(settings, "TIMETABLE_TIME_SLOTS", _DEFAULT_TIMETABLE_SLOTS)
    slots = []
    for start_str, end_str in configured_slots:
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()
        slots.append({
            "start": start_time,
            "end": end_time,
            "label": f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        })
    return slots
