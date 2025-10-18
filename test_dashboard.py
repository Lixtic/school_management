#!/usr/bin/env python
"""Test script to check dashboard endpoint"""
import os
import sys
import django
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from accounts.models import User

# Create test user if doesn't exist
user, created = User.objects.get_or_create(
    username='testadmin',
    defaults={
        'email': 'testadmin@example.com',
        'user_type': 'admin',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    user.set_password('password123')
    user.save()
    print(f"✓ Created test admin user: testadmin")
else:
    print(f"✓ Using existing test admin user: testadmin")

# Test the dashboard endpoint
client = Client()
print("\nTesting dashboard endpoint...")

try:
    # Login first
    login_success = client.login(username='testadmin', password='password123')
    if login_success:
        print("✓ Login successful")
    else:
        print("✗ Login failed")
        
    # Access dashboard
    response = client.get('/dashboard/')
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Dashboard loaded successfully")
    else:
        print(f"✗ Dashboard returned status {response.status_code}")
        if hasattr(response, 'context') and response.context:
            print(f"Context: {response.context}")
        
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
