from django import forms
from django.contrib.auth import get_user_model
from .models import School

User = get_user_model()


class SchoolRegistrationForm(forms.ModelForm):
    """Form for registering a new school"""
    
    # Admin User Fields
    admin_first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admin First Name'})
    )
    admin_last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admin Last Name'})
    )
    admin_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Admin Email'})
    )
    admin_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admin Username'})
    )
    admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    admin_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    class Meta:
        model = School
        fields = ['name', 'email', 'phone', 'address', 'city', 'state', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'School Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+233XXXXXXXXX'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'School Address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Region'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'Ghana'}),
        }
    
    def clean_admin_username(self):
        username = self.cleaned_data.get('admin_username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def clean_admin_email(self):
        email = self.cleaned_data.get('admin_email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('admin_password')
        password_confirm = cleaned_data.get('admin_password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
