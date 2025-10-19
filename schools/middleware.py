"""
Middleware for multi-tenant school filtering.
Automatically filters all queries by the current user's school to ensure data isolation.
"""
from django.utils.deprecation import MiddlewareMixin
from django.db.models import Q
from threading import local

# Thread-local storage for current school
_thread_locals = local()


def get_current_school():
    """Get the current school from thread-local storage"""
    return getattr(_thread_locals, 'school', None)


def set_current_school(school):
    """Set the current school in thread-local storage"""
    _thread_locals.school = school


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to set the current school based on the logged-in user.
    This ensures all database queries are automatically filtered by school.
    """
    
    def process_request(self, request):
        """Set the current school from the authenticated user"""
        if request.user.is_authenticated and hasattr(request.user, 'school'):
            set_current_school(request.user.school)
        else:
            set_current_school(None)
    
    def process_response(self, request, response):
        """Clear the current school after request is processed"""
        set_current_school(None)
        return response
    
    def process_exception(self, request, exception):
        """Clear the current school if an exception occurs"""
        set_current_school(None)
        return None


class SchoolQuerySetMixin:
    """
    Mixin to automatically filter querysets by the current school.
    Add this to model managers that should be school-filtered.
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        school = get_current_school()
        
        # Don't filter for superusers or if no school is set
        if school and hasattr(self.model, 'school'):
            return queryset.filter(school=school)
        return queryset
