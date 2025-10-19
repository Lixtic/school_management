from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    path('register/', views.register_school, name='register'),
    path('profile/', views.school_profile, name='profile'),
]
