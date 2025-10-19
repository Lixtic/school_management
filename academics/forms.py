# academics/forms.py
from django import forms
from .models import AcademicYear, Class, Subject, ClassSubject, Schedule
from teachers.models import Teacher


class AcademicYearForm(forms.ModelForm):
    """Form for creating/editing academic years"""
    
    class Meta:
        model = AcademicYear
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024/2025'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        self.fields['is_current'].widget.attrs.update({'class': 'form-check-input'})
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_current = cleaned_data.get('is_current')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('End date must be after start date.')
        
        # Check if another current year exists
        if is_current and self.school:
            existing_current = AcademicYear.objects.filter(
                school=self.school,
                is_current=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_current.exists():
                raise forms.ValidationError(
                    f'An active academic year already exists: {existing_current.first().name}. '
                    'Please deactivate it first.'
                )
        
        return cleaned_data


class ClassForm(forms.ModelForm):
    """Form for creating/editing classes"""
    
    class_teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Class Teacher'
    )
    
    class Meta:
        model = Class
        fields = ['name', 'academic_year', 'class_teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Grade 5, Form 3'}),
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if self.school:
            # Filter academic years and teachers by school
            self.fields['academic_year'].queryset = AcademicYear.objects.filter(school=self.school)
            self.fields['class_teacher'].queryset = Teacher.objects.filter(school=self.school)


class SubjectForm(forms.ModelForm):
    """Form for creating/editing subjects"""
    
    class Meta:
        model = Subject
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MATH101'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mathematics'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if self.school:
            existing = Subject.objects.filter(
                code=code,
                school=self.school
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError('A subject with this code already exists in your school.')
        
        return code


class ClassSubjectForm(forms.ModelForm):
    """Form for assigning subjects to classes with teachers"""
    
    class Meta:
        model = ClassSubject
        fields = ['class_name', 'subject', 'teacher']
        widgets = {
            'class_name': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if self.school:
            self.fields['class_name'].queryset = Class.objects.filter(school=self.school)
            self.fields['subject'].queryset = Subject.objects.filter(school=self.school)
            self.fields['teacher'].queryset = Teacher.objects.filter(school=self.school)
    
    def clean(self):
        cleaned_data = super().clean()
        class_name = cleaned_data.get('class_name')
        subject = cleaned_data.get('subject')
        
        if class_name and subject:
            existing = ClassSubject.objects.filter(
                class_name=class_name,
                subject=subject,
                school=self.school
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'{subject.name} is already assigned to {class_name.name}'
                )
        
        return cleaned_data


class ScheduleForm(forms.ModelForm):
    """Form for creating class schedules/timetables"""
    
    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]
    
    PERIODS = [(i, f'Period {i}') for i in range(1, 9)]
    
    day = forms.ChoiceField(choices=DAYS, widget=forms.Select(attrs={'class': 'form-select'}))
    period = forms.ChoiceField(choices=PERIODS, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Schedule
        fields = ['class_subject', 'day', 'period', 'start_time', 'end_time']
        widgets = {
            'class_subject': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if self.school:
            self.fields['class_subject'].queryset = ClassSubject.objects.filter(
                school=self.school
            ).select_related('class_name', 'subject', 'teacher')
