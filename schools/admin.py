from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subscription_status', 'student_count', 'teacher_count', 'created_at']
    list_filter = ['subscription_status', 'is_active', 'created_at']
    search_fields = ['name', 'email', 'slug']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'student_count', 'teacher_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Branding', {
            'fields': ('logo', 'primary_color', 'secondary_color')
        }),
        ('Administration', {
            'fields': ('admin_user',)
        }),
        ('Subscription', {
            'fields': ('subscription_status', 'trial_end_date', 'subscription_start_date')
        }),
        ('Limits', {
            'fields': ('max_students', 'max_teachers', 'student_count', 'teacher_count')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
