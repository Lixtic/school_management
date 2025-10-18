import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
import django
django.setup()

import pandas as pd
import load_sample_data
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.filter(is_superuser=True).first() or User.objects.first()

df = pd.read_csv('data/sample_grades.csv')
print('Calling importer...')
res = load_sample_data.import_grades_from_dataframe(df, dry_run=False, created_by=user)
print('Result:', res)
