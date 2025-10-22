from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from teachers.models import Teacher
from academics.models import ClassSubject, AcademicYear
from students.models import Student, Grade
from students.forms import GradesCsvUploadForm
import pandas as pd
import load_sample_data
from django.conf import settings
from pathlib import Path
import time
import os

@login_required
def teacher_classes(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    school = request.user.school
    
    try:
        teacher = Teacher.objects.get(user=request.user, school=school)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found. Please contact administrator.')
        return redirect('dashboard')
    class_subjects = ClassSubject.objects.filter(
        teacher=teacher,
        school=school
    ).select_related('class_name', 'subject')
    
    return render(request, 'teachers/my_classes.html', {'class_subjects': class_subjects})


@login_required
def my_classes(request):
    """Compatibility wrapper: some URLs or templates may reference `my_classes`.
    Delegate to the main `teacher_classes` view to keep behavior consistent.
    """
    return teacher_classes(request)


@login_required
def enter_grades(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    school = request.user.school
    try:
        teacher = Teacher.objects.get(user=request.user, school=school)
    except Teacher.DoesNotExist:
        messages.error(request, 'You are not registered as a teacher in this school.')
        return redirect('dashboard')
    
    class_subjects = ClassSubject.objects.filter(
        teacher=teacher,
        school=school
    ).select_related('class_name', 'subject')
    
    if request.method == 'POST':
        term = request.POST.get('term')
        subject_id = request.POST.get('subject_id')
        student_ids = request.POST.getlist('student_id[]')
        
        academic_year = AcademicYear.objects.filter(school=school, is_current=True).first()
        
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
                    'created_by': request.user,
                    'school': school  # Set school on grade
                }
            )
        
        messages.success(request, f'Grades entered successfully for {len(student_ids)} students!')
        return redirect('teachers:enter_grades')
    
    return render(request, 'teachers/enter_grades.html', {'class_subjects': class_subjects})


@login_required
def get_students(request, class_id):
    # Filter by school
    students = Student.objects.filter(
        current_class_id=class_id,
        school=request.user.school
    ).select_related('user')
    data = [
        {
            'id': s.id,
            'name': s.user.get_full_name(),
            'admission_number': s.admission_number
        }
        for s in students
    ]
    return JsonResponse(data, safe=False)


@login_required
def import_grades_csv(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')

    if request.method == 'POST':
        form = GradesCsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            update_existing = form.cleaned_data.get('update_existing', True)
            academic_year_val = form.cleaned_data.get('academic_year')
            class_id_val = form.cleaned_data.get('class_id') if 'class_id' in form.cleaned_data else None
            confirm = request.POST.get('confirm') == 'on'
            tmp_token = request.POST.get('tmp_token')
            try:
                tmp_dir = Path(getattr(settings, 'MEDIA_ROOT', 'media')) / 'tmp_imports'
                tmp_dir.mkdir(parents=True, exist_ok=True)

                # If confirm and a tmp token exists, use that temp file instead of re-upload
                if confirm and tmp_token:
                    tmp_path = tmp_dir / tmp_token
                    if not tmp_path.exists():
                        messages.error(request, 'Temporary upload not found; please re-upload the CSV and preview again.')
                        return redirect('teachers:import_grades_csv')
                    df = pd.read_csv(tmp_path)
                else:
                    # Save uploaded file to temp for confirmation step
                    timestamp = int(time.time())
                    token = f"grades_{request.user.id}_{timestamp}.csv"
                    tmp_path = tmp_dir / token
                    with open(tmp_path, 'wb') as f:
                        for chunk in csv_file.chunks():
                            f.write(chunk)
                    df = pd.read_csv(tmp_path)


                # enforce required selection
                if not academic_year_val or not class_id_val:
                    messages.error(request, 'Please select Academic Year and Class before uploading.')
                    return redirect('teachers:import_grades_csv')

                # resolve academic year
                ay_obj = None
                try:
                    from academics.models import AcademicYear
                    ay_obj = AcademicYear.objects.filter(id=int(academic_year_val)).first()
                except Exception:
                    ay_obj = None

                # resolve class if provided
                class_obj = None
                if class_id_val:
                    try:
                        from academics.models import Class as SchoolClass
                        class_obj = SchoolClass.objects.filter(id=int(class_id_val)).first()
                    except Exception:
                        class_obj = None

                # preview (dry-run)
                preview = load_sample_data.import_grades_from_dataframe(df, academic_year=ay_obj, class_obj=class_obj, update_existing=update_existing, dry_run=True)
                p_created = p_updated = p_skipped = 0
                p_details = []
                if isinstance(preview, tuple) and len(preview) == 4:
                    p_created, p_updated, p_skipped, p_details = preview
                else:
                    try:
                        p_created = preview[0]
                        p_updated = preview[1]
                        p_skipped = preview[2]
                        p_details = preview[3]
                    except Exception:
                        p_details = []

                if confirm:
                    # perform actual import (will call the real importer if present)
                    res = load_sample_data.import_grades_from_dataframe(df, academic_year=ay_obj, class_obj=class_obj, update_existing=update_existing, dry_run=False, created_by=request.user)
                    created = res[0] if len(res) > 0 else 0
                    updated = res[1] if len(res) > 1 else 0
                    skipped = res[2] if len(res) > 2 else 0
                    details = res[3] if len(res) > 3 else []
                    student_ids = sorted({d.get('student_id') for d in details if d.get('student_id')})
                    context = {'created': created, 'updated': updated, 'skipped': skipped, 'details': details, 'confirmed': True, 'affected_student_ids': student_ids}
                    return render(request, 'teachers/import_grades_result.html', context)

                context = {'preview_created': p_created, 'preview_updated': p_updated, 'preview_skipped': p_skipped, 'preview_details': p_details, 'confirmed': False, 'form': form}
                return render(request, 'teachers/import_grades_result.html', context)
            except Exception as e:
                messages.error(request, f'Import failed: {e}')
    else:
        form = GradesCsvUploadForm()

    return render(request, 'teachers/import_grades.html', {'form': form})


@login_required
def register_teacher(request):
    """View for registering a new teacher - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can register teachers.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import TeacherRegistrationForm
    
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, school=school)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Teacher {teacher.user.get_full_name()} registered successfully!')
            return redirect('teachers:list')
    else:
        form = TeacherRegistrationForm(school=school)
    
    return render(request, 'teachers/register_teacher.html', {'form': form})


@login_required
def teacher_list(request):
    """View to list all teachers in the school"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can view teacher list.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    teachers = Teacher.objects.filter(school=school).select_related('user').prefetch_related('subjects')
    
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers})


@login_required
def update_teacher(request, teacher_id):
    """View for updating teacher information - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can update teachers.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import TeacherUpdateForm
    
    try:
        teacher = Teacher.objects.get(id=teacher_id, school=school)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher not found.')
        return redirect('teachers:list')
    
    if request.method == 'POST':
        form = TeacherUpdateForm(request.POST, instance=teacher, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'Teacher {teacher.user.get_full_name()} updated successfully!')
            return redirect('teachers:list')
    else:
        form = TeacherUpdateForm(instance=teacher, school=school)
    
    return render(request, 'teachers/update_teacher.html', {'form': form, 'teacher': teacher})


@login_required
def delete_teacher(request, teacher_id):
    """View for deleting a teacher - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can delete teachers.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    try:
        teacher = Teacher.objects.get(id=teacher_id, school=school)
        teacher_name = teacher.user.get_full_name()
        
        # Delete associated user account
        user = teacher.user
        teacher.delete()
        if user:
            user.delete()
        
        messages.success(request, f'Teacher {teacher_name} deleted successfully!')
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher not found.')
    
    return redirect('teachers:list')