"""
Global Search Views
Provides API endpoint for searching across the system
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from students.models import Student
from teachers.models import Teacher
from academics.models import Class, Subject
from django.urls import reverse


@login_required
def global_search_api(request):
    """
    API endpoint for global search
    Searches across students, teachers, classes, and subjects
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({
            'results': [],
            'message': 'Query too short'
        })
    
    results = []
    
    # Search Students (if user has permission)
    if request.user.user_type in ['admin', 'teacher']:
        students = Student.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(email__icontains=query)
        ).select_related('current_class', 'user')[:10]
        
        for student in students:
            results.append({
                'type': 'students',
                'title': f"{student.first_name} {student.last_name}",
                'subtitle': f"ID: {student.student_id} | Class: {student.current_class.name if student.current_class else 'N/A'}",
                'url': reverse('students:student_list'),  # Update with actual student detail URL
                'grades_url': reverse('students:student_list'),  # Update with grades URL
                'attendance_url': reverse('students:student_list'),  # Update with attendance URL
            })
    
    # Search Teachers (if user has permission)
    if request.user.user_type in ['admin']:
        teachers = Teacher.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(email__icontains=query) |
            Q(specialization__icontains=query)
        ).select_related('user')[:10]
        
        for teacher in teachers:
            results.append({
                'type': 'teachers',
                'title': f"{teacher.first_name} {teacher.last_name}",
                'subtitle': f"ID: {teacher.employee_id} | {teacher.specialization or 'General'}",
                'url': reverse('teachers:teacher_list'),  # Update with actual teacher detail URL
                'schedule_url': reverse('teachers:teacher_list'),  # Update with schedule URL
            })
    
    # Search Classes
    classes = Class.objects.filter(
        Q(name__icontains=query) |
        Q(academic_year__year_name__icontains=query)
    ).select_related('academic_year', 'class_teacher')[:10]
    
    for cls in classes:
        teacher_name = f"{cls.class_teacher.first_name} {cls.class_teacher.last_name}" if cls.class_teacher else "No teacher"
        results.append({
            'type': 'classes',
            'title': cls.name,
            'subtitle': f"{cls.academic_year.year_name} | Teacher: {teacher_name}",
            'url': f'/academics/classes/{cls.id}/',  # Update with actual class detail URL
            'students_url': f'/academics/classes/{cls.id}/students/',  # Update with students URL
        })
    
    # Search Subjects
    subjects = Subject.objects.filter(
        Q(name__icontains=query) |
        Q(code__icontains=query)
    )[:10]
    
    for subject in subjects:
        results.append({
            'type': 'subjects',
            'title': subject.name,
            'subtitle': f"Code: {subject.code}",
            'url': f'/academics/subjects/{subject.id}/',  # Update with actual subject detail URL
        })
    
    return JsonResponse({
        'results': results,
        'total': len(results),
        'query': query
    })
