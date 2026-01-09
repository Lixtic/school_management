from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from accounts import views as account_views

admin.site.site_header = "Daboya Girls Model JHS Administration"
admin.site.site_title = "School Admin"
admin.site.index_title = "Welcome to Girls Model JHS Management System"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', account_views.homepage, name='home'),
    path('', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    path('dashboard/', account_views.dashboard, name='dashboard'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/password/change/done/'
    ), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    path('teachers/', include('teachers.urls')),
    path('students/', include('students.urls')),
    path('parents/', include('parents.urls')),
    path('academics/', include('academics.urls')),
    path('announcements/', include('announcements.urls')),
    path('finance/', include('finance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)