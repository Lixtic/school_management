from django.core.management.base import BaseCommand
from academics.models import Resource
from accounts.models import User

class Command(BaseCommand):
    help = 'Populates the standard GES JHS Curriculum resources'

    def handle(self, *args, **kwargs):
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No superuser found to assign as uploader.'))
            return

        curriculum_data = [
            {
                'title': 'GES JHS Computing Curriculum',
                'description': 'Official GES Common Core Programme Curriculum for Computing (B7-B9).',
                'link': 'https://ncca.gov.gh/wp-content/uploads/2021/02/COMPUTING-B7-B10.pdf',
                'curriculum': 'ges_jhs_new',
                'subject_tag': 'Computing'
            },
            {
                'title': 'GES JHS Mathematics Curriculum',
                'description': 'Official GES Common Core Programme Curriculum for Mathematics (B7-B9).',
                'link': 'https://ncca.gov.gh/wp-content/uploads/2021/02/MATHEMATICS-B7-B10.pdf',
                'curriculum': 'ges_jhs_new',
                'subject_tag': 'Mathematics'
            },
            {
                'title': 'GES JHS Science Curriculum',
                'description': 'Official GES Common Core Programme Curriculum for Integrated Science (B7-B9).',
                'link': 'https://ncca.gov.gh/wp-content/uploads/2021/02/SCIENCE-B7-B10.pdf',
                'curriculum': 'ges_jhs_new',
                'subject_tag': 'Science'
            },
            {
                'title': 'GES JHS English Language Curriculum',
                'description': 'Official GES Common Core Programme Curriculum for English Language (B7-B9).',
                'link': 'https://ncca.gov.gh/wp-content/uploads/2021/02/ENGLISH-LANGUAGE-B7-B10.pdf',
                'curriculum': 'ges_jhs_new',
                'subject_tag': 'English'
            },
               {
                'title': 'GES JHS Social Studies Curriculum',
                'description': 'Official GES Common Core Programme Curriculum for Social Studies (B7-B9).',
                'link': 'https://ncca.gov.gh/wp-content/uploads/2021/02/SOCIAL-STUDIES-B7-B10.pdf',
                'curriculum': 'ges_jhs_new',
                'subject_tag': 'Social Studies'
            },
             {
                'title': 'GES JHS RME Curriculum',
                'description': 'Official GES Common Core Programme Curriculum for RME (B7-B9).',
                'link': 'https://ncca.gov.gh/wp-content/uploads/2021/02/RME-B7-B10.pdf',
                'curriculum': 'ges_jhs_new',
                'subject_tag': 'RME'
            },
            {
                'title': 'GES JHS CAD/Creative Arts Curriculum',
                'description': 'Official GES Common Core Programme Curriculum for Career Technology (B7-B9).',
                'link': 'https://ncca.gov.gh/wp-content/uploads/2021/02/CAREER-TECHNOLOGY-B7-B10.pdf',
                'curriculum': 'ges_jhs_new',
                'subject_tag': 'Career Technology'
            },
        ]

        created_count = 0
        for item in curriculum_data:
            resource, created = Resource.objects.get_or_create(
                title=item['title'],
                defaults={
                    'description': item['description'],
                    'link': item['link'],
                    'resource_type': 'curriculum',
                    'curriculum': item['curriculum'],
                    'target_audience': 'teachers',
                    'uploaded_by': admin_user,
                    # No class_subject means it's a global/shared resource
                    'class_subject': None 
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {item['title']}"))
            else:
                self.stdout.write(f"Skipped (exists): {item['title']}")

        self.stdout.write(self.style.SUCCESS(f"Done. Added {created_count} curriculum resources."))
