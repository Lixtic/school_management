from django import forms


class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV file', help_text='CSV file containing student data')
    auto_create_classes = forms.BooleanField(required=False, initial=True, label='Auto-create classes')
    confirm = forms.BooleanField(required=False, initial=False, label='Confirm import (perform writes)')


class GradesCsvUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV file', help_text='CSV file containing grades data')
    update_existing = forms.BooleanField(required=False, initial=True, label='Update existing grades')
    academic_year = forms.ChoiceField(required=True, label='Academic year', help_text='Select target academic year for imported grades')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # populate choices lazily to avoid import-time Django setup issues
        try:
            from academics.models import AcademicYear
            years = list(AcademicYear.objects.all().order_by('-name').values_list('id', 'name'))
            choices = [('', '--- Select ---')] + [(str(y[0]), y[1]) for y in years]
            self.fields['academic_year'].choices = choices
        except Exception:
            # fallback: empty choice until runtime
            self.fields['academic_year'].choices = [('', '--- Select ---')]
        # populate class choices (required)
        try:
            from academics.models import Class as SchoolClass
            classes = list(SchoolClass.objects.all().order_by('name').values_list('id', 'name'))
            class_choices = [('', '--- Select ---')] + [(str(c[0]), c[1]) for c in classes]
            self.fields['class_id'] = forms.ChoiceField(required=True, label='Class', choices=class_choices, help_text='Select class to scope student lookup')
        except Exception:
            self.fields['class_id'] = forms.ChoiceField(required=True, label='Class', choices=[('', '--- Select ---')], help_text='Select class to scope student lookup')
