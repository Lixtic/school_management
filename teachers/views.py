from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
import django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from teachers.models import Teacher, DutyWeek
from academics.models import ClassSubject, AcademicYear, Timetable, SchoolInfo, Resource
from students.models import Student, Grade, ClassExercise, StudentExerciseScore
from students.utils import normalize_term
from .forms import ResourceForm

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


@login_required
def teacher_schedule(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')

    # Get all schedule entries for this teacher/class-subject
    timetable_qs = Timetable.objects.filter(class_subject__teacher=teacher).select_related(
        'class_subject', 'class_subject__class_name', 'class_subject__subject'
    ).order_by('day', 'start_time')
    
    # Organize by day for simpler template loop
    days_data = []
    # Timetable.DAY_CHOICES is ((0,'Monday'), ...)
    for code, name in Timetable.DAY_CHOICES:
        # Filter in python to avoid N queries, 
        # or just filter in loop if list is short. 
        # Since timetable_qs is likely small ( < 50 items), list filter is fine.
        entries = [t for t in timetable_qs if t.day == code]
        days_data.append({
            'name': name,
            'entries': entries
        })
            
    return render(request, 'teachers/schedule.html', {'days': days_data})

@login_required
def print_duty_roster(request):
    # Only Admin or Teachers can see this? Assuming Admin/Staff.
    # if request.user.user_type not in ['admin', 'teacher']: ...
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        current_year = AcademicYear.objects.first()

    from django.utils import timezone
    today = timezone.now().date()
    # Auto-detect term if not provided
    req_term = request.GET.get('term')
    if req_term:
        term = req_term
    else:
        # Default based on active duty week
        current_week = DutyWeek.objects.filter(
            academic_year=current_year,
            start_date__lte=today,
            end_date__gte=today
        ).first()
        term = current_week.term if current_week else ('Second' if 1 <= today.month <= 4 else ('Third' if 5 <= today.month <= 8 else 'First'))

    year_id = request.GET.get('year', current_year.id if current_year else None)
    
    if year_id:
        year = get_object_or_404(AcademicYear, id=year_id)
    else:
        year = None

    weeks = DutyWeek.objects.filter(academic_year=year, term=term).prefetch_related('assignments', 'assignments__teacher', 'assignments__teacher__user').order_by('week_number')
    
    context = {
        'weeks': weeks,
        'year': year,
        'term': term,
        'school_info': SchoolInfo.objects.first(),
        'available_terms': ['First', 'Second', 'Third'],
        'academic_years': AcademicYear.objects.all(),
    }
    return render(request, 'teachers/duty_roster_pdf.html', context)


@login_required
def manage_exercises(request, class_subject_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    class_subject = get_object_or_404(ClassSubject, id=class_subject_id, teacher=teacher)
    
    term = request.GET.get('term', 'first')
    
    exercises = ClassExercise.objects.filter(
        class_subject=class_subject,
        term=term
    ).order_by('-date_assigned')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        max_marks = request.POST.get('max_marks')
        term_input = request.POST.get('term')
        
        if title and max_marks:
            ClassExercise.objects.create(
                class_subject=class_subject,
                term=term_input,
                title=title,
                max_marks=max_marks
            )
            messages.success(request, 'Exercise created successfully.')
            return redirect(f"{request.path}?term={term_input}")

    # Helper for term names
    term_choices = Grade.TERM_CHOICES

    return render(request, 'teachers/manage_exercises.html', {
        'class_subject': class_subject,
        'exercises': exercises,
        'selected_term': term,
        'term_choices': term_choices,
    })


@login_required
def enter_exercise_scores(request, exercise_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    exercise = get_object_or_404(ClassExercise, id=exercise_id, class_subject__teacher=teacher)
    
    students = Student.objects.filter(current_class=exercise.class_subject.class_name).order_by('user__last_name')
    
    if request.method == 'POST':
        try:
            with django.db.transaction.atomic():
                updated_count = 0
                for student in students:
                    score_val = request.POST.get(f'score_{student.id}')
                    remarks_val = request.POST.get(f'remarks_{student.id}', '')
                    
                    if score_val:
                        try:
                            score = Decimal(score_val)
                            score = max(Decimal('0'), min(score, exercise.max_marks))
                            
                            StudentExerciseScore.objects.update_or_create(
                                student=student,
                                exercise=exercise,
                                defaults={'score': score, 'remarks': remarks_val}
                            )
                            updated_count += 1
                        except (InvalidOperation, TypeError):
                            continue
                
                # RECALCULATION LOGIC
                all_exercises = ClassExercise.objects.filter(
                    class_subject=exercise.class_subject,
                    term=exercise.term
                )
                total_possible = sum(ex.max_marks for ex in all_exercises)
                
                if total_possible > 0:
                    current_year = AcademicYear.objects.filter(is_current=True).first()
                    if not current_year:
                        current_year = AcademicYear.objects.order_by('-start_date').first()

                    # Pre-fetch all scores for this subject/term to avoid N+1 inside loop if possible 
                    # but simple iteration is fine for class size < 50
                    
                    for student in students:
                        student_scores = StudentExerciseScore.objects.filter(
                            student=student,
                            exercise__in=all_exercises
                        ).aggregate(total=models.Sum('score'))['total'] or Decimal('0')
                        
                        # (Obtained / Possible) * 30
                        new_class_score = (student_scores / total_possible) * Decimal('30')
                        
                        grade_obj, _ = Grade.objects.get_or_create(
                            student=student,
                            subject=exercise.class_subject.subject,
                            academic_year=current_year,
                            term=exercise.term,
                            defaults={'created_by': request.user}
                        )
                        grade_obj.class_score = new_class_score
                        grade_obj.save()

            messages.success(request, f'Scores saved for {updated_count} students. Class assessment totals updated.')
        except Exception as e:
            messages.error(request, f"Error saving scores: {e}")
            
        return redirect('teachers:enter_exercise_scores', exercise_id=exercise.id)

    existing_scores = StudentExerciseScore.objects.filter(exercise=exercise)
    score_map = {s.student_id: s for s in existing_scores}
    
    student_list = []
    for s in students:
        student_list.append({
            'student': s,
            'score_obj': score_map.get(s.id)
        })

    return render(request, 'teachers/enter_exercise_scores.html', {
        'exercise': exercise,
        'student_list': student_list,
    })


@login_required
def search_students(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    query = request.GET.get('q', '').strip()
    students = []
    
    if query:
        students = Student.objects.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) |
            Q(admission_number__icontains=query)
        ).select_related('user', 'current_class').distinct()[:20]
        
    return render(request, 'teachers/search_results.html', {
        'query': query,
        'students': students,
        'school_name': SchoolInfo.objects.first().name if SchoolInfo.objects.exists() else 'School'
    })


@login_required
def class_resources(request, class_subject_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    class_subject = get_object_or_404(ClassSubject, id=class_subject_id, teacher=teacher)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.class_subject = class_subject
            resource.save()
            messages.success(request, 'Resource uploaded successfully.')
            return redirect('teachers:class_resources', class_subject_id=class_subject.id)
    else:
        form = ResourceForm()
        
    resources = Resource.objects.filter(class_subject=class_subject).order_by('-uploaded_at')
    
    return render(request, 'teachers/class_resources.html', {
        'class_subject': class_subject,
        'resources': resources,
        'form': form,
    })

@login_required
def delete_resource(request, resource_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
        
    resource = get_object_or_404(Resource, id=resource_id, class_subject__teacher__user=request.user)
    class_subject_id = resource.class_subject.id
    resource.delete()
    messages.success(request, 'Resource deleted successfully.')
    return redirect('teachers:class_resources', class_subject_id=class_subject_id)

