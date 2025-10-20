import calendar
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from students.models import Student, Attendance
from academics.models import Class
from django.utils import timezone

@login_required
def attendance_calendar_view(request):
    """
    Render the main attendance calendar view.
    Provides a list of classes for filtering.
    """
    classes = Class.objects.all()
    context = {
        'classes': classes,
        'page_title': 'Attendance Calendar'
    }
    return render(request, 'attendance_tracking/attendance_calendar.html', context)

@login_required
def attendance_data(request):
    """
    API endpoint to fetch attendance data for the calendar.
    Filters by year, month, and optionally by class.
    """
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')
    class_id = request.GET.get('class_id')

    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'Start and end dates are required.'}, status=400)

    try:
        start_date = timezone.datetime.fromisoformat(start_date_str.split('T')[0])
        end_date = timezone.datetime.fromisoformat(end_date_str.split('T')[0])
    except ValueError:
        return JsonResponse({'error': 'Invalid date format.'}, status=400)

    # Base query for attendance counts per day
    daily_counts_query = Attendance.objects.filter(
        date__range=[start_date, end_date]
    ).values('date').annotate(
        present_count=Count('id', filter=Q(status='present')),
        absent_count=Count('id', filter=Q(status='absent'))
    ).order_by('date')

    # If a class is selected, filter the query
    if class_id and class_id.isdigit():
        daily_counts_query = daily_counts_query.filter(student__student_class_id=class_id)

    events = []
    for daily_summary in daily_counts_query:
        date = daily_summary['date']
        present = daily_summary['present_count']
        absent = daily_summary['absent_count']
        total = present + absent

        if total > 0:
            present_percentage = (present / total) * 100 if total > 0 else 0
            
            # Determine color based on attendance percentage
            if present_percentage >= 95:
                backgroundColor = '#27ae60' # Green
                borderColor = '#2ecc71'
            elif present_percentage >= 80:
                backgroundColor = '#f39c12' # Orange
                borderColor = '#f1c40f'
            else:
                backgroundColor = '#e74c3c' # Red
                borderColor = '#c0392b'

            events.append({
                'title': f"{present}/{total} Present",
                'start': date.isoformat(),
                'allDay': True,
                'backgroundColor': backgroundColor,
                'borderColor': borderColor,
                'extendedProps': {
                    'present': present,
                    'absent': absent,
                    'total': total,
                    'present_percentage': round(present_percentage, 2),
                    'day_of_week': calendar.day_name[date.weekday()]
                }
            })

    return JsonResponse(events, safe=False)

