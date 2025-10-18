"""Grades importer: create/update Grade records from CSV DataFrame.

Features:
- Lookup student by admission_number, email or username.
- Lookup subject by code or name.
- Accepts 'term' values (first, second, third) and common variants.
- Supports dry_run=True to preview changes without DB writes.
- Returns (created, updated, skipped, details)
"""
from __future__ import annotations

from typing import List, Dict, Tuple
from datetime import datetime
from decimal import Decimal, InvalidOperation

# Defer Django imports to runtime


def _normalize_col(c: str) -> str:
    return str(c).strip().lower().replace(' ', '_').replace('-', '_')


def _term_normalize(val: str) -> str:
    if not val:
        return 'first'
    v = str(val).strip().lower()
    if v in ('1', 'first', 'first_term'):
        return 'first'
    if v in ('2', 'second', 'second_term'):
        return 'second'
    if v in ('3', 'third', 'third_term'):
        return 'third'
    return v


def import_grades_from_dataframe(df, academic_year=None, class_obj=None, update_existing=True, dry_run=True, created_by=None) -> Tuple[int, int, int, List[Dict]]:
    """Import grades. Returns (created, updated, skipped, details).

    Expected columns (aliases accepted): admission_number, email, username, subject, subject_code, class_score, exams_score, term
    """
    from students.models import Student, Grade
    from academics.models import Subject, AcademicYear
    from django.contrib.auth import get_user_model

    User = get_user_model()

    created = 0
    updated = 0
    skipped = 0
    details: List[Dict] = []

    col_map = {c: _normalize_col(c) for c in df.columns}

    # helper: resolve academic_year input (can be model instance, id, or string)
    def _resolve_academic_year(val):
        if not val:
            return None
        if isinstance(val, AcademicYear):
            return val
        # try numeric id
        try:
            maybe_id = int(val)
            ay = AcademicYear.objects.filter(id=maybe_id).first()
            if ay:
                return ay
        except Exception:
            pass
        # try match by name/code (case-insensitive)
        sval = str(val).strip()
        ay = AcademicYear.objects.filter(name__iexact=sval).first()
        if ay:
            return ay
        ay = AcademicYear.objects.filter(label__iexact=sval).first() if hasattr(AcademicYear, 'label') else None
        if ay:
            return ay
        # try common formatting variants (e.g. '2024-2025' vs '2024/2025')
        alt = sval.replace('-', '/').replace('/', '-')
        ay = AcademicYear.objects.filter(name__iexact=alt).first()
        if ay:
            return ay
        return None

    for idx, row in df.fillna('').to_dict(orient='index').items():
        data = {col_map[k]: v for k, v in row.items()}

        # identify student
        student = None
        adm = data.get('admission_number') or data.get('admission_no')
        email = data.get('email')
        username = data.get('username')

        if adm:
            q = Student.objects.filter(admission_number=str(adm).strip())
            if class_obj:
                q = q.filter(current_class=class_obj)
            student = q.first()
        if not student and email:
            user_qs = User.objects.filter(email__iexact=str(email).strip())
            if user_qs.exists():
                q = Student.objects.filter(user__in=user_qs)
                if class_obj:
                    q = q.filter(current_class=class_obj)
                student = q.first()
        if not student and username:
            user_qs = User.objects.filter(username__iexact=str(username).strip())
            if user_qs.exists():
                q = Student.objects.filter(user__in=user_qs)
                if class_obj:
                    q = q.filter(current_class=class_obj)
                student = q.first()

        subject = None
        # narrow-format: subject specified in a column
        subj_val = data.get('subject') or data.get('subject_code') or data.get('subject_name')
        if subj_val:
            subject = Subject.objects.filter(code__iexact=str(subj_val).strip()).first() or Subject.objects.filter(name__iexact=str(subj_val).strip()).first()

        # wide-format support: detect when the CSV has many subject-named columns
        # If no explicit subject column present, we'll scan the original column headers
        wide_subjects = []
        if not subject:
            # alias map for common header variants -> subject code
            alias_map = {
                'maths': 'MATH', 'mathematics': 'MATH', 'math': 'MATH', 'maths': 'MATH',
                'english': 'ENG', 'eng': 'ENG',
                'science': 'SCI', 'sci': 'SCI',
                'socialstudies': 'SOC', 'social_studies': 'SOC', 'social': 'SOC',
                'history': 'HIS', 'geography': 'GEO',
                'physics': 'PHY', 'chemistry': 'CHEM', 'biology': 'BIO',
            }
            for orig_col in df.columns:
                nc = _normalize_col(orig_col)
                # skip known non-subject columns
                if nc in ('admission_number', 'admission_no', 'email', 'username', 'term', 'class_score', 'exams_score', 'academic_year', 'first_name', 'last_name', 'class', 'roll_number'):
                    continue
                header_key = nc.replace(' ', '').replace('_', '')
                mapped_code = alias_map.get(header_key) or alias_map.get(nc)
                s = None
                if mapped_code:
                    s = Subject.objects.filter(code__iexact=mapped_code).first()
                if not s:
                    # try exact code or name
                    s = Subject.objects.filter(code__iexact=orig_col.strip()).first() or Subject.objects.filter(name__iexact=orig_col.strip()).first()
                if not s:
                    # try normalized name contains or startswith match
                    sval = orig_col.strip().lower()
                    s = Subject.objects.filter(name__icontains=sval).first() or Subject.objects.filter(name__istartswith=sval).first()
                if s:
                    wide_subjects.append((orig_col, s))

        # If no student found, we can't proceed regardless of format
        if not student:
            details.append({'row': idx, 'status': 'skipped', 'message': 'missing student', 'data': data})
            skipped += 1
            continue

        # If neither a narrow-format subject nor wide-format subject columns exist, skip
        if not subject and not wide_subjects:
            details.append({'row': idx, 'status': 'skipped', 'message': 'missing subject', 'data': data})
            skipped += 1
            continue

        term = _term_normalize(data.get('term'))

        # allow per-row academic_year value (string or id) in CSV; fall back to caller param
        row_academic_year = _resolve_academic_year(data.get('academic_year') or academic_year)
        if row_academic_year is None:
            # if caller didn't pass an academic year, try to use a single current year
            if academic_year is None:
                current_qs = AcademicYear.objects.filter(is_current=True)
                if current_qs.count() == 1:
                    row_academic_year = current_qs.first()
            # still None -> skip with helpful message
        if row_academic_year is None:
            details.append({'row': idx, 'status': 'skipped', 'message': 'could not resolve academic_year', 'data': data})
            skipped += 1
            continue

        # parse scores
        try:
            class_score = Decimal(str(data.get('class_score') or '0').strip())
        except (InvalidOperation, ValueError):
            class_score = Decimal('0')
        try:
            exams_score = Decimal(str(data.get('exams_score') or '0').strip())
        except (InvalidOperation, ValueError):
            exams_score = Decimal('0')
        # If wide-format subject columns found, create/update one grade per subject column
        if wide_subjects:
            for orig_col, subj in wide_subjects:
                raw_val = row.get(orig_col)
                try:
                    exams_val = Decimal(str(raw_val or '0').strip())
                except (InvalidOperation, ValueError):
                    exams_val = Decimal('0')
                cls_val = Decimal('0')

                if dry_run:
                    exists = Grade.objects.filter(student=student, subject=subj, academic_year=row_academic_year, term=term).exists()
                    if exists and update_existing:
                        details.append({'row': idx, 'subject_column': orig_col, 'status': 'would_update', 'message': 'grade exists and would be updated', 'data': {**data, 'subject': orig_col, 'exams_score': exams_val}})
                        updated += 1
                    else:
                        details.append({'row': idx, 'subject_column': orig_col, 'status': 'would_create', 'message': 'grade would be created', 'data': {**data, 'subject': orig_col, 'exams_score': exams_val}})
                        created += 1
                    continue

                grade, created_flag = Grade.objects.update_or_create(
                    student=student,
                    subject=subj,
                    academic_year=row_academic_year,
                    term=term,
                    defaults={
                        'class_score': cls_val,
                        'exams_score': exams_val,
                        'created_by': created_by or None,
                    }
                )
                if created_flag:
                    created += 1
                    details.append({'row': idx, 'subject_column': orig_col, 'status': 'created', 'message': 'created grade', 'student_id': student.id, 'data': {**data, 'subject': orig_col, 'exams_score': exams_val}})
                else:
                    updated += 1
                    details.append({'row': idx, 'subject_column': orig_col, 'status': 'updated', 'message': 'updated grade', 'student_id': student.id, 'data': {**data, 'subject': orig_col, 'exams_score': exams_val}})
            # after processing wide-format columns, continue to next row
            continue

        # narrow-format single-subject handling
        if dry_run:
            # Check if grade exists (use resolved academic year)
            exists = Grade.objects.filter(student=student, subject=subject, academic_year=row_academic_year, term=term).exists()
            if exists and update_existing:
                details.append({'row': idx, 'status': 'would_update', 'message': 'grade exists and would be updated', 'data': data})
                updated += 1
            else:
                details.append({'row': idx, 'status': 'would_create', 'message': 'grade would be created', 'data': data})
                created += 1
            continue

        # Actual DB write for narrow-format
        grade, created_flag = Grade.objects.update_or_create(
            student=student,
            subject=subject,
            academic_year=row_academic_year,
            term=term,
            defaults={
                'class_score': class_score,
                'exams_score': exams_score,
                'created_by': created_by or None,
            }
        )
        if created_flag:
            created += 1
            details.append({'row': idx, 'status': 'created', 'student_id': student.id, 'message': 'created grade', 'data': data})
        else:
            updated += 1
            details.append({'row': idx, 'status': 'updated', 'student_id': student.id, 'message': 'updated grade', 'data': data})

    return (created, updated, skipped, details)
