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

    def get_deleted_objects(self, objs, request):
        """
        Override to handle missing announcements_notification table during preview.
        """
        from django.db import ProgrammingError, connection
        
        try:
            return super().get_deleted_objects(objs, request)
        except ProgrammingError as e:
            if 'announcements_notification' in str(e):
                # Clear the broken transaction flag so Django can continue
                connection.needs_rollback = False
                
                # Return a simplified preview without checking cascade deletes
                deleted_objects = [f"Timetable #{obj.id}" for obj in objs]
                model_count = {self.model._meta.verbose_name_plural: len(objs)}
                perms_needed = set()
                protected = []
                
                return (deleted_objects, model_count, perms_needed, protected)
            else:
                raise e

    def delete_queryset(self, request, queryset):
        """
        Override bulk delete to handle missing announcements_notification table gracefully.
        """
        from django.db import connection, ProgrammingError
        
        try:
            # Try standard bulk delete first
            queryset.delete()
        except ProgrammingError as e:
            if 'announcements_notification' in str(e):
                # Clear broken transaction state
                connection.needs_rollback = False
                
                # Fallback: Raw SQL delete ignoring cascade to missing table
                ids = list(queryset.values_list('id', flat=True))
                if not ids:
                    return

                with connection.cursor() as cursor:
                    # Format tuple of IDs for SQL IN clause
                    placeholders = ', '.join(['%s'] * len(ids))
                    sql = f"DELETE FROM academics_timetable WHERE id IN ({placeholders})"
                    cursor.execute(sql, ids)
                
                self.message_user(request, f"Successfully deleted {len(ids)} timetables (Force Delete Mode)", level="WARNING")
            else:
                raise e

    def delete_model(self, request, obj):
        """
        Override single instance delete to handle missing announcements_notification table gracefully.
        """
        from django.db import connection, ProgrammingError, transaction
        
        try:
            obj.delete()
        except ProgrammingError as e:
            if 'announcements_notification' in str(e):
                # Clear broken transaction state
                connection.needs_rollback = False
                
                # Fallback: Raw SQL delete within a new savepoint
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM academics_timetable WHERE id = %s", [obj.id])
            else:
                raise e
