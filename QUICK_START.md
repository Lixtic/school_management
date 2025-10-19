# Quick Start Guide - School Management System

**Status:** ✅ READY TO USE  
**Server:** http://127.0.0.1:8000/  
**Date:** October 19, 2025

---

## 🚀 Start the System

```bash
# Navigate to project directory
cd D:\E\code\school_management

# Start the development server
python manage.py runserver
```

Server will start at: **http://127.0.0.1:8000/**

---

## 🔑 Login

**Admin Credentials:**
- Username: `admin`
- Password: `admin123`
- School: Riverside

**Login URL:** http://127.0.0.1:8000/login/

---

## 📋 Quick Actions

### 1. Register a Teacher ✅ (FIXED - Now Working!)
1. Go to: http://127.0.0.1:8000/teachers/register/
2. Fill in required fields:
   - ✅ First Name, Last Name, Email
   - ✅ Username, Password
   - ✅ Employee ID
   - ✅ **Date of Birth** (required) ⭐
   - ✅ **Date of Joining** (required) ⭐ NEW!
   - ✅ **Qualification** (required) ⭐
   - ⚪ Subjects (optional)
3. Click "Register Teacher"
4. Success! Redirects to teacher list

**Note:** All fields marked with (*) are required

### 2. Create Academic Year
1. Go to: http://127.0.0.1:8000/academics/academic-years/
2. Click "Create New Academic Year"
3. Set start/end dates
4. Mark as "Current" if active
5. Save

### 3. Add a Class
1. Go to: http://127.0.0.1:8000/academics/classes/
2. Click "Create New Class"
3. Select grade level, academic year
4. Assign class teacher
5. Save

### 4. Create Subjects
1. Go to: http://127.0.0.1:8000/academics/subjects/
2. Click "Create New Subject"
3. Enter name and unique code
4. Save

### 5. Register a Student
1. Go to: http://127.0.0.1:8000/students/register/
2. Fill in student details
3. Assign to class
4. Save

### 6. Register a Parent
1. Go to: http://127.0.0.1:8000/parents/register/
2. Fill in parent details
3. Select children from dropdown
4. Save

---

## 🎯 Common Tasks

### Mark Attendance
- URL: http://127.0.0.1:8000/students/attendance/mark/
- Select date, class, and mark present/absent

### Enter Grades (Teachers)
- Teachers can enter grades for their subjects
- Access through teacher dashboard

### View Dashboard
- Admin Dashboard: http://127.0.0.1:8000/dashboard/
- Shows statistics, quick actions, charts

### Update School Profile
- URL: http://127.0.0.1:8000/schools/profile/
- Edit school information

---

## 🔍 Navigation Menu

The sidebar menu has these sections:

### 📊 Dashboard
- Main overview page

### 🎓 Academics
- Students (list, register)
- Attendance
- Report Cards

### 📚 Administration
- Academic Years
- Classes
- Subjects
- Teachers
- Parents
- Timetable

### ⚙️ Settings
- School Profile

---

## ⚠️ Important Notes

### Teacher Registration (RECENTLY FIXED)
The teacher registration form now requires ALL these fields:
1. **Personal Info:** First name, last name, email, phone, address
2. **Account:** Username, password, confirm password
3. **Professional Info:**
   - Employee ID (unique)
   - Date of Birth ⭐ REQUIRED
   - Date of Joining ⭐ REQUIRED (NEW!)
   - Qualification ⭐ REQUIRED
   - Subjects (optional)

**Previous Issue:** The form was missing "Date of Joining" field, causing 500 errors.  
**Status:** ✅ FIXED in commit 19cf214

### Multi-Tenancy
- All data is scoped to the school
- Admin users must be assigned to a school
- Users can only see data from their school

---

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check for errors
python manage.py check

# Apply migrations
python manage.py migrate

# Try running server again
python manage.py runserver
```

### Can't login?
- Check username: `admin`
- Check password: `admin123`
- If needed, create new superuser:
```bash
python manage.py createsuperuser
```

### Teacher registration fails?
- ✅ FIXED! Make sure you're using the latest code
- Ensure all required fields are filled:
  - Date of Birth ⭐
  - Date of Joining ⭐
  - Qualification ⭐

### Pages not loading?
- Check server is running at http://127.0.0.1:8000/
- Clear browser cache
- Try incognito/private mode

---

## 📊 Test the System

Quick test checklist:
- [ ] Server starts without errors
- [ ] Login works
- [ ] Dashboard displays
- [ ] Can view academic years
- [ ] Can view classes
- [ ] Can view subjects
- [ ] Can view teachers list
- [ ] **Can register a teacher** ✅ FIXED
- [ ] Can view students list
- [ ] Can register a student
- [ ] Can view parents list
- [ ] Can register a parent

All should be ✅ working!

---

## 🎓 Workflow Example

**Setting up a new school year:**

1. **Create Academic Year**
   - Name: "2025-2026"
   - Start: 2025-09-01
   - End: 2026-06-30
   - Mark as Current: ✅

2. **Create Classes**
   - Grade 1 - Section A
   - Grade 1 - Section B
   - Grade 2 - Section A
   - (etc.)

3. **Create Subjects**
   - Mathematics (MATH)
   - English (ENG)
   - Science (SCI)
   - (etc.)

4. **Register Teachers**
   - Fill complete profile
   - Assign subjects they teach
   - Set date of joining

5. **Assign Class Teachers**
   - Edit each class
   - Assign primary teacher

6. **Register Students**
   - Fill student details
   - Assign to class

7. **Register Parents**
   - Fill parent details
   - Link to their children

8. **Daily Operations**
   - Mark attendance
   - Enter grades
   - Generate reports

---

## 📱 Access Points

### For Admins
- Full access to all features
- Can register users
- Can manage academic structure
- Can view all reports

### For Teachers (Future)
- View assigned classes
- Enter grades for their subjects
- Mark attendance
- View student lists

### For Students (Future)
- View their grades
- View attendance
- Download report cards

### For Parents (Future)
- View children's information
- View grades and attendance
- Receive notifications

---

## ✅ Current Status

**Everything is working!** 🎉

- ✅ Server running
- ✅ Database connected
- ✅ All features tested
- ✅ Teacher registration fixed
- ✅ Multi-tenant isolation working
- ✅ Forms validated
- ✅ URLs accessible
- ✅ Dashboard displaying

**You're all set to use the system!**

---

## 📞 Need Help?

### Documentation
- SYSTEM_STATUS.md - Current status
- TEACHER_REGISTRATION_FIX.md - Recent fix details
- FINAL_TEST_REPORT.md - Test results
- copilot-instructions.md - Developer guide

### Git
- Branch: `add_schools`
- Latest commit: `19cf214`
- Remote: https://github.com/Lixtic/school_management.git

---

**Last Updated:** October 19, 2025  
**Status:** 🟢 OPERATIONAL  
**Ready to use!** 🚀

---
