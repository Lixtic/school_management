import os
import sys
import django
from django.db import transaction

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_tenants():
    # Lazy import to avoid loading apps before django.setup() if imported
    from tenants.models import School, Domain
    
    print("Starting tenant setup...")

    # 1. Create Public Tenant
    # The public tenant is required for the system to work.
    # It manages shared data and doesn't hold student records.
    if not School.objects.filter(schema_name='public').exists():
        try:
            with transaction.atomic():
                public_tenant = School(
                    schema_name='public',
                    name='Public Tenant',
                    on_trial=False,
                    is_active=True
                )
                public_tenant.save()
                
                # Domain for public tenant
                domain = Domain()
                domain.domain = 'localhost' # Matches standard local dev
                domain.tenant = public_tenant
                domain.is_primary = True
                domain.save()
                
                print("SUCCESS: Created Public Tenant and Domain ('localhost')")
        except Exception as e:
            print(f"ERROR: Failed to create public tenant: {e}")
    else:
        print("INFO: Public Tenant already exists")

    # 2. Create a Demo School Tenant
    # This will create a separate schema 'school1' in the postgres DB.
    if not School.objects.filter(schema_name='school1').exists():
        try:
            with transaction.atomic():
                school_tenant = School(
                    schema_name='school1',
                    name='First School',
                    on_trial=True,
                    is_active=True
                )
                school_tenant.save()
                
                # Domain for the school
                domain = Domain()
                domain.domain = 'school1.localhost' 
                domain.tenant = school_tenant
                domain.is_primary = True
                domain.save()
                
                print("SUCCESS: Created 'school1' Tenant and Domain ('school1.localhost')")
        except Exception as e:
            print(f"ERROR: Failed to create school1 tenant: {e}")
    else:
        print("INFO: 'school1' Tenant already exists")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
    django.setup()
    setup_tenants()
