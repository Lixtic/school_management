# Mock Data Loader for Riverside School

This script generates comprehensive mock/test data for Riverside School to facilitate testing and development.

## Usage

```bash
python load_riverside_data.py
```

## What It Creates

### 1. School Setup
- **School**: Riverside (or creates if doesn't exist)
- **Location**: Accra, Greater Accra, Ghana
- **Status**: Active subscription
- **Branding**: Custom colors (#1e40af, #7c3aed)

### 2. Users & Credentials

#### Admin
- **Username**: `riverside_admin`
- **Password**: `admin123`
- **Access**: School admin dashboard at `/school/admin/`

#### Teachers (8 total)
- **Usernames**: `teacher1` through `teacher8`
- **Password**: `password123` (all teachers)
- **Names**: Kwame Mensah, Akua Asante, Kofi Boateng, Ama Adjei, Yaw Owusu, Efua Osei, Kwabena Amponsah, Abena Darko
- **Subjects**: Each teacher assigned to 1-2 subjects

#### Students (85-90 total)
- **Usernames**: `student1` through `student90` (approximately)
- **Password**: `password123` (all students)
- **Distribution**: 8-12 students per class
- **Names**: Random Ghanaian names (Kwame, Akua, Kofi, Ama, etc.)

#### Parents (20 total)
- **Usernames**: `parent1` through `parent20`
- **Password**: `password123` (all parents)
- **Links**: Each parent linked to 1 student

### 3. Academic Data

#### Academic Year
- **Current Year**: 2025/2026
- **Start Date**: September 1, 2025
- **End Date**: June 30, 2026
- **Status**: Active/Current

#### Classes (9 total)
- Primary 1
- Primary 2
- Primary 3
- Primary 4
- Primary 5
- Primary 6
- JHS 1
- JHS 2
- JHS 3

#### Subjects (10 total)
- Mathematics (MATH)
- English Language (ENG)
- Science (SCI)
- Social Studies (SOC)
- Integrated Science (ISCI)
- Information Technology (ICT)
- French (FRE)
- Religious & Moral Education (RME)
- Physical Education (PE)
- Creative Arts (CA)

### 4. Transactional Data

#### Attendance Records
- **Period**: Last 30 days (excluding weekends)
- **Total Records**: ~1,786 records
- **Distribution**: 
  - 90% Present
  - 5% Absent
  - 3% Late
  - 2% Excused

#### Grades
- **Terms**: First and Second terms
- **Total Records**: ~1,092 grade entries
- **Subjects per Student**: 5-7 random subjects
- **Score Range**: 
  - Class Score: 15-30 (out of 30)
  - Exams Score: 35-70 (out of 70)
  - Total: 50-100

## Features

### Smart Data Handling
- ✅ Detects existing school and updates it
- ✅ Finds existing users and updates their school
- ✅ Handles existing subjects to avoid duplicates
- ✅ Skips existing classes and academic years
- ✅ Prevents duplicate attendance records
- ✅ Idempotent - can be run multiple times safely

### Data Integrity
- ✅ All users linked to Riverside School
- ✅ Class teachers assigned to classes
- ✅ Teachers assigned to subjects
- ✅ Students distributed across classes
- ✅ Parents linked to children
- ✅ Attendance has proper date ranges
- ✅ Grades calculated and ranked automatically

### Visual Feedback
- ✅ Colored terminal output
- ✅ Progress indicators
- ✅ Success/Error messages
- ✅ Summary report at the end

## Testing the Data

After running the script, you can test with:

### 1. School Admin Dashboard
```
URL: http://127.0.0.1:8000/school/admin/
Login: riverside_admin / admin123
```

**What to test:**
- Dashboard statistics (students, teachers, parents, attendance)
- View students list
- View teachers list
- View parents list
- Add new students/teachers/parents
- Attendance overview
- Grades overview
- School settings

### 2. Django Admin
```
URL: http://127.0.0.1:8000/admin/
Login: riverside_admin / admin123
```

**What to test:**
- School management
- User management
- Class and subject management
- Academic year settings

### 3. Teacher Dashboard
```
URL: http://127.0.0.1:8000/
Login: teacher1 / password123 (or teacher2-8)
```

**What to test:**
- Enter grades for students
- Mark attendance
- View assigned classes and subjects
- View class timetables

### 4. Student Dashboard
```
URL: http://127.0.0.1:8000/
Login: student1 / password123 (or student2-90)
```

**What to test:**
- View grades and report card
- View attendance history
- View class information
- View timetable

### 5. Parent Dashboard
```
URL: http://127.0.0.1:8000/
Login: parent1 / password123 (or parent2-20)
```

**What to test:**
- View children's information
- View children's grades
- View children's attendance
- Communication with teachers

## Data Statistics

| Entity | Count | Details |
|--------|-------|---------|
| Schools | 1 | Riverside |
| Admin Users | 1 | riverside_admin |
| Teachers | 8 | teacher1-8 |
| Students | 85-90 | student1-90 |
| Parents | 20 | parent1-20 |
| Classes | 9 | Primary 1-6, JHS 1-3 |
| Subjects | 10 | Core subjects |
| Attendance Records | ~1,786 | 30 days × 85 students (weekdays) |
| Grade Records | ~1,092 | 2 terms × 85 students × 6 subjects avg |

## Troubleshooting

### Issue: UNIQUE constraint failed
**Solution**: The script handles existing data. If you see this error, it means some data already exists. The script will skip creating duplicates.

### Issue: No data created
**Solution**: Check if the school "Riverside" already exists with data. The script won't overwrite existing data.

### Issue: Teachers not showing subjects
**Solution**: Run the script again. Subject assignment happens even for existing teachers.

### Issue: Want to reset all data
**Solution**: 
1. Backup your database
2. Delete Riverside School from Django admin
3. Run the script again

## Customization

You can modify the script to:

- Change number of students per class (line ~290)
- Adjust attendance distribution (line ~405)
- Modify grade score ranges (line ~453)
- Add more subjects
- Add more classes
- Change date ranges

## Notes

- The script is idempotent - safe to run multiple times
- Existing data is preserved and updated where appropriate
- All passwords are "password123" for testing convenience
- Real names use Ghanaian naming conventions
- Attendance uses realistic distribution (90% present)
- Grades use Ghana Education Service grading system (1-9)

## Next Steps

After loading the data, you can:

1. Test the school admin dashboard features
2. Test multi-tenant isolation (login as different schools)
3. Test teacher workflows (grades, attendance)
4. Test student/parent views
5. Test reporting features
6. Add more custom data as needed

## Security Warning

⚠️ **This is for TESTING ONLY!**

- All passwords are weak and identical
- Do not use this data in production
- Reset all passwords before going live
- Use strong passwords in production
- Enable email verification for production
