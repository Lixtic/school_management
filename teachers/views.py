from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from teachers.models import Teacher
from academics.models import ClassSubject, AcademicYear
from students.models import Student, Grade

@login_required
def teacher_classes(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    class_subjects = ClassSubject.objects.filter(teacher=teacher).select_related(
        'class_name', 'subject'
    )
    
    return render(request, 'teachers/my_classes.html', {'class_subjects': class_subjects})


@login_required
def enter_grades(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    class_subjects = ClassSubject.objects.filter(teacher=teacher).select_related(
        'class_name', 'subject'
    )
    
    if request.method == 'POST':
        term = request.POST.get('term')
        subject_id = request.POST.get('subject_id')
        student_ids = request.POST.getlist('student_id[]')
        
        academic_year = AcademicYear.objects.filter(is_current=True).first()
        
        for student_id in student_ids:
            class_score = request.POST.get(f'class_score_{student_id}')
            exams_score = request.POST.get(f'exams_score_{student_id}')
            
            # Create or update grade
            Grade.objects.update_or_create(
                student_id=student_id,
                subject_id=subject_id,
                academic_year=academic_year,
                term=term,
                defaults={
                    'class_score': class_score,
                    'exams_score': exams_score,
                    'created_by': request.user
                }
            )
        
        messages.success(request, f'Grades entered successfully for {len(student_ids)} students!')
        return redirect('teachers:enter_grades')
    
    return render(request, 'teachers/enter_grades.html', {'class_subjects': class_subjects})


@login_required
def get_students(request, class_id):
    students = Student.objects.filter(current_class_id=class_id).select_related('user')
    data = [
        {
            'id': s.id,
            'name': s.user.get_full_name(),
            'admission_number': s.admission_number
        }
        for s in students
    ]
    return JsonResponse(data, safe=False)