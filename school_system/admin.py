from django.contrib import admin
from django.template.loader import render_to_string
from schools.models import School


class DynamicAdminSite(admin.AdminSite):
    """Admin site with dynamic headers based on user's school"""
    
    # Point to our custom templates
    index_template = 'admin/index.html'
    base_site_template = 'admin/base_site.html'
    
    def each_context(self, request):
        """Add dynamic context to every admin page"""
        context = super().each_context(request)
        
        user = request.user
        school = None
        
        # Get school for the current user
        if not user.is_superuser:
            # First try to get school as admin_user
            school = School.objects.filter(admin_user=user).first()
            
            # If not found, try to get from user.school field
            if not school and hasattr(user, 'school') and user.school:
                school = user.school
        
        if school:
            # School-specific admin - set context variables
            context['school'] = school
            context['site_header'] = f"{school.name} - Administration Panel"
            context['site_title'] = f"{school.name} Admin"
            context['index_title'] = f"Welcome to {school.name} Management"
        else:
            # Super admin or system-wide view
            context['site_header'] = "School Management System - Administration"
            context['site_title'] = "School Management System"
            context['index_title'] = "Welcome to School Management System"
        
        return context
    
    def index(self, request, extra_context=None):
        """Customize admin index with dynamic headers and statistics"""
        if extra_context is None:
            extra_context = {}
        
        user = request.user
        school = None
        
        # Get school for the current user
        if not user.is_superuser:
            # First try to get school as admin_user
            school = School.objects.filter(admin_user=user).first()
            
            # If not found, try to get from user.school field
            if not school and hasattr(user, 'school') and user.school:
                school = user.school
        
        if school:
            # School-specific admin
            extra_context['school'] = school
            extra_context['site_header'] = f"{school.name} - Administration Panel"
            extra_context['site_title'] = f"{school.name} Admin"
            extra_context['index_title'] = f"Welcome to {school.name} Management"
            
            # Add school-specific statistics
            from students.models import Student
            from teachers.models import Teacher
            from academics.models import Class
            from communications.models import Message
            
            unread_messages = Message.objects.filter(
                school=school,
                recipient=user,
                is_read=False
            ).count()
            
            extra_context['school_stats'] = {
                'school_name': school.name,
                'total_students': Student.objects.filter(school=school).count(),
                'total_teachers': Teacher.objects.filter(school=school).count(),
                'total_classes': Class.objects.filter(school=school).count(),
                'unread_messages': unread_messages,
                'subscription_status': school.get_subscription_status_display() if hasattr(school, 'get_subscription_status_display') else school.subscription_status,
                'is_active': school.is_active,
                'primary_color': school.primary_color,
                'secondary_color': school.secondary_color,
            }
        else:
            # Super admin or system-wide view
            extra_context['site_header'] = "School Management System - Administration"
            extra_context['site_title'] = "School Management System"
            extra_context['index_title'] = "Welcome to School Management System"
            
            # Add system-wide statistics
            from students.models import Student
            from teachers.models import Teacher
            from academics.models import Class
            from schools.models import School as SchoolModel
            
            extra_context['system_stats'] = {
                'total_schools': SchoolModel.objects.count(),
                'total_students': Student.objects.count(),
                'total_teachers': Teacher.objects.count(),
                'total_classes': Class.objects.count(),
            }
        
        return super().index(request, extra_context=extra_context)


# Use the custom admin site
admin.site.__class__ = DynamicAdminSite

# Set custom templates
admin.site.index_template = 'admin/index.html'
admin.site.base_site_template = 'admin/base_site.html'
