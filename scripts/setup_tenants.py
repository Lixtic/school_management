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
    public_tenant = None
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
                print("SUCCESS: Created Public Tenant")
        except Exception as e:
            print(f"ERROR: Failed to create public tenant: {e}")
    else:
        public_tenant = School.objects.get(schema_name='public')
        print("INFO: Public Tenant already exists")

    # 1.1 Ensure Domains for Public Tenant
    if public_tenant:
        # List of domains that should point to public tenant
        public_domains = [
            'localhost',
            '127.0.0.1',
            'school-portal-jhominuy0-lixtics-projects.vercel.app', # User's current URL
            'school-portal-git-feature-multi-tenant-0e3ec0-lixtics-projects.vercel.app', # Branch URL
            'portalsgh.vercel.app', # Custom Domain
            'www.portalsgh.vercel.app',
        ]
        
        # Add VERCEL_URL if present
        vercel_url = os.environ.get('VERCEL_URL')
        if vercel_url:
            public_domains.append(vercel_url)
            
        for domain_url in public_domains:
            if not Domain.objects.filter(domain=domain_url).exists():
                try:
                    domain = Domain()
                    domain.domain = domain_url
                    domain.tenant = public_tenant
                    domain.is_primary = (domain_url == 'localhost')
                    domain.save()
                    print(f"SUCCESS: Added domain '{domain_url}' to Public Tenant")
                except Exception as e:
                    print(f"ERROR: Failed to add domain '{domain_url}': {e}")
            else:
                print(f"INFO: Domain '{domain_url}' already exists")

    # 2. Create a Demo School Tenant
    # This will create a separate schema 'school1' in the postgres DB.
    school_tenant = None
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
        school_tenant = School.objects.get(schema_name='school1')
        print("INFO: 'school1' Tenant already exists")

    # 2.1 Create Admin User for School 1
    if school_tenant:
        from django.contrib.auth import get_user_model
        from django.db import connection
        
        # Switch to tenant schema to create user
        connection.set_tenant(school_tenant)
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            try:
                User.objects.create_superuser(
                    username='admin',
                    email='admin@school1.com',
                    password='admin',
                    user_type='admin' # Assuming custom user model needs this
                )
                print("SUCCESS: Created superuser 'admin' / 'admin' for school1")
            except Exception as e:
                print(f"ERROR: Failed to create superuser for school1: {e}")
        else:
             print("INFO: Superuser 'admin' already exists for school1")
        
        # Switch back to public for safety (though script ends here)
        connection.set_schema_to_public()

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
    django.setup()
    setup_tenants()
