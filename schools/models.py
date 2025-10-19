from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import RegexValidator

User = get_user_model()


class School(models.Model):
    """
    Multi-tenant School model - each school is a separate tenant
    """
    SUBSCRIPTION_STATUS = (
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    )
    
    # Basic Information
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Ghana')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='schools/logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#2563eb', help_text='Hex color code')
    secondary_color = models.CharField(max_length=7, default='#7c3aed', help_text='Hex color code')
    
    # Admin User (School Owner)
    admin_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='owned_schools',
        help_text='Primary admin user for this school'
    )
    
    # Subscription & Status
    subscription_status = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_STATUS, 
        default='trial'
    )
    trial_end_date = models.DateField(null=True, blank=True)
    subscription_start_date = models.DateField(null=True, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Settings
    max_students = models.IntegerField(default=1000, help_text='Maximum students allowed')
    max_teachers = models.IntegerField(default=100, help_text='Maximum teachers allowed')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while School.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def student_count(self):
        return self.student_set.count()
    
    @property
    def teacher_count(self):
        return self.teacher_set.count()
    
    @property
    def is_trial(self):
        return self.subscription_status == 'trial'
    
    @property
    def is_subscription_active(self):
        return self.subscription_status == 'active'
