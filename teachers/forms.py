# teachers/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Teacher
from academics.models import Subject

User = get_user_model()


class TeacherRegistrationForm(forms.ModelForm):
    """Form for registering a new teacher"""
    
    # User account fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    # Teacher-specific fields
    employee_id = forms.CharField(max_length=20, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    qualification = forms.CharField(max_length=200, required=False)
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Teacher
        fields = ['employee_id', 'date_of_birth', 'qualification', 'subjects']
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        # Filter subjects by school
        if self.school:
            self.fields['subjects'].queryset = Subject.objects.filter(school=self.school)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if self.school and Teacher.objects.filter(employee_id=employee_id, school=self.school).exists():
            raise forms.ValidationError('Employee ID already exists in your school.')
        return employee_id
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        # Create user account
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            user_type='teacher',
            phone=self.cleaned_data.get('phone', ''),
            address=self.cleaned_data.get('address', ''),
            school=self.school
        )
        
        teacher.user = user
        teacher.school = self.school
        
        if commit:
            teacher.save()
            self.save_m2m()  # Save many-to-many relationships (subjects)
        
        return teacher


class TeacherUpdateForm(forms.ModelForm):
    """Form for updating teacher information"""
    
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = Teacher
        fields = ['employee_id', 'date_of_birth', 'qualification', 'subjects']
    
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
        
        # Filter subjects by school
        if self.school:
            self.fields['subjects'].queryset = Subject.objects.filter(school=self.school)
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        # Update user information
        if teacher.user:
            teacher.user.first_name = self.cleaned_data['first_name']
            teacher.user.last_name = self.cleaned_data['last_name']
            teacher.user.email = self.cleaned_data['email']
            teacher.user.phone = self.cleaned_data.get('phone', '')
            teacher.user.address = self.cleaned_data.get('address', '')
            teacher.user.save()
        
        if commit:
            teacher.save()
            self.save_m2m()
        
        return teacher
