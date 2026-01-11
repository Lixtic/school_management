from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('my-classes/', views.teacher_classes, name='my_classes'),
    path('schedule/', views.teacher_schedule, name='schedule'),
    path('grades/enter/', views.enter_grades, name='enter_grades'),
    path('get-students/<int:class_id>/', views.get_students, name='get_students'),
    path('duty-roster/', views.print_duty_roster, name='duty_roster'),
    # Exercises
    path('exercises/<int:class_subject_id>/', views.manage_exercises, name='manage_exercises'),
    path('exercises/<int:exercise_id>/scores/', views.enter_exercise_scores, name='enter_exercise_scores'),
    # Search
    path('search/', views.search_students, name='search_students'),
    # Resources
    path('resources/<int:class_subject_id>/', views.class_resources, name='class_resources'),
    path('resources/delete/<int:resource_id>/', views.delete_resource, name='delete_resource'),
]