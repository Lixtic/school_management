# teachers/admin.py
from django.contrib import admin, messages
import secrets
from .models import Teacher, DutyWeek, DutyAssignment

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'date_of_joining', 'qualification']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    list_filter = ['date_of_joining']
    filter_horizontal = ['subjects']
    actions = ['reset_teacher_passwords']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

    def reset_teacher_passwords(self, request, queryset):
        """Admin action to generate new passwords for selected teachers."""
        creds = []
        for teacher in queryset.select_related('user'):
            user = teacher.user
            if not user:
                continue
            new_pwd = secrets.token_urlsafe(8)[:10]
            user.set_password(new_pwd)
            user.save(update_fields=['password'])
            creds.append(f"{user.username}: {new_pwd}")

        if creds:
            message = "Reset passwords for {} teacher(s):\n".format(len(creds)) + "\n".join(creds)
            messages.warning(request, message)
        else:
            messages.info(request, "No passwords reset.")

    reset_teacher_passwords.short_description = "Reset passwords (generate random)"

class DutyAssignmentInline(admin.TabularInline):
    model = DutyAssignment
    extra = 1
    autocomplete_fields = ['teacher']

@admin.register(DutyWeek)
class DutyWeekAdmin(admin.ModelAdmin):
    list_display = ('week_number', 'term', 'academic_year', 'start_date', 'end_date')
    list_filter = ('term', 'academic_year')
    inlines = [DutyAssignmentInline]
    ordering = ('academic_year', 'start_date')
