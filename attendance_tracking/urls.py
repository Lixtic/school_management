from django.urls import path
from . import views

app_name = 'attendance_tracking'

urlpatterns = [
    path('calendar/', views.attendance_calendar_view, name='calendar_view'),
    path('api/attendance-data/', views.attendance_data, name='attendance_data_api'),
]
