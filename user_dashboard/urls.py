from django.urls import path
from . import views

app_name = 'user_dashboard'

urlpatterns = [
    path('save-layout/', views.save_dashboard_layout, name='save_dashboard_layout'),
]
