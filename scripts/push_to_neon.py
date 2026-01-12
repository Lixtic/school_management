import os
import sys
import subprocess

def push_data():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set.")
        print("   Please set it to your Neon database connection string.")
        print("   Example: export DATABASE_URL='postgres://user:pass@host/db'")
        sys.exit(1)

    dump_file = os.path.join("data", "academics_dump.json")
    if not os.path.exists(dump_file):
        print(f"❌ ERROR: Dump file {dump_file} not found.")
        sys.exit(1)

    print(f"🚀 Pushing data from {dump_file} to remote database...")
    
    try:
        # We assume the settings.py is configured to use DATABASE_URL if present
        subprocess.check_call([sys.executable, "manage.py", "loaddata", dump_file])
        print("✅ SUCCESS: Data pushed to Neon database successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to load data.\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    push_data()
