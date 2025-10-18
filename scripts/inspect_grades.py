import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
import django
django.setup()

from students.models import Grade

print('Grade count:', Grade.objects.count())
for g in Grade.objects.select_related('student__user', 'subject', 'academic_year')[:50]:
    student = getattr(g.student, 'admission_number', None)
    subj = getattr(g.subject, 'code', None) or getattr(g.subject, 'name', None)
    ay = getattr(g.academic_year, 'name', None)
    print(f'id={g.id} student={student} subject={subj} year={ay} term={g.term} total={g.total_score} created_by={getattr(g.created_by, "username", None)}')
