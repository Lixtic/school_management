# Dashboard Routing System

## Overview

The school management system now has a centralized dashboard routing system that automatically directs users to their appropriate dashboard based on their user type.

## Routing Logic

### Main Dashboard URL: `/dashboard/`

All users access the same URL (`/dashboard/`), but are automatically routed to the correct dashboard:

```python
@login_required
def dashboard_router(request):
    """Main dashboard router that redirects users based on their type"""
    user = request.user
    
    if user.user_type == 'admin':
        return redirect('school_admin:dashboard')
    elif user.user_type == 'teacher':
        return redirect('accounts:dashboard')
    elif user.user_type == 'student':
        return redirect('students:student_dashboard')
    elif user.user_type == 'parent':
        return redirect('accounts:dashboard')
    else:
        return redirect('login')
```

## Dashboard Destinations

### Admin Users → `/school/admin/`
- **URL Pattern**: `school/admin/`
- **View**: `school_admin.views.dashboard`
- **Template**: `templates/school_admin/dashboard.html`
- **Features**:
  - Modern styled dashboard with gradients
  - School statistics (students, teachers, parents, attendance)
  - Quick actions (add users, mark attendance, enter grades)
  - Recent students and grades
  - Class overview table
  - Performance summary with charts

### Teacher Users → `/accounts/dashboard/`
- **URL Pattern**: `accounts/dashboard/`
- **View**: `accounts.views.dashboard`
- **Template**: `templates/dashboard/teacher_dashboard.html`
- **Features**:
  - Teacher-specific widgets
  - My classes overview
  - Grade entry shortcuts
  - Attendance marking

### Student Users → `/students/dashboard/`
- **URL Pattern**: `students/dashboard/`
- **View**: `students.views.student_dashboard`
- **Template**: `templates/students/student_dashboard.html`
- **Features**:
  - Student profile
  - Report cards
  - Attendance history
  - Performance tracking

### Parent Users → `/accounts/dashboard/`
- **URL Pattern**: `accounts/dashboard/`
- **View**: `accounts.views.dashboard`
- **Template**: `templates/dashboard/parent_dashboard.html`
- **Features**:
  - Children summary
  - Quick access to child reports
  - Communication with teachers

## URL Configuration

### Main URLs (`school_system/urls.py`)
```python
urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin
    path('school/admin/', include('school_admin.urls')),  # School admin dashboard
    path('dashboard/', account_views.dashboard_router, name='dashboard'),  # Main router
    path('accounts/', include('accounts.urls')),
    # ... other URLs
]
```

### School Admin URLs (`school_admin/urls.py`)
```python
app_name = 'school_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.students_list, name='students'),
    path('teachers/', views.teachers_list, name='teachers'),
    # ... other school admin URLs
]
```

### Accounts URLs (`accounts/urls.py`)
```python
app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
```

## Access Control

### School Admin Dashboard Protection
```python
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def school_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.user_type != 'admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

@school_admin_required
def dashboard(request):
    # School admin dashboard view
    pass
```

### Preventing Wrong Dashboard Access
The `accounts.views.dashboard` function now checks user type:

```python
@login_required
def dashboard(request):
    """Dashboard for teachers and parents (non-admin users)"""
    user = request.user
    
    # Admins should not reach this view
    if user.user_type == 'admin':
        return redirect('school_admin:dashboard')
    
    # Rest of the teacher/parent dashboard logic
```

## Navigation Links

All navigation links use the main dashboard URL:

```html
<!-- In templates/base.html -->
<a href="{% url 'dashboard' %}" class="nav-link">
    <i class="bi bi-speedometer2"></i>
    <span class="nav-text">Dashboard</span>
</a>
```

This ensures that clicking "Dashboard" always takes users to their correct dashboard.

## Login Flow

1. User enters credentials on login page
2. System authenticates user
3. On successful login, redirects to `/dashboard/`
4. Dashboard router checks `user.user_type`
5. Router redirects to appropriate dashboard

```python
def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')  # Router handles the rest
```

## Common Redirects Throughout the System

Many views redirect to `'dashboard'` after completing actions:

```python
# After creating a record
messages.success(request, 'Record created successfully!')
return redirect('dashboard')

# After updating a record
messages.success(request, 'Record updated successfully!')
return redirect('dashboard')

# On permission denied
messages.error(request, 'Permission denied.')
return redirect('dashboard')
```

