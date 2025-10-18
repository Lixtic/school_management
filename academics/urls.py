from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('timetable/', views.view_timetable, name='view_timetable'),
    path('timetable/class/<int:class_id>/', views.class_timetable, name='class_timetable'),
    path('timetable/auto-schedule/', views.auto_schedule_view, name='auto_schedule'),
]