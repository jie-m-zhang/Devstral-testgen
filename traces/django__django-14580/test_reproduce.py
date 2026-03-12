#!/usr/bin/env python
"""
Test to reproduce the issue with missing 'models' import in generated migrations.

The issue occurs when:
1. A custom field class is defined (MyField)
2. An abstract base model is defined (MyBaseModel)
3. A mixin class is defined (MyMixin)
4. A model inherits from both mixin and abstract base model

The generated migration should import 'models' but doesn't, causing NameError.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def test_makemigrations_import_issue():
    # Create a temporary directory for our test app
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create the Django app structure
        app_dir = tmpdir_path / "test_app"
        app_dir.mkdir()

        # Create __init__.py
        (app_dir / "__init__.py").write_text("")

        # Create models.py with the exact structure from the issue
        models_content = '''from django.db import models

class MyField(models.TextField):
    pass

class MyBaseModel(models.Model):
    class Meta:
        abstract = True

class MyMixin:
    pass

class MyModel(MyMixin, MyBaseModel):
    name = MyField(primary_key=True)
'''
        (app_dir / "models.py").write_text(models_content)

        # Create a minimal Django project structure
        project_dir = tmpdir_path / "test_project"
        project_dir.mkdir()

        # Create settings.py
        settings_content = f'''
import os
from pathlib import Path

BASE_DIR = Path("{tmpdir_path}")
SECRET_KEY = 'test-secret-key'
DEBUG = True
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'test_app',
]
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '{tmpdir_path}/db.sqlite3',
    }}
}}
USE_TZ = True
'''
        (project_dir / "settings.py").write_text(settings_content)

        # Create __init__.py for project
        (project_dir / "__init__.py").write_text("")

        # Set up Django environment
        sys.path.insert(0, str(tmpdir_path))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')

        # Import Django and setup
        import django
        django.setup()

        # Run makemigrations
        from django.core.management import call_command
        from io import StringIO

        # Capture output
        out = StringIO()
        try:
            call_command('makemigrations', 'test_app', stdout=out, stderr=StringIO())
        except Exception as e:
            print(f"Error running makemigrations: {e}")
            return False

        # Check if migration was created
        migrations_dir = app_dir / "migrations"
        if not migrations_dir.exists():
            print("No migrations directory created")
            return False

        # Find the initial migration file
        migration_files = list(migrations_dir.glob("0001_*.py"))
        if not migration_files:
            print("No initial migration file found")
            return False

        migration_file = migration_files[0]
        migration_content = migration_file.read_text()

        print("Generated migration content:")
        print("=" * 80)
        print(migration_content)
        print("=" * 80)

        # Check if 'models' is imported (could be in various forms)
        has_models_import = (
            'from django.db import models' in migration_content or
            'from django.db import migrations, models' in migration_content or
            'import django.db.models' in migration_content
        )

        if not has_models_import:
            print("ERROR: 'models' is not imported in the migration file!")
            print("This will cause NameError when the migration is loaded.")
            return False

        # Try to import the migration to verify it's valid Python
        try:
            # Add the app to sys.path so we can import the migration
            sys.path.insert(0, str(app_dir))
            # Import the migration module
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_migration", str(migration_file))
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            print("Migration imported successfully!")
            return True
        except NameError as e:
            print(f"NameError when importing migration: {e}")
            print("This confirms the bug - 'models' is not defined in the migration!")
            return False
        except Exception as e:
            print(f"Other error when importing migration: {e}")
            return False

if __name__ == "__main__":
    success = test_makemigrations_import_issue()
    if success:
        print("\n✓ Test PASSED - Migration is valid (issue is fixed)")
        sys.exit(0)
    else:
        print("\n✗ Test FAILED - Migration has missing 'models' import (issue reproduced)")
        sys.exit(1)