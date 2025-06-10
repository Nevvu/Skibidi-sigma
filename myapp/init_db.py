# init_db.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()

from django.core.management import call_command

def initialize_database():
    call_command('makemigrations')
    call_command('migrate')

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")