# Fix: Accounts URL Namespace Error (Commit c1c7009)

## Problem
The dashboard page was throwing a `NoReverseMatch` error:
```
'accounts' is not a registered namespace
```

This occurred in `templates/components/breadcrumb.html` at line 6, where the template tried to reference `{% url 'accounts:dashboard' %}` but the `accounts` app URLs were not registered with a namespace.

## Root Cause
- The `accounts` app did not have a `urls.py` file with URL patterns
- Account URLs were defined directly in `school_system/urls.py` without a namespace
- Templates expected namespaced URLs like `'accounts:dashboard'`, `'accounts:login'`, `'accounts:logout'`
- This mismatch caused the Django URL reverser to fail

## Solution

### 1. Created `accounts/urls.py`
New file with proper namespace and URL patterns:
```python
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
```

### 2. Updated `school_system/urls.py`
- Removed individual account URL patterns
- Added `path('accounts/', include('accounts.urls'))` to include the accounts URL configuration
- Preserved the home view at project root level

### 3. Fixed Template References
Updated `templates/students/report_card.html` to use namespaced URL:
- Changed: `{% url 'dashboard' %}`
- To: `{% url 'accounts:dashboard' %}`

## Files Changed
- ✅ `accounts/urls.py` (new file)
- ✅ `school_system/urls.py` (modified)
- ✅ `templates/students/report_card.html` (modified)

## Verification
- ✅ Server starts without errors
- ✅ System checks pass (0 issues)
- ✅ Dashboard page loads successfully
- ✅ All URL reversals work correctly

## Benefits
1. **Proper URL Organization**: Accounts URLs are now encapsulated in the accounts app
2. **Namespace Isolation**: Reduces URL name conflicts
3. **Maintainability**: Easier to manage URL patterns for each app
4. **Django Best Practices**: Follows standard Django app structure conventions

## Testing
All account-related URLs now properly reverse with namespace:
- `reverse('accounts:dashboard')` → `/accounts/dashboard/`
- `reverse('accounts:login')` → `/accounts/login/`
- `reverse('accounts:logout')` → `/accounts/logout/`

The templates can now consistently use namespaced URL tags:
```django
<a href="{% url 'accounts:dashboard' %}">Dashboard</a>
```

## Commit Info
- **Commit ID**: c1c7009
- **Branch**: asetena_systems
- **Files**: 3 changed, 12 insertions(+), 4 deletions(-)
