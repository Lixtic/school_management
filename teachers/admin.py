# teachers/admin.py
from django.contrib import admin, messages
from django import forms
from django.utils.text import slugify
from datetime import date
import secrets
from accounts.models import User
from .models import Teacher, DutyWeek, DutyAssignment

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    class AddTeacherForm(forms.ModelForm):
        first_name = forms.CharField(max_length=150)
        last_name = forms.CharField(max_length=150)
        age = forms.IntegerField(min_value=18, max_value=70, help_text="Age in years")

        class Meta:
            model = Teacher
            fields = []

    add_form = AddTeacherForm
    add_fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'age'),
        }),
    )
    list_display = ['employee_id', 'get_full_name', 'date_of_joining', 'qualification']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    list_filter = ['date_of_joining']
    filter_horizontal = ['subjects']
    actions = ['reset_teacher_passwords']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def _generate_username(self, first_name, last_name):
        base = slugify(f"{first_name}.{last_name}") or 'teacher'
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

        username = self._generate_username(first_name, last_name)
        user = User(username=username, first_name=first_name, last_name=last_name, user_type='teacher')
        user.set_unusable_password()
        user.save()

        employee_id = f"T{user.id:05d}"
        obj.user = user
        obj.employee_id = employee_id
        obj.date_of_birth = self._dob_from_age(age)
        obj.date_of_joining = date.today()
        obj.qualification = obj.qualification or "N/A"
        obj.save()

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
