from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('my-classes/', views.my_classes, name='my_classes'),
    path('grades/enter/', views.enter_grades, name='enter_grades'),
    path('get-students/<int:class_id>/', views.get_students, name='get_students'),
    path('grades/import/', views.import_grades_csv, name='import_grades_csv'),
    
    # Teacher management (admin only)
    path('register/', views.register_teacher, name='register'),
    path('list/', views.teacher_list, name='list'),
    path('update/<int:teacher_id>/', views.update_teacher, name='update'),
    path('delete/<int:teacher_id>/', views.delete_teacher, name='delete'),
]