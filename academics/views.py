from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.models import User
from .models import Activity, GalleryImage, SchoolInfo, Class, Timetable, ClassSubject
from .forms import SchoolInfoForm



def gallery_view(request):
    images = GalleryImage.objects.all()
    
    # Filter by category if requested
    category = request.GET.get('category')
    if category and category != 'all':
        images = images.filter(category=category)
        
    categories = GalleryImage.CATEGORY_CHOICES
        
    context = {
        'images': images,
        'categories': categories,
        'current_category': category
    }
    return render(request, 'gallery.html', context)



@login_required
def manage_activities(request):
	if request.user.user_type not in ['admin', 'teacher']:
		messages.error(request, 'Access denied')
		return redirect('dashboard')

	is_admin = request.user.user_type == 'admin'
	staff_queryset = User.objects.filter(user_type__in=['admin', 'teacher']).order_by('first_name', 'last_name')

	# Determine which activities the user can see
	if is_admin:
		activities = Activity.objects.all()
	else:
		activities = Activity.objects.filter(Q(created_by=request.user) | Q(assigned_staff=request.user)).distinct()

	if request.method == 'POST':
		activity_id = request.POST.get('activity_id')
		title = request.POST.get('title')
		summary = request.POST.get('summary', '')
		date = request.POST.get('date')
		tag = request.POST.get('tag', '')
		is_active = request.POST.get('is_active') == 'on'

		if not title or not date:
			messages.error(request, 'Title and date are required')
			return redirect('academics:manage_activities')

		if activity_id:
			activity = get_object_or_404(Activity, id=activity_id)
			if not is_admin and request.user not in activity.assigned_staff.all() and activity.created_by != request.user:
				messages.error(request, 'You are not allowed to update this activity')
				return redirect('academics:manage_activities')
		else:
			activity = Activity(created_by=request.user)

		activity.title = title
		activity.summary = summary
		activity.date = date
		activity.tag = tag
		activity.is_active = is_active
		activity.save()

		# Assign staff: admins can pick; teachers default to themselves
		assigned_ids = request.POST.getlist('assigned_staff') if is_admin else [request.user.id]
		assigned_users = staff_queryset.filter(id__in=assigned_ids)
		activity.assigned_staff.set(assigned_users)

		messages.success(request, 'Activity saved successfully')
		return redirect('academics:manage_activities')

	context = {
		'activities': activities.order_by('-date'),
		'staff_queryset': staff_queryset,
		'is_admin': is_admin,
	}
	return render(request, 'academics/manage_activities.html', context)


@login_required
def school_settings_view(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    info = SchoolInfo.objects.first()
    if not info:
        info = SchoolInfo()
        
    if request.method == 'POST':
        form = SchoolInfoForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, 'School settings updated successfully')
            return redirect('academics:school_settings')
    else:
        form = SchoolInfoForm(instance=info)
        
    return render(request, 'academics/school_settings.html', {'form': form})


@login_required
def timetable_view(request):
    if request.user.user_type not in ['admin', 'teacher', 'student']:
        messages.error(request, 'Access denied')
        return redirect('dashboard')

    classes = Class.objects.filter(academic_year__is_current=True)
    selected_class_id = request.GET.get('class_id')
    
    # Auto-select class for students/teachers if not specified
    if not selected_class_id:
        if request.user.user_type == 'student':
            student = getattr(request.user, 'student', None)
            if student and student.current_class:
                selected_class_id = student.current_class.id
        elif request.user.user_type == 'teacher':
            # Pick first class where they teach
            teacher_classes = ClassSubject.objects.filter(teacher__user=request.user)
            if teacher_classes.exists():
                selected_class_id = teacher_classes.first().class_name.id
            elif classes.exists():
                selected_class_id = classes.first().id
    
    selected_class = None
    timetable_grid = None
    
    if selected_class_id:
        selected_class = get_object_or_404(Class, id=selected_class_id)
        entries = Timetable.objects.filter(class_subject__class_name=selected_class).select_related('class_subject__subject', 'class_subject__teacher')
        
        # Structure for grid: {day: {start_time: entry}}
        # But simpler: grouped by day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        timetable_grid = {day: [] for day in days}
        
        for entry in entries:
            day_name = entry.get_day_display()
            if day_name in timetable_grid:
                timetable_grid[day_name].append(entry)
        
        # Sort each day by start time
        for day in days:
            timetable_grid[day].sort(key=lambda x: x.start_time)

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'timetable': timetable_grid,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    return render(request, 'academics/timetable.html', context)
