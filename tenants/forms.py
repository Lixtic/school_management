import re
from django import forms
from django.core.exceptions import ValidationError
from .models import School, Domain

class SchoolSignupForm(forms.Form):
    school_name = forms.CharField(label="School Name", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kings College'}))
    schema_name = forms.CharField(label="School ID (Subdomain)", max_length=50, help_text="No spaces. e.g. 'kings'", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'kings'}))
    email = forms.EmailField(label="Admin Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'admin@kings.edu'}))
    
    def clean_schema_name(self):
        data = self.cleaned_data['schema_name'].lower().strip()
        
        # Validation checks
        if not re.match(r'^[a-z0-9]+$', data):
            raise ValidationError("School ID must contain only lowercase letters and numbers (no spaces).")
            
        reserved = ['public', 'admin', 'static', 'media', 'accounts', 'school', 'login', 'signup', 'register']
        if data in reserved:
            raise ValidationError(f"'{data}' is a reserved system name.")
            
        if School.objects.filter(schema_name=data).exists():
            raise ValidationError(f"The School ID '{data}' is already taken.")
            
        return data
