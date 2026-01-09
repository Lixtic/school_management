from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from teachers.models import Teacher
from academics.models import ClassSubject, AcademicYear
from students.models import Student, Grade
from students.utils import normalize_term

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
    class_subjects = ClassSubject.objects.filter(teacher=teacher).select_related('class_name', 'subject')
    selected_cs_id = request.GET.get('class_subject_id')
    
    if request.method == 'POST':
        term = normalize_term(request.POST.get('term', 'first'))
        class_subject_id = request.POST.get('class_subject_id') or request.POST.get('class_subject')
        student_ids = request.POST.getlist('student_id[]') or request.POST.getlist('student_id')

        academic_year = AcademicYear.objects.filter(is_current=True).first()
        if not academic_year:
            messages.error(request, 'No academic year is marked as current.')
            return redirect('teachers:enter_grades')

        try:
            cs = class_subjects.get(id=class_subject_id)
        except ClassSubject.DoesNotExist:
            messages.error(request, 'Invalid class/subject selection.')
            return redirect('teachers:enter_grades')

        created_count = 0
        for student_id in student_ids:
            overall_raw = request.POST.get(f'overall_score_{student_id}')
            class_score_raw = request.POST.get(f'class_score_{student_id}', '')
            exams_score_raw = request.POST.get(f'exams_score_{student_id}', '')

            class_score = exams_score = None

            # Prefer the explicit class/exam fields; fall back to overall if needed
            try:
                if class_score_raw != '' and exams_score_raw != '':
                    class_score = Decimal(class_score_raw)
                    exams_score = Decimal(exams_score_raw)
                elif overall_raw not in (None, ''):
                    overall = Decimal(overall_raw)
                    overall = max(Decimal('0'), min(overall, Decimal('100')))
                    class_score = overall * Decimal('0.3')
                    exams_score = overall * Decimal('0.7')
                else:
                    continue
            except (InvalidOperation, TypeError):
                continue

            # Server-side validation of maxima
            class_score = max(Decimal('0'), min(class_score, Decimal('30')))
            exams_score = max(Decimal('0'), min(exams_score, Decimal('70')))

            Grade.objects.update_or_create(
                student_id=student_id,
                subject=cs.subject,
                academic_year=academic_year,
                term=term,
                defaults={
                    'class_score': class_score,
                    'exams_score': exams_score,
                    'created_by': request.user
                }
            )
            created_count += 1

        if created_count == 0:
            messages.warning(request, 'No grades were saved. Please ensure you loaded students and entered scores.')
        else:
            messages.success(request, f'Grades entered/updated for {created_count} students in {cs.class_name} - {cs.subject}.')
        return redirect('teachers:enter_grades')
    
    return render(request, 'teachers/enter_grades.html', {
        'class_subjects': class_subjects,
        'selected_cs_id': selected_cs_id,
    })


@login_required
def get_students(request, class_id):
    subject_id = request.GET.get('subject_id')
    term = normalize_term(request.GET.get('term', 'first'))

    students = Student.objects.filter(current_class_id=class_id).select_related('user')

    academic_year = AcademicYear.objects.filter(is_current=True).first()
    grades_by_student = {}
    if academic_year and subject_id:
        grades = Grade.objects.filter(
            student__current_class_id=class_id,
            subject_id=subject_id,
            academic_year=academic_year,
            term=term,
        )
        grades_by_student = {g.student_id: g for g in grades}

    data = []
    for s in students:
        g = grades_by_student.get(s.id)
        data.append({
            'id': s.id,
            'name': s.user.get_full_name(),
            'admission_number': s.admission_number,
            'class_score': str(g.class_score) if g else '',
            'exams_score': str(g.exams_score) if g else '',
            'total_score': str(g.total_score) if g else '',
            'grade': g.grade if g else '',
            'remarks': g.remarks if g else '',
        })

    return JsonResponse(data, safe=False)