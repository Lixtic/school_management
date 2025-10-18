#!/usr/bin/env python
"""Test dashboard with full error traceback"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.test import Client
from django.contrib import auth
from accounts.models import User

# Setup test client
client = Client()

# Create an admin user
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'user_type': 'admin',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True
    }
)
admin_user.set_password('admin123')
admin_user.save()

# Test accessing dashboard
print("Testing Dashboard...")
print("=" * 60)

try:
    # Manually set up the request with Django's test client
    from django.test import RequestFactory
    from accounts.views import dashboard
    
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    request.user = admin_user
    request.session = client.session
    
    response = dashboard(request)
    print(f"✓ Dashboard response: {response.status_code}")
    
except Exception as e:
    print(f"✗ Error occurred: {type(e).__name__}")
    print(f"   {str(e)}")
    
    import traceback
    print("\nFull Traceback:")
    print("-" * 60)
    traceback.print_exc()
    print("-" * 60)
