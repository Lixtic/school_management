from django import forms
from .models import SchoolInfo, GalleryImage

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'caption', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class SchoolInfoForm(forms.ModelForm):
    class Meta:
        model = SchoolInfo
        fields = ['name', 'address', 'phone', 'email', 'motto', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'motto': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
