from django.contrib import admin
from .models import Student, Attendance, Grade
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html

from .forms import CsvUploadForm
from .forms import GradesCsvUploadForm
import pandas as pd
import load_sample_data

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'get_full_name', 'gender', 'current_class', 'roll_number']
    search_fields = ['admission_number', 'user__first_name', 'user__last_name']
    list_filter = ['current_class', 'date_of_admission', 'gender']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

    change_list_template = "admin/students/student_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='students_import_csv'),
            path('import-grades/', self.admin_site.admin_view(self.import_grades_view), name='students_import_grades'),
        ]
        return custom_urls + urls

    def import_csv_view(self, request):
        if request.method == 'POST':
            form = CsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                auto_create = form.cleaned_data.get('auto_create_classes', True)
                confirm = form.cleaned_data.get('confirm', False)
                try:
                    df = pd.read_csv(csv_file)
                    # First, run a dry-run preview to show the admin what would
                    # change without writing.
                    preview = load_sample_data.import_students_from_dataframe(df, auto_create_classes=auto_create, dry_run=True)

                    # preview expected shape: (created, updated, created_classes, details)
                    p_created, p_updated, p_created_classes, p_details = (0, 0, [], [])
                    if isinstance(preview, tuple) and len(preview) == 4:
                        p_created, p_updated, p_created_classes, p_details = preview
                    elif isinstance(preview, tuple) and len(preview) == 3:
                        p_created, _, p_details = preview
                        p_updated = 0
                        p_created_classes = []
                    else:
                        try:
                            p_created = preview[0]
                            p_updated = preview[1]
                            p_created_classes = preview[2]
                            p_details = preview[3]
                        except Exception:
                            p_created = p_updated = 0
                            p_created_classes = []
                            p_details = []

                    # If the admin confirmed, perform the real import
                    if confirm:
                        res = load_sample_data.import_students_from_dataframe(df, auto_create_classes=auto_create, dry_run=False)
                        if isinstance(res, tuple) and len(res) == 4:
                            created, updated, created_classes, details = res
                        elif isinstance(res, tuple) and len(res) == 3:
                            created, skipped, details = res
                            updated = 0
                            created_classes = []
                        else:
                            created = res[0] if len(res) > 0 else 0
                            updated = res[1] if len(res) > 1 else 0
                            created_classes = res[2] if len(res) > 2 else []
                            details = res[3] if len(res) > 3 else []

                        context = dict(self.admin_site.each_context(request), created=created, updated=updated, created_classes=created_classes, details=details, confirmed=True)
                        return render(request, 'admin/students/import_csv_result.html', context)

                    # Otherwise show preview results and ask for confirmation
                    context = dict(self.admin_site.each_context(request), preview_created=p_created, preview_updated=p_updated, preview_created_classes=p_created_classes, preview_details=p_details, confirmed=False, form=form)
                    return render(request, 'admin/students/import_csv_result.html', context)
                except Exception as e:
                    messages.error(request, f"Import failed: {e}")
        else:
            form = CsvUploadForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
        )
        return render(request, 'admin/students/import_csv.html', context)

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['import_csv_url'] = 'import-csv/'
        extra_context['import_grades_url'] = 'import-grades/'
        return super().changelist_view(request, extra_context=extra_context)

    def import_grades_view(self, request):
        if request.method == 'POST':
            form = GradesCsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                update_existing = form.cleaned_data.get('update_existing', True)
                academic_year_val = form.cleaned_data.get('academic_year')
                class_id_val = form.cleaned_data.get('class_id') if 'class_id' in form.cleaned_data else None
                if not academic_year_val or not class_id_val:
                    messages.error(request, 'Please select both Academic Year and Class before importing.')
                    return render(request, 'admin/students/import_grades.html', dict(self.admin_site.each_context(request), form=form))
                try:
                    df = pd.read_csv(csv_file)
                    # resolve academic year id if provided
                    ay_obj = None
                    if academic_year_val:
                        from academics.models import AcademicYear
                        try:
                            ay_obj = AcademicYear.objects.filter(id=int(academic_year_val)).first()
                        except Exception:
                            ay_obj = None

                    # resolve class if provided
                    class_obj = None
                    if class_id_val:
                        try:
                            from academics.models import Class as SchoolClass
                            class_obj = SchoolClass.objects.filter(id=int(class_id_val)).first()
                        except Exception:
                            class_obj = None

                    created, updated, skipped, details = load_sample_data.import_grades_from_dataframe(df, academic_year=ay_obj, class_obj=class_obj, update_existing=update_existing, dry_run=False)
                    # collect affected student ids for quick links
                    student_ids = sorted({d.get('student_id') for d in details if d.get('student_id')})
                    context = dict(self.admin_site.each_context(request), created=created, updated=updated, skipped=skipped, details=details, affected_student_ids=student_ids)
                    return render(request, 'admin/students/import_grades_result.html', context)
                except Exception as e:
                    messages.error(request, f"Import failed: {e}")
        else:
            form = GradesCsvUploadForm()
        context = dict(
            self.admin_site.each_context(request),
            form=form,
        )
        return render(request, 'admin/students/import_grades.html', context)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    date_hierarchy = 'date'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'term', 'class_score', 'exams_score', 
                    'total_score', 'grade', 'subject_position', 'remarks']
    list_filter = ['academic_year', 'term', 'subject', 'grade']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    readonly_fields = ['total_score', 'grade', 'remarks', 'subject_position']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'subject', 'academic_year', 'term')
        }),
        ('Scores', {
            'fields': ('class_score', 'exams_score')
        }),
        ('Auto-Calculated Results', {
            'fields': ('total_score', 'grade', 'remarks', 'subject_position'),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        })
    )