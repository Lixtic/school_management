from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import School
from .forms import SchoolRegistrationForm

User = get_user_model()


def register_school(request):
    """View for school registration"""
    if request.method == 'POST':
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            # Create the school
            school = form.save(commit=False)
            school.subscription_status = 'trial'
            school.trial_end_date = timezone.now().date() + timedelta(days=30)
            school.save()
            
            # Create admin user
            admin_user = User.objects.create_user(
                username=form.cleaned_data['admin_username'],
                email=form.cleaned_data['admin_email'],
                password=form.cleaned_data['admin_password'],
                first_name=form.cleaned_data['admin_first_name'],
                last_name=form.cleaned_data['admin_last_name'],
                user_type='admin',
                school=school
            )
            
            # Link admin to school
            school.admin_user = admin_user
            school.save()
            
            # Log the admin user in
            login(request, admin_user)
            
            messages.success(
                request,
                f'Welcome to the platform! Your school "{school.name}" has been registered. '
                f'You have a 30-day free trial.'
            )
            return redirect('dashboard')
        else:
            # If form has errors, redirect back to home with errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('home')
    else:
        # For GET requests, redirect to home page where the modal is
        return redirect('home')


def school_profile(request):
    """View for school profile management"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    school = request.user.school
    if not school:
        messages.error(request, 'You are not associated with any school.')
        return redirect('home')
    
    # Only admins can edit school profile
    if request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can edit school profile.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Update school information
        school.name = request.POST.get('name')
        school.email = request.POST.get('email')
        school.phone = request.POST.get('phone')
        school.address = request.POST.get('address')
        school.city = request.POST.get('city', '')
        school.state = request.POST.get('state', '')
        school.country = request.POST.get('country')
        school.primary_color = request.POST.get('primary_color', '#2563eb')
        school.secondary_color = request.POST.get('secondary_color', '#7c3aed')
        
        # Handle logo upload
        if 'logo' in request.FILES:
            school.logo = request.FILES['logo']
        
        school.save()
        messages.success(request, 'School profile updated successfully!')
        return redirect('schools:profile')
    
    # Get usage statistics
    from students.models import Student
    from teachers.models import Teacher
    
    current_students = Student.objects.filter(school=school).count()
    current_teachers = Teacher.objects.filter(school=school).count()
    
    context = {
        'school': school,
        'current_students': current_students,
        'current_teachers': current_teachers,
    }
    return render(request, 'schools/profile.html', context)
