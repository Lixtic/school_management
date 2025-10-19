"""
Admin mixins for multi-tenant school management.
Provides automatic school-based filtering and permissions.
"""
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied


class TenantAdminMixin:
    """
    Mixin for ModelAdmin classes to automatically filter by school.
    This ensures admins only see and manage their own school's data.
    """
    
    def get_queryset(self, request):
        """Filter queryset to show only current school's data"""
        qs = super().get_queryset(request)
        
        # Superusers can see all schools' data
        if request.user.is_superuser:
            return qs
        
        # Regular admins only see their school's data
        if hasattr(request.user, 'school') and request.user.school:
            # Only filter if the model has a school field
            if hasattr(self.model, 'school'):
                return qs.filter(school=request.user.school)
        
        # If user has no school, return empty queryset
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """Automatically set school when creating new objects"""
        if not change:  # Only on creation
            if hasattr(obj, 'school') and not obj.school:
                # Set school from current user
                if hasattr(request.user, 'school'):
                    obj.school = request.user.school
        
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """Check if user can change this object"""
        has_perm = super().has_change_permission(request, obj)
        
        if not has_perm:
            return False
        
        # Superusers can change anything
        if request.user.is_superuser:
            return True
        
        # Check if object belongs to user's school
        if obj is not None and hasattr(obj, 'school'):
            if hasattr(request.user, 'school') and request.user.school:
                return obj.school == request.user.school
            return False
        
        return has_perm
    
    def has_delete_permission(self, request, obj=None):
        """Check if user can delete this object"""
        has_perm = super().has_delete_permission(request, obj)
        
        if not has_perm:
            return False
        
        # Superusers can delete anything
        if request.user.is_superuser:
            return True
        
        # Check if object belongs to user's school
        if obj is not None and hasattr(obj, 'school'):
            if hasattr(request.user, 'school') and request.user.school:
                return obj.school == request.user.school
            return False
        
        return has_perm
    
    def has_view_permission(self, request, obj=None):
        """Check if user can view this object"""
        has_perm = super().has_view_permission(request, obj)
        
        if not has_perm:
            return False
        
        # Superusers can view anything
        if request.user.is_superuser:
            return True
        
        # Check if object belongs to user's school
        if obj is not None and hasattr(obj, 'school'):
            if hasattr(request.user, 'school') and request.user.school:
                return obj.school == request.user.school
            return False
        
        return has_perm
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter foreign key choices to only show items from the same school.
        For example, when selecting a class, only show classes from the admin's school.
        """
        if db_field.name == 'school':
            # If editing school field, only allow selecting user's own school
            if not request.user.is_superuser:
                if hasattr(request.user, 'school') and request.user.school:
                    kwargs['queryset'] = db_field.related_model.objects.filter(id=request.user.school.id)
        else:
            # For other foreign keys, filter by school if the related model has a school field
            if hasattr(db_field.related_model, 'school'):
                if not request.user.is_superuser:
                    if hasattr(request.user, 'school') and request.user.school:
                        kwargs['queryset'] = db_field.related_model.objects.filter(school=request.user.school)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filter many-to-many choices to only show items from the same school"""
        if hasattr(db_field.related_model, 'school'):
            if not request.user.is_superuser:
                if hasattr(request.user, 'school') and request.user.school:
                    kwargs['queryset'] = db_field.related_model.objects.filter(school=request.user.school)
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class SchoolFieldAdminMixin(TenantAdminMixin):
    """
    Extended mixin that adds school to list_display and list_filter for superusers.
    """
    
    def get_list_display(self, request):
        """Add school to list display for superusers"""
        list_display = super().get_list_display(request)
        
        if request.user.is_superuser and hasattr(self.model, 'school'):
            # Add school to the beginning if not already there
            if 'school' not in list_display:
                return ['school'] + list(list_display)
        
        return list_display
    
    def get_list_filter(self, request):
        """Add school to list filter for superusers"""
        list_filter = super().get_list_filter(request) if hasattr(super(), 'get_list_filter') else self.list_filter or ()
        
        if request.user.is_superuser and hasattr(self.model, 'school'):
            # Add school to filter if not already there
            if 'school' not in list_filter:
                return ['school'] + list(list_filter)
        
        return list_filter
