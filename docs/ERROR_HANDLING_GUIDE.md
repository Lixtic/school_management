# Error Handling & Logging Improvements

## 1. Custom Error Pages

### Create custom error templates
```html
<!-- templates/errors/404.html -->
{% extends "base.html" %}
{% block title %}Page Not Found{% endblock %}

{% block content %}
<div class="error-page text-center py-5">
    <h1 class="display-1">404</h1>
    <h2>Oops! Page Not Found</h2>
    <p class="lead">The page you're looking for doesn't exist.</p>
    <a href="{% url 'dashboard' %}" class="btn btn-primary">
        <i class="bi bi-house"></i> Go to Dashboard
    </a>
</div>
{% endblock %}

<!-- templates/errors/500.html -->
<h1>500 - Server Error</h1>
<p>Something went wrong. Our team has been notified.</p>

<!-- templates/errors/403.html -->
<h1>403 - Permission Denied</h1>
<p>You don't have permission to access this resource.</p>
```

### Configure error handlers
```python
# school_system/urls.py
handler404 = 'school_system.views.custom_404'
handler500 = 'school_system.views.custom_500'
handler403 = 'school_system.views.custom_403'

# school_system/views.py
def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)
```

## 2. Enhanced Logging Configuration

### Update settings.py logging
```python
# settings.py
import os
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'students': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO' if DEBUG else 'WARNING',
        },
        'teachers': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO' if DEBUG else 'WARNING',
        },
        'academics': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO' if DEBUG else 'WARNING',
        },
        # Add custom app loggers
        'grading': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
        },
    },
}

# Admin email configuration for error notifications
if not DEBUG:
    ADMINS = [
        ('Admin', os.getenv('ADMIN_EMAIL', 'admin@schoolmanagement.local')),
    ]
    MANAGERS = ADMINS
```

## 3. Add Structured Logging in Views

### Example: Enhanced error handling in views
```python
# students/views.py
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction, IntegrityError

logger = logging.getLogger(__name__)

@login_required
@teacher_required
def enter_grades(request, student_id):
    try:
        student = get_object_or_404(
            Student.objects.select_related('user', 'current_class'),
            id=student_id,
            school=request.user.school  # Security check
        )
        
        if request.method == 'POST':
            with transaction.atomic():
                # Process grade entry
                class_score = request.POST.get('class_score')
                exams_score = request.POST.get('exams_score')
                
                grade, created = Grade.objects.update_or_create(
                    student=student,
                    subject_id=request.POST.get('subject_id'),
                    academic_year_id=request.POST.get('academic_year_id'),
                    term=request.POST.get('term'),
                    defaults={
                        'class_score': class_score,
                        'exams_score': exams_score,
                        'created_by': request.user,
                        'school': request.user.school,
                    }
                )
                
                action = 'created' if created else 'updated'
                logger.info(
                    f'Grade {action} for student {student.admission_number} '
                    f'by teacher {request.user.username}',
                    extra={
                        'student_id': student.id,
                        'teacher_id': request.user.id,
                        'school_id': request.user.school.id,
                        'action': action,
                    }
                )
                
                messages.success(request, f'Grade {action} successfully!')
                return redirect('students:student_detail', pk=student.id)
        
        context = {'student': student}
        return render(request, 'students/enter_grades.html', context)
    
    except Student.DoesNotExist:
        logger.warning(
            f'Student {student_id} not found or not in user school',
            extra={'student_id': student_id, 'user': request.user.username}
        )
        messages.error(request, 'Student not found.')
        return redirect('students:student_list')
    
    except IntegrityError as e:
        logger.error(
            f'Database integrity error while entering grades: {str(e)}',
            exc_info=True,
            extra={'student_id': student_id}
        )
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('students:student_detail', pk=student_id)
    
    except Exception as e:
        logger.exception(
            f'Unexpected error in enter_grades view',
            extra={
                'student_id': student_id,
                'user': request.user.username,
                'error': str(e)
            }
        )
        messages.error(request, 'An unexpected error occurred. Please contact support.')
        return redirect('dashboard')
```

## 4. Add Sentry for Production Error Tracking

### Install Sentry SDK
```bash
pip install sentry-sdk
```

### Configure Sentry in settings.py
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        send_default_pii=False,  # Don't send personally identifiable information
        environment=os.getenv('ENVIRONMENT', 'production'),
        release=f"school-management@{os.getenv('APP_VERSION', '1.0.0')}",
    )
```

## 5. Add Health Check Endpoint

### Create health check view
```python
# school_system/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import sys

def health_check(request):
    """
    Health check endpoint for monitoring systems
    Returns 200 if all systems operational
    """
    health = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health['checks']['database'] = 'ok'
    except Exception as e:
        health['status'] = 'unhealthy'
        health['checks']['database'] = f'error: {str(e)}'
    
    # Check cache
    try:
        cache_key = 'health_check'
        cache.set(cache_key, 'test', 10)
        cache.get(cache_key)
        cache.delete(cache_key)
        health['checks']['cache'] = 'ok'
    except Exception as e:
        health['status'] = 'unhealthy'
        health['checks']['cache'] = f'error: {str(e)}'
    
    # Python version
    health['python_version'] = sys.version
    
    status_code = 200 if health['status'] == 'healthy' else 503
    return JsonResponse(health, status=status_code)

# urls.py
urlpatterns = [
    ...
    path('health/', health_check, name='health_check'),
]
```

## 6. Add Request ID Middleware for Debugging

```python
# school_system/middleware.py
import uuid
import logging

class RequestIDMiddleware:
    """Add unique request ID to each request for log tracking"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.id = str(uuid.uuid4())
        
        # Add to log records
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = getattr(request, 'id', None)
            return record
        
        logging.setLogRecordFactory(record_factory)
        
        response = self.get_response(request)
        response['X-Request-ID'] = request.id
        
        return response

# settings.py
MIDDLEWARE = [
    'school_system.middleware.RequestIDMiddleware',  # Add first
    ...
]

# Update logging formatter
LOGGING['formatters']['verbose']['format'] = (
    '[{levelname}] {asctime} [{request_id}] {module} {message}'
)
```

## Error Handling Checklist:
- [ ] Create custom 404, 500, 403 error templates
- [ ] Configure comprehensive logging
- [ ] Add structured logging in all views
- [ ] Set up Sentry or similar error tracking (production)
- [ ] Create health check endpoint
- [ ] Add request ID middleware for debugging
- [ ] Configure admin email notifications for errors
- [ ] Log all security-related events
- [ ] Use try-except blocks in views with proper logging
- [ ] Set up log rotation to prevent disk space issues
