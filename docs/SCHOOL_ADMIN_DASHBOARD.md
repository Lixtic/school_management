# School Admin Dashboard

## Overview

A separate administrative dashboard specifically designed for school administrators, accessible at `/school/admin/`. This is distinct from Django's built-in admin interface and provides school-specific administrative functions with proper access control.

## Access URL

```
http://127.0.0.1:8000/school/admin/
```

## Features

### 1. **Role-Based Access Control**
- Only accessible to users with `user_type='admin'` who belong to a school
- Each school admin can only see and manage data from their own school
- Superusers can access all schools' dashboards

### 2. **Dashboard Sections**

#### Main Dashboard (`/school/admin/`)
- **Statistics Overview:**
  - Total students, teachers, classes
  - Attendance rate (last 7 days)
  - Average academic performance
  - Unread messages count

- **Quick Actions:**
  - Add Student
  - Add Teacher
  - Mark Attendance
  - Enter Grades
  - View Reports
  - School Settings

- **Recent Activity:**
  - Recently admitted students
  - Recent grade entries
  - Class overview with student counts

#### Students Management (`/school/admin/students/`)
- List all students in the school
- View student details
- Quick access to add new students

#### Teachers Management (`/school/admin/teachers/`)
- List all teachers
- View assigned subjects
- Teacher details and profiles

#### Classes Management (`/school/admin/classes/`)
- All classes with student counts
- Class teacher assignments
- Academic year information

#### Subjects Management (`/school/admin/subjects/`)
- List of all subjects offered
- Subject codes and descriptions

#### Attendance Overview (`/school/admin/attendance/`)
- Attendance statistics (last 30 days)
- Status breakdown (present, absent, late, excused)
- Date-wise attendance records

#### Grades Overview (`/school/admin/grades/`)
- Subject-wise performance analytics
- Average scores per subject
- Recent grade entries
- Current academic year grades

#### Reports (`/school/admin/reports/`)
- Quick links to various reports
- Student performance reports
- Attendance reports
- Grade distribution reports

#### School Settings (`/school/admin/settings/`)
- Update school information
- Manage school logo
- Update contact details (email, phone, address, website)
- View subscription status
- Branding colors display

## Security Features

### Access Control Decorator
```python
@school_admin_required
def dashboard(request):
    # Only accessible to school admins
    pass
```

### Automatic School Filtering
All data is automatically filtered by the logged-in admin's school:
```python
students = Student.objects.filter(school=request.user.school)
```

### Permission Checks
1. User must be authenticated (`@login_required`)
2. User must have `user_type='admin'`
3. User must belong to a school (`user.school` must exist)
4. Superusers bypass all restrictions

## How It Works

### 1. **Access Flow**
```
User logs in → Clicks "School Admin" link → 
Decorator checks permissions → 
Loads school-specific data → 
Displays dashboard
```

### 2. **Data Isolation**
Each school admin sees only their school's data:
- Students from their school
- Teachers employed at their school
- Classes in their school
- Grades from their school
- Attendance records for their students

### 3. **Integration with Existing Apps**
The school admin dashboard integrates seamlessly with existing apps:
- Uses `students`, `teachers`, `academics` models
- Leverages existing views for detailed pages
- Provides quick navigation to specialized functions

## Usage Examples

### For School Administrators

1. **Daily Operations:**
   - Log in with admin credentials
   - Navigate to `/school/admin/`
   - View daily statistics and attendance
   - Mark attendance or enter grades via quick actions

2. **Student Management:**
   - Click "Students" in navigation
   - View all students in your school
   - Add new students via "Add Student" button
   - View individual student details

3. **Reports:**
   - Access "Reports" section
   - Generate student performance reports
   - View attendance statistics
   - Export data for analysis

4. **School Settings:**
   - Update school contact information
   - Upload/change school logo
   - Manage branding (colors shown as reference)

### For Developers

