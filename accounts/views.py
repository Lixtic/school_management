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

@login_required
def dashboard_router(request):
    """Main dashboard router that redirects users based on their type"""
    user = request.user
    
    if user.user_type == 'admin':
        # Redirect school admins to the dedicated school admin dashboard
        return redirect('school_admin:dashboard')
    elif user.user_type == 'teacher':
        # Redirect to teacher dashboard
        return redirect('accounts:dashboard')
    elif user.user_type == 'student':
        # Redirect to student dashboard
        return redirect('students:student_dashboard')
    elif user.user_type == 'parent':
        # Redirect to parent dashboard
        return redirect('accounts:dashboard')
    else:
        # Fallback to login
        return redirect('login')

from academics.models import Schedule, ClassSubject
from academics.utils import get_timetable_slots

@login_required
def dashboard(request):
    """Dashboard for teachers and parents (non-admin users)"""
    user = request.user
    
    # Admins should not reach this view
    if user.user_type == 'admin':
        return redirect('school_admin:dashboard')
    
    # Fetch user's widget layout or create default
    from user_dashboard.models import DashboardWidget
    widgets = user.dashboard_widgets.filter(is_visible=True).order_by('order')
    
    if not widgets.exists():
        # Create default layout for the user if none exists
        default_widgets = []
        if user.user_type == 'teacher':
            default_widgets = [
                {'type': 'stats_summary', 'order': 0},
                {'type': 'quick_actions', 'order': 1},
            ]
        elif user.user_type == 'parent':
            default_widgets = [
                {'type': 'children_summary', 'order': 0},
                {'type': 'quick_actions', 'order': 1},
            ]
        
        for w_data in default_widgets:
            DashboardWidget.objects.create(
                user=user,
                widget_type=w_data['type'],
                order=w_data['order'],
                is_visible=True
            )
        widgets = user.dashboard_widgets.filter(is_visible=True).order_by('order')

    context = {'widgets': widgets}

    if user.user_type == 'teacher':
        return render(request, 'dashboard/teacher_dashboard.html', context)
    elif user.user_type == 'parent':
        return render(request, 'dashboard/parent_dashboard.html', context)
    
    return redirect('login')