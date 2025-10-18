from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Schedule, Class, ClassSubject

# Existing code...

@login_required
def manage_schedule(request):
    """Add or edit class schedules"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Get form data
            class_subject_id = request.POST.get('class_subject')
            day = request.POST.get('day')
            period = request.POST.get('period')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            
            # Create or update schedule
            class_subject = ClassSubject.objects.get(id=class_subject_id)
            schedule = Schedule(
                class_subject=class_subject,
                day=day,
                period=period,
                start_time=start_time,
                end_time=end_time
            )
            schedule.full_clean()  # This will run validation
            schedule.save()
            messages.success(request, 'Schedule updated successfully.')
            
            # Redirect to timetable view
            return redirect('academics:class_timetable', class_id=class_subject.class_name.id)
            
        except Exception as e:
            messages.error(request, str(e))
            
    # Get form context
    classes = Class.objects.all()
    class_subjects = ClassSubject.objects.select_related('class_name', 'subject', 'teacher')
    
    context = {
        'classes': classes,
        'class_subjects': class_subjects,
        'days': Schedule.DAYS_OF_WEEK,
        'periods': Schedule.PERIOD_CHOICES
    }
    
    return render(request, 'academics/manage_schedule.html', context)