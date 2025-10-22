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
    path('students/add/', views.add_student, name='add_student'),
    
    path('teachers/', views.teachers_management, name='teachers'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    
    path('parents/', views.parents_management, name='parents'),
    path('parents/add/', views.add_parent, name='add_parent'),
    
    path('classes/', views.classes_management, name='classes'),
    path('subjects/', views.subjects_management, name='subjects'),
    
    # Overview pages
    path('attendance/', views.attendance_overview, name='attendance'),
    path('grades/', views.grades_overview, name='grades'),
    
    # Reports and settings
    path('reports/', views.reports, name='reports'),
    path('settings/', views.school_settings, name='settings'),
]

