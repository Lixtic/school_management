from django.contrib import admin
from django.template.loader import render_to_string
from schools.models import School


class DynamicAdminSite(admin.AdminSite):
    """Admin site with dynamic headers based on user's school"""
    
    # Point to our custom template
    index_template = 'admin/index.html'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site_title = "School Management System"
        self.site_header = "School Management System Administration"
        self.index_title = "Welcome to School Management System"
    
    def index(self, request, extra_context=None):
        """Customize admin index with dynamic headers and statistics"""
        if extra_context is None:
            extra_context = {}
        
        user = request.user
        school = None
        
        # Get school for the current user
        if not user.is_superuser:
            school = School.objects.filter(admin_user=user).first()
        
        if school:
            # School-specific admin
            extra_context['school'] = school
            self.site_header = f"{school.name} - Administration Panel"
            self.site_title = f"{school.name} Admin"
            self.index_title = f"Welcome to {school.name} Management"
            
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
            self.site_header = "School Management System - Administration"
            self.site_title = "School Management System"
            self.index_title = "Welcome to School Management System"
            
            # Add system-wide statistics
            from students.models import Student
            from teachers.models import Teacher
            from academics.models import Class
            from schools.models import School
            
            extra_context['system_stats'] = {
                'total_schools': School.objects.count(),
                'total_students': Student.objects.count(),
                'total_teachers': Teacher.objects.count(),
                'total_classes': Class.objects.count(),
            }
        
        extra_context['site_header'] = self.site_header
        extra_context['site_title'] = self.site_title
        extra_context['index_title'] = self.index_title
        
        return super().index(request, extra_context=extra_context)


# Use the custom admin site
admin.site.__class__ = DynamicAdminSite

# Set initial values
admin.site.site_header = "School Management System Administration"
admin.site.site_title = "School Admin"
admin.site.index_title = "Welcome to School Management System"
admin.site.index_template = 'admin/index.html'
