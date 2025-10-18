from django.db import models
from django.core.exceptions import ValidationError

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


class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]
    
    PERIOD_CHOICES = [
        (1, '1st Period'),
        (2, '2nd Period'),
        (3, '3rd Period'),
        (4, '4th Period'),
        (5, '5th Period'),
        (6, '6th Period'),
        (7, '7th Period'),
        (8, '8th Period'),
    ]
    
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    period = models.IntegerField(choices=PERIOD_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def clean(self):
        # Check for time conflicts
        conflicts = Schedule.objects.filter(
            class_subject__class_name=self.class_subject.class_name,
            day=self.day,
        ).exclude(id=self.id)
        
        for schedule in conflicts:
            if (self.start_time <= schedule.end_time and 
                self.end_time >= schedule.start_time):
                raise ValidationError(
                    f'Time conflict with {schedule.class_subject.subject} '
                    f'({schedule.start_time.strftime("%I:%M %p")} - '
                    f'{schedule.end_time.strftime("%I:%M %p")})'
                )
    
    def __str__(self):
        return (f"{self.class_subject} - {self.get_day_display()} "
                f"Period {self.period} ({self.start_time.strftime('%I:%M %p')} - "
                f"{self.end_time.strftime('%I:%M %p')})")
    
    class Meta:
        ordering = ['day', 'period']
        unique_together = ['class_subject', 'day', 'period']