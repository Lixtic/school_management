"""
Forms for School Admin Dashboard
Forms for adding staff, students, and parents
"""
from django import forms
from django.contrib.auth import get_user_model
from students.models import Student
from teachers.models import Teacher
from parents.models import Parent
from academics.models import Class, Subject

User = get_user_model()


class AddTeacherForm(forms.ModelForm):
    """Form for adding a new teacher"""
    
    # User fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    # Teacher fields
    employee_id = forms.CharField(max_length=20, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_of_joining = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    qualification = forms.CharField(max_length=200, required=True)
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Teacher
        fields = ['employee_id', 'date_of_birth', 'date_of_joining', 'qualification', 'subjects']
    
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        if school:
            self.fields['subjects'].queryset = Subject.objects.filter(school=school)


class AddStudentForm(forms.ModelForm):
    """Form for adding a new student"""
    
    # User fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    # Student fields
    admission_number = forms.CharField(max_length=20, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=Student.GENDER_CHOICES, required=True)
    date_of_admission = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    current_class = forms.ModelChoiceField(
        queryset=Class.objects.none(),
        required=False
    )
    roll_number = forms.CharField(max_length=10, required=False)
    blood_group = forms.CharField(max_length=5, required=False)
    emergency_contact = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = Student
        fields = [
            'admission_number', 'date_of_birth', 'gender', 'date_of_admission',
            'current_class', 'roll_number', 'blood_group', 'emergency_contact'
        ]
    
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        if school:
            self.fields['current_class'].queryset = Class.objects.filter(school=school)


class AddParentForm(forms.ModelForm):
    """Form for adding a new parent"""
    
    # User fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    # Parent fields
    relation = forms.ChoiceField(choices=Parent.RELATION_CHOICES, required=True)
    occupation = forms.CharField(max_length=100, required=False)
    children = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select the children this parent is associated with"
    )
    
    class Meta:
        model = Parent
        fields = ['relation', 'occupation', 'children']
    
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        if school:
            self.fields['children'].queryset = Student.objects.filter(school=school).select_related('user')
