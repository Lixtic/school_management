# Performance Optimization Recommendations

## Database Query Optimization

### 1. Add Database Indexes
```python
# students/models.py
class Student(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['school', 'current_class']),
            models.Index(fields=['school', 'date_of_admission']),
        ]

class Grade(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['student', 'academic_year', 'term']),
            models.Index(fields=['school', 'academic_year', 'term']),
            models.Index(fields=['subject', 'academic_year', 'term']),
            models.Index(fields=['-total_score']),  # For rankings
        ]
        unique_together = ['student', 'subject', 'academic_year', 'term']

class Attendance(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['student', '-date']),
            models.Index(fields=['school', 'date']),
            models.Index(fields=['status', 'date']),
        ]
```

### 2. Use select_related() and prefetch_related()
```python
# accounts/views.py - Dashboard view BEFORE
def dashboard(request):
    students = Student.objects.filter(school=school)  # N+1 queries!
    
# AFTER - Optimized
def dashboard(request):
    students = Student.objects.filter(school=school).select_related(
        'user', 'current_class', 'school'
    ).prefetch_related('grades', 'parents')
```

### 3. Optimize Grade Ranking Calculation
```python
# students/models.py - Current implementation causes many saves
def update_subject_rankings(self):
    grades_in_subject = Grade.objects.filter(...).order_by('-total_score')
    
    for grade in grades_in_subject:
        Grade.objects.filter(id=grade.id).update(subject_position=position)
        # This is inefficient - multiple UPDATE queries

# IMPROVED - Use bulk_update
def update_subject_rankings(self):
    grades_in_subject = list(Grade.objects.filter(
        subject=self.subject,
        academic_year=self.academic_year,
        term=self.term,
        student__current_class=self.student.current_class
    ).exclude(total_score__isnull=True).order_by('-total_score'))
    
    previous_score = None
    position = 0
    grades_to_update = []
    
    for grade in grades_in_subject:
        current_score = Decimal(str(grade.total_score))
        if current_score != previous_score:
            position += 1
            previous_score = current_score
        
        grade.subject_position = position
        grades_to_update.append(grade)
    
    # Bulk update - single query
    Grade.objects.bulk_update(grades_to_update, ['subject_position'])
```

### 4. Add Caching for Expensive Queries
```python
# students/views.py
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def student_list(request):
    # Expensive query
    pass

# Or use manual caching
def get_school_statistics(school):
    cache_key = f'school_stats_{school.id}'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = {
            'total_students': Student.objects.filter(school=school).count(),
            'total_teachers': Teacher.objects.filter(school=school).count(),
            # ... other stats
        }
        cache.set(cache_key, stats, 60 * 15)  # 15 minutes
    
    return stats
```

### 5. Use Database Views for Complex Reports
```python
# reporting/models.py
class StudentPerformanceView(models.Model):
    """
    Database view for student performance metrics
    """
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    average_score = models.DecimalField(max_digits=5, decimal_places=2)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        managed = False  # Don't create/modify table
        db_table = 'student_performance_view'

# Create migration to add view
# migrations/XXXX_create_performance_view.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [...]
    
    operations = [
        migrations.RunSQL(
            """
            CREATE VIEW student_performance_view AS
            SELECT 
                s.id as id,
                s.id as student_id,
                AVG(g.total_score) as average_score,
                (COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / 
                 NULLIF(COUNT(a.id), 0)) as attendance_percentage
            FROM students_student s
            LEFT JOIN students_grade g ON s.id = g.student_id
            LEFT JOIN students_attendance a ON s.id = a.student_id
            GROUP BY s.id
            """,
            reverse_sql="DROP VIEW IF EXISTS student_performance_view"
        )
    ]
```

### 6. Optimize File Uploads
```python
# settings.py - Add image optimization
INSTALLED_APPS = [
    ...
    'imagekit',  # pip install django-imagekit pillow
]

# schools/models.py
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

class School(models.Model):
    logo = ProcessedImageField(
        upload_to='schools/logos/',
        processors=[ResizeToFill(200, 200)],
        format='WEBP',
        options={'quality': 90},
        blank=True,
        null=True
    )
```

### 7. Add Database Connection Pooling (Production)
```python
# requirements.txt
# Add for PostgreSQL connection pooling
psycopg2-binary==2.9.11
django-db-connection-pool==1.2.4

# settings.py
if not DEBUG and DATABASE_URL:
    DATABASES['default']['ENGINE'] = 'dj_db_conn_pool.backends.postgresql'
    DATABASES['default']['POOL_OPTIONS'] = {
        'POOL_SIZE': 10,
        'MAX_OVERFLOW': 10,
    }
```

### 8. Use Query Annotations Instead of Python Loops
```python
# BEFORE - Inefficient
students = Student.objects.filter(school=school)
for student in students:
    student.avg_grade = Grade.objects.filter(student=student).aggregate(
        Avg('total_score')
    )['total_score__avg']

# AFTER - Single query with annotation
from django.db.models import Avg
students = Student.objects.filter(school=school).annotate(
    avg_grade=Avg('grade__total_score')
)
```

### 9. Implement Pagination Everywhere
```python
# students/views.py
from django.core.paginator import Paginator

def student_list(request):
    students = Student.objects.filter(
        school=request.user.school
    ).select_related('user', 'current_class')
    
    paginator = Paginator(students, 25)  # 25 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'students/list.html', {'page_obj': page_obj})
```

### 10. Add Query Monitoring (Django Debug Toolbar)
```python
# requirements.txt
django-debug-toolbar==4.2.0

# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# urls.py
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
```

### Performance Checklist:
- [ ] Add database indexes on foreign keys and frequently queried fields
- [ ] Use select_related() for OneToOne and ForeignKey
- [ ] Use prefetch_related() for ManyToMany and reverse ForeignKey
- [ ] Implement query result caching for expensive operations
- [ ] Add pagination to all list views
- [ ] Optimize grade ranking calculation with bulk_update
- [ ] Use database views for complex aggregations
- [ ] Add Django Debug Toolbar in development
- [ ] Monitor query counts (aim for < 10 queries per page)
- [ ] Implement database connection pooling for production
