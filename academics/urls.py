from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('activities/manage/', views.manage_activities, name='manage_activities'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gallery/upload/', views.upload_gallery_image, name='upload_gallery_image'),
    path('settings/', views.school_settings_view, name='school_settings'),
    path('timetable/', views.timetable_view, name='timetable'),
]
