from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta

def home_view(request):
    """Landing page/welcome screen"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

def login_view(request):
    # Redirect to dashboard if already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, 'accounts/home.html')
    
    # If GET request, render home page (which contains the login modal)
    return render(request, 'accounts/home.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
from academics.models import Schedule, ClassSubject
from academics.utils import get_timetable_slots

@login_required
def dashboard(request):
    user = request.user
    
    # Fetch user's widget layout or create default
    from user_dashboard.models import DashboardWidget
    widgets = user.dashboard_widgets.filter(is_visible=True).order_by('order')
    
    if not widgets.exists():
        # Create default layout for the user if none exists
        default_widgets = []
        if user.user_type == 'admin':
            default_widgets = [
                {'type': 'stats_summary', 'order': 0},
                {'type': 'student_distribution', 'order': 1},
                {'type': 'attendance_trend', 'order': 2},
                {'type': 'quick_actions', 'order': 3},
            ]
        # Add default widgets for other user types here...
        
        for w_data in default_widgets:
            DashboardWidget.objects.create(
                user=user,
                widget_type=w_data['type'],
                order=w_data['order'],
                is_visible=True
            )
        widgets = user.dashboard_widgets.filter(is_visible=True).order_by('order')

    context = {'widgets': widgets}

    if user.user_type == 'admin':
        from students.models import Student, Attendance
        from teachers.models import Teacher
        from academics.models import Class, Subject
        from django.db.models import Count, Q
        import json
        from datetime import datetime, timedelta

        school = user.school
        context['total_students'] = Student.objects.filter(school=school).count()
        context['total_teachers'] = Teacher.objects.filter(school=school).count()
        context['total_classes'] = Class.objects.filter(school=school).count()
        context['total_subjects'] = Subject.objects.filter(school=school).count()

        students_by_class = Class.objects.filter(school=school).annotate(
            student_count=Count('student_set')
        ).values('name', 'student_count').order_by('name')
        
        context['class_names'] = json.dumps([c['name'] for c in students_by_class])
        context['student_counts'] = json.dumps([c['student_count'] for c in students_by_class])

        seven_days_ago = datetime.now().date() - timedelta(days=7)
        attendance_data = Attendance.objects.filter(
            student__school=school,
            date__gte=seven_days_ago
        ).values('date').annotate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        ).order_by('date')
        
        context['attendance_labels'] = json.dumps([a['date'].strftime('%Y-%m-%d') for a in attendance_data])
        context['present_count'] = json.dumps([a['present'] for a in attendance_data])
        context['absent_count'] = json.dumps([a['absent'] for a in attendance_data])
        
        return render(request, 'dashboard/admin_dashboard.html', context)
    
    elif user.user_type == 'teacher':
        # ... existing teacher dashboard logic ...
        return render(request, 'dashboard/teacher_dashboard.html', context)
    elif user.user_type == 'student':
        return redirect('students:student_dashboard')
    elif user.user_type == 'parent':
        return render(request, 'dashboard/parent_dashboard.html', context)
    
    return redirect('login')