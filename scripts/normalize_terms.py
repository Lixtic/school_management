import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from students.models import Grade
from students.utils import normalize_term
from django.db import transaction

with transaction.atomic():
    total = Grade.objects.count()
    changed = 0
    for g in Grade.objects.all():
        c = normalize_term(g.term)
        if g.term != c:
            Grade.objects.filter(id=g.id).update(term=c)
            changed += 1

print(f"Updated {changed} of {total} grades to canonical terms")
