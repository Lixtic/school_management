from students.models import Grade
from django.db.models import Sum

def calculate_class_position(student, academic_year, term):
    """Calculate student's overall position in class for a given term"""
    
    if not student.current_class:
        return None
    
    # Get all students in the same class
    students_in_class = student.current_class.student_set.all()
    
    # Calculate total scores for each student
    student_totals = []
    for s in students_in_class:
        total = Grade.objects.filter(
            student=s,
            academic_year=academic_year,
            term=term
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