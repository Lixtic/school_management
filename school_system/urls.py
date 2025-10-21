from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views
from school_system import search_views

admin.site.site_header = "Daboya Girls Model JHS Administration"
admin.site.site_title = "School Admin"
admin.site.index_title = "Welcome to Girls Model JHS Management System"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.home_view, name='home'),
    path('api/global-search/', search_views.global_search_api, name='global_search_api'),
    path('accounts/', include('accounts.urls')),
    path('schools/', include('schools.urls')),
    path('teachers/', include('teachers.urls')),
    path('students/', include('students.urls')),
    path('parents/', include('parents.urls')),
    path('academics/', include('academics.urls')),
    path('messages/', include('communications.urls')),
    path('attendance/', include('attendance_tracking.urls')),
    path('dashboard-settings/', include('user_dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)