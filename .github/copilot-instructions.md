## Quick orientation

This is a Django-based single-repo school management web app. Key apps live at the repo root: `accounts`, `students`, `teachers`, `academics`, and `parents`. The primary Django project is `school_system` (settings in `school_system/settings.py`).

Work locally with SQLite (default) and use `DATABASE_URL` in env to switch to Postgres in production. Static files are served by WhiteNoise in production; `STATICFILES_DIRS` points to `static` and `STATIC_ROOT` is `staticfiles`.

## What to modify and where

- Models and core business logic: each app has `models.py` (e.g., `students/models.py` contains grading, attendance and ranking logic). When changing grade logic, update `Grade.save()` and tests that assume ranking behavior.
- Views and templates: templates live in `templates/` (project-level) and per-app templates under each `templates/<app>/`. Many views rely on `AUTH_USER_MODEL = 'accounts.User'`.
- Fixtures and sample data: `load_sample_data.py` is a runnable script that bootstraps users, academic years, classes, subjects, teachers, students, grades, attendance and parents. Use it to create predictable dev data.

## Developer workflows (commands you can run)

- Create venv & install deps: use Python 3.12 (see `runtime.txt`), then pip install `-r requirements.txt`.
- Run locally (SQLite default):

  1) Apply migrations: `python manage.py migrate`
  2) Create superuser: `python manage.py createsuperuser` (or run `load_sample_data.py` to create sample users)
  3) Run dev server: `python manage.py runserver`

- Production / CI notes: `Procfile` uses gunicorn: `web: gunicorn school_system.wsgi --log-file -` and the code expects `DATABASE_URL` for Postgres (handled via `dj-database-url`).

## Project-specific conventions & gotchas

- Custom User: `accounts.models.User` extends `AbstractUser` and adds `user_type`. Use `get_user_model()` where possible and avoid assuming `auth.User`.
- Grade term values: `students.models.Grade.term` uses choices `('first','second','third')` (stored as short keys). Template and form code sometimes display human readable names — prefer `get_term_display()` for consistent labels.
- Rankings: `Grade.save()` calls `update_subject_rankings()` which updates `subject_position` for all grades in the class — expect DB writes during saves; avoid infinite save recursion when changing related grades.
- Attendance uniqueness: `Attendance` has `unique_together = ['student','date']`; creating attendance programmatically should use `get_or_create` or handle IntegrityError.
- Media uploads: `MEDIA_ROOT` is `media/` and `User.profile_picture` uploads to `profiles/`.

## Where to look for common change tasks

- Add/change a field on User: `accounts/models.py` and create migration; update admin in `accounts/admin.py`.
- Change grading rules: `students/models.py` (Grade.save). Update `load_sample_data.py` if new fields are required for the sample data.
- Add a new app: add to `INSTALLED_APPS` in `school_system/settings.py`, register URLs in `school_system/urls.py` and add templates under `templates/<app>/`.

## Tests & quick checks

- There are per-app `tests.py` files. Run tests with `python manage.py test`.
- Quick smoke checks: after migrations, run `python load_sample_data.py` to populate data and then `python manage.py runserver` and login with the printed credentials (admin/admin123, teacher*/password123, student*/password123).

## Integration points / external deps

- Database: optionally Postgres via `DATABASE_URL` (dj-database-url is used to parse it).
- Static: WhiteNoise + `whitenoise.storage.CompressedManifestStaticFilesStorage` (run `collectstatic` for production builds).
- WSGI: `school_system.wsgi` used by gunicorn (Procfile).

## Short examples to reference code patterns

- Creating or getting a model instance (pattern used throughout):

  obj, created = Model.objects.get_or_create(field=value, defaults={...})

- Grade ranking update (see `students/models.py`): saving a Grade recalculates `total_score`, `grade` and then updates `subject_position` for classmates in same class/term/year.

## If you're an automation agent

- Prefer to use management commands or `load_sample_data.py` for data setup rather than crafting SQL. Use Django ORM (call `django.setup()` first in scripts outside `manage.py`).
- When modifying models, always create migrations and run `python manage.py migrate` before running the server or loaders.

If anything in this file is unclear or you'd like me to add CI, Docker, or more examples (URL layout, key templates), tell me what area to expand. 
