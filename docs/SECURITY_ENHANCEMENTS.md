# Security Enhancement Recommendations

## 1. Add Security Middleware & Headers

### Install django-csp and django-axes
```bash
pip install django-csp django-axes
```

### Update settings.py
```python
INSTALLED_APPS = [
    ...
    'axes',  # Brute-force protection
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'axes.middleware.AxesMiddleware',  # Must be after SecurityMiddleware
    ...
]

# django-axes configuration (brute-force protection)
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1  # Lock for 1 hour
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ACCESS_FAILURE_LOG = True
AXES_LOCKOUT_TEMPLATE = 'errors/account_locked.html'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # AxesStandaloneBackend should be first
    'django.contrib.auth.backends.ModelBackend',
]
```

## 2. Implement Rate Limiting

### Install django-ratelimit
```bash
pip install django-ratelimit
```

### Apply rate limiting to sensitive views
```python
# accounts/views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')  # 5 attempts per minute
def login_view(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Too many login attempts. Please try again later.')
        return render(request, 'accounts/login.html')
    
    # ... rest of login logic

@ratelimit(key='user_or_ip', rate='10/h', method='POST')
def send_message(request):
    # Prevent message spam
    pass

@ratelimit(key='ip', rate='3/h', method='POST')
def password_reset(request):
    # Prevent password reset abuse
    pass
```

## 3. Add CSRF Token Validation

### Ensure all forms have CSRF protection
```html
<!-- All POST forms must include {% csrf_token %} -->
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>

<!-- For AJAX requests -->
<script>
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
</script>
```

## 4. Input Validation & Sanitization

### Add model-level validation
```python
# students/models.py
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError

class Grade(models.Model):
    class_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(0, message='Score cannot be negative'),
            MaxValueValidator(30, message='Class score cannot exceed 30')
        ]
    )
    
    exams_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(0, message='Score cannot be negative'),
            MaxValueValidator(70, message='Exam score cannot exceed 70')
        ]
    )
    
    def clean(self):
        super().clean()
        if self.class_score + self.exams_score > 100:
            raise ValidationError('Total score cannot exceed 100')

class Student(models.Model):
    admission_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9-]+$',
                message='Admission number must contain only uppercase letters, numbers, and hyphens'
            )
        ]
    )
    
    emergency_contact = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Enter a valid phone number'
            )
        ]
    )
```

### Add form-level validation
```python
# students/forms.py
from django import forms
from .models import Student
import bleach

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['admission_number', 'date_of_birth', 'emergency_contact']
    
    def clean_admission_number(self):
        admission_number = self.cleaned_data.get('admission_number')
        # Sanitize input
        admission_number = bleach.clean(admission_number, strip=True)
        # Additional validation
        if Student.objects.filter(
            admission_number=admission_number
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This admission number is already in use.')
        return admission_number.upper()
    
    def clean_emergency_contact(self):
        contact = self.cleaned_data.get('emergency_contact')
        # Remove any non-numeric characters except +
        contact = ''.join(c for c in contact if c.isdigit() or c == '+')
        return contact
```

## 5. Implement Object-Level Permissions

### Create permission checking utilities
```python
# school_system/permissions.py
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

def check_school_access(user, obj):
    """
    Verify user can access object from their school
    """
    if user.is_superuser:
        return True
    
    if not hasattr(obj, 'school'):
        return True
    
    if obj.school != user.school:
        raise PermissionDenied('You do not have permission to access this resource.')
    
    return True

def check_user_type_permission(user, allowed_types):
    """
    Check if user type is in allowed list
    """
    if user.is_superuser:
        return True
    
    if user.user_type not in allowed_types:
        raise PermissionDenied(
            f'This action requires {" or ".join(allowed_types)} privileges.'
        )
    
    return True

# Usage in views
@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Check permissions
    check_school_access(request.user, student)
    check_user_type_permission(request.user, ['admin', 'teacher'])
    
    # ... rest of view logic
```

## 6. Secure File Uploads

### Validate file types and sizes
```python
# accounts/models.py
from django.core.validators import FileExtensionValidator

def validate_image_size(image):
    from django.conf import settings
    max_size = getattr(settings, 'MAX_PROFILE_PICTURE_SIZE', 2 * 1024 * 1024)  # 2MB
    
    if image.size > max_size:
        raise ValidationError(
            f'Image file too large ( > {max_size // (1024*1024)}MB )'
        )

class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
            ),
            validate_image_size,
        ]
    )
```

### Sanitize uploaded filenames
```python
# school_system/utils.py
import os
import uuid
from django.utils.text import slugify

def safe_filename(instance, filename):
    """Generate safe filename for uploads"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads', filename)

# In model
class Document(models.Model):
    file = models.FileField(upload_to=safe_filename)
```

## 7. SQL Injection Prevention

### Always use ORM, never raw SQL
```python
# BAD - Vulnerable to SQL injection
def search_students(request):
    query = request.GET.get('q')
    students = Student.objects.raw(
        f"SELECT * FROM students WHERE name LIKE '%{query}%'"
    )

# GOOD - Use ORM
def search_students(request):
    query = request.GET.get('q', '')
    students = Student.objects.filter(
        user__first_name__icontains=query
    ) | Student.objects.filter(
        user__last_name__icontains=query
    )

# If you MUST use raw SQL, use parameterized queries
def advanced_search(request):
    query = request.GET.get('q')
    students = Student.objects.raw(
        "SELECT * FROM students WHERE name LIKE %s",
        [f'%{query}%']  # Parameterized
    )
```

## 8. Add Security Audit Logging

### Create audit log model
```python
# schools/models.py
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('failed_login', 'Failed Login'),
        ('permission_denied', 'Permission Denied'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

# Create audit log utility
def log_audit(user, action, request, model_name='', object_id=None, details=None):
    """Create audit log entry"""
    AuditLog.objects.create(
        user=user if user.is_authenticated else None,
        action=action,
        model_name=model_name,
        object_id=object_id,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        details=details or {}
    )

def get_client_ip(request):
    """Get real IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

## 9. Implement Two-Factor Authentication (2FA)

### Install django-otp
```bash
pip install django-otp qrcode
```

### Configure 2FA
```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

MIDDLEWARE = [
    ...
    'django_otp.middleware.OTPMiddleware',
]

# Optional: Require 2FA for admins
OTP_LOGIN_URL = '/accounts/2fa/'
```

## 10. Security Checklist

### Production Security Checklist:
- [ ] DEBUG = False in production
- [ ] SECRET_KEY is random and not in version control
- [ ] ALLOWED_HOSTS is properly configured
- [ ] HTTPS enforced (SECURE_SSL_REDIRECT = True)
- [ ] CSRF protection enabled
- [ ] All forms use {% csrf_token %}
- [ ] Secure cookies (SECURE_COOKIE = True)
- [ ] XSS protection headers configured
- [ ] Content Security Policy implemented
- [ ] Rate limiting on login and sensitive endpoints
- [ ] Brute-force protection (django-axes)
- [ ] File upload validation
- [ ] SQL injection prevention (use ORM)
- [ ] Input sanitization (bleach library)
- [ ] Output encoding in templates (Django does this automatically)
- [ ] Security headers (django-csp)
- [ ] Regular security updates (pip-audit)
- [ ] Audit logging for sensitive operations
- [ ] Two-factor authentication for admins
- [ ] Database backups automated
- [ ] Error messages don't reveal sensitive info
- [ ] Static files served via CDN with proper headers
- [ ] Dependencies regularly updated
- [ ] Penetration testing conducted

### Run security audit
```bash
# Install security audit tools
pip install pip-audit safety bandit

# Check for known vulnerabilities
pip-audit
safety check

# Static security analysis
bandit -r . -x ./venv,./migrations

# Django security check
python manage.py check --deploy
```
