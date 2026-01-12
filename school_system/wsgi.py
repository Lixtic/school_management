"""
WSGI config for school_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')

application = get_wsgi_application()

# --- Vercel Auto-Migration Hook ---
# Attempts to fix the database if the public tenant table is missing.
# This bypasses the need for a separate build script on serverless platforms.
try:
    from django.db import connection, OperationalError, ProgrammingError
    from django.core.management import call_command
    
    # Run setup tenants ALMOST always on this branch to ensure domain is added
    # In a real heavy traffic prod, we wouldn't do this every request, but for this stage it's safe-ish.
    # Actually, let's keep the table check, but ALSO run setup_tenants if table exists, just to ensure domains.
    try:
        from scripts.setup_tenants import setup_tenants
        setup_tenants()
    except Exception as e:
        print(f">>> WSGI SETUP TENANTS ERROR: {e}")

    try:
        cursor.execute("SELECT 1 FROM tenants_school LIMIT 1;")
        cursor.close()
    except (OperationalError, ProgrammingError):
        # Connection might be in a failed state, so we might need a fresh cursor for the next steps? 
        # Actually django handles connection reset usually.
        print(">>> WSGI: tenants_school table missing. Running migrate_schemas --shared...")
        
        # Ensure connection is usable
        connection.close()
        
        # Run Migration
        try:
            call_command('migrate_schemas', shared=True, interactive=False)
            print(">>> WSGI: Migration successful.")
            
            # Run Tenant Setup (Redundant call but ensures strictly after migration if migration logic runs)
            # from scripts.setup_tenants import setup_tenants
            setup_tenants()
            print(">>> WSGI: Setup complete.")
        except Exception as e:
            print(f">>> WSGI MIGRATION ERROR: {e}")
            
except Exception as e:
    print(f">>> WSGI HOOK ERROR: {e}")
# ----------------------------------

app = application
