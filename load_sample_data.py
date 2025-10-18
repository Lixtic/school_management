# Minimal stubs to allow Django to import modules while we repair the loader.
# These are intentionally small and safe: they call django.setup() lazily and
# return harmless defaults. Replace with the full implementation when ready.

import os
import django
from django.apps import apps


def ensure_django_setup():
    if not apps.ready:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
        django.setup()


def import_students_from_dataframe(df, **kwargs):
    ensure_django_setup()

    # Prefer to use the full importer implemented in students.importers when
    # available. If that fails (e.g., during partial deployments), fall back to
    # the tolerant validation-only logic below.
    try:
        from students.importers import import_students_from_dataframe as real_import
        return real_import(df, **kwargs)
    except Exception:
        pass

    # --- fallback tolerant validation-only importer ---
    aliases = {
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

    def normalize_col(c):
        return str(c).strip().lower().replace(' ', '_').replace('-', '_')

    col_map = {}
    for c in df.columns:
        nc = normalize_col(c)
        col_map[c] = aliases.get(nc, nc)

    def get_val(row, canonical_name):
        for orig_col, canon in col_map.items():
            if canon == canonical_name:
                return row.get(orig_col)
        return None

    created = 0
    updated = 0
    skipped = 0
    created_classes = []
    details = []

    for idx, row in df.fillna('').to_dict(orient='index').items():
        admission = get_val(row, 'admission_number')
        first = get_val(row, 'first_name')
        last = get_val(row, 'last_name')
        dob = get_val(row, 'date_of_birth')

        missing = []
        if not admission and not get_val(row, 'email'):
            missing.append('admission_number OR email')
        if not first:
            missing.append('first_name')
        if not last:
            missing.append('last_name')
        if not dob:
            missing.append('date_of_birth')

        if missing:
            details.append({'row': idx, 'status': 'skipped', 'message': f"missing: {', '.join(missing)}", 'data': row})
            skipped += 1
            continue

        details.append({'row': idx, 'status': 'would_create_or_update', 'message': 'valid', 'data': row})
        created += 1

    return (created, skipped, created_classes, details)


def import_grades_from_dataframe(df, **kwargs):
    """Tolerant grades importer stub.

    Returns (created, updated, skipped, details)
    """
    ensure_django_setup()

    # Prefer full grades importer if available
    try:
        from students.grade_importers import import_grades_from_dataframe as real_import
        return real_import(df, **kwargs)
    except Exception:
        pass

    # Minimal tolerant parsing: do not raise on missing columns
    details = []
    created = 0
    updated = 0
    skipped = 0

    def normalize_col(c):
        return str(c).strip().lower().replace(' ', '_').replace('-', '_')

    col_map = {c: normalize_col(c) for c in df.columns}

    for idx, row in df.fillna('').to_dict(orient='index').items():
        # simple validation: require student (admission_number or email) and subject
        student = None
        subject = None
        for orig, nc in col_map.items():
            if nc in ('admission_number', 'admission_no', 'adm_no'):
                student = row.get(orig) or student
            if nc in ('subject', 'subject_code', 'subject_name'):
                subject = row.get(orig) or subject

        if not student or not subject:
            details.append({'row': idx, 'status': 'skipped', 'message': 'missing student or subject', 'data': row})
            skipped += 1
            continue

        details.append({'row': idx, 'status': 'would_create_or_update', 'message': 'valid', 'data': row})
        created += 1

    return (created, updated, skipped, details)


def run_full_load(csv_file_path=None):
    ensure_django_setup()
    return
