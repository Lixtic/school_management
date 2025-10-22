"""
Decorators for school admin access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def school_admin_required(view_func):
    """
    Decorator to restrict access to school admins only.
    A school admin is a user with user_type='admin' who belongs to a school.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        
        # Superusers can access everything
        if user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check if user is admin type and has a school
        if user.user_type == 'admin' and hasattr(user, 'school') and user.school:
            return view_func(request, *args, **kwargs)
        
        # Deny access
        messages.error(
            request,
            'Access denied. This area is only accessible to school administrators.'
        )
        return redirect('dashboard')
    
    return _wrapped_view
