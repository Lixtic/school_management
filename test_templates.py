#!/usr/bin/env python
"""Test script to verify templates render without syntax errors"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.template.loader import render_to_string
from django.test import RequestFactory
from accounts.models import User

# Create a test request
factory = RequestFactory()
request = factory.get('/dashboard/')

# Create a test user
test_user, _ = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com', 'user_type': 'admin'}
)
request.user = test_user

print("Testing templates...")
print("-" * 60)

templates_to_test = [
    'students/student_list.html',
    'students/mark_attendance.html',
    'teachers/enter_grades.html',
    'teachers/my_classes.html',
    'dashboard/parent_dashboard.html',
    'parents/my_children.html',
]

for template_name in templates_to_test:
    try:
        # Try to render with minimal context
        context = {
            'class_subjects': [],
            'children': [],
            'students': [],
            'classes': [],
            'request': request,
            'user': test_user,
        }
        html = render_to_string(template_name, context, request=request)
        print(f"✓ {template_name}: OK ({len(html)} bytes)")
    except Exception as e:
        print(f"✗ {template_name}: ERROR")
        print(f"  {type(e).__name__}: {str(e)}")

print("-" * 60)
print("Template test complete!")
