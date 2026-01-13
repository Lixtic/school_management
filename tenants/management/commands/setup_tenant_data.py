from django.core.management.base import BaseCommand
from django.db import connection
from tenants.models import School
from academics.models import AcademicYear, Class, Subject, SchoolInfo
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate a tenant schema with sample data for quick start'

    def add_arguments(self, parser):
        parser.add_argument('schema_name', type=str, help='The schema name of the tenant to populate')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        
        try:
            tenant = School.objects.get(schema_name=schema_name)
        except School.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'School with schema "{schema_name}" does not exist'))
            return

        # Switch to tenant schema
        connection.set_tenant(tenant)
        
        self.stdout.write(self.style.SUCCESS(f'Setting up data for tenant: {tenant.name}'))
        
        # 1. Create Academic Year
        current_year = timezone.now().year
        academic_year, created = AcademicYear.objects.get_or_create(
            name=f'{current_year}/{current_year + 1}',
            defaults={
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=365),
                'is_current': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created Academic Year: {academic_year.name}'))
        
        # 2. Create Sample Classes
        classes = ['Basic 7', 'Basic 8', 'Basic 9']
        for class_name in classes:
            cls, created = Class.objects.get_or_create(
                name=class_name,
                academic_year=academic_year
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created Class: {class_name}'))
        
        # 3. Create Sample Subjects
        subjects = [
            'Mathematics', 'English Language', 'Integrated Science', 
            'Social Studies', 'Computing', 'French', 'Religious & Moral Education',
            'Creative Arts', 'Career Technology'
        ]
        for subject_name in subjects:
            subj, created = Subject.objects.get_or_create(
                name=subject_name,
                defaults={'code': subject_name[:3].upper()}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created Subject: {subject_name}'))
        
        # 4. Update School Info (if not set)
        school_info = SchoolInfo.objects.first()
        if not school_info:
            SchoolInfo.objects.create(
                name=tenant.name,
                address="Address not set",
                phone="Phone not set",
                email="info@school.edu",
                motto="Excellence in Education"
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created School Info'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Tenant "{tenant.name}" setup complete!'))
        
        # Switch back to public
        connection.set_schema_to_public()
