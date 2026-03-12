#!/usr/bin/env python
"""
Test to reproduce the SQLite unique constraint issue.

The issue occurs when:
1. A model has a UniqueConstraint on two fields
2. A migration alters one of those fields
3. SQLite crashes with "the "." operator prohibited in index expressions"

This test creates a Django app with the problematic model and migrations,
then runs the migrations to reproduce the issue.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def create_test_app():
    """Create a temporary Django app with the problematic model and migrations."""
    # Create a temporary directory for our test app
    test_dir = tempfile.mkdtemp(prefix="django_test_")
    app_dir = Path(test_dir) / "myapp"
    app_dir.mkdir()

    # Create __init__.py
    (app_dir / "__init__.py").write_text("")

    # Create models.py with the Tag model
    models_content = '''
from django.db import models

class Tag(models.Model):
    name = models.SlugField(help_text="The tag key.")
    value = models.CharField(max_length=150, help_text="The tag value.")

    class Meta:
        ordering = ["name", "value"]
        constraints = [
            models.UniqueConstraint(
                "name",
                "value",
                name="unique_name_value",
            )
        ]

    def __str__(self):
        return f"{self.name}={self.value}"
'''
    (app_dir / "models.py").write_text(models_content)

    # Create migrations directory
    migrations_dir = app_dir / "migrations"
    migrations_dir.mkdir()

    # Create __init__.py in migrations
    (migrations_dir / "__init__.py").write_text("")

    # Create 0001_initial.py migration
    initial_migration = '''
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
    ]
    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(help_text='The tag key.')),
                ('value', models.CharField(help_text='The tag value.', max_length=200)),
            ],
            options={
                'ordering': ['name', 'value'],
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(models.F('name'), models.F('value'), name='unique_name_value'),
        ),
    ]
'''
    (migrations_dir / "0001_initial.py").write_text(initial_migration)

    # Create 0002_alter_tag_value.py migration
    alter_migration = '''
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
    ]
    operations = [
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(help_text='The tag value.', max_length=150),
        ),
    ]
'''
    (migrations_dir / "0002_alter_tag_value.py").write_text(alter_migration)

    return test_dir

def setup_django_settings(test_dir):
    """Create Django settings for the test."""
    settings_content = f'''
import os

BASE_DIR = '{test_dir}'
SECRET_KEY = 'test-secret-key'
DEBUG = True
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }}
}}
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'myapp',
]
USE_TZ = True
'''
    settings_path = Path(test_dir) / "settings.py"
    settings_path.write_text(settings_content)
    return str(settings_path)

def run_migrations(test_dir):
    """Run Django migrations and capture output."""
    # Add test_dir to Python path so we can import settings
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    # Set up environment
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    # Import Django and set up
    import django
    django.setup()

    from django.core.management import call_command
    from django.db import connection

    # Create the database
    with connection.schema_editor() as schema_editor:
        pass  # This will create the database file

    # Run migrations
    try:
        call_command('migrate', 'myapp', '--verbosity=2')
        return True, "Migrations completed successfully"
    except Exception as e:
        return False, str(e)

def main():
    """Main test function."""
    test_dir = None
    try:
        # Create test app
        test_dir = create_test_app()
        print(f"Created test app in: {test_dir}")

        # Set up Django settings
        settings_path = setup_django_settings(test_dir)
        print(f"Created settings at: {settings_path}")

        # Run migrations
        success, message = run_migrations(test_dir)
        print(f"\nMigration result: {message}")

        if success:
            print("\n✓ TEST PASSED - Migrations completed successfully (issue is fixed)")
            return 0
        else:
            print("\n✗ TEST FAILED - Migration error occurred (issue reproduced)")
            if "the \".\" operator prohibited in index expressions" in message:
                print("✓ Confirmed: This is the expected SQLite error")
                return 1
            else:
                print(f"✗ Unexpected error: {message}")
                return 1

    except Exception as e:
        print(f"\n✗ TEST ERROR - Unexpected exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if test_dir and os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")

if __name__ == "__main__":
    sys.exit(main())