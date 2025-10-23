from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Schedule, Class, ClassSubject
from .auto_scheduler import auto_schedule_all_classes
from django.db.models import Prefetch
from .utils import get_timetable_slots

@login_required
def view_timetable(request):
    """View class schedule for teachers, students, and admins"""
    user = request.user
    context = {}
    
    if user.user_type == 'admin':
        # School admins can view all classes in their school
        classes = Class.objects.filter(school=user.school).prefetch_related(
            Prefetch(
                'classsubject_set',
                queryset=ClassSubject.objects.select_related('subject', 'teacher', 'teacher__user')
            )
        )
        
        # Get all schedules for the school
        schedules = Schedule.objects.filter(
            class_subject__school=user.school
        ).select_related(
            'class_subject',
            'class_subject__subject',
            'class_subject__class_name',
            'class_subject__teacher',
            'class_subject__teacher__user'
        )
        
        context.update({
            'classes': classes,
            'schedules': schedules,
            'days': Schedule.DAYS_OF_WEEK
        })
        template = 'academics/admin_timetable.html'
        
    elif user.user_type == 'teacher':
        # Get all classes where this teacher teaches
        class_subjects = ClassSubject.objects.filter(
            teacher__user=user
        ).select_related('class_name', 'subject')
        
        # Get schedules for these classes
        schedules = Schedule.objects.filter(
            class_subject__in=class_subjects
        ).select_related(
            'class_subject',
            'class_subject__subject',
            'class_subject__class_name'
        )
        
        time_slots = []
        for slot in get_timetable_slots():
            time_slots.append({
                'start': slot['start'],
                'end': slot['end'],
                'label': slot['label'],
                'classes': {}
            })
        
        # Organize schedules by time slot and day
        for schedule in schedules:
            for slot in time_slots:
                if slot['start'] <= schedule.start_time < slot['end']:
                    day_classes = slot['classes'].setdefault(schedule.day, [])
                    day_classes.append({
                        'subject': schedule.class_subject.subject.name,
                        'class_name': schedule.class_subject.class_name.name
                    })
                    break
        
        # Sort entries for consistent ordering
        for slot in time_slots:
            for day_code in slot['classes']:
                slot['classes'][day_code].sort(key=lambda item: (item['class_name'], item['subject']))
        
        context.update({
            'time_slots': time_slots,
            'days': Schedule.DAYS_OF_WEEK
        })
        template = 'academics/teacher_timetable.html'
        
    elif user.user_type == 'student':
        # Get student's class schedule
        try:
            student = user.student
            if student.current_class:
                schedules = Schedule.objects.filter(
                    class_subject__class_name=student.current_class
                ).select_related('class_subject', 'class_subject__subject', 
                               'class_subject__teacher', 'class_subject__teacher__user')
                context['schedules'] = schedules
                template = 'academics/student_timetable.html'
            else:
                messages.warning(request, 'You are not assigned to any class yet.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    else:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    return render(request, template, context)


@login_required
def class_timetable(request, class_id):
    """View timetable for a specific class"""
    try:
        class_obj = Class.objects.get(id=class_id)
        
        # Check if user has permission to view this class's timetable
        if request.user.user_type == 'admin':
            # Admins can view any class in their school
            if class_obj.school_id != request.user.school_id:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        elif request.user.user_type == 'teacher':
            if not ClassSubject.objects.filter(
                class_name=class_obj,
                teacher__user=request.user
            ).exists():
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        elif request.user.user_type == 'student':
            if request.user.student.current_class_id != class_id:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        
        schedules = Schedule.objects.filter(
            class_subject__class_name=class_obj
        ).select_related('class_subject', 'class_subject__subject', 
                        'class_subject__teacher', 'class_subject__teacher__user')
        
        # Create timetable grid
        timetable = {}
        for day_code, day_name in Schedule.DAYS_OF_WEEK:
            timetable[day_code] = {i: None for i in range(1, 9)}  # 8 periods per day
        
        # Fill in the timetable
        for schedule in schedules:
            timetable[schedule.day][schedule.period] = {
                'subject': schedule.class_subject.subject.name,
                'teacher': schedule.class_subject.teacher.user.get_full_name(),
                'start_time': schedule.start_time.strftime('%I:%M %p'),
                'end_time': schedule.end_time.strftime('%I:%M %p'),
            }
        
        context = {
            'class': class_obj,
            'timetable': timetable,
            'days': dict(Schedule.DAYS_OF_WEEK),
            'periods': range(1, 9)
        }
        
        return render(request, 'academics/class_timetable.html', context)
        
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('dashboard')


@login_required
def auto_schedule_view(request):
    """Auto generate schedules for all classes"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Only administrators can auto-generate schedules.')
        return redirect('dashboard')
    
    context = {}
    
    if request.method == 'POST':
        try:
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            period_duration = int(request.POST.get('period_duration', 45))
            break_periods = [int(p.strip()) for p in request.POST.get('break_periods', '3,6').split(',')]
            
            success = auto_schedule_all_classes(
                start_time=start_time,
                end_time=end_time,
                period_duration=period_duration,
                break_periods=break_periods
            )
            
            if success:
                messages.success(request, 'Schedules generated successfully!')
                # Get all schedules to display
                context['schedules'] = Schedule.objects.all().select_related(
                    'class_subject',
                    'class_subject__class_name',
                    'class_subject__subject',
                    'class_subject__teacher',
                    'class_subject__teacher__user'
                ).order_by(
                    'class_subject__class_name',
                    'day',
                    'period'
                )
                context['generated'] = True
            else:
                messages.error(request, 'Failed to generate schedules. Please try different parameters.')
            
            # Pass back the form values
            context.update({
                'start_time': start_time,
                'end_time': end_time,
                'period_duration': period_duration,
                'break_periods': ','.join(map(str, break_periods))
            })
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'academics/auto_schedule.html', context)


# ========== ACADEMIC YEAR MANAGEMENT ==========

@login_required
def academic_year_list(request):
    """List all academic years for the school"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can manage academic years.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .models import AcademicYear
    academic_years = AcademicYear.objects.filter(school=school).order_by('-is_current', '-start_date')
    
    return render(request, 'academics/academic_year_list.html', {'academic_years': academic_years})


@login_required
def create_academic_year(request):
    """Create a new academic year"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can create academic years.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import AcademicYearForm
    
    if request.method == 'POST':
        form = AcademicYearForm(request.POST, school=school)
        if form.is_valid():
            academic_year = form.save(commit=False)
            academic_year.school = school
            academic_year.save()
            messages.success(request, f'Academic year {academic_year.name} created successfully!')
            return redirect('academics:academic_year_list')
    else:
        form = AcademicYearForm(school=school)
    
    return render(request, 'academics/academic_year_form.html', {'form': form, 'action': 'Create'})


@login_required
def update_academic_year(request, pk):
    """Update an academic year"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can update academic years.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .models import AcademicYear
    from .forms import AcademicYearForm
    
    try:
        academic_year = AcademicYear.objects.get(pk=pk, school=school)
    except AcademicYear.DoesNotExist:
        messages.error(request, 'Academic year not found.')
        return redirect('academics:academic_year_list')
    
    if request.method == 'POST':
        form = AcademicYearForm(request.POST, instance=academic_year, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'Academic year {academic_year.name} updated successfully!')
            return redirect('academics:academic_year_list')
    else:
        form = AcademicYearForm(instance=academic_year, school=school)
    
    return render(request, 'academics/academic_year_form.html', {
        'form': form,
        'action': 'Update',
        'academic_year': academic_year
    })


@login_required
def delete_academic_year(request, pk):
    """Delete an academic year"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can delete academic years.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .models import AcademicYear
    
    try:
        academic_year = AcademicYear.objects.get(pk=pk, school=school)
        name = academic_year.name
        academic_year.delete()
        messages.success(request, f'Academic year {name} deleted successfully!')
    except AcademicYear.DoesNotExist:
        messages.error(request, 'Academic year not found.')
    
    return redirect('academics:academic_year_list')


# ========== CLASS MANAGEMENT ==========

@login_required
def class_list(request):
    """List all classes for the school"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can manage classes.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    classes = Class.objects.filter(school=school).select_related('academic_year', 'class_teacher__user').order_by('name')
    
    return render(request, 'academics/class_list.html', {'classes': classes})


@login_required
def create_class(request):
    """Create a new class"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can create classes.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import ClassForm
    
    if request.method == 'POST':
        form = ClassForm(request.POST, school=school)
        if form.is_valid():
            class_obj = form.save(commit=False)
            class_obj.school = school
            class_obj.save()
            messages.success(request, f'Class {class_obj.name} created successfully!')
            return redirect('academics:class_list')
    else:
        form = ClassForm(school=school)
    
    return render(request, 'academics/class_form.html', {'form': form, 'action': 'Create'})


@login_required
def update_class(request, pk):
    """Update a class"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can update classes.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import ClassForm
    
    try:
        class_obj = Class.objects.get(pk=pk, school=school)
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('academics:class_list')
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'Class {class_obj.name} updated successfully!')
            return redirect('academics:class_list')
    else:
        form = ClassForm(instance=class_obj, school=school)
    
    return render(request, 'academics/class_form.html', {
        'form': form,
        'action': 'Update',
        'class': class_obj
    })


@login_required
def delete_class(request, pk):
    """Delete a class"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can delete classes.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    try:
        class_obj = Class.objects.get(pk=pk, school=school)
        name = class_obj.name
        class_obj.delete()
        messages.success(request, f'Class {name} deleted successfully!')
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
    
    return redirect('academics:class_list')


# ========== SUBJECT MANAGEMENT ==========

@login_required
def subject_list(request):
    """List all subjects for the school"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can manage subjects.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .models import Subject
    subjects = Subject.objects.filter(school=school).order_by('name')
    
    return render(request, 'academics/subject_list.html', {'subjects': subjects})


@login_required
def create_subject(request):
    """Create a new subject"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can create subjects.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import SubjectForm
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, school=school)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.school = school
            subject.save()
            messages.success(request, f'Subject {subject.name} created successfully!')
            return redirect('academics:subject_list')
    else:
        form = SubjectForm(school=school)
    
    return render(request, 'academics/subject_form.html', {'form': form, 'action': 'Create'})


@login_required
def update_subject(request, pk):
    """Update a subject"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can update subjects.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .models import Subject
    from .forms import SubjectForm
    
    try:
        subject = Subject.objects.get(pk=pk, school=school)
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found.')
        return redirect('academics:subject_list')
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject {subject.name} updated successfully!')
            return redirect('academics:subject_list')
    else:
        form = SubjectForm(instance=subject, school=school)
    
    return render(request, 'academics/subject_form.html', {
        'form': form,
        'action': 'Update',
        'subject': subject
    })


@login_required
def delete_subject(request, pk):
    """Delete a subject"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can delete subjects.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .models import Subject
    
    try:
        subject = Subject.objects.get(pk=pk, school=school)
        name = subject.name
        subject.delete()
        messages.success(request, f'Subject {name} deleted successfully!')
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found.')
    
    return redirect('academics:subject_list')
