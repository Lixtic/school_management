from django.db import models
from accounts.models import User

class Announcement(models.Model):
    TARGET_CHOICES = (
        ('all', 'All Users'),
        ('staff', 'Staff Only (Admin & Teachers)'),
        ('teachers', 'Teachers Only'),
        ('students', 'Students Only'),
        ('parents', 'Parents Only'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
