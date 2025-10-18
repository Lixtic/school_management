import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'school_system' can be imported
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
import django
django.setup()

import pandas as pd
from students.models import Student
import load_sample_data

print('Students before:', Student.objects.count())
try:
    df = pd.read_csv('data/sample_students.csv')
    res = load_sample_data.import_students_from_dataframe(df.head(3), dry_run=False)
    print('Import result:', res)
except Exception as e:
    print('Import raised exception:', repr(e))

print('Students after:', Student.objects.count())
