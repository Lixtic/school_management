# Copilot Instructions for this Project

- **Stack**: Django 5 with custom user model, crispy-forms + bootstrap5, WhiteNoise static serving. Apps: accounts (auth + dashboards), students (attendance, grades, reports), teachers (class/grade entry), academics (years/classes/subjects), parents (child access/homework), announcements (notices), finance (fees).
- **Auth & roles**: Custom user `accounts.User` with `user_type` field (admin/teacher/student/parent) and profile models per role. Dashboards route by role in [accounts/views.py](accounts/views.py) via `dashboard` view.
- **URLs**: Root login at `/`, dashboards at `/dashboard/`, role modules mounted under `/students/`, `/teachers/`, `/parents/`, `/finance/`, `/announcements/`, admin at `/admin/` as set in [school_system/urls.py](school_system/urls.py).
- **Templates & forms**: Templates live under `templates/`; role dashboards under `templates/dashboard/`. Forms lean on crispy-bootstrap5; keep Bootstrap 5 classes consistent.
- **Key models**: 
  - [academics/models.py](academics/models.py): `AcademicYear.is_current` drives filters. `SchoolInfo` stores global branding. `Timetable` links Class/Subject to Day/Time.
  - [students/models.py](students/models.py): `Attendance` is unique per student/date.
  - [finance/models.py](finance/models.py): `FeeStructure` defines charges; `StudentFee` tracks individual liability; `Payment` records receipts.
  - [announcements/models.py](announcements/models.py): `Announcement` targets audience groups (Staff, Parents, All).
- **Dashboard Logic**: Admin dashboard (`admin_dashboard.html`) layout is grid-based with quick links to Timetable, Finance, Notices, Settings. Includes Chart.js analytics for attendance/class size.
- **Grade logic**: `Grade.save` coerces scores, caps at 100, assigns grade/remarks. `term` values are `first|second|third`.
- **Finance**: Admin manages fees (`finance:manage_fees`); payments handled via `finance:record_payment` with receipt generation at `finance:print_receipt`.
- **Reporting**: Report cards (`students:report_card`) fetch dynamic branding from `SchoolInfo` model.
- **Data seeding**: `load_sample_data.py` populates Users, Classes, Subjects, Fees, Announcements, and Timetable.
- **Dev runbook**: Create venv, `pip install -r requirements.txt`, `migrate`, `python load_sample_data.py` (seeds full test set), `runserver`.
- **Static/media**: User avatars and homework files stored under `media/`; ensure `MEDIA_ROOT` writable. When `DEBUG=True`, static/media served via `django.conf.urls.static` in [school_system/urls.py](school_system/urls.py).
- **Tests**: No custom tests present; add Django `TestCase`s per app in `tests.py` files if extending behavior.
- **Conventions**: Guard privileged views with `user.user_type` checks; prefer `select_related` on user/class for listings; preserve Decimal score handling and ranking side-effects in `Grade.save`.

If anything is unclear or missing, tell me which sections need more detail and I will refine this file.