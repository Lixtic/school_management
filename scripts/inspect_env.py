import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
import django
django.setup()

from academics.models import AcademicYear, Subject
from students.models import Student, Grade

print('AcademicYears:')
for ay in AcademicYear.objects.all():
    print(' -', ay.id, ay.name, ay.is_current)

print('\nSubjects:')
for s in Subject.objects.all():
    print(' -', s.id, s.code, s.name)

print('\nStudents:', Student.objects.count())
print('Grades:', Grade.objects.count())

print('\nSample Students:')
for st in Student.objects.select_related('user')[:10]:
    print(' -', st.admission_number, st.user.username)
