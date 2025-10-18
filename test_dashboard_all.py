#!/usr/bin/env python
"""Test script to check dashboard for all user types"""
import os
import sys
import django
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from accounts.models import User
from teachers.models import Teacher
from students.models import Student

print("Testing dashboard for all user types...")
print("=" * 60)

user_types = [
    ('admin', 'testadmin'),
    ('teacher', 'testteacher'),
    ('student', 'teststudent'),
    ('parent', 'testparent'),
]

for user_type, username in user_types:
    print(f"\n{user_type.upper()} User:")
    print("-" * 40)
    
    try:
        # Create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'user_type': user_type,
                'is_staff': user_type == 'admin',
                'is_superuser': user_type == 'admin'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✓ Created {user_type} user: {username}")
        else:
            print(f"  ✓ Using existing {user_type} user: {username}")

        # Create teacher/student records if needed
        if user_type == 'teacher' and not Teacher.objects.filter(user=user).exists():
            Teacher.objects.create(user=user)
            print(f"  ✓ Created teacher profile")
        elif user_type == 'student' and not Student.objects.filter(user=user).exists():
            Student.objects.create(user=user)
            print(f"  ✓ Created student profile")

        # Test dashboard
        client = Client()
        login_success = client.login(username=username, password='password123')
        
        if login_success:
            print(f"  ✓ Login successful")
            
            response = client.get('/dashboard/')
            if response.status_code == 200:
                print(f"  ✓ Dashboard: 200 OK")
            else:
                print(f"  ✗ Dashboard: {response.status_code}")
                if response.status_code >= 500:
                    print(f"    Error content: {response.content[:200]}")
        else:
            print(f"  ✗ Login failed")
            
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Dashboard test complete!")
