from django.contrib import admin
from django import forms
from django.utils.text import slugify
from datetime import date
from accounts.models import User
from .models import Student, Attendance, Grade

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    class AddStudentForm(forms.ModelForm):
        first_name = forms.CharField(max_length=150)
        last_name = forms.CharField(max_length=150)
        age = forms.IntegerField(min_value=3, max_value=25, help_text="Age in years")

        class Meta:
            model = Student
            fields = ['current_class']

    add_form = AddStudentForm
    add_fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'age', 'current_class'),
        }),
    )
    list_display = ['admission_number', 'get_full_name', 'gender', 'current_class', 'roll_number']
    search_fields = ['admission_number', 'user__first_name', 'user__last_name']
    list_filter = ['current_class', 'date_of_admission', 'gender']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def _generate_username(self, first_name, last_name):
        base = slugify(f"{first_name}.{last_name}") or 'student'
        candidate = base
        idx = 1
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base}{idx}"
            idx += 1
        return candidate

    def _dob_from_age(self, age):
        today = date.today()
        year = today.year - age
        try:
            return date(year, today.month, min(today.day, 28))
        except ValueError:
            return date(year, today.month, 28)

    def save_model(self, request, obj, form, change):
        if change:
            return super().save_model(request, obj, form, change)

        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        age = form.cleaned_data['age']
        current_class = form.cleaned_data['current_class']

        username = self._generate_username(first_name, last_name)
        user = User(username=username, first_name=first_name, last_name=last_name, user_type='student')
        user.set_unusable_password()
        user.save()

        admission_number = f"ADM{user.id:05d}"
        obj.user = user
        obj.admission_number = admission_number
        obj.date_of_birth = self._dob_from_age(age)
        obj.date_of_admission = date.today()
        obj.current_class = current_class
        obj.emergency_contact = obj.emergency_contact or "N/A"
        obj.save()


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