from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    path('children/', views.parent_children, name='my_children'),
    path('children/<int:student_id>/', views.child_details, name='child_details'),
]