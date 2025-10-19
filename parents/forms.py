from django import forms
from django.contrib.auth import get_user_model
from .models import Parent
from students.models import Student

User = get_user_model()


class ParentRegistrationForm(forms.ModelForm):
    """Form for registering a new parent"""
    
    # User fields
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    # Parent fields
    relation = forms.ChoiceField(
        choices=Parent.RELATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    occupation = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter occupation (optional)'
        })
    )
    
    # Children selection
    children = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select the children this parent is responsible for"
    )
    
    class Meta:
        model = Parent
        fields = ['relation', 'occupation']
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        
        # Filter children by school
        if school:
            self.fields['children'].queryset = Student.objects.filter(school=school).select_related('user')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        # Create user account
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone=self.cleaned_data['phone'],
            user_type='parent',
            school=self.school
        )
        
        # Create parent profile
        parent = super().save(commit=False)
        parent.user = user
        parent.school = self.school
        
        if commit:
            parent.save()
            # Set children
            parent.children.set(self.cleaned_data['children'])
        
        return parent


class ParentUpdateForm(forms.ModelForm):
    """Form for updating parent information"""
    
    # User fields
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )
    
    # Parent fields
    relation = forms.ChoiceField(
        choices=Parent.RELATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    occupation = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter occupation (optional)'
        })
    )
    
    # Children selection
    children = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select the children this parent is responsible for"
    )
    
    class Meta:
        model = Parent
        fields = ['relation', 'occupation']
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        
        # Filter children by school
        if school:
            self.fields['children'].queryset = Student.objects.filter(school=school).select_related('user')
        
        # Populate user fields from instance
        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['children'].initial = self.instance.children.all()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Exclude current user from uniqueness check
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        # Update user account
        user = self.instance.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        
        if commit:
            user.save()
        
        # Update parent profile
        parent = super().save(commit=commit)
        
        if commit:
            # Update children
            parent.children.set(self.cleaned_data['children'])
        
        return parent
