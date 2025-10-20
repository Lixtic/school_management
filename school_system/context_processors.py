"""
Context processors for the school management system.
Provides global context variables accessible in all templates.
"""

def breadcrumbs(request):
    """
    Generate breadcrumbs based on the current URL path.
    Returns a list of breadcrumb items with title, url, and optional icon.
    """
    breadcrumbs_list = []
    path = request.path
    
    # Define breadcrumb mappings
    breadcrumb_map = {
        # Students
        '/students/': {'title': 'Students', 'icon': 'bi bi-people-fill'},
        '/students/register/': {'title': 'Register Student', 'icon': 'bi bi-person-plus-fill'},
        '/students/list/': {'title': 'Student List', 'icon': 'bi bi-list-ul'},
        '/students/mark-attendance/': {'title': 'Mark Attendance', 'icon': 'bi bi-calendar-check'},
        
        # Teachers
        '/teachers/': {'title': 'Teachers', 'icon': 'bi bi-person-badge'},
        '/teachers/register/': {'title': 'Register Teacher', 'icon': 'bi bi-person-plus-fill'},
        '/teachers/list/': {'title': 'Teacher List', 'icon': 'bi bi-list-ul'},
        '/teachers/enter-grades/': {'title': 'Enter Grades', 'icon': 'bi bi-pencil-square'},
        
        # Parents
        '/parents/': {'title': 'Parents', 'icon': 'bi bi-people'},
        '/parents/list/': {'title': 'Parent List', 'icon': 'bi bi-list-ul'},
        '/parents/my-children/': {'title': 'My Children', 'icon': 'bi bi-person-hearts'},
        
        # Academics
        '/academics/': {'title': 'Academics', 'icon': 'bi bi-book'},
        '/academics/years/': {'title': 'Academic Years', 'icon': 'bi bi-calendar-range'},
        '/academics/classes/': {'title': 'Classes', 'icon': 'bi bi-door-open'},
        '/academics/subjects/': {'title': 'Subjects', 'icon': 'bi bi-journals'},
        
        # Dashboard
        '/dashboard/': {'title': 'Dashboard', 'icon': 'bi bi-speedometer2'},
    }
    
    # Build breadcrumbs based on path
    path_parts = [p for p in path.split('/') if p]
    current_path = ''
    
    for i, part in enumerate(path_parts):
        current_path += f'/{part}/'
        
        if current_path in breadcrumb_map:
            crumb = breadcrumb_map[current_path].copy()
            # Only add URL if not the last item
            if i < len(path_parts) - 1 or not path.endswith('/'):
                crumb['url'] = current_path
            breadcrumbs_list.append(crumb)
        elif part.isdigit():
            # Handle detail pages (e.g., /students/123/)
            prev_section = breadcrumbs_list[-1]['title'] if breadcrumbs_list else 'Details'
            breadcrumbs_list.append({
                'title': f'{prev_section} Details',
                'icon': 'bi bi-info-circle'
            })
    
    return {
        'breadcrumbs': breadcrumbs_list
    }


def user_notifications(request):
    """
    Provide unread notification count for the current user.
    """
    if request.user.is_authenticated:
        # TODO: Implement actual notification system
        unread_count = 0
        return {
            'unread_notifications': unread_count
        }
    return {
        'unread_notifications': 0
    }


def school_settings(request):
    """
    Provide school-specific settings and branding.
    """
    if request.user.is_authenticated and hasattr(request.user, 'school'):
        school = request.user.school
        return {
            'school_name': school.name if school else 'Asetena Management System',
            'school_logo': school.logo.url if school and school.logo else None,
            'primary_color': school.primary_color if school else '#2c3e50',
            'secondary_color': school.secondary_color if school else '#3498db',
        }
    return {
        'school_name': 'Asetena Management System',
        'school_logo': None,
        'primary_color': '#2c3e50',
        'secondary_color': '#3498db',
    }
