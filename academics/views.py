from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Schedule, Class, ClassSubject
from .auto_scheduler import auto_schedule_all_classes
from django.db.models import Prefetch
from .utils import get_timetable_slots

@login_required
def view_timetable(request):
    """View class schedule for teachers and students"""
    user = request.user
    context = {}
    
    if user.user_type == 'teacher':
        # Get all classes where this teacher teaches
        class_subjects = ClassSubject.objects.filter(
            teacher__user=user
        ).select_related('class_name', 'subject')
        
        # Get schedules for these classes
        schedules = Schedule.objects.filter(
            class_subject__in=class_subjects
        ).select_related(
            'class_subject',
            'class_subject__subject',
            'class_subject__class_name'
        )
        
        time_slots = []
        for slot in get_timetable_slots():
            time_slots.append({
                'start': slot['start'],
                'end': slot['end'],
                'label': slot['label'],
                'classes': {}
            })
        
        # Organize schedules by time slot and day
        for schedule in schedules:
            for slot in time_slots:
                if slot['start'] <= schedule.start_time < slot['end']:
                    day_classes = slot['classes'].setdefault(schedule.day, [])
                    day_classes.append({
                        'subject': schedule.class_subject.subject.name,
                        'class_name': schedule.class_subject.class_name.name
                    })
                    break
        
        # Sort entries for consistent ordering
        for slot in time_slots:
            for day_code in slot['classes']:
                slot['classes'][day_code].sort(key=lambda item: (item['class_name'], item['subject']))
        
        context.update({
            'time_slots': time_slots,
            'days': Schedule.DAYS_OF_WEEK
        })
        template = 'academics/teacher_timetable.html'
        
    elif user.user_type == 'student':
        # Get student's class schedule
        try:
            student = user.student
            if student.current_class:
                schedules = Schedule.objects.filter(
                    class_subject__class_name=student.current_class
                ).select_related('class_subject', 'class_subject__subject', 
                               'class_subject__teacher', 'class_subject__teacher__user')
                context['schedules'] = schedules
                template = 'academics/student_timetable.html'
            else:
                messages.warning(request, 'You are not assigned to any class yet.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    else:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    return render(request, template, context)


@login_required
def class_timetable(request, class_id):
    """View timetable for a specific class"""
    try:
        class_obj = Class.objects.get(id=class_id)
        
        # Check if user has permission to view this class's timetable
        if request.user.user_type == 'teacher':
            if not ClassSubject.objects.filter(
                class_name=class_obj,
                teacher__user=request.user
            ).exists():
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        elif request.user.user_type == 'student':
            if request.user.student.current_class_id != class_id:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        
        schedules = Schedule.objects.filter(
            class_subject__class_name=class_obj
        ).select_related('class_subject', 'class_subject__subject', 
                        'class_subject__teacher', 'class_subject__teacher__user')
        
        # Create timetable grid
        timetable = {}
        for day_code, day_name in Schedule.DAYS_OF_WEEK:
            timetable[day_code] = {i: None for i in range(1, 9)}  # 8 periods per day
        
        # Fill in the timetable
        for schedule in schedules:
            timetable[schedule.day][schedule.period] = {
                'subject': schedule.class_subject.subject.name,
                'teacher': schedule.class_subject.teacher.user.get_full_name(),
                'start_time': schedule.start_time.strftime('%I:%M %p'),
                'end_time': schedule.end_time.strftime('%I:%M %p'),
            }
        
        context = {
            'class': class_obj,
            'timetable': timetable,
            'days': dict(Schedule.DAYS_OF_WEEK),
            'periods': range(1, 9)
        }
        
        return render(request, 'academics/class_timetable.html', context)
        
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('dashboard')


@login_required
def auto_schedule_view(request):
    """Auto generate schedules for all classes"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Only administrators can auto-generate schedules.')
        return redirect('dashboard')
    
    context = {}
    
    if request.method == 'POST':
        try:
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            period_duration = int(request.POST.get('period_duration', 45))
            break_periods = [int(p.strip()) for p in request.POST.get('break_periods', '3,6').split(',')]
            
            success = auto_schedule_all_classes(
                start_time=start_time,
                end_time=end_time,
                period_duration=period_duration,
                break_periods=break_periods
            )
            
            if success:
                messages.success(request, 'Schedules generated successfully!')
                # Get all schedules to display
                context['schedules'] = Schedule.objects.all().select_related(
                    'class_subject',
                    'class_subject__class_name',
                    'class_subject__subject',
                    'class_subject__teacher',
                    'class_subject__teacher__user'
                ).order_by(
                    'class_subject__class_name',
                    'day',
                    'period'
                )
                context['generated'] = True
            else:
                messages.error(request, 'Failed to generate schedules. Please try different parameters.')
            
            # Pass back the form values
            context.update({
                'start_time': start_time,
                'end_time': end_time,
                'period_duration': period_duration,
                'break_periods': ','.join(map(str, break_periods))
            })
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'academics/auto_schedule.html', context)
