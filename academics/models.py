from django.db import models
from accounts.models import User

class AcademicYear(models.Model):
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-start_date']


class Class(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Grade 10A", "Grade 9B"
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='managed_classes')
    
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ['name', 'academic_year']


class Activity(models.Model):
    title = models.CharField(max_length=120)
    summary = models.TextField(blank=True)
    date = models.DateField()
    tag = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_activities')
    assigned_staff = models.ManyToManyField(User, blank=True, related_name='assigned_activities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        ordering = ['date', '-created_at']


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassSubject(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.class_name} - {self.subject}"
    
    class Meta:
        unique_together = ['class_name', 'subject']


class Timetable(models.Model):
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, help_text="e.g. Room 101 or Lab A")

    class Meta:
        ordering = ['day', 'start_time']
        verbose_name_plural = "Timetables"

    def __str__(self):
        day_name = self.get_day_display()
        return f"{self.class_subject} on {day_name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"