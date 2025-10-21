# Developer Quick Reference - School Management System

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Purpose**: Fast lookup guide for developers

---

## 🚀 First-Time Setup

```bash
# 1. Clone and navigate
git clone <repo-url>
cd school_management

# 2. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # PowerShell: .\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python manage.py migrate
python create_test_data.py

# 5. Run server
$env:DEBUG='true'; python manage.py runserver
```

**Access**: http://127.0.0.1:8000/  
**Credentials**: See accounts/views.py sample data comments

---

## 📁 Directory Quick Map

| Directory | Contains |
|-----------|----------|
| `accounts/` | User auth, custom User model, dashboards |
| `students/` | Student models, grades, ranking logic |
| `teachers/` | Teacher profiles and assignments |
| `academics/` | Classes, subjects, academic years |
| `parents/` | Parent portal, child monitoring |
| `schools/` | School model, multi-tenancy |
| `templates/` | HTML files organized by app |
| `static/` | CSS, JavaScript, images |
| `school_system/` | Django project settings, URLs |

---

## 🔑 Critical File Locations

```
settings.py           → Django configuration (430 lines)
accounts/models.py    → Custom User model (4 roles)
accounts/views.py     → Dashboard & login logic
students/models.py    → Grade calculation & ranking
parents/views.py      → Parent portal queries
schools/models.py     → Multi-tenant school model
base.html             → Main template layout
```

---

## 🎯 Common Tasks (Copy & Paste)

### Create Test Data
```bash
python create_test_data.py
```

### Run Tests
```bash
python manage.py test
python manage.py test accounts.tests.LoginTest
```

### Check System Health
```bash
$env:DEBUG='true'; python manage.py check
```

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
python create_test_data.py
```

### Access Database Shell
```bash
python manage.py shell
>>> from accounts.models import User
>>> User.objects.all()
```

### Create New Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Access Admin Panel
```
http://127.0.0.1:8000/admin/
User: admin
Pass: admin123
```

---

## 🐛 Bug Fixes Summary (This Session)

| Bug | Fix | Commit |
|-----|-----|--------|
| Attendance import error | Changed `academics.models` to `students.models` | 219e303 |
| Parent portal teacher query | Fixed ORM through ClassSubject | 3d31244 |
| Grade percentage field | Changed `percentage` to `total_score` | 3d31244 |
| Message timestamp field | Changed `timestamp` to `sent_at` | efd0541 |
| Dashboard student count | Changed `student_set` to `student` | 68adc00 |
| School count properties | Fixed to explicit ORM queries | e464aed |
| Login CSRF issue | Render form on GET instead of redirect | 9be8f01 |
| Dashboard query error | Changed `student_set` to `student` | 4598f82 |

---

## 🔐 Security Essentials

### Template Security
```html
<!-- ✅ Always include CSRF token in forms -->
<form method="POST">
    {% csrf_token %}
    <!-- form content -->
</form>

<!-- ✅ Django auto-escapes by default -->
{{ user_input }}

<!-- ✅ Use |safe filter only for trusted content -->
{{ trusted_html|safe }}
```

### View Security
```python
# ✅ Require login
@login_required
def my_view(request):
    pass

# ✅ Check permissions
if not request.user.is_staff:
    return HttpResponseForbidden()

# ✅ Filter by school (multi-tenant)
items = Item.objects.filter(school=request.user.school)
```

### ORM Security
```python
# ✅ Use ORM (prevents SQL injection)
users = User.objects.filter(username=username)

# ❌ Never use string formatting
users = User.objects.raw(f"SELECT * FROM users WHERE id={user_id}")
```

---

## 📊 Database Relations Quick Ref

```python
# Student → Class (ForeignKey)
student.current_class                    # Get class
Class.objects.prefetch_related('student') # Get students

# User → Student (OneToOneField)
student.user.username
user.student                             # Reverse

# Grade → Subject (ForeignKey)
grade.subject
Subject.objects.prefetch_related('grade_set')

# All records: Filter by school
Model.objects.filter(school=request.user.school)
```

---

## 🚨 Error Codes Quick Fix

| Error | Cause | Fix |
|-------|-------|-----|
| `FieldError: Cannot resolve keyword` | Wrong field/relation name | Check model, use `student` not `student_set` |
| `IntegrityError: UNIQUE constraint` | Duplicate record | Check unique_together, use `get_or_create()` |
| `DoesNotExist` | Record not found | Check query, use `.first()` or `.exists()` |
| `RelatedObjectDoesNotExist` | OneToOne not set | Check if relation exists before access |
| `FieldError: Local field` | Model not defined yet | Check import order, use string references |

---

## 🔄 Git Workflow Quick Ref

```bash
# Check status
git status

