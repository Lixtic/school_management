from django.contrib import admin
from .models import AcademicYear, Class, Subject, ClassSubject, Activity, Timetable, SchoolInfo, GalleryImage

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'caption']

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    list_editable = ['is_current']

@admin.register(SchoolInfo)
class SchoolInfoAdmin(admin.ModelAdmin):
    # Only allow one instance
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True

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


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['class_subject', 'day', 'start_time', 'end_time', 'room']
    list_filter = ['day', 'class_subject__class_name']
    search_fields = ['class_subject__teacher__user__first_name', 'class_subject__teacher__user__last_name', 'room']