1. **Adding New Pages:**
```python
# school_admin/views.py
@school_admin_required
def new_feature(request):
    school = request.user.school
    # Your logic here
    return render(request, 'school_admin/new_feature.html', context)

# school_admin/urls.py
path('new-feature/', views.new_feature, name='new_feature'),
```

2. **Extending Statistics:**
```python
# Add more stats to dashboard view
custom_stat = YourModel.objects.filter(school=school).count()
context['custom_stat'] = custom_stat
```

## Differences from Django Admin

| Feature | Django Admin (`/admin/`) | School Admin (`/school/admin/`) |
|---------|-------------------------|--------------------------------|
| **Purpose** | System-wide admin | School-specific admin |
| **Access** | Superusers & staff | School admins only |
| **Scope** | All schools | Single school |
| **Interface** | Django's default | Custom branded UI |
| **Navigation** | Model-centric | Task-centric |
| **Branding** | Generic | School colors/logo |

## File Structure

```
school_admin/
├── __init__.py
├── apps.py
├── decorators.py          # @school_admin_required
├── views.py               # All dashboard views
├── urls.py                # URL routing
├── models.py              # (Currently empty - uses existing models)
├── admin.py               # (No Django admin needed)
├── tests.py               # Tests
└── migrations/
    └── __init__.py

templates/school_admin/
├── dashboard.html         # Main dashboard
├── students_list.html     # Students management
├── teachers_list.html     # Teachers management
├── classes_list.html      # Classes overview
├── subjects_list.html     # Subjects list
├── attendance_overview.html  # Attendance stats
├── grades_overview.html   # Grades and performance
├── reports.html           # Reports hub
└── settings.html          # School settings
```

## Customization

### Styling
The dashboard uses the school's branding colors:
```html
<style>
    .stat-card {
        border-left: 4px solid {{ school.primary_color }};
    }
    .quick-action-btn {
        background: {{ school.primary_color }};
    }
</style>
```

### Adding Quick Actions
Edit `templates/school_admin/dashboard.html`:
```html
<a href="{% url 'your_url' %}" class="quick-action-btn">
    <i class="bi bi-icon"></i> Your Action
</a>
```

### Adding Statistics
Edit `school_admin/views.py`:
```python
@school_admin_required
def dashboard(request):
    # ... existing code ...
    
    # Add your custom stat
    custom_count = YourModel.objects.filter(school=school).count()
    context['custom_count'] = custom_count
```

## Testing

To test the school admin dashboard:

1. **Login as School Admin:**
   ```
   Username: riverside_admin (or any admin user with a school)
   Password: password123
   ```

2. **Navigate to:**
   ```
   http://127.0.0.1:8000/school/admin/
   ```

3. **Expected Result:**
   - See dashboard with Riverside school branding
   - Statistics for Riverside school only
   - Quick action buttons functional
   - All management pages accessible

4. **Test Permissions:**
   - Try accessing as student/teacher (should be denied)
   - Try accessing as user without school (should be denied)

## Future Enhancements

Potential additions:
- [ ] Export data to Excel/PDF
- [ ] Advanced analytics and charts
- [ ] Bulk operations (import/export)
- [ ] Email notifications
- [ ] Calendar integration
- [ ] Fee management
- [ ] Report card generation
- [ ] Parent communication portal
- [ ] SMS integration
- [ ] Mobile-responsive improvements

## Support

For issues or questions:
1. Check decorator permissions
2. Verify user has `user_type='admin'`
3. Confirm user has a school assigned
4. Check browser console for JavaScript errors
5. Review Django logs for backend errors

## Summary

The School Admin Dashboard provides a dedicated, school-specific administrative interface that:
- ✅ Separates concerns from Django's system admin
- ✅ Implements proper role-based access control
- ✅ Ensures data isolation between schools
- ✅ Provides intuitive, task-focused navigation
- ✅ Uses school branding for personalization
- ✅ Integrates seamlessly with existing functionality
- ✅ Maintains security and multi-tenant architecture
