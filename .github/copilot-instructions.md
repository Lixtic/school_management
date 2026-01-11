# Copilot Instructions for School Management System

## Project Overview
- **Type**: Django 5 School Management System
- **Stack**: Django, Crispy Forms (Bootstrap 5), WhiteNoise (Static), SQLite (Local)/PostgreSQL (Prod).
- **Core Apps**:
  - `accounts`: Auth & Dashboards
  - `academics`: Years, Classes, Subjects, Timetable, School Info
  - `students`: Profiles, Attendance, Grades
  - `teachers`: Profiles, Duty Roster
  - `finance`: Fees, Payments
  - `announcements`: Notifications
  - `parents`: Parent portal
- **Inactive Apps**: `communication` (files exist but not installed).

## Architecture & Patterns
- **User Model**: Custom `accounts.models.User` with `user_type` ('admin', 'teacher', 'student', 'parent'). Authentication logic relies on this field.
- **Dashboards**: Route logic in `accounts.views.dashboard` directs users to role-specific templates (`templates/dashboard/`).
- **Global Context**: `academics.context_processors.school_info` injects school branding (Name, Logo) into all templates.
- **Static Assets**:
  - `static/`: Global CSS/JS.
  - `media/`: User uploads (profiles, gallery).
  -Served via WhiteNoise in production.

## Key Developer Workflows
- **Setup & Seeding**:
  - Run `python load_sample_data.py` to populate a full test environment with Users, Classes, Subjects, Fees, and Timetables.
  - `scripts/` directory contains standalone automation scripts (e.g., `import_basic7.py`). Run these via `python scripts/script_name.py` (they handle `django.setup()`).
- **Styles**: Use Bootstrap 5 utility classes. `crispy_forms` handles form rendering.

## Critical Conventions & "Gotchas"
- **Term Inconsistency**: 
  - `students.Grade` and `finance.FeeStructure` use lowercase: `('first', 'second', 'third')`.
  - `teachers.DutyWeek` uses Capitalized: `('First', 'Second', 'Third')`.
  - *Action*: Always check the specific model's `choices` before querying or filtering by term.
- **Access Control**: Privileged views *must* check `request.user.user_type`.
- **Filtering**:
  - Always filter by `AcademicYear.objects.filter(is_current=True)` for active records.
  - Student lookups should typically include `select_related('user', 'current_class')`.
- **Finance**: Fee logic is split between `FeeStructure` (definitions) and `StudentFee` (individual liability).

## Important File Locations
- **Settings**: [school_system/settings.py](school_system/settings.py)
- **Routing**: [school_system/urls.py](school_system/urls.py) and app-level `urls.py`.
- **Data Loaders**: [load_sample_data.py](load_sample_data.py), [scripts/](scripts/)
- **Templates**: `templates/dashboard/[role]_dashboard.html` for main landing pages.