All these redirects now properly route users to their correct dashboard.

## Testing the Routing

### Test Admin Routing
1. Login as: `riverside_admin` / `admin123`
2. Click "Dashboard" or navigate to `/dashboard/`
3. Should redirect to: `/school/admin/`
4. Verify: Modern styled school admin dashboard appears

### Test Teacher Routing
1. Login as: `teacher1` / `password123`
2. Click "Dashboard" or navigate to `/dashboard/`
3. Should redirect to: `/accounts/dashboard/`
4. Verify: Teacher dashboard with classes and grade entry options appears

### Test Student Routing
1. Login as: `student1` / `password123`
2. Click "Dashboard" or navigate to `/dashboard/`
3. Should redirect to: `/students/dashboard/`
4. Verify: Student dashboard with grades and attendance appears

### Test Parent Routing
1. Login as: `parent1` / `password123`
2. Click "Dashboard" or navigate to `/dashboard/`
3. Should redirect to: `/accounts/dashboard/`
4. Verify: Parent dashboard with children information appears

## Troubleshooting

### Issue: Admin still goes to `/accounts/dashboard/`
**Solution**: Clear browser cache and restart server
```bash
python manage.py runserver
```

### Issue: "Dashboard not found" error
**Solution**: Check that all URL namespaces are correct
- `school_admin:dashboard` exists in `school_admin/urls.py`
- `accounts:dashboard` exists in `accounts/urls.py`
- `students:student_dashboard` exists in `students/urls.py`

### Issue: Redirect loop
**Solution**: Ensure `dashboard_router` doesn't redirect to itself
- Main URL uses `dashboard_router`
- `accounts.views.dashboard` redirects admins away
- No circular redirects

### Issue: Permission denied after login
**Solution**: Check user_type is set correctly
```python
# In Django shell
from accounts.models import User
user = User.objects.get(username='riverside_admin')
print(user.user_type)  # Should be 'admin'
```

## Migration Path

If you have existing code that directly uses:
- `redirect('accounts:dashboard')` for admins → Change to `redirect('dashboard')`
- `{% url 'accounts:dashboard' %}` in templates → Change to `{% url 'dashboard' %}`

The router will handle the correct destination.

## Benefits of This Approach

1. **Single Entry Point**: All users use the same `/dashboard/` URL
2. **Automatic Routing**: No need to remember different URLs for different user types
3. **Type Safety**: User type is checked server-side
4. **Easy Maintenance**: Routing logic in one place
5. **Better UX**: Users don't see different URLs based on their role
6. **Security**: Can't access wrong dashboard by manipulating URL

## Future Enhancements

### Planned Features
- [ ] Dashboard preferences per user
- [ ] Custom dashboard layouts
- [ ] Widget-based dashboard customization
- [ ] Real-time dashboard updates with WebSocket
- [ ] Mobile-optimized dashboard views
- [ ] Dashboard analytics and usage tracking

### Under Consideration
- Role-based widget visibility
- Multi-school admin access
- Dashboard templates for different school types
- Integration with third-party analytics

## Related Documentation

- [School Admin Dashboard Styling](DASHBOARD_STYLING.md)
- [School Admin User Management](SCHOOL_ADMIN_ADD_USERS.md)
- [Mock Data Loader](MOCK_DATA_LOADER.md)
- [Error Handling Guide](ERROR_HANDLING_GUIDE.md)

## Code Files

### Key Files Modified
- `school_system/urls.py` - Main URL routing with dashboard_router
- `accounts/views.py` - Dashboard router and dashboard views
- `school_admin/views.py` - School admin dashboard view
- `school_admin/urls.py` - School admin URL patterns
- `school_admin/decorators.py` - Access control decorators

### Template Files
- `templates/school_admin/dashboard.html` - School admin dashboard
- `templates/dashboard/teacher_dashboard.html` - Teacher dashboard
- `templates/dashboard/parent_dashboard.html` - Parent dashboard
- `templates/students/student_dashboard.html` - Student dashboard
- `templates/base.html` - Base template with navigation

---

**Last Updated**: October 22, 2025  
**Version**: 2.0  
**Status**: Production Ready ✅
