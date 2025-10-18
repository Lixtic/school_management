import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
import django
django.setup()

from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from students.admin import StudentAdmin
from students.models import Student
from django.contrib import admin
from django.contrib.admin.sites import AdminSite

User = get_user_model()
# Ensure a superuser exists
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')

rf = RequestFactory()
request = rf.get('/admin/students/student/import-grades/')
user = User.objects.filter(is_superuser=True).first()
request.user = user

site = AdminSite()
ma = StudentAdmin(Student, site)
try:
    response = ma.import_grades_view(request)
    print('Response status:', getattr(response, 'status_code', 'n/a'))
    print(type(response))
except Exception as e:
    import traceback
    traceback.print_exc()