# View recent commits
git log --oneline -n 10

# Create branch
git checkout -b feature/description

# Make changes and commit
git add <files>
git commit -m "type: description"

# Push
git push origin feature/description

# Pull latest
git pull origin asetena_systems

# View diff
git diff
```

### Commit Message Format
```
fix: Correct dashboard student count query

Changed Count('student_set') to Count('student')
for correct reverse relation name.

Fixes #123
```

---

## 🧪 Testing Quick Ref

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test accounts
python manage.py test students
```

### Run Specific Test Class
```bash
python manage.py test accounts.tests.UserCreationTest
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
```

---

## 📈 Performance Quick Tips

```python
# ❌ Bad: N+1 queries
for student in Student.objects.all():
    print(student.current_class.name)  # Query per student!

# ✅ Good: Prefetch related
for student in Student.objects.prefetch_related('current_class'):
    print(student.current_class.name)  # 1 query

# ❌ Bad: All fields loaded
items = Item.objects.all()

# ✅ Good: Specific fields only
items = Item.objects.only('id', 'name')

# ❌ Bad: Multiple queries
grades = Grade.objects.all()
subjects = Subject.objects.all()

# ✅ Good: Batch query
grades = Grade.objects.select_related('subject')
```

---

## 📚 Settings Environment Variables

### Development (Default - No Setup Needed)
```bash
# Automatically uses DEBUG=true, SQLite, console email
$env:DEBUG='true'; python manage.py runserver
```

### Production Minimal
```bash
export DEBUG=false
export SECRET_KEY="<random-key>"
export DATABASE_URL="postgresql://user:pass@host/db"
```

### Production Full
```bash
export DEBUG=false
export SECRET_KEY="<random-key>"
export DATABASE_URL="postgresql://user:pass@host/db"
export REDIS_URL="redis://user:pass@host:6379/1"
export EMAIL_HOST_USER="noreply@school.edu"
export EMAIL_HOST_PASSWORD="<app-password>"
export ALLOWED_HOSTS="school.edu,www.school.edu"
```

---

## 🎓 Code Examples

### Create New Record
```python
from students.models import Student

# Method 1: Direct create
student = Student.objects.create(
    user=user,
    current_class=class_obj,
    gender='M',
    date_of_birth=date(2005, 1, 15)
)

# Method 2: get_or_create (safer)
student, created = Student.objects.get_or_create(
    user=user,
    defaults={'current_class': class_obj}
)
```

### Query with Filters
```python
# Simple filter
students = Student.objects.filter(current_class=class_obj)

# Multiple conditions (AND)
students = Student.objects.filter(
    current_class=class_obj,
    gender='M'
)

# OR conditions
from django.db.models import Q
students = Student.objects.filter(
    Q(gender='M') | Q(gender='F')
)

# Exclude
students = Student.objects.exclude(gender='M')

# Count
count = Student.objects.filter(current_class=class_obj).count()
```

### Update Records
```python
# Update single record
student = Student.objects.get(user__username='john')
student.gender = 'M'
student.save()

# Bulk update
Student.objects.filter(current_class=class_obj).update(
    gender='M'
)
```

### Delete Records
```python
# Delete single
student = Student.objects.get(id=1)
student.delete()

# Bulk delete
Student.objects.filter(current_class=class_obj).delete()
```

---

## 🔍 Debugging Tips

### Print SQL Queries
```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    users = User.objects.all()
    
print(f"Queries: {len(ctx)}")
for query in ctx:
    print(query['sql'])
```

### Django Debug Toolbar
```python
# Add to INSTALLED_APPS in settings.py
'debug_toolbar',

# Add to MIDDLEWARE
'debug_toolbar.middleware.DebugToolbarMiddleware',

# Then access admin pages to see SQL, templates, signals
```

### Print Variables
```python
import pdb
pdb.set_trace()  # Debugger breakpoint

# Or use print()
print(f"User: {user}, Class: {user.school}")
```

---

## 📞 Support Quick Links

- **Django Docs**: https://docs.djangoproject.com/
- **Project Settings**: `school_system/settings.py`
- **Models**: `*/models.py` in each app
- **Views**: `*/views.py` in each app
- **Git Log**: `git log --oneline`

---

**Quick Ref Version**: 1.0  
**Last Update**: Oct 21, 2025  
**Next Review**: As needed
