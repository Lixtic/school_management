from datetime import date
import random
import string
from django import forms
from django.utils.text import slugify
from accounts.models import User
from academics.models import Class
from .models import Student


class StudentQuickAddForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label="First name")
    last_name = forms.CharField(max_length=150, label="Last name")
    age = forms.IntegerField(min_value=3, max_value=25, label="Age")
    current_class = forms.ModelChoiceField(queryset=Class.objects.all(), label="Class")

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'age', 'current_class']

    def _generate_username(self, base):
        base_slug = slugify(base).replace('-', '') or 'student'
        candidate = base_slug
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base_slug}{random.randint(1000, 9999)}"
        return candidate

    def _generate_admission_number(self):
        prefix = 'ADM'
        while True:
            suffix = ''.join(random.choices(string.digits, k=4))
            adm_no = f"{prefix}{suffix}"
            if not Student.objects.filter(admission_number=adm_no).exists():
                return adm_no

    def save(self, commit=True):
        first_name = self.cleaned_data['first_name'].strip()
        last_name = self.cleaned_data['last_name'].strip()
        age = self.cleaned_data['age']
        current_class = self.cleaned_data['current_class']

        username = self._generate_username(f"{first_name}.{last_name}")
        email = f"{username}@school.local"
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            user_type='student',
        )
        user.set_unusable_password()
        if commit:
            user.save()

        dob_year = max(1900, date.today().year - age)
        date_of_birth = date(dob_year, 1, 1)

        admission_number = self._generate_admission_number()

        student = Student(
            user=user,
            admission_number=admission_number,
            date_of_birth=date_of_birth,
            gender='male',
            date_of_admission=date.today(),
            current_class=current_class,
            roll_number='',
            blood_group='',
            emergency_contact='N/A',
        )

        if commit:
            student.save()
        return student
