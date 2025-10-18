#!/usr/bin/env python
"""Capture full error traceback from views"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from accounts.views import dashboard
from students.views import student_list

User = get_user_model()

print("Testing endpoints with full error capture...")
print("=" * 70)

# Create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'user_type': 'admin',
        'is_staff': True,
        'is_superuser': True,
        'first_name': 'Test',
        'last_name': 'User'
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print("✓ Created test user")

# Test 1: Dashboard
print("\n1. Testing /dashboard/")
print("-" * 70)
try:
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    request.user = user
    
    response = dashboard(request)
    print(f"✓ Dashboard OK: {response.status_code}")
except Exception as e:
    print(f"✗ Dashboard Error: {type(e).__name__}")
    print(f"  Message: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: Student list
print("\n2. Testing /students/")
print("-" * 70)
try:
    factory = RequestFactory()
    request = factory.get('/students/')
    request.user = user
    request.session = {}
    
    response = student_list(request)
    print(f"✓ Student List OK: {response.status_code}")
except Exception as e:
    print(f"✗ Student List Error: {type(e).__name__}")
    print(f"  Message: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test complete")
