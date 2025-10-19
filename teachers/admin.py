# teachers/admin.py
from django.contrib import admin
from .models import Teacher
from schools.admin_mixins import SchoolFieldAdminMixin

@admin.register(Teacher)
class TeacherAdmin(SchoolFieldAdminMixin, admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'date_of_joining', 'qualification']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    list_filter = ['date_of_joining']
    filter_horizontal = ['subjects']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
