from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('activities/manage/', views.manage_activities, name='manage_activities'),
]
