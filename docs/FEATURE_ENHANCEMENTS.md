# Additional Feature & UX Improvements

## 1. Real-time Notifications System

### Install channels for WebSockets
```bash
pip install channels channels-redis daphne
```

### Configure channels
```python
# settings.py
INSTALLED_APPS = [
    ...
    'daphne',  # Add before django.contrib.staticfiles
    'channels',
]

ASGI_APPLICATION = 'school_system.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.getenv('REDIS_URL', 'redis://127.0.0.1:6379')],
        },
    },
}

# school_system/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')

from communications.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

# communications/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'icon': event.get('icon', 'info'),
        }))
```

## 2. Advanced Reporting & Analytics

### Create comprehensive reports
```python
# reporting/views.py
from django.db.models import Avg, Count, Q, F
from django.http import HttpResponse
import pandas as pd
from io.BytesIO import BytesIO
from openpyxl import Workbook

@login_required
@admin_required
def student_performance_report(request):
    """Generate detailed performance report"""
    school = request.user.school
    academic_year_id = request.GET.get('academic_year')
    
    # Aggregate data
    students = Student.objects.filter(
        school=school
    ).annotate(
        avg_score=Avg('grade__total_score'),
        total_subjects=Count('grade'),
        attendance_rate=(
            Count('attendance', filter=Q(attendance__status='present')) * 100.0 /
            Count('attendance')
        )
    ).select_related('user', 'current_class')
    
    if academic_year_id:
        students = students.filter(grade__academic_year_id=academic_year_id)
    
    # Export options
    export_format = request.GET.get('format', 'html')
    
    if export_format == 'excel':
        return export_to_excel(students)
    elif export_format == 'pdf':
        return export_to_pdf(students)
    
    context = {'students': students}
    return render(request, 'reporting/performance_report.html', context)

def export_to_excel(queryset):
    """Export queryset to Excel file"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Student Performance"
    
    # Headers
    headers = ['Admission Number', 'Name', 'Class', 'Average Score', 
               'Total Subjects', 'Attendance Rate']
    ws.append(headers)
    
    # Data
    for student in queryset:
        ws.append([
            student.admission_number,
            student.user.get_full_name(),
            str(student.current_class),
            round(student.avg_score or 0, 2),
            student.total_subjects,
            f"{round(student.attendance_rate or 0, 2)}%"
        ])
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=student_performance.xlsx'
    
    return response
```

## 3. Bulk Import/Export Enhancements

### Improve CSV import with validation
```python
# students/views.py
import csv
from django.contrib import messages
from django.db import transaction

@login_required
@admin_required
def bulk_import_students(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('students:import')
        
        # Parse and validate
        errors = []
        success_count = 0
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate required fields
                        required_fields = ['admission_number', 'first_name', 
                                          'last_name', 'date_of_birth']
                        missing = [f for f in required_fields if not row.get(f)]
                        if missing:
                            errors.append(
                                f"Row {row_num}: Missing fields: {', '.join(missing)}"
                            )
                            continue
                        
                        # Create user and student
                        user, created = User.objects.get_or_create(
                            username=row['admission_number'].lower(),
                            defaults={
                                'first_name': row['first_name'],
                                'last_name': row['last_name'],
                                'user_type': 'student',
                                'school': request.user.school,
                            }
                        )
                        
                        if created:
                            user.set_password(row.get('password', 'changeme123'))
                            user.save()
                        
                        student, created = Student.objects.get_or_create(
                            admission_number=row['admission_number'],
                            defaults={
                                'user': user,
                                'date_of_birth': row['date_of_birth'],
                                'date_of_admission': row.get('date_of_admission', 
                                                            timezone.now().date()),
                                'gender': row.get('gender', 'male'),
                                'school': request.user.school,
                            }
                        )
                        
                        success_count += 1
                    
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            # Report results
            if errors:
                messages.warning(
                    request,
                    f"Import completed with {len(errors)} errors. "
                    f"{success_count} students imported successfully."
                )
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
            else:
                messages.success(
                    request,
                    f"Successfully imported {success_count} students!"
                )
        
        except Exception as e:
            messages.error(request, f"Import failed: {str(e)}")
        
        return redirect('students:list')
    
    return render(request, 'students/import.html')
```

## 4. Email Notifications

### Configure email templates
```python
# communications/email.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_grade_notification(student, grade):
    """Send email notification when grade is entered"""
    subject = f'New Grade Posted - {grade.subject.name}'
    
    context = {
        'student': student,
        'grade': grade,
        'school': student.school,
    }
    
    # Render HTML email
    html_content = render_to_string('emails/grade_notification.html', context)
    text_content = render_to_string('emails/grade_notification.txt', context)
    
    # Send to student and parents
    recipients = [student.user.email]
    for parent in student.parents.all():
        recipients.append(parent.user.email)
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipients
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_attendance_alert(student, date, status):
    """Alert parents about attendance"""
    if status in ['absent', 'late']:
        subject = f'Attendance Alert - {student.user.get_full_name()}'
        
        context = {
            'student': student,
            'date': date,
            'status': status,
        }
        
        html_content = render_to_string('emails/attendance_alert.html', context)
        text_content = render_to_string('emails/attendance_alert.txt', context)
        
        recipients = [p.user.email for p in student.parents.all()]
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            recipients
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
```

## 5. Calendar Integration

### Add event calendar
```python
# academics/views.py
from django.http import JsonResponse

@login_required
def calendar_events(request):
    """Return calendar events as JSON for FullCalendar.js"""
    user = request.user
    events = []
    
    if user.user_type == 'student':
        student = user.student
        # Add schedule events
        schedules = Schedule.objects.filter(
            class_subject__class_name=student.current_class
        ).select_related('class_subject__subject')
        
        for schedule in schedules:
            events.append({
                'title': schedule.class_subject.subject.name,
                'daysOfWeek': [get_day_number(schedule.day)],
                'startTime': schedule.start_time.strftime('%H:%M'),
                'endTime': schedule.end_time.strftime('%H:%M'),
                'color': '#3788d8'
            })
    
    # Add exam dates, holidays, etc.
    
    return JsonResponse(events, safe=False)
```

## 6. Mobile-Responsive Dashboard

### Enhance mobile UX
```html
<!-- templates/base.html -->
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Add PWA support -->
<link rel="manifest" href="{% static 'manifest.json' %}">
<meta name="theme-color" content="#2c3e50">

<script>
// Register service worker for offline support
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
}
</script>
```

### Create PWA manifest
```json
// static/manifest.json
{
  "name": "School Management System",
  "short_name": "School MS",
  "start_url": "/dashboard/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2c3e50",
  "icons": [
    {
      "src": "/static/images/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## 7. Advanced Search & Filtering

### Implement Elasticsearch or PostgreSQL full-text search
```python
# Install django-elasticsearch-dsl
pip install django-elasticsearch-dsl

# settings.py
INSTALLED_APPS = [
    ...
    'django_elasticsearch_dsl',
]

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': os.getenv('ELASTICSEARCH_URL', 'localhost:9200')
    },
}

# students/documents.py
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Student

@registry.register_document
class StudentDocument(Document):
    user = fields.ObjectField(properties={
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
        'email': fields.TextField(),
    })
    
    current_class = fields.ObjectField(properties={
        'name': fields.TextField(),
    })
    
    class Index:
        name = 'students'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    
    class Django:
        model = Student
        fields = [
            'admission_number',
            'date_of_birth',
            'gender',
        ]

# Search view
def search_students(request):
    query = request.GET.get('q', '')
    if query:
        students = StudentDocument.search().query(
            "multi_match",
            query=query,
            fields=['user.first_name', 'user.last_name', 'admission_number']
        )
    else:
        students = Student.objects.none()
    
    return render(request, 'students/search_results.html', {'students': students})
```

## 8. Data Export Templates

### Create report card template
```python
# reporting/views.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_report_card_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Check permissions
    check_school_access(request.user, student)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_card_{student.admission_number}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, height - 1*inch, student.school.name)
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, height - 1.3*inch, "STUDENT REPORT CARD")
    
    # Student Info
    y = height - 2*inch
    p.drawString(1*inch, y, f"Name: {student.user.get_full_name()}")
    p.drawString(1*inch, y-0.3*inch, f"Admission No: {student.admission_number}")
    
    # Grades table
    # ... (add grade table generation)
    
    p.showPage()
    p.save()
    
    return response
```

## Feature Enhancement Checklist:
- [ ] Real-time notifications (WebSockets)
- [ ] Advanced reporting and analytics
- [ ] Bulk import with validation and error reporting
- [ ] Email notifications for grades, attendance
- [ ] Calendar integration for events and schedules
- [ ] Mobile-responsive PWA
- [ ] Advanced search with Elasticsearch
- [ ] PDF report generation
- [ ] Data visualization charts
- [ ] Export to multiple formats (Excel, PDF, CSV)
- [ ] Parent portal for monitoring children
- [ ] SMS notifications (Twilio integration)
- [ ] Payment integration for fees
- [ ] Library management module
- [ ] Transportation tracking
