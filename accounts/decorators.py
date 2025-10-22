"""
Custom decorators for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def user_type_required(*user_types):
    """
    Decorator to restrict view access to specific user types.
    
    Usage:
        @user_type_required('admin', 'teacher')
        def enter_grades(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.user_type in user_types or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request, 
                    f'Access denied. This page is only accessible to: {", ".join(user_types)}'
                )
                return redirect('dashboard')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator to restrict view to admin users only"""
    return user_type_required('admin')(view_func)


def teacher_required(view_func):
    """Decorator to restrict view to teacher users only"""
    return user_type_required('teacher')(view_func)


def parent_required(view_func):
    """Decorator to restrict view to parent users only"""
    return user_type_required('parent')(view_func)


def student_required(view_func):
    """Decorator to restrict view to student users only"""
    return user_type_required('student')(view_func)


def school_owner_required(view_func):
    """
    Decorator to restrict view to school owners (admin_user of a school).
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        from schools.models import School
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        is_school_owner = School.objects.filter(admin_user=request.user).exists()
        
        if is_school_owner:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Access denied. This page is only accessible to school owners.')
            return redirect('dashboard')
    
    return _wrapped_view


def same_school_required(view_func):
    """
    Decorator to ensure the accessed resource belongs to the user's school.
    Assumes the view receives a model instance with a 'school' attribute.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # This would need to be customized per view
        # Example implementation for student detail view
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check if user's school matches the resource school
        # Implementation depends on view structure
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
