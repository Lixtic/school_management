from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Timetable views
    path('timetable/', views.view_timetable, name='view_timetable'),
    path('timetable/class/<int:class_id>/', views.class_timetable, name='class_timetable'),
    path('timetable/auto-schedule/', views.auto_schedule_view, name='auto_schedule'),
    
    # Academic Year Management
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/create/', views.create_academic_year, name='create_academic_year'),
    path('academic-years/update/<int:pk>/', views.update_academic_year, name='update_academic_year'),
    path('academic-years/delete/<int:pk>/', views.delete_academic_year, name='delete_academic_year'),
    
    # Class Management
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.create_class, name='create_class'),
    path('classes/update/<int:pk>/', views.update_class, name='update_class'),
    path('classes/delete/<int:pk>/', views.delete_class, name='delete_class'),
    
    # Subject Management
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.create_subject, name='create_subject'),
    path('subjects/update/<int:pk>/', views.update_subject, name='update_subject'),
    path('subjects/delete/<int:pk>/', views.delete_subject, name='delete_subject'),
]