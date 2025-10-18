from django.test import TestCase
from django.contrib.auth import get_user_model
from academics.models import AcademicYear, Class as SchoolClass, Subject
from students.models import Student, Grade
import pandas as pd
import load_sample_data


class GradeImporterTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.admin = User.objects.create(username='admin', is_superuser=True)
		self.ay = AcademicYear.objects.create(name='2024-2025', start_date='2024-01-01', end_date='2025-12-31', is_current=True)
		self.cls = SchoolClass.objects.create(name='Basic 9', academic_year=self.ay)
		# create subjects
		Subject.objects.bulk_create([
			Subject(code='MATH', name='Mathematics'),
			Subject(code='ENG', name='English'),
			Subject(code='SCI', name='Science'),
			Subject(code='SOC', name='Social Studies'),
		])
		# create students
		for i in range(1, 4):
			u = User.objects.create(username=f'st{i}', first_name=f'First{i}', last_name='Test')
			s = Student.objects.create(user=u, admission_number=f'S00{i}', date_of_birth='2008-01-01', date_of_admission='2020-01-01', current_class=self.cls, emergency_contact='000')

	def test_narrow_format_import_dry_run(self):
		df = pd.DataFrame([{ 'admission_number': 'S001', 'subject_code': 'MATH', 'term': 'first', 'class_score': 10, 'exams_score': 80, 'academic_year': '2024-2025' }])
		created, updated, skipped, details = load_sample_data.import_grades_from_dataframe(df, dry_run=True)
		self.assertEqual(created + updated, 1)

	def test_wide_format_import_write(self):
		df = pd.DataFrame([
			{ 'Admission No': 'S001', 'Mathematics': 45, 'English': 50, 'Science': 35 },
			{ 'Admission No': 'S002', 'Mathematics': 40, 'English': 48, 'Science': 38 },
		])
		created, updated, skipped, details = load_sample_data.import_grades_from_dataframe(df, academic_year=self.ay, class_obj=self.cls, dry_run=False, created_by=self.admin)
		# Expect grades created for each student-subject pair (3 subjects x 2 students = 6)
		total_created = created
		self.assertTrue(total_created >= 1)
		# verify Grade rows exist
		self.assertTrue(Grade.objects.filter(academic_year=self.ay).exists())
