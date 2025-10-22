# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from schools.admin_mixins import SchoolFieldAdminMixin

@admin.register(User)
class CustomUserAdmin(SchoolFieldAdminMixin, UserAdmin):
    list_display = ['username', 'email', 'user_type', 'first_name', 'last_name', 'is_active', 'school']
    list_filter = ['user_type', 'is_active', 'is_staff', 'school']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'address', 'profile_picture', 'school')}),
    )
    
    def get_queryset(self, request):
        """Filter users by school for non-superusers"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        # School admins only see users in their school
        if hasattr(request.user, 'school') and request.user.school:
            return qs.filter(school=request.user.school)
        
        return qs.none()