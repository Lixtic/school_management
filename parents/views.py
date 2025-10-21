from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from parents.models import Parent
from students.models import Student, Attendance, Grade
from communications.models import Message
from django.db.models import Q

@login_required
def parent_children(request):
    if request.user.user_type != 'parent':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    try:
        parent = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, 'Parent profile not found. Please contact administrator.')
        return redirect('dashboard')
    
    children = parent.children.all()
    children_data = []
    
    for child in children:
        total_attendance = Attendance.objects.filter(student=child).count()
        present_count = Attendance.objects.filter(student=child, status='present').count()
        
        attendance_percentage = 0
        if total_attendance > 0:
            attendance_percentage = round((present_count / total_attendance) * 100, 2)
        
        grade_count = Grade.objects.filter(student=child).count()
        
        child.attendance_percentage = attendance_percentage
        child.grade_count = grade_count
        children_data.append(child)
    
    return render(request, 'parents/my_children.html', {'children': children_data})


@login_required
def child_details(request, student_id):
    if request.user.user_type != 'parent':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    try:
        parent = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, id=student_id)
    
    if student not in parent.children.all():
        messages.error(request, 'Access denied - This is not your child')
        return redirect('parents:my_children')
    
    attendances = Attendance.objects.filter(student=student).order_by('-date')[:30]
    
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
    
    grades = Grade.objects.filter(student=student).select_related('subject').order_by('-created_at')
    
    average_percentage = 0
    if grades.exists():
        total_percentage = sum([g.percentage for g in grades])
        average_percentage = round(total_percentage / grades.count(), 2)
    
    overall_grade = 'N/A'
    if average_percentage >= 90: overall_grade = 'A+'
    elif average_percentage >= 80: overall_grade = 'A'
    elif average_percentage >= 70: overall_grade = 'B+'
    elif average_percentage >= 60: overall_grade = 'B'
    elif average_percentage >= 50: overall_grade = 'C'
    elif grades.exists(): overall_grade = 'F'

    # Fetch communication with teachers
    teacher_ids = student.current_class.teachers.values_list('user_id', flat=True)
    communications = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient_id__in=teacher_ids)) |
        (Q(sender_id__in=teacher_ids) & Q(recipient=request.user))
    ).order_by('-timestamp')

    context = {
        'student': student,
        'attendances': attendances,
        'attendance_stats': attendance_stats,
        'grades': grades,
        'average_percentage': average_percentage,
        'overall_grade': overall_grade,
        'communications': communications,
    }
    
    return render(request, 'parents/child_details.html', context)


# ========== PARENT MANAGEMENT (ADMIN ONLY) ==========

@login_required
def parent_list(request):
    """List all parents for the school"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can manage parents.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    parents = Parent.objects.filter(school=school).select_related('user').prefetch_related('children__user')
    
    return render(request, 'parents/parent_list.html', {'parents': parents})


@login_required
def register_parent(request):
    """Register a new parent"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can register parents.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import ParentRegistrationForm
    
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST, school=school)
        if form.is_valid():
            parent = form.save()
            messages.success(request, f'Parent {parent.user.get_full_name()} registered successfully!')
            return redirect('parents:parent_list')
    else:
        form = ParentRegistrationForm(school=school)
    
    return render(request, 'parents/register_parent.html', {'form': form})


@login_required
def update_parent(request, pk):
    """Update parent information"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can update parents.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    from .forms import ParentUpdateForm
    
    try:
        parent = Parent.objects.get(pk=pk, school=school)
    except Parent.DoesNotExist:
        messages.error(request, 'Parent not found.')
        return redirect('parents:parent_list')
    
    if request.method == 'POST':
        form = ParentUpdateForm(request.POST, instance=parent, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'Parent {parent.user.get_full_name()} updated successfully!')
            return redirect('parents:parent_list')
    else:
        form = ParentUpdateForm(instance=parent, school=school)
    
    return render(request, 'parents/update_parent.html', {'form': form, 'parent': parent})


@login_required
def delete_parent(request, pk):
    """Delete a parent"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can delete parents.')
        return redirect('dashboard')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('dashboard')
    
    try:
        parent = Parent.objects.get(pk=pk, school=school)
        user = parent.user
        name = user.get_full_name()
        
        # Delete parent and associated user account
        parent.delete()
        user.delete()
        
        messages.success(request, f'Parent {name} deleted successfully!')
    except Parent.DoesNotExist:
        messages.error(request, 'Parent not found.')
    
    return redirect('parents:parent_list')
