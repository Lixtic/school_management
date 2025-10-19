from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    # Parent portal views
    path('children/', views.parent_children, name='my_children'),
    path('children/<int:student_id>/', views.child_details, name='child_details'),
    
    # Admin: Parent management
    path('list/', views.parent_list, name='parent_list'),
    path('register/', views.register_parent, name='register_parent'),
    path('update/<int:pk>/', views.update_parent, name='update_parent'),
    path('delete/<int:pk>/', views.delete_parent, name='delete_parent'),
]