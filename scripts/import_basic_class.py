"""Reusable importer for Basic classes.

Usage:
  python manage.py shell -c "from scripts.import_basic_class import run; run('Basic 7', 'data/basic7.csv', prefix='B7', default_dob='2012-01-01')"

Defaults:
- Uses current AcademicYear (is_current=True); creates one if missing.
- Creates class if not present for that academic year.
- All students are female.
- Admission numbers: <prefix>-### (prefix arg required).
- Default password: password123.
- Default DOB: provided as YYYY-MM-DD.
- date_of_admission = today; emergency_contact="N/A".
"""

import csv
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_system.settings")
sys.path.append(str(BASE_DIR))
django.setup()

from accounts.models import User
from academics.models import AcademicYear, Class
from students.models import Student

DEFAULT_PASSWORD = "password123"


def slugify_username(name: str) -> str:
    base = re.sub(r"[^a-z0-9]", "", name.lower())
    return base or "student"


def next_admission_number(prefix: str):
    existing = Student.objects.filter(admission_number__startswith=f"{prefix}-").values_list("admission_number", flat=True)
    max_seq = 0
    for adm in existing:
        try:
            seq = int(adm.split("-")[-1])
            max_seq = max(max_seq, seq)
        except ValueError:
            continue
    return max_seq + 1


def ensure_class(class_name: str):
    ay = AcademicYear.objects.filter(is_current=True).first()
    if not ay:
        ay = AcademicYear.objects.create(name=str(date.today().year), start_date=date.today(), end_date=date.today(), is_current=True)
    cls, _ = Class.objects.get_or_create(name=class_name, academic_year=ay)
    return cls


def parse_dob(dob_str: str):
    if not dob_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(dob_str, fmt).date()
        except ValueError:
            continue
    return None


def create_student_record(full_name: str, class_obj: Class, seq_start: int, prefix: str, default_dob: date):
    seq = seq_start
    base_username = slugify_username(full_name)
    username = base_username
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base_username}{suffix}"

    admission_number = f"{prefix}-{seq:03d}"

    user = User.objects.create(
        username=username,
        first_name=full_name.title(),
        user_type="student",
        is_active=True,
    )
    user.set_password(DEFAULT_PASSWORD)
    user.save()

    Student.objects.create(
        user=user,
        admission_number=admission_number,
        date_of_birth=default_dob,
        gender="female",
        date_of_admission=date.today(),
        current_class=class_obj,
        roll_number=str(seq),
        emergency_contact="N/A",
    )

    return seq + 1


def run(class_name: str, csv_path: str, prefix: str, default_dob: str = None):
    path = Path(csv_path)
    if not path.is_absolute():
        path = BASE_DIR / csv_path
    if not path.exists():
        raise FileNotFoundError(f"CSV not found at {path}")

    class_obj = ensure_class(class_name)
    seq = next_admission_number(prefix)

    dob_default = parse_dob(default_dob) if default_dob else None
    if not dob_default:
        dob_default = date(2010, 1, 1)

    created = 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("STUDENT NAME") or "").strip()
            if not name:
                continue
            seq = create_student_record(name, class_obj, seq, prefix, dob_default)
            created += 1

    print(f"Created {created} students into class {class_obj.name}")


if __name__ == "__main__":
    # Example usage for manual runs
    run("Basic 7", "data/basic7.csv", prefix="B7", default_dob="2012-01-01")
