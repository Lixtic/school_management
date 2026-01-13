"""
Quick script to verify admin user exists and test password
Run with: python check_admin.py <schema_name>
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from tenants.models import School

def check_admin(schema_name):
    try:
        # Get the tenant
        tenant = School.objects.get(schema_name=schema_name)
        print(f"✓ Found tenant: {tenant.name}")
        
        # Switch to tenant schema
        connection.set_tenant(tenant)
        print(f"✓ Switched to schema: {schema_name}")
        
        User = get_user_model()
        
        # Check if admin exists
        try:
            admin = User.objects.get(username='admin')
            print(f"✓ Admin user exists: {admin.username}")
            print(f"  - Email: {admin.email}")
            print(f"  - User type: {admin.user_type}")
            print(f"  - Is superuser: {admin.is_superuser}")
            print(f"  - Is active: {admin.is_active}")
            
            # Test password
            if admin.check_password('admin'):
                print(f"✓ Password 'admin' is correct")
            else:
                print(f"✗ Password 'admin' does NOT match")
                print(f"  Resetting password to 'admin'...")
                admin.set_password('admin')
                admin.save()
                print(f"✓ Password reset successfully")
                
        except User.DoesNotExist:
            print(f"✗ Admin user does NOT exist in {schema_name}")
            print(f"  Creating admin user...")
            
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@school.edu',
                password='admin',
                user_type='admin'
            )
            print(f"✓ Admin user created successfully")
            
    except School.DoesNotExist:
        print(f"✗ Tenant '{schema_name}' does not exist")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Switch back to public
        connection.set_schema_to_public()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_admin.py <schema_name>")
        print("Example: python check_admin.py school1")
        sys.exit(1)
    
    schema_name = sys.argv[1]
    check_admin(schema_name)
