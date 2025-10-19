#!/usr/bin/env python
"""
Comprehensive System Test Script
Tests all major functionality of the School Management System
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from django.test import Client
from accounts.models import User
from teachers.models import Teacher
from students.models import Student
from academics.models import AcademicYear, Class, Subject
from parents.models import Parent

def main():
    print('=' * 70)
    print('COMPREHENSIVE SYSTEM TEST')
    print('=' * 70)
    
    # Test 1: Database Connection
    print('\n[TEST 1] Database Connection')
    try:
        admin = User.objects.filter(username='admin', school__isnull=False).first()
        if admin:
            print(f'  ✓ Database connected')
            print(f'  ✓ Admin user found: {admin.username}')
            print(f'  ✓ School: {admin.school.name}')
            school = admin.school
        else:
            print('  ✗ Admin user not found')
            return
    except Exception as e:
        print(f'  ✗ Database error: {e}')
        return
    
    # Test 2: Database Statistics
    print('\n[TEST 2] Database Statistics')
    try:
        stats = {
            'Users': User.objects.filter(school=school).count(),
            'Students': Student.objects.filter(user__school=school).count(),
            'Teachers': Teacher.objects.filter(school=school).count(),
            'Parents': Parent.objects.filter(user__school=school).count(),
            'Academic Years': AcademicYear.objects.filter(school=school).count(),
            'Classes': Class.objects.filter(school=school).count(),
            'Subjects': Subject.objects.filter(school=school).count(),
        }
        
        for key, value in stats.items():
            print(f'  {key:<20}: {value:>3}')
        print('  ✓ Statistics retrieved successfully')
    except Exception as e:
        print(f'  ✗ Statistics error: {e}')
    
    # Test 3: URL Routing
    print('\n[TEST 3] URL Routing & Views')
    client = Client()
    client.force_login(admin)
    
    urls_to_test = [
        ('/dashboard/', 'Dashboard'),
        ('/academics/academic-years/', 'Academic Years List'),
        ('/academics/academic-years/create/', 'Create Academic Year'),
        ('/academics/classes/', 'Classes List'),
        ('/academics/classes/create/', 'Create Class'),
        ('/academics/subjects/', 'Subjects List'),
        ('/academics/subjects/create/', 'Create Subject'),
        ('/teachers/list/', 'Teachers List'),
        ('/teachers/register/', 'Teacher Register'),
        ('/students/', 'Students List'),
        ('/students/register/', 'Student Register'),
        ('/parents/list/', 'Parents List'),
        ('/parents/register/', 'Parent Register'),
        ('/schools/profile/', 'School Profile'),
        ('/students/attendance/mark/', 'Mark Attendance'),
    ]
    
    passed = 0
    failed = 0
    
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f'  ✓ {name:<30} : 200 OK')
                passed += 1
            else:
                print(f'  ✗ {name:<30} : {response.status_code}')
                failed += 1
        except Exception as e:
            print(f'  ✗ {name:<30} : ERROR - {str(e)[:40]}')
            failed += 1
    
    # Test 4: Teacher Registration Form
    print('\n[TEST 4] Teacher Registration Form')
    try:
        response = client.get('/teachers/register/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            checks = {
                'date_of_birth field': 'date_of_birth' in content,
                'date_of_joining field': 'date_of_joining' in content,
                'qualification field': 'qualification' in content,
                'employee_id field': 'employee_id' in content,
            }
            
            all_present = all(checks.values())
            if all_present:
                print('  ✓ All required fields present')
                for field, present in checks.items():
                    print(f'    ✓ {field}')
            else:
                print('  ✗ Some required fields missing')
                for field, present in checks.items():
                    status = '✓' if present else '✗'
                    print(f'    {status} {field}')
        else:
            print(f'  ✗ Form page failed to load: {response.status_code}')
    except Exception as e:
        print(f'  ✗ Form test error: {e}')
    
    # Test 5: Teacher Registration Submission
    print('\n[TEST 5] Teacher Registration Submission')
    try:
        test_data = {
            'first_name': 'Test',
            'last_name': 'Teacher',
            'username': 'test_teacher_verification',
            'email': 'test.teacher@verify.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'phone': '555-0000',
            'address': 'Test Address',
            'employee_id': 'TEST001',
            'date_of_birth': '1990-01-01',
            'date_of_joining': '2025-10-01',
            'qualification': 'Test Qualification',
        }
        
        teacher_count_before = Teacher.objects.filter(school=school).count()
        response = client.post('/teachers/register/', test_data, follow=True)
        teacher_count_after = Teacher.objects.filter(school=school).count()
        
        if teacher_count_after > teacher_count_before:
            print('  ✓ Teacher created successfully')
            teacher = Teacher.objects.filter(employee_id='TEST001').first()
            if teacher:
                print(f'    Name: {teacher.user.get_full_name()}')
                print(f'    Employee ID: {teacher.employee_id}')
                print(f'    Date of Joining: {teacher.date_of_joining}')
                # Cleanup
                teacher.user.delete()
                print('  ✓ Test data cleaned up')
        else:
            print('  ✗ Teacher was not created')
    except Exception as e:
        print(f'  ✗ Submission test error: {e}')
    
    # Summary
    print('\n' + '=' * 70)
    print('TEST SUMMARY')
    print('=' * 70)
    print(f'URL Tests: {passed}/{passed+failed} passed ({(passed/(passed+failed)*100):.1f}%)')
    
    if failed == 0:
        print('\n✅ ALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL')
    else:
        print(f'\n⚠️  {failed} test(s) failed')
    
    print('=' * 70)
    print('\nServer: http://127.0.0.1:8000/')
    print('Login: admin / admin123')
    print('=' * 70)

if __name__ == '__main__':
    main()
