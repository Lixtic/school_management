"""
Phase 1 UX Improvements - Simple File Check Test
Verifies all Phase 1 files are in place
"""

import os
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_test(name):
    print(f"{BOLD}{YELLOW}📋 {name}{RESET}")
    print(f"{'-'*70}")

def print_success(text):
    print(f"{GREEN}   ✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}   ✗ {text}{RESET}")

def print_result(passed, total):
    if passed == total:
        print(f"\n{BOLD}{GREEN}✅ All {total} checks passed!{RESET}\n")
    else:
        print(f"\n{BOLD}{YELLOW}⚠ {passed}/{total} checks passed{RESET}\n")

# Get base directory
BASE_DIR = Path(__file__).resolve().parent

def test_file_exists(file_path, description):
    """Test if a file exists"""
    full_path = BASE_DIR / file_path
    if full_path.exists():
        print_success(f"{description} exists")
        return True
    else:
        print_error(f"{description} NOT FOUND at {file_path}")
        return False

def test_file_contains(file_path, search_text, description):
    """Test if a file contains specific text"""
    full_path = BASE_DIR / file_path
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print_success(f"{description}")
                return True
            else:
                print_error(f"{description} - text not found")
                return False
    except Exception as e:
        print_error(f"{description} - Error: {str(e)}")
        return False

def run_tests():
    """Run all Phase 1 tests"""
    print_header("🧪 PHASE 1 UX IMPROVEMENTS - FILE VERIFICATION TEST")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Breadcrumb Component
    print_test("Test 1: Breadcrumb Navigation System")
    total_tests += 3
    if test_file_exists("templates/components/breadcrumb.html", "Breadcrumb component"):
        passed_tests += 1
    if test_file_exists("school_system/context_processors.py", "Context processors"):
        passed_tests += 1
    if test_file_contains("templates/base.html", "components/breadcrumb.html", "Breadcrumb included in base"):
        passed_tests += 1
    
    # Test 2: Toast Notifications
    print_test("\nTest 2: Toast Notification System")
    total_tests += 4
    if test_file_exists("static/js/toast-notifications.js", "Toast JavaScript"):
        passed_tests += 1
    if test_file_exists("static/css/toast-notifications.css", "Toast CSS"):
        passed_tests += 1
    if test_file_contains("templates/base.html", "toast-notifications.js", "Toast JS included in base"):
        passed_tests += 1
    if test_file_contains("templates/base.html", "toast-notifications.css", "Toast CSS included in base"):
        passed_tests += 1
    
    # Test 3: Form Validation
    print_test("\nTest 3: Form Validation System")
    total_tests += 4
    if test_file_exists("static/js/form-validation.js", "Form validation JavaScript"):
        passed_tests += 1
    if test_file_exists("static/css/form-enhancements.css", "Form enhancements CSS"):
        passed_tests += 1
    if test_file_contains("templates/base.html", "form-validation.js", "Form validation JS included"):
        passed_tests += 1
    if test_file_contains("templates/base.html", "form-enhancements.css", "Form enhancements CSS included"):
        passed_tests += 1
    
    # Test 4: Settings Configuration
    print_test("\nTest 4: Django Settings Configuration")
    total_tests += 3
    if test_file_contains("school_system/settings.py", "school_system.context_processors.breadcrumbs", "Breadcrumb context processor configured"):
        passed_tests += 1
    if test_file_contains("school_system/settings.py", "school_system.context_processors.user_notifications", "Notifications context processor configured"):
        passed_tests += 1
    if test_file_contains("school_system/settings.py", "school_system.context_processors.school_settings", "School settings context processor configured"):
        passed_tests += 1
    
    # Test 5: JavaScript Features
    print_test("\nTest 5: JavaScript Features")
    total_tests += 5
    if test_file_contains("static/js/toast-notifications.js", "class ToastNotification", "Toast class defined"):
        passed_tests += 1
    if test_file_contains("static/js/toast-notifications.js", "toast.success", "Toast success method"):
        passed_tests += 1
    if test_file_contains("static/js/form-validation.js", "class FormValidator", "Form validator class defined"):
        passed_tests += 1
    if test_file_contains("static/js/form-validation.js", "addPasswordStrengthMeter", "Password strength meter"):
        passed_tests += 1
    if test_file_contains("static/js/form-validation.js", "Bootstrap.Tooltip", "Tooltip initialization"):
        passed_tests += 1
    
    # Test 6: CSS Responsive Design
    print_test("\nTest 6: Responsive Design")
    total_tests += 2
    if test_file_contains("static/css/toast-notifications.css", "@media", "Toast responsive design"):
        passed_tests += 1
    if test_file_contains("static/css/form-enhancements.css", "@media", "Form responsive design"):
        passed_tests += 1
    
    # Test 7: Base Template Integration
    print_test("\nTest 7: Base Template Integration")
    total_tests += 3
    if test_file_contains("templates/base.html", "{% include 'components/breadcrumb.html' %}", "Breadcrumb include statement"):
        passed_tests += 1
    if test_file_contains("templates/base.html", "django-message", "Django messages conversion"):
        passed_tests += 1
    if test_file_contains("templates/base.html", "{% if breadcrumbs %}", "Breadcrumb conditional check"):
        passed_tests += 1
    
    # Test 8: Context Processor Functions
    print_test("\nTest 8: Context Processor Functions")
    total_tests += 3
    if test_file_contains("school_system/context_processors.py", "def breadcrumbs", "Breadcrumb function"):
        passed_tests += 1
    if test_file_contains("school_system/context_processors.py", "def user_notifications", "Notifications function"):
        passed_tests += 1
    if test_file_contains("school_system/context_processors.py", "def school_settings", "School settings function"):
        passed_tests += 1
    
    # Print Summary
    print_header("📊 TEST RESULTS SUMMARY")
    print_result(passed_tests, total_tests)
    
    if passed_tests == total_tests:
        print(f"{BOLD}{GREEN}🎉 Phase 1 Implementation: COMPLETE!{RESET}\n")
        print(f"{BOLD}All files are in place and properly configured.{RESET}\n")
    else:
        print(f"{BOLD}{YELLOW}⚠ Phase 1 Implementation: INCOMPLETE{RESET}\n")
        print(f"{BOLD}Some files are missing or not properly configured.{RESET}\n")
    
    # Print Manual Test Checklist
    print_header("📝 MANUAL TESTING CHECKLIST")
    print("Please perform these manual tests to verify functionality:\n")
    
    manual_tests = [
        ("1. Server Running", "Verify http://127.0.0.1:8000/ is accessible"),
        ("2. Breadcrumbs", "Navigate to different pages and check breadcrumb trail"),
        ("3. Toast Notifications", "Submit a form and observe toast messages"),
        ("4. Form Validation", "Enter invalid data in forms and see real-time feedback"),
        ("5. Password Strength", "Test password field shows strength meter"),
        ("6. Tooltips", "Hover over form fields to see helpful tooltips"),
        ("7. Loading States", "Submit form and watch button loading spinner"),
        ("8. Mobile Responsive", "Resize browser to mobile size (< 768px)"),
        ("9. Cross-Browser", "Test in Chrome, Firefox, and Edge"),
        ("10. Accessibility", "Test with screen reader if available"),
    ]
    
    for test_name, description in manual_tests:
        print(f"   [ ] {BOLD}{test_name}{RESET}")
        print(f"       → {description}")
    
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
