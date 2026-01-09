from students.models import Grade
from django.db.models import Sum


# Map various user-facing term labels to canonical values
_TERM_NORMALIZATION = {
    'first': 'first',
    'first term': 'first',
    '1': 'first',
    'second': 'second',
    'second term': 'second',
    '2': 'second',
    'third': 'third',
    'third term': 'third',
    '3': 'third',
}

_TERM_ALIASES_BY_CANONICAL = {
    'first': ['First Term', 'first term'],
    'second': ['Second Term', 'second term'],
    'third': ['Third Term', 'third term'],
}


def normalize_term(term: str) -> str:
    """Normalize incoming term strings to canonical values first|second|third."""
    if term is None:
        return 'first'
    key = str(term).strip().lower()
    return _TERM_NORMALIZATION.get(key, key or 'first')


def term_filter_values(term: str):
    """Return canonical term plus legacy aliases for querying."""
    canonical = normalize_term(term)
    aliases = _TERM_ALIASES_BY_CANONICAL.get(canonical, [])
    return [canonical] + aliases


def calculate_class_position(student, academic_year, term):
    """Calculate student's overall position in class for a given term."""

    if not student.current_class:
        return None

    term_values = term_filter_values(term)

    # Get all students in the same class
    students_in_class = student.current_class.student_set.all()

    # Calculate total scores for each student
    student_totals = []
    for s in students_in_class:
        total = Grade.objects.filter(
            student=s,
            academic_year=academic_year,
            term__in=term_values
        ).aggregate(total=Sum('total_score'))['total'] or 0

        student_totals.append({
            'student': s,
            'total': total
        })

    # Sort by total (descending)
    student_totals.sort(key=lambda x: x['total'], reverse=True)

    # Find position
    for position, data in enumerate(student_totals, start=1):
        if data['student'].id == student.id:
            return position

    return None