import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from scripts.import_basic_class import run as import_run


class Command(BaseCommand):
    help = "Import students for a basic class from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('--class', dest='class_name', required=True, help='Class name, e.g., "Basic 7"')
        parser.add_argument('--csv', dest='csv_path', required=True, help='Path to CSV file')
        parser.add_argument('--prefix', dest='prefix', required=True, help='Admission number prefix, e.g., B7')
        parser.add_argument('--dob', dest='default_dob', default=None, help='Default DOB (YYYY-MM-DD)')

    def handle(self, *args, **options):
        class_name = options['class_name']
        csv_path = options['csv_path']
        prefix = options['prefix']
        default_dob = options['default_dob']

        # Resolve CSV to absolute path for clarity
        path = Path(csv_path)
        if not path.is_absolute():
            path = Path(os.getcwd()) / path

        if not path.exists():
            raise CommandError(f"CSV not found at {path}")

        import_run(class_name, str(path), prefix=prefix, default_dob=default_dob)
        self.stdout.write(self.style.SUCCESS(f"Imported students for {class_name} from {path}"))
