from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Announcement
from .forms import AnnouncementForm
from django.db.models import Q

@login_required
def manage_announcements(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
        
    announcements = Announcement.objects.all()
    
    if request.method == 'POST':
        # Check if delete
        if 'delete' in request.POST:
            a_id = request.POST.get('delete')
            Announcement.objects.filter(id=a_id).delete()
            messages.success(request, 'Announcement deleted')
            return redirect('announcements:manage')
            
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement posted')
            return redirect('announcements:manage')
    else:
        form = AnnouncementForm()
        
    return render(request, 'announcements/manage.html', {
        'announcements': announcements,
        'form': form
    })
