from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('my-classes/', views.teacher_classes, name='my_classes'),
    path('grades/enter/', views.enter_grades, name='enter_grades'),
    path('get-students/<int:class_id>/', views.get_students, name='get_students'),
]