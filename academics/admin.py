from django.contrib import admin
from .models import AcademicYear, Class, Subject, ClassSubject, Schedule
from schools.admin_mixins import SchoolFieldAdminMixin

@admin.register(AcademicYear)
class AcademicYearAdmin(SchoolFieldAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    list_editable = ['is_current']

@admin.register(Class)
class ClassAdmin(SchoolFieldAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'class_teacher']
    list_filter = ['academic_year']
    search_fields = ['name']

@admin.register(Subject)
class SubjectAdmin(SchoolFieldAdminMixin, admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']

@admin.register(Schedule)
class ScheduleAdmin(SchoolFieldAdminMixin, admin.ModelAdmin):
    list_display = ['class_subject', 'day', 'period', 'start_time', 'end_time']
    list_filter = ['day', 'period', 'class_subject__class_name']
    search_fields = ['class_subject__class_name__name', 'class_subject__subject__name']
    ordering = ['day', 'period', 'start_time']

@admin.register(ClassSubject)
class ClassSubjectAdmin(SchoolFieldAdminMixin, admin.ModelAdmin):
    list_display = ['class_name', 'subject', 'teacher']
    list_filter = ['class_name', 'subject']