"""
URL configuration for School Admin Dashboard
"""
from django.urls import path
from . import views

app_name = 'school_admin'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Management pages
    path('students/', views.students_management, name='students'),
    path('teachers/', views.teachers_management, name='teachers'),
    path('classes/', views.classes_management, name='classes'),
    path('subjects/', views.subjects_management, name='subjects'),
    
    # Overview pages
    path('attendance/', views.attendance_overview, name='attendance'),
    path('grades/', views.grades_overview, name='grades'),
    
    # Reports and settings
    path('reports/', views.reports, name='reports'),
    path('settings/', views.school_settings, name='settings'),
]
