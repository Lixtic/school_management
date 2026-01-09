from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import Class, AcademicYear, ClassSubject, Activity
from teachers.models import Teacher
import datetime

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

    return render(request, 'home.html', {
        'activities': activities,
        'highlights': highlights,
    })

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


@login_required
def dashboard(request):
    user = request.user
    
    if user.user_type == 'admin':
        return render(request, 'dashboard/admin_dashboard.html', {'user': user})
    elif user.user_type == 'teacher':
        teacher_profile = Teacher.objects.filter(user=user).first()
        current_year = AcademicYear.objects.filter(is_current=True).first()

        class_subjects = ClassSubject.objects.filter(teacher=teacher_profile)
        class_teacher_classes = Class.objects.filter(class_teacher=teacher_profile)

        if current_year:
            class_subjects = class_subjects.filter(class_name__academic_year=current_year)
            class_teacher_classes = class_teacher_classes.filter(academic_year=current_year)

        class_ids = set(class_subjects.values_list('class_name_id', flat=True))
        class_ids.update(class_teacher_classes.values_list('id', flat=True))

        teacher_context = {
            'user': user,
            'teacher_has_classes': len(class_ids) > 0,
            'teacher_class_count': len(class_ids),
        }

        return render(request, 'dashboard/teacher_dashboard.html', teacher_context)
    elif user.user_type == 'student':
        # Redirect to enhanced student dashboard
        return redirect('students:student_dashboard')
    elif user.user_type == 'parent':
        return render(request, 'dashboard/parent_dashboard.html', {'user': user})
    
    return redirect('login')