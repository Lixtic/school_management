"""
School Admin Dashboard Views
Separate from Django admin - this is a custom admin interface for school administrators
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .decorators import school_admin_required
from .forms import AddTeacherForm, AddStudentForm, AddParentForm
from students.models import Student, Grade, Attendance
from teachers.models import Teacher
from academics.models import Class, Subject, AcademicYear
from parents.models import Parent
from communications.models import Message
from schools.models import School

User = get_user_model()


@school_admin_required
def dashboard(request):
    """
    Main school admin dashboard
    Shows overview statistics and quick actions for the school
    """
    user = request.user
    school = user.school
    
    # Get current academic year
    current_year = AcademicYear.objects.filter(
        school=school, 
        is_current=True
    ).first()
    
    # Statistics
    total_students = Student.objects.filter(school=school).count()
    total_teachers = Teacher.objects.filter(school=school).count()
    total_classes = Class.objects.filter(school=school).count()
    total_subjects = Subject.objects.filter(school=school).count()
    total_parents = Parent.objects.filter(school=school).count()
    
    # Recent attendance (last 7 days)
    week_ago = timezone.now().date() - timedelta(days=7)
    recent_attendance = Attendance.objects.filter(
        school=school,
        date__gte=week_ago
    ).values('date', 'status').annotate(count=Count('id'))
    
    # Attendance statistics
    attendance_stats = Attendance.objects.filter(
        school=school,
        date__gte=week_ago
    ).aggregate(
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
        excused=Count('id', filter=Q(status='excused')),
    )
    
    total_attendance = sum(attendance_stats.values())
    attendance_percentage = (
        (attendance_stats['present'] * 100 / total_attendance)
        if total_attendance > 0 else 0
    )
    
    # Recent grades
    recent_grades = Grade.objects.filter(
        school=school,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).select_related('student__user', 'subject').order_by('-created_at')[:10]
    
    # Average performance
    if current_year:
        avg_performance = Grade.objects.filter(
            school=school,
            academic_year=current_year
        ).aggregate(avg_score=Avg('total_score'))['avg_score'] or 0
    else:
        avg_performance = 0
    
    # Unread messages
    unread_messages = Message.objects.filter(
        school=school,
        recipient=user,
        is_read=False
    ).count()
    
    # Recent students
    recent_students = Student.objects.filter(
        school=school
    ).select_related('user', 'current_class').order_by('-date_of_admission')[:5]
    
    # Classes with student count
    classes_data = Class.objects.filter(
        school=school
    ).annotate(
        student_count=Count('student')
    ).order_by('name')[:10]
    
    context = {
        'school': school,
        'current_year': current_year,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'total_parents': total_parents,
        'attendance_percentage': round(attendance_percentage, 1),
        'attendance_stats': attendance_stats,
        'avg_performance': round(avg_performance, 1),
        'unread_messages': unread_messages,
        'recent_grades': recent_grades,
        'recent_students': recent_students,
        'classes_data': classes_data,
    }
    
    return render(request, 'school_admin/dashboard.html', context)


@school_admin_required
def students_management(request):
    """Manage students - list, add, edit, delete"""
    school = request.user.school
    students = Student.objects.filter(
        school=school
    ).select_related('user', 'current_class').order_by('user__last_name')
    
    context = {
        'school': school,
        'students': students,
    }
    return render(request, 'school_admin/students_list.html', context)


@school_admin_required
def add_student(request):
    """Add a new student"""
    school = request.user.school
    
    if request.method == 'POST':
        form = AddStudentForm(request.POST, school=school)
        if form.is_valid():
            # Create user account
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                user_type='student',
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                school=school
            )
            
            # Create student profile
            student = form.save(commit=False)
            student.user = user
            student.school = school
            student.save()
            
            messages.success(
                request,
                f'Student {user.get_full_name()} added successfully!'
            )
            return redirect('school_admin:students')
    else:
        form = AddStudentForm(school=school)
    
    context = {
        'school': school,
        'form': form,
    }
    return render(request, 'school_admin/add_student.html', context)


@school_admin_required
def teachers_management(request):
    """Manage teachers - list, add, edit, delete"""
    school = request.user.school
    teachers = Teacher.objects.filter(
        school=school
    ).select_related('user').prefetch_related('subjects').order_by('user__last_name')
    
    context = {
        'school': school,
        'teachers': teachers,
    }
    return render(request, 'school_admin/teachers_list.html', context)


@school_admin_required
def add_teacher(request):
    """Add a new teacher"""
    school = request.user.school
    
    if request.method == 'POST':
        form = AddTeacherForm(request.POST, school=school)
        if form.is_valid():
            # Create user account
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                user_type='teacher',
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                school=school
            )
            
            # Create teacher profile
            teacher = form.save(commit=False)
            teacher.user = user
            teacher.school = school
            teacher.save()
            
            # Save many-to-many relationships (subjects)
            form.save_m2m()
            
            messages.success(
                request,
                f'Teacher {user.get_full_name()} added successfully!'
            )
            return redirect('school_admin:teachers')
    else:
        form = AddTeacherForm(school=school)
    
    context = {
        'school': school,
        'form': form,
    }
    return render(request, 'school_admin/add_teacher.html', context)


@school_admin_required
def classes_management(request):
    """Manage classes"""
    school = request.user.school
    classes = Class.objects.filter(
        school=school
    ).select_related('academic_year', 'class_teacher').annotate(
        student_count=Count('student')
    ).order_by('name')
    
    context = {
        'school': school,
        'classes': classes,
    }
    return render(request, 'school_admin/classes_list.html', context)


@school_admin_required
def subjects_management(request):
    """Manage subjects"""
    school = request.user.school
    subjects = Subject.objects.filter(school=school).order_by('name')
    
    context = {
        'school': school,
        'subjects': subjects,
    }
    return render(request, 'school_admin/subjects_list.html', context)


@school_admin_required
def attendance_overview(request):
    """Attendance overview and reports"""
    school = request.user.school
    
    # Get date range (default last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    attendance_data = Attendance.objects.filter(
        school=school,
        date__range=[start_date, end_date]
    ).values('date', 'status').annotate(count=Count('id')).order_by('date')
    
    context = {
        'school': school,
        'attendance_data': attendance_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'school_admin/attendance_overview.html', context)


@school_admin_required
def grades_overview(request):
    """Grades overview and reports"""
    school = request.user.school
    current_year = AcademicYear.objects.filter(
        school=school, 
        is_current=True
    ).first()
    
    if current_year:
        grades = Grade.objects.filter(
            school=school,
            academic_year=current_year
        ).select_related(
            'student__user', 'subject', 'academic_year'
        ).order_by('-created_at')[:50]
        
        # Subject-wise performance
        subject_performance = Grade.objects.filter(
            school=school,
            academic_year=current_year
        ).values(
            'subject__name'
        ).annotate(
            avg_score=Avg('total_score'),
            student_count=Count('student', distinct=True)
        ).order_by('-avg_score')
    else:
        grades = []
        subject_performance = []
    
    context = {
        'school': school,
        'current_year': current_year,
        'grades': grades,
        'subject_performance': subject_performance,
    }
    return render(request, 'school_admin/grades_overview.html', context)


@school_admin_required
def school_settings(request):
    """School settings and configuration"""
    school = request.user.school
    
    if request.method == 'POST':
        # Update school settings
        school.name = request.POST.get('name', school.name)
        school.email = request.POST.get('email', school.email)
        school.phone = request.POST.get('phone', school.phone)
        school.address = request.POST.get('address', school.address)
        school.website = request.POST.get('website', school.website)
        
        # Handle logo upload
        if request.FILES.get('logo'):
            school.logo = request.FILES['logo']
        
        school.save()
        messages.success(request, 'School settings updated successfully!')
        return redirect('school_admin:settings')
    
    context = {
        'school': school,
    }
    return render(request, 'school_admin/settings.html', context)


@school_admin_required
def reports(request):
    """Reports and analytics"""
    school = request.user.school
    current_year = AcademicYear.objects.filter(
        school=school, 
        is_current=True
    ).first()
    
    context = {
        'school': school,
        'current_year': current_year,
    }
    return render(request, 'school_admin/reports.html', context)


@school_admin_required
def parents_management(request):
    """Manage parents - list and view"""
    school = request.user.school
    parents = Parent.objects.filter(
        school=school
    ).select_related('user').prefetch_related('children__user').order_by('user__last_name')
    
    context = {
        'school': school,
        'parents': parents,
    }
    return render(request, 'school_admin/parents_list.html', context)


@school_admin_required
def add_parent(request):
    """Add a new parent"""
    school = request.user.school
    
    if request.method == 'POST':
        form = AddParentForm(request.POST, school=school)
        if form.is_valid():
            # Create user account
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                user_type='parent',
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                school=school
            )
            
            # Create parent profile
            parent = form.save(commit=False)
            parent.user = user
            parent.school = school
            parent.save()
            
            # Save many-to-many relationships (children)
            form.save_m2m()
            
            messages.success(
                request,
                f'Parent {user.get_full_name()} added successfully!'
            )
            return redirect('school_admin:parents')
    else:
        form = AddParentForm(school=school)
    
    context = {
        'school': school,
        'form': form,
    }
    return render(request, 'school_admin/add_parent.html', context)
