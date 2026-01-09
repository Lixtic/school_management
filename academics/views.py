from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.models import User
from .models import Activity


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
