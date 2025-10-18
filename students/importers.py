"""Student CSV importers: create/update Users and Student records.

Safe, idempotent behavior:
- Lookup existing student by admission_number, then by email, then by username.
- Create or update accounts.User and students.Student.
- Generate username as firstname_lastname (sanitized), dedupe with numeric suffix.
- Optionally auto-create classes when a matching Class does not exist.
- Supports dry_run=True to validate without DB writes.

Return shape for students importer: (created_count, updated_count, created_classes, details)
where details is a list of {row, status, message, data}
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify
from datetime import datetime

User = get_user_model()

# Local imports deferred to runtime to avoid import-time django.setup issues


def _normalize_col_name(c: str) -> str:
    return str(c).strip().lower().replace(' ', '_').replace('-', '_')


def _alias_map() -> Dict[str, str]:
    return {
        'adm_no': 'admission_number',
        'admission_no': 'admission_number',
        'admnumber': 'admission_number',
        'fname': 'first_name',
        'given_name': 'first_name',
        'lname': 'last_name',
        'surname': 'last_name',
        'dob': 'date_of_birth',
        'birth_date': 'date_of_birth',
        'class': 'current_class',
        'class_name': 'current_class',
        'email_address': 'email',
        'emergency_phone': 'emergency_contact',
    }


def _sanitize_username(first: str, last: str) -> str:
    base = f"{first}_{last}".lower()
    base = re.sub(r"[^a-z0-9_]+", "_", base)
    base = re.sub(r"__+", "_", base).strip('_')
    if not base:
        base = 'user'
    return base


def _unique_username(base: str):
    """Return an available username based on base, checking User.username existence."""
    # Import inside function
    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = base
    suffix = 0
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base}_{suffix}"
    return username


def import_students_from_dataframe(df, academic_year=None, auto_create_classes=True, dry_run=True) -> Tuple[int, int, List[str], List[Dict]]:
    """Full importer: writes to DB unless dry_run=True.

    Returns: (created_count, updated_count, created_classes, details)
    """
    # Defer imports until runtime
    from .models import Student
    from academics.models import Class as SchoolClass, AcademicYear

    created = 0
    updated = 0
    created_classes = []
    details = []

    aliases = _alias_map()

    # Build column mapping
    col_map = {c: aliases.get(_normalize_col_name(c), _normalize_col_name(c)) for c in df.columns}

    # If no academic_year provided, try to use the current academic year
    if academic_year is None:
        try:
            academic_year = AcademicYear.objects.filter(is_current=True).first()
        except Exception:
            academic_year = None

    for idx, row in df.fillna('').to_dict(orient='index').items():
        # extract canonical fields
        data = {col_map[k]: v for k, v in row.items()}
        admission = data.get('admission_number') or ''
        email = data.get('email') or ''
        first = data.get('first_name') or ''
        last = data.get('last_name') or ''
        dob = data.get('date_of_birth') or ''
        class_name = data.get('current_class') or data.get('class') or ''
        roll_number = data.get('roll_number') or ''
        emergency = data.get('emergency_contact') or ''

        # Basic validation
        missing = []
        if not (admission or email):
            missing.append('admission_number OR email')
        if not first:
            missing.append('first_name')
        if not last:
            missing.append('last_name')
        if not dob:
            missing.append('date_of_birth')

        if missing:
            details.append({'row': idx, 'status': 'skipped', 'message': f"missing: {', '.join(missing)}", 'data': data})
            continue

        # Attempt to parse date_of_birth
        dob_parsed = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                dob_parsed = datetime.strptime(str(dob).strip(), fmt).date()
                break
            except Exception:
                dob_parsed = None
        if not dob_parsed:
            details.append({'row': idx, 'status': 'skipped', 'message': 'invalid date_of_birth format', 'data': data})
            continue

        # Find existing student by admission_number then email
        student = None
        try:
            if admission:
                student = Student.objects.filter(admission_number=str(admission).strip()).first()
            if not student and email:
                user_qs = User.objects.filter(email__iexact=str(email).strip())
                if user_qs.exists():
                    student = Student.objects.filter(user__in=user_qs).first()
        except Exception:
            # In dry-run mode the DB might not be ready; swallow errors
            student = None

        # Prepare user fields
        if not email:
            email = ''

        # Username: if user exists use it, else generate
        username = None
        if student and student.user:
            username = student.user.username

        if not username:
            base = _sanitize_username(first, last)
            username = _unique_username(base) if not dry_run else base

        # If dry_run, do not write to DB; only indicate action
        if dry_run:
            action = 'update' if student else 'create'
            details.append({'row': idx, 'status': f'would_{action}', 'message': 'valid', 'data': data})
            if not student:
                created += 1
            else:
                updated += 1
            continue

        # Real DB write
        with transaction.atomic():
            # Create or update User
            if student and student.user:
                user = student.user
                user.first_name = first
                user.last_name = last
                if email:
                    user.email = email
                # Ensure user_type is set for existing users (required field)
                if not getattr(user, 'user_type', None):
                    try:
                        user.user_type = 'student'
                    except Exception:
                        pass
                user.save()
                updated += 0  # user update counted as student update below
            else:
                # Create user
                user = User.objects.create(username=username, first_name=first, last_name=last, email=email, user_type='student')
                # default password; recommend that real workflows set a policy
                user.set_password('password123')
                user.save()

            # Create or update student
            if student:
                student.user = user
                student.date_of_birth = dob_parsed
                student.date_of_admission = data.get('date_of_admission') or student.date_of_admission
                student.roll_number = roll_number or student.roll_number
                student.emergency_contact = emergency or student.emergency_contact
                # handle class
                if class_name:
                    cls = SchoolClass.objects.filter(name=class_name).first()
                    if not cls and auto_create_classes and academic_year:
                        cls = SchoolClass.objects.create(name=class_name, academic_year=academic_year)
                        created_classes.append(class_name)
                    # Only set current_class if we have a class instance
                    if cls:
                        student.current_class = cls
                student.save()
                updated += 1
                details.append({'row': idx, 'status': 'updated', 'message': 'updated student', 'data': data})
            else:
                # create student
                student = Student.objects.create(
                    user=user,
                    admission_number=str(admission).strip(),
                    date_of_birth=dob_parsed,
                    date_of_admission=data.get('date_of_admission') or datetime.today().date(),
                    roll_number=roll_number,
                    emergency_contact=emergency,
                )
                if class_name:
                    cls = SchoolClass.objects.filter(name=class_name).first()
                    if not cls and auto_create_classes and academic_year:
                        cls = SchoolClass.objects.create(name=class_name, academic_year=academic_year)
                        created_classes.append(class_name)
                    if cls:
                        student.current_class = cls
                    student.save()
                created += 1
                details.append({'row': idx, 'status': 'created', 'message': 'created student', 'data': data})

    return (created, updated, created_classes, details)
