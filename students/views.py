from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg
from datetime import date, timedelta
import csv
from .models import Student, Attendance, Grade
from academics.models import Class, AcademicYear

@login_required
def student_list(request):
    if request.user.user_type not in ['admin', 'teacher']:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Filter by current user's school
    school = request.user.school
    students = Student.objects.select_related('user', 'current_class').filter(school=school)
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(admission_number__icontains=search)
        )
    
    # Filter by class
    class_filter = request.GET.get('class', '')
    if class_filter:
        students = students.filter(current_class_id=class_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'name':
        students = students.order_by('user__first_name', 'user__last_name')
    elif sort_by == '-name':
        students = students.order_by('-user__first_name', '-user__last_name')
    elif sort_by == 'admission_number':
        students = students.order_by('admission_number')
    elif sort_by == '-admission_number':
        students = students.order_by('-admission_number')
    
    # Statistics (filtered by school)
    total_students = Student.objects.filter(school=school).count()
    active_students = Student.objects.filter(school=school, user__is_active=True).count()
    total_classes = Class.objects.filter(school=school, academic_year__is_current=True).count()
    classes = Class.objects.filter(school=school, academic_year__is_current=True)
    
    context = {
        'students': students,
        'total_students': total_students,
        'active_students': active_students,
        'total_classes': total_classes,
        'classes': classes,
    }
    
    return render(request, 'students/student_list.html', context)


@login_required
def student_details_ajax(request, student_id):
    """Return student details as JSON for modal"""
    # Ensure student belongs to user's school
    student = get_object_or_404(Student, id=student_id, school=request.user.school)
    
    # Attendance stats (filtered by school)
    total_attendance = Attendance.objects.filter(student=student, school=request.user.school).count()
    present_count = Attendance.objects.filter(student=student, school=request.user.school, status='present').count()
    absent_count = Attendance.objects.filter(student=student, school=request.user.school, status='absent').count()
    
    attendance_percentage = 0
    if total_attendance > 0:
        attendance_percentage = round((present_count / total_attendance) * 100, 2)
    
    # Grade stats
    grades = Grade.objects.filter(student=student)
    grades_count = grades.count()
    
    average_percentage = 0
    if grades.exists():
        total_percentage = sum([g.percentage() for g in grades])
        average_percentage = round(total_percentage / grades_count, 2)
    
    data = {
        'name': student.user.get_full_name(),
        'admission_number': student.admission_number,
        'date_of_birth': student.date_of_birth.strftime('%B %d, %Y'),
        'current_class': str(student.current_class) if student.current_class else None,
        'email': student.user.email,
        'emergency_contact': student.emergency_contact,
        'blood_group': student.blood_group,
        'attendance': {
            'present': present_count,
            'absent': absent_count,
            'total': total_attendance,
            'percentage': attendance_percentage
        },
        'grades_count': grades_count,
        'average_percentage': average_percentage
    }
    
    return JsonResponse(data)


@login_required
def bulk_assign_class(request):
    """Bulk assign students to a class"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        student_ids = data.get('student_ids', [])
        class_id = data.get('class_id')
        
        if not student_ids or not class_id:
            return JsonResponse({'error': 'Missing data'}, status=400)
        
        class_obj = get_object_or_404(Class, id=class_id)
        Student.objects.filter(id__in=student_ids).update(current_class=class_obj)
        
        return JsonResponse({
            'message': f'{len(student_ids)} students assigned to {class_obj.name}'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def export_students(request):
    """Export selected students as CSV"""
    student_ids = request.GET.get('ids', '').split(',')
    students = Student.objects.filter(id__in=student_ids).select_related('user', 'current_class')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Admission No', 'First Name', 'Last Name', 'Class', 'Roll No', 'Email', 'Emergency Contact'])
    
    for student in students:
        writer.writerow([
            student.admission_number,
            student.user.first_name,
            student.user.last_name,
            str(student.current_class) if student.current_class else '',
            student.roll_number,
            student.user.email,
            student.emergency_contact
        ])
    
    return response


@login_required
def mark_attendance(request):
    if request.user.user_type not in ['admin', 'teacher']:
        messages.error(request, 'You do not have permission to mark attendance')
        return redirect('dashboard')
    
    school = request.user.school
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        student_ids = request.POST.getlist('students')
        
        for student_id in student_ids:
            status = request.POST.get(f'status_{student_id}')
            student = Student.objects.get(id=student_id, school=school)
            
            Attendance.objects.update_or_create(
                student=student,
                date=date_str,
                defaults={
                    'status': status,
                    'marked_by': request.user,
                    'school': school  # Set school on attendance
                }
            )
        
        messages.success(request, f'Attendance marked successfully for {len(student_ids)} students')
        return redirect('students:mark_attendance')
    
    classes = Class.objects.filter(school=school, academic_year__is_current=True)
    return render(request, 'students/mark_attendance.html', {
        'classes': classes,
        'today': date.today()
    })


@login_required
def get_class_students(request, class_id):
    # Filter by school
    students = Student.objects.filter(
        current_class_id=class_id, 
        school=request.user.school
    ).select_related('user')
    data = [
        {
            'id': s.id,
            'name': s.user.get_full_name(),
            'admission_number': s.admission_number,
            'roll_number': s.roll_number
        }
        for s in students
    ]
    return JsonResponse(data, safe=False)


@login_required
def student_dashboard_view(request):
    """Enhanced student dashboard with grades and attendance"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Check if student profile exists
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please contact administrator.')
        return redirect('login')
    
    # Get recent attendance (last 10 records)
    recent_attendance = Attendance.objects.filter(
        student=student
    ).order_by('-date')[:10]
    
    # Calculate attendance stats
    total_attendance = Attendance.objects.filter(student=student).count()
    present_count = Attendance.objects.filter(student=student, status='present').count()
    absent_count = Attendance.objects.filter(student=student, status='absent').count()
    
    attendance_percentage = 0
    if total_attendance > 0:
        attendance_percentage = round((present_count / total_attendance) * 100, 2)
    
    attendance_stats = {
        'present': present_count,
        'absent': absent_count,
        'total': total_attendance,
        'percentage': attendance_percentage
    }
    
    # Get all grades
    grades = Grade.objects.filter(student=student).select_related('subject').order_by('-created_at')
    
    # Calculate grade statistics
    from django.db.models import Avg, Count as DbCount, Q
    import json
    
    # Get grades per subject
    subject_grades = grades.values('subject__name').annotate(
        avg_marks=Avg('total_score'),
        count=DbCount('id')
    ).order_by('subject__name')
    
    subject_names = [s['subject__name'] for s in subject_grades]
    subject_avg_marks = [round(s['avg_marks'], 2) if s['avg_marks'] else 0 for s in subject_grades]
    
    # Get grade distribution (A, B, C, D, etc.)
    grade_distribution = grades.values('grade').annotate(
        count=DbCount('id')
    ).order_by('grade')
    
    grade_labels = [g['grade'] for g in grade_distribution]
    grade_counts = [g['count'] for g in grade_distribution]
    
    # Overall performance metrics
    overall_avg = 0
    if grades.exists():
        overall_avg = round(grades.aggregate(Avg('total_score'))['total_score__avg'], 2)
    
    # Last 30 days performance trend
    thirty_days_ago = date.today() - timedelta(days=30)
    performance_trend = grades.filter(
        created_at__gte=thirty_days_ago
    ).values('created_at__date').annotate(
        avg_marks=Avg('total_score')
    ).order_by('created_at__date')
    
    trend_dates = [str(p['created_at__date']) for p in performance_trend]
    trend_marks = [round(p['avg_marks'], 2) if p['avg_marks'] else 0 for p in performance_trend]
    
    context = {
        'student': student,
        'recent_attendance': recent_attendance,
        'attendance_stats': attendance_stats,
        'grades': grades,
        'subject_names': json.dumps(subject_names),
        'subject_avg_marks': json.dumps(subject_avg_marks),
        'grade_labels': json.dumps(grade_labels),
        'grade_counts': json.dumps(grade_counts),
        'overall_avg': overall_avg,
        'trend_dates': json.dumps(trend_dates),
        'trend_marks': json.dumps(trend_marks),
        'has_subject_grades': bool(subject_grades),
        'has_grade_distribution': bool(grade_distribution),
        'has_performance_trend': bool(performance_trend),
    }
    
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
def generate_report_card(request, student_id):
    """Generate a printable report card for a student"""
    
    student = get_object_or_404(Student, id=student_id)
    
    # Check permissions
    if request.user.user_type == 'student':
        try:
            student_profile = Student.objects.get(user=request.user)
            if student_profile.id != student_id:
                messages.error(request, 'You can only view your own report card')
                return redirect('dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found')
            return redirect('dashboard')
    elif request.user.user_type == 'parent':
        try:
            from parents.models import Parent
            parent = Parent.objects.get(user=request.user)
            if student not in parent.children.all():
                messages.error(request, 'You can only view your children\'s report cards')
                return redirect('parents:my_children')
        except Parent.DoesNotExist:
            messages.error(request, 'Parent profile not found')
            return redirect('dashboard')
    elif request.user.user_type not in ['admin', 'teacher']:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Get current academic year
    academic_year = AcademicYear.objects.filter(is_current=True).first()
    
    if not academic_year:
        messages.error(request, 'No active academic year found')
        return redirect('dashboard')
    
    # Get term from request, default to 'first'
    term = request.GET.get('term', 'first')
    
    # Get all grades for current academic year and term
    grades = Grade.objects.filter(
        student=student,
        academic_year=academic_year,
        term=term,
        school=student.school
    ).select_related('subject').order_by('subject__name')
    
    # Calculate statistics
    total_subjects = grades.count()
    
    # Calculate totals
    total_class_work = 0
    total_exams = 0
    grand_total = 0
    
    if grades.exists():
        for grade in grades:
            total_class_work += float(grade.class_score)
            total_exams += float(grade.exams_score)
            grand_total += float(grade.total_score)
        
        average_percentage = grand_total / total_subjects if total_subjects > 0 else 0
    else:
        average_percentage = 0
    
    # Calculate overall grade based on average
    if average_percentage >= 80:
        overall_grade = '1'
        overall_remarks = 'Highest'
    elif average_percentage >= 70:
        overall_grade = '2'
        overall_remarks = 'Higher'
    elif average_percentage >= 65:
        overall_grade = '3'
        overall_remarks = 'High'
    elif average_percentage >= 60:
        overall_grade = '4'
        overall_remarks = 'High Average'
    elif average_percentage >= 55:
        overall_grade = '5'
        overall_remarks = 'Average'
    elif average_percentage >= 50:
        overall_grade = '6'
        overall_remarks = 'Low Average'
    elif average_percentage >= 45:
        overall_grade = '7'
        overall_remarks = 'Low'
    elif average_percentage >= 40:
        overall_grade = '8'
        overall_remarks = 'Lower'
    else:
        overall_grade = '9'
        overall_remarks = 'Lowest'
    
    # Calculate class position
    from students.utils import calculate_class_position
    class_position = calculate_class_position(student, academic_year, term)
    
    # Get attendance stats
    total_attendance = Attendance.objects.filter(student=student).count()
    present_count = Attendance.objects.filter(student=student, status='present').count()
    absent_count = Attendance.objects.filter(student=student, status='absent').count()
    late_count = Attendance.objects.filter(student=student, status='late').count()
    
    attendance_percentage = 0
    if total_attendance > 0:
        attendance_percentage = round((present_count / total_attendance) * 100, 2)
    
    attendance_stats = {
        'present': present_count,
        'absent': absent_count,
        'late': late_count,
        'total': total_attendance,
        'percentage': attendance_percentage
    }
    
    context = {
        'student': student,
        'academic_year': academic_year,
        'term': term,
        'grades': grades,
        'total_subjects': total_subjects,
        'total_class_work': total_class_work,
        'total_exams': total_exams,
        'grand_total': grand_total,
        'average_percentage': average_percentage,
        'overall_grade': overall_grade,
        'overall_remarks': overall_remarks,
        'class_position': class_position,
        'attendance_stats': attendance_stats,
        'report_date': date.today(),
        'remarks': '',
    }
    
    return render(request, 'students/report_card.html', context)


@login_required
def class_report_cards(request, class_id):
    """Generate printable report cards for an entire class"""
    
    # Check permissions - only admin and teachers can access
    if request.user.user_type not in ['admin', 'teacher']:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Get the class and verify it belongs to user's school
    class_obj = get_object_or_404(Class, id=class_id, school=request.user.school)
    
    # Get current academic year
    academic_year = AcademicYear.objects.filter(is_current=True).first()
    
    if not academic_year:
        messages.error(request, 'No active academic year found')
        return redirect('dashboard')
    
    # Get term from request, default to 'first'
    term = request.GET.get('term', 'first')
    
    # Get all students in the class
    students = Student.objects.filter(
        current_class=class_obj,
        school=request.user.school
    ).select_related('user').order_by('roll_number', 'user__first_name')
    
    if not students.exists():
        messages.warning(request, f'No students found in {class_obj.name}')
        return redirect('academics:class_list')
    
    # Build report data for each student
    student_reports = []
    
    for student in students:
        # Get all grades for current academic year and term
        grades = Grade.objects.filter(
            student=student,
            academic_year=academic_year,
            term=term,
            school=student.school
        ).select_related('subject').order_by('subject__name')
        
        # Calculate statistics
        total_subjects = grades.count()
        
        # Calculate totals
        total_class_work = 0
        total_exams = 0
        grand_total = 0
        
        if grades.exists():
            for grade in grades:
                total_class_work += float(grade.class_score)
                total_exams += float(grade.exams_score)
                grand_total += float(grade.total_score)
            
            average_percentage = grand_total / total_subjects if total_subjects > 0 else 0
        else:
            average_percentage = 0
        
        # Calculate overall grade based on average
        if average_percentage >= 80:
            overall_grade = '1'
            overall_remarks = 'Highest'
        elif average_percentage >= 70:
            overall_grade = '2'
            overall_remarks = 'Higher'
        elif average_percentage >= 65:
            overall_grade = '3'
            overall_remarks = 'High'
        elif average_percentage >= 60:
            overall_grade = '4'
            overall_remarks = 'High Average'
        elif average_percentage >= 55:
            overall_grade = '5'
            overall_remarks = 'Average'
        elif average_percentage >= 50:
            overall_grade = '6'
            overall_remarks = 'Low Average'
        elif average_percentage >= 45:
            overall_grade = '7'
            overall_remarks = 'Low'
        elif average_percentage >= 40:
            overall_grade = '8'
            overall_remarks = 'Lower'
        else:
            overall_grade = '9'
            overall_remarks = 'Lowest'
        
        # Calculate class position
        from students.utils import calculate_class_position
        class_position = calculate_class_position(student, academic_year, term)
        
        # Get attendance stats
        total_attendance = Attendance.objects.filter(student=student).count()
        present_count = Attendance.objects.filter(student=student, status='present').count()
        absent_count = Attendance.objects.filter(student=student, status='absent').count()
        late_count = Attendance.objects.filter(student=student, status='late').count()
        
        attendance_percentage = 0
        if total_attendance > 0:
            attendance_percentage = round((present_count / total_attendance) * 100, 2)
        
        attendance_stats = {
            'present': present_count,
            'absent': absent_count,
            'late': late_count,
            'total': total_attendance,
            'percentage': attendance_percentage
        }
        
        student_reports.append({
            'student': student,
            'grades': grades,
            'total_subjects': total_subjects,
            'total_class_work': total_class_work,
            'total_exams': total_exams,
            'grand_total': grand_total,
            'average_percentage': average_percentage,
            'overall_grade': overall_grade,
            'overall_remarks': overall_remarks,
            'class_position': class_position,
            'attendance_stats': attendance_stats,
        })
    
    context = {
        'class_obj': class_obj,
        'academic_year': academic_year,
        'term': term,
        'student_reports': student_reports,
        'report_date': date.today(),
        'total_students': students.count(),
    }
    
    return render(request, 'students/class_report_cards.html', context)


@login_required
def register_student(request):
    """View for registering a new student - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can register students.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import StudentRegistrationForm
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, school=school)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.user.get_full_name()} registered successfully!')
            return redirect('students:list')
    else:
        form = StudentRegistrationForm(school=school)
    
    return render(request, 'students/register_student.html', {'form': form})


@login_required
def update_student(request, student_id):
    """View for updating student information - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can update students.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import StudentUpdateForm
    
    try:
        student = Student.objects.get(id=student_id, school=school)
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('students:list')
    
    if request.method == 'POST':
        form = StudentUpdateForm(request.POST, instance=student, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.user.get_full_name()} updated successfully!')
            return redirect('students:list')
    else:
        form = StudentUpdateForm(instance=student, school=school)
    
    return render(request, 'students/update_student.html', {'form': form, 'student': student})


@login_required
def delete_student(request, student_id):
    """View for deleting a student - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can delete students.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    try:
        student = Student.objects.get(id=student_id, school=school)
        student_name = student.user.get_full_name()
        
        # Delete associated user account
        user = student.user
        student.delete()
        if user:
            user.delete()
        
        messages.success(request, f'Student {student_name} deleted successfully!')
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
    
    return redirect('students:list')