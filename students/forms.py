from django import forms
from django.contrib.auth import get_user_model
from .models import Student
from academics.models import Class
from parents.models import Parent

User = get_user_model()


class StudentRegistrationForm(forms.ModelForm):
    """Form for registering a new student"""
    
    # User account fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    # Student-specific fields
    admission_number = forms.CharField(max_length=20, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], required=True)
    current_class = forms.ModelChoiceField(
        queryset=Class.objects.none(),
        required=True,
        label='Class'
    )
    
    class Meta:
        model = Student
        fields = ['admission_number', 'date_of_birth', 'gender', 'current_class']
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        # Filter by school
        if self.school:
            self.fields['current_class'].queryset = Class.objects.filter(school=self.school)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email
    
    def clean_admission_number(self):
        admission_number = self.cleaned_data.get('admission_number')
        if self.school and Student.objects.filter(admission_number=admission_number, school=self.school).exists():
            raise forms.ValidationError('Admission number already exists in your school.')
        return admission_number
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        student = super().save(commit=False)
        
        # Create user account
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data.get('email', ''),
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            user_type='student',
            phone=self.cleaned_data.get('phone', ''),
            address=self.cleaned_data.get('address', ''),
            school=self.school
        )
        
        student.user = user
        student.school = self.school
        
        # Set required fields with defaults if not provided
        from datetime import date
        student.date_of_admission = date.today()
        student.emergency_contact = self.cleaned_data.get('phone', '')
        
        if commit:
            student.save()
        
        return student


class StudentUpdateForm(forms.ModelForm):
    """Form for updating student information"""
    
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = Student
        fields = ['admission_number', 'date_of_birth', 'gender', 'current_class']
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate user fields
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['address'].initial = self.instance.user.address
        
        # Filter by school
        if self.school:
            self.fields['current_class'].queryset = Class.objects.filter(school=self.school)
    
    def save(self, commit=True):
        student = super().save(commit=False)
        
        # Update user information
        if student.user:
            student.user.first_name = self.cleaned_data['first_name']
            student.user.last_name = self.cleaned_data['last_name']
            student.user.email = self.cleaned_data.get('email', '')
            student.user.phone = self.cleaned_data.get('phone', '')
            student.user.address = self.cleaned_data.get('address', '')
            student.user.save()
        
        if commit:
            student.save()
        
        return student


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
