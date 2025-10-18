from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
from academics.models import Schedule, ClassSubject
from academics.utils import get_timetable_slots

@login_required
def dashboard(request):
    user = request.user
    
    if user.user_type == 'admin':
        # Get statistics
        from students.models import Student, Attendance
        from teachers.models import Teacher
        from academics.models import Class, Subject
        from django.db.models import Count, Q
        
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_classes = Class.objects.count()
        total_subjects = Subject.objects.count()
        
        # Students by class
        students_by_class = Class.objects.annotate(
            student_count=Count('student')
        ).values('name', 'student_count').order_by('name')
        
        class_names = [c['name'] for c in students_by_class]
        student_counts = [c['student_count'] for c in students_by_class]
        
        # Attendance stats for the last 7 days
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        attendance_data = Attendance.objects.filter(
            date__gte=seven_days_ago
        ).values('date').annotate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        ).order_by('date')
        
        attendance_labels = [str(a['date']) for a in attendance_data]
        present_count = [a['present'] for a in attendance_data]
        absent_count = [a['absent'] for a in attendance_data]
        
        import json
        context = {
            'user': user,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'total_subjects': total_subjects,
            'class_names': json.dumps(class_names),
            'student_counts': json.dumps(student_counts),
            'attendance_labels': json.dumps(attendance_labels),
            'present_count': json.dumps(present_count),
            'absent_count': json.dumps(absent_count),
            'students_by_class': bool(students_by_class),
            'attendance_stats': bool(attendance_data),
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    elif user.user_type == 'teacher':
        from teachers.models import Teacher
        from students.models import Grade, Student
        from django.db.models import Count as DbCount, Avg
        import json
        
        # Determine requested day (defaults to today)
        days = Schedule.DAYS_OF_WEEK
        day_lookup = {code: label for code, label in days}
        requested_day = request.GET.get('day', '').lower()
        if requested_day not in day_lookup:
            requested_day = datetime.now().strftime('%A').lower()
            if requested_day not in day_lookup:
                # Fallback in case today is a weekend
                requested_day = days[0][0]
        selected_day_label = day_lookup.get(requested_day, requested_day.capitalize())

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
        
        # Build time slots from settings configuration
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
        
        # Sort classes within each slot alphabetically for consistency
        for slot in time_slots:
            for day_code in slot['classes']:
                slot['classes'][day_code].sort(key=lambda item: (item['class_name'], item['subject']))
        
        # Get teacher statistics
        try:
            teacher = Teacher.objects.get(user=user)
            # Count students taught by this teacher across all their classes
            from students.models import Student
            students_taught = Student.objects.filter(
                current_class__in=class_subjects.values_list('class_name', flat=True)
            ).distinct().count()
        except:
            teacher = None
            students_taught = 0
        
        total_classes_taught = class_subjects.count()
        total_subjects_taught = class_subjects.values('subject').distinct().count()
        
        # Get grades for students in classes taught by this teacher
        from students.models import Student as StudentModel
        students_in_classes = StudentModel.objects.filter(
            current_class__in=class_subjects.values_list('class_name', flat=True)
        )
        grades_data = Grade.objects.filter(
            student__in=students_in_classes
        )
        
        # Count grades by grade value
        grade_distribution = grades_data.values('grade').annotate(
            count=DbCount('id')
        ).order_by('grade')
        
        grade_labels = [g['grade'] for g in grade_distribution]
        grade_counts = [g['count'] for g in grade_distribution]
        
        # Average marks in subjects taught by this teacher
        subject_performance = grades_data.values('subject__name').annotate(
            avg_marks=Avg('total_score')
        ).order_by('-avg_marks') if grades_data.exists() else []
        
        subject_names = [s['subject__name'] for s in subject_performance]
        avg_marks = [round(s['avg_marks'], 2) if s['avg_marks'] else 0 for s in subject_performance]
        
        context = {
            'user': user,
            'time_slots': time_slots,
            'selected_day': requested_day,
            'selected_day_label': selected_day_label,
            'days': days,
            'students_taught': students_taught,
            'total_classes_taught': total_classes_taught,
            'total_subjects_taught': total_subjects_taught,
            'grade_labels': json.dumps(grade_labels),
            'grade_counts': json.dumps(grade_counts),
            'subject_names': json.dumps(subject_names),
            'avg_marks': json.dumps(avg_marks),
            'has_grades': bool(grade_distribution),
            'has_subjects': bool(subject_performance),
        }
        return render(request, 'dashboard/teacher_dashboard.html', context)
    elif user.user_type == 'student':
        # Redirect to enhanced student dashboard
        return redirect('students:student_dashboard')
    elif user.user_type == 'parent':
        return render(request, 'dashboard/parent_dashboard.html', {'user': user})
    
    return redirect('login')