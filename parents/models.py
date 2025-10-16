# parents/models.py
from django.db import models
from accounts.models import User

class Parent(models.Model):
    RELATION_CHOICES = (
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    relation = models.CharField(max_length=10, choices=RELATION_CHOICES)
    occupation = models.CharField(max_length=100, blank=True)
    children = models.ManyToManyField('students.Student', related_name='parents')
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_relation_display()})"


class Homework(models.Model):
    class_name = models.ForeignKey('academics.Class', on_delete=models.CASCADE)
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    assigned_by = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='homework/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.class_name} - {self.subject} - {self.title}"
    
    class Meta:
        ordering = ['-assigned_date']