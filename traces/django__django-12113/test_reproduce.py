#!/usr/bin/env python
"""
Test to reproduce the issue with persistent SQLite databases and multidb tests.

The issue is that when using persistent SQLite databases with --keepdb,
the test_db_signature() method doesn't include the test database name
for non-in-memory databases, causing both databases to have the same signature
even though they're different files. This leads to "database is locked" errors.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the testbed to the path
sys.path.insert(0, '/testbed')

# Set up Django settings before importing Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'test_sqlite_settings'

# Create a temporary settings file with persistent database names
settings_content = '''
# Test settings for reproducing the persistent SQLite database issue

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'test_default.sqlite3'
        },
    },
    'other': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'test_other.sqlite3'
        },
    }
}

SECRET_KEY = "django_tests_secret_key"

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'tests.admin_views',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

SITE_ID = 1

USE_TZ = True
'''

# Write the settings file
with open('/testbed/test_sqlite_settings.py', 'w') as f:
    f.write(settings_content)

# Now import Django and set up
import django
from django.conf import settings
from django.db import connections
from django.test.utils import get_unique_databases_and_mirrors

def test_persistent_sqlite_signature():
    """
    Test that persistent SQLite databases have unique signatures.

    This test reproduces the issue where two databases with different
    TEST NAME values but the same NAME value would have the same signature,
    causing them to be treated as the same database.
    """
    print("Testing persistent SQLite database signatures...")

    # Get the signatures for both databases
    default_creation = connections['default'].creation
    other_creation = connections['other'].creation

    default_sig = default_creation.test_db_signature()
    other_sig = other_creation.test_db_signature()

    print(f"Default database signature: {default_sig}")
    print(f"Other database signature: {other_sig}")

    # The signatures should be different because they use different test database files
    # In the buggy version, they will be the same because test_db_signature()
    # doesn't include the test database name for non-in-memory databases
    if default_sig == other_sig:
        print("ERROR: Database signatures are the same!")
        print("This will cause 'database is locked' errors when running tests with --keepdb")
        print("because both databases will try to use the same file.")
        return False
    else:
        print("SUCCESS: Database signatures are different")
        print("Each database will use its own file, avoiding lock issues.")
        return True

def test_multidb_setup():
    """
    Test that the multidb test setup works correctly with persistent databases.
    """
    print("\nTesting multidb setup with persistent databases...")

    # Try to get unique databases and mirrors
    try:
        test_databases, mirrored_aliases = get_unique_databases_and_mirrors()
        print(f"Test databases: {test_databases}")
        print(f"Mirrored aliases: {mirrored_aliases}")

        # Check if both databases are recognized as separate
        if len(test_databases) < 2:
            print("ERROR: Not enough test databases recognized")
            print("This means the databases are being treated as the same database")
            return False

        print("SUCCESS: Both databases are recognized as separate")
        return True
    except Exception as e:
        print(f"ERROR: Exception during multidb setup: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Set up Django
    django.setup()

    print("=" * 70)
    print("Reproducing issue: admin_views.test_multidb fails with persistent test SQLite database")
    print("=" * 70)

    # Run the signature test
    sig_ok = test_persistent_sqlite_signature()

    # Run the multidb setup test
    setup_ok = test_multidb_setup()

    print("\n" + "=" * 70)
    print("Test Results:")
    print("=" * 70)

    if sig_ok and setup_ok:
        print("All tests passed - issue is fixed!")
        return 0
    else:
        print("Tests failed - issue reproduced!")
        print("\nThe issue is that when using persistent SQLite databases with")
        print("different TEST NAME values, the test_db_signature() method")
        print("doesn't include the test database name in the signature,")
        print("causing both databases to be treated as the same database.")
        print("This leads to 'database is locked' errors.")
        return 1

if __name__ == '__main__':
    # Clean up any existing test databases
    for db_name in ['test_default.sqlite3', 'test_other.sqlite3']:
        if os.path.exists(db_name):
            os.remove(db_name)

    try:
        exit_code = main()
        sys.exit(exit_code)
    finally:
        # Clean up test databases and settings file
        for db_name in ['test_default.sqlite3', 'test_other.sqlite3']:
            if os.path.exists(db_name):
                os.remove(db_name)
        if os.path.exists('/testbed/test_sqlite_settings.py'):
            os.remove('/testbed/test_sqlite_settings.py')