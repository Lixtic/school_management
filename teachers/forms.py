from django import forms
from academics.models import Resource
from teachers.models import Teacher

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'file', 'link', 'resource_type', 'curriculum']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'resource_type': forms.Select(attrs={'class': 'form-select'}),
            'curriculum': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curriculum'].initial = 'ges_jhs_new'


class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['notification_ahead_minutes']
        widgets = {
            'notification_ahead_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 120, 'step': 5}),
        }


from .models import LessonPlan
from academics.models import Subject, Class

class LessonPlanForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        fields = [
            'week_number', 'subject', 'school_class', 'topic', 
            'objectives', 'teaching_materials', 
            'introduction', 'presentation', 'evaluation', 'homework'
        ]
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'week_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 52}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'teaching_materials': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'introduction': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'presentation': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'evaluation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'homework': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super(LessonPlanForm, self).__init__(*args, **kwargs)
        if self.teacher:
            # Filter subjects if teacher assign to subjects
            if self.teacher.subjects.exists():
                self.fields['subject'].queryset = self.teacher.subjects.all()

