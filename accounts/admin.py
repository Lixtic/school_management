# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from schools.admin_mixins import SchoolFieldAdminMixin

@admin.register(User)
class CustomUserAdmin(SchoolFieldAdminMixin, UserAdmin):
    list_display = ['username', 'email', 'user_type', 'first_name', 'last_name', 'is_active']
    list_filter = ['user_type', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'address', 'profile_picture')}),
    )