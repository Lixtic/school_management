
import os
import sys
import django
from django.core.management import call_command

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

def migrate_remote():
    print("--- Applying Migrations to Remote Database ---")
    try:
        call_command('migrate')
        print("✅ SUCCESS: Migrations applied successfully.")
    except Exception as e:
        print(f"❌ ERROR: Failed to apply migrations.\n{e}")

if __name__ == '__main__':
    migrate_remote()
