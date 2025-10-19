# teachers/models.py
from django.db import models
from accounts.models import User

class Teacher(models.Model):
    # Multi-tenant: Link to school
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='teachers', null=True, blank=True)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    qualification = models.CharField(max_length=200)
    subjects = models.ManyToManyField('academics.Subject', blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"