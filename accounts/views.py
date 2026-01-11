from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import Class, AcademicYear, ClassSubject, Activity, Timetable, GalleryImage
from teachers.models import Teacher, DutyAssignment
from students.models import Student, Attendance
from announcements.models import Announcement
from django.db.models import Q, Count
from django.utils import timezone
import datetime
import json

def homepage(request):
    activities_qs = Activity.objects.filter(is_active=True).order_by('date')[:12]
    activities = [
        {
            'title': a.title,
            'date': a.date,
            'summary': a.summary,
            'tag': a.tag,
        }
        for a in activities_qs
    ]

    # Fallback if no activities in DB
    if not activities:
        today = datetime.date.today()
        activities = [
            {'title': 'STEM Makers Fair', 'date': today + datetime.timedelta(days=5), 'summary': 'Robotics, circuits, and coding demos led by Basic 9 tech club.', 'tag': 'Innovation'},
            {'title': 'Cultural Day Showcase', 'date': today + datetime.timedelta(days=12), 'summary': 'Performances and exhibits celebrating local heritage and arts.', 'tag': 'Community'},
            {'title': 'Reading Marathon', 'date': today + datetime.timedelta(days=20), 'summary': 'Whole-school literacy sprint with parent volunteers and prizes.', 'tag': 'Academics'},
        ]

    highlights = [
        {
            'title': 'Attendance at 98%',
            'detail': 'Consistent daily check-ins across classes.',
            'icon': 'bi-activity'
        },
        {
            'title': 'Clubs growing',
            'detail': 'STEM, Debate, and Arts clubs expanded this term.',
            'icon': 'bi-people'
        },
        {
            'title': 'Parent portal live',
            'detail': 'Guardians follow homework and grades in real time.',
            'icon': 'bi-shield-check'
        },
    ]

    hero_images = GalleryImage.objects.all().order_by('-created_at')[:3]

    return render(request, 'home.html', {
        'activities': activities,
        'highlights': highlights,
        'hero_images': hero_images,
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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


@login_required
def dashboard(request):
    user = request.user
    # Base query without slicing
    base_notices = Announcement.objects.filter(is_active=True).order_by('-created_at')
    
    if user.user_type == 'admin':
        # Admin gets top 5 of all active notices
        notices = base_notices[:5]
        
        # Analytics Data
        
        # 1. Students per Class (Top 5 largest classes)
        # Using current academic year would be precise, but for now simple grouping
        students_per_class = Student.objects.values('current_class__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        chart_labels_classes = [item['current_class__name'] or 'Unassigned' for item in students_per_class]
        chart_data_classes = [item['count'] for item in students_per_class]

        # 2. Daily Attendance (Last 7 days)
        today = timezone.now().date()
        date_7_days_ago = today - datetime.timedelta(days=6)
        
        attendance_stats = Attendance.objects.filter(
            date__gte=date_7_days_ago, 
            status='present'
        ).values('date').annotate(
            present_count=Count('id')
        ).order_by('date')

        # Fill in missing dates with 0
        daily_presence = {}
        for item in attendance_stats:
            daily_presence[item['date']] = item['present_count']
        
        chart_labels_attendance = []
        chart_data_attendance = []
        
        for i in range(7):
            d = date_7_days_ago + datetime.timedelta(days=i)
            chart_labels_attendance.append(d.strftime("%a")) # Mon, Tue...
            chart_data_attendance.append(daily_presence.get(d, 0))

        context = {
            'user': user,
            'notices': notices,
            'chart_labels_classes': json.dumps(chart_labels_classes),
            'chart_data_classes': json.dumps(chart_data_classes),
            'chart_labels_attendance': json.dumps(chart_labels_attendance),
            'chart_data_attendance': json.dumps(chart_data_attendance),
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
        }

        return render(request, 'dashboard/admin_dashboard.html', context)
    elif user.user_type == 'teacher':
        teacher_profile = Teacher.objects.filter(user=user).first()
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            # Fallback to the latest academic year if none is marked current
            current_year = AcademicYear.objects.order_by('-start_date').first()

        class_subjects = ClassSubject.objects.filter(teacher=teacher_profile)
        class_teacher_classes = Class.objects.filter(class_teacher=teacher_profile)

        if current_year:
            class_subjects = class_subjects.filter(class_name__academic_year=current_year)
            class_teacher_classes = class_teacher_classes.filter(academic_year=current_year)

        class_ids = set(class_subjects.values_list('class_name_id', flat=True))
        class_ids.update(class_teacher_classes.values_list('id', flat=True))
        
        # Check for upcoming Duty
        next_duty = None
        current_date_val = timezone.now().date()
        
        if teacher_profile and current_year:
            # Look for duty in current year ending today or in future
            next_duty = DutyAssignment.objects.filter(
                teacher=teacher_profile,
                week__academic_year=current_year,
                week__end_date__gte=current_date_val
            ).select_related('week').order_by('week__start_date').first()
            
            # Debugging (visible in server logs) - REMOVE IN PROD
            # print(f"DEBUG: Teacher={teacher_profile}, Year={current_year}, Date={current_date_val}")
            # print(f"DEBUG: Next Duty Found: {next_duty}")

        # Get Today's Timetable
        today_weekday = timezone.now().weekday()
        todays_classes = Timetable.objects.filter(
            class_subject__teacher=teacher_profile,
            day=today_weekday
        ).select_related('class_subject', 'class_subject__class_name', 'class_subject__subject').order_by('start_time')

        # Calculate Student Count (Restored)
        teacher_students_count = Student.objects.filter(current_class__id__in=class_ids).distinct().count()

        # Filter notices for teacher
        teacher_notices = base_notices.filter(target_audience__in=['all', 'staff', 'teachers'])[:5]

        teacher_context = {
            'user': user,
            'teacher_has_classes': len(class_ids) > 0,
            'teacher_class_count': len(class_ids),
            'total_students_taught': teacher_students_count,
            'notices': teacher_notices,
            'next_duty': next_duty,
            'todays_classes': todays_classes,
        }

        return render(request, 'dashboard/teacher_dashboard.html', teacher_context)
    elif user.user_type == 'student':
        # Redirect to enhanced student dashboard
        return redirect('students:student_dashboard')
    elif user.user_type == 'parent':
        from finance.models import StudentFee
        parent_notices = notices.filter(target_audience__in=['all', 'parents'])
        
        # Calculate fees for all children
        parent_profile = user.parent_profile
        children = parent_profile.children.all()
        
        total_outstanding = 0
        total_paid = 0
        
        for child in children:
            fees = StudentFee.objects.filter(student=child)
            for fee in fees:
                total_outstanding += fee.balance
                total_paid += fee.total_paid

        return render(request, 'dashboard/parent_dashboard.html', {
            'user': user, 
            'notices': parent_notices,
            'children': children,
            'finance_stats': {
                'outstanding': total_outstanding,
                'paid': total_paid
            }
        })
    
    return redirect('login')