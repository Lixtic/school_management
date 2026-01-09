from django.contrib import admin
from .models import AcademicYear, Class, Subject, ClassSubject, Activity

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    list_editable = ['is_current']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'class_teacher']
    list_filter = ['academic_year']
    search_fields = ['name']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'subject', 'teacher']
    list_filter = ['class_name', 'subject']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'tag', 'is_active']
    list_filter = ['is_active', 'tag']
    search_fields = ['title', 'summary', 'tag']
    filter_horizontal = ['assigned_staff']