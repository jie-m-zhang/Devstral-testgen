"""
Test to reproduce the issue with TEST: {"MIGRATE": False} causing crashes
when setting up test databases.

The issue is that when MIGRATE=False, the code needs to set MIGRATION_MODULES to None
for all apps to ensure tables are created via syncdb instead of migrations. Without this,
serialization fails because tables don't exist.
"""

import os
import sys
import django
from django.conf import settings
from unittest import mock

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test_db',
                'TEST': {
                    'NAME': 'test_db',
                    'MIGRATE': False,  # This is the key setting that triggers the bug
                },
            },
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

    django.setup()

def test_migrate_false_migration_modules():
    """
    Test that when MIGRATE=False, MIGRATION_MODULES is properly managed.
    The fix ensures it's set to None for all apps during create_test_db and restored afterwards.
    """
    from django.db.backends.base.creation import BaseDatabaseCreation
    from django.db import connection
    from django import apps

    # Get the database creation object
    creator = BaseDatabaseCreation(connection)

    # Mock the methods that would interact with the database
    with mock.patch.object(creator, '_create_test_db'):
        with mock.patch.object(creator, '_destroy_test_db'):
            with mock.patch('django.core.management.call_command') as mock_call_command:
                # Set up initial MIGRATION_MODULES
                settings.MIGRATION_MODULES = {'test_app': 'test_migrations'}

                try:
                    print("Testing MIGRATE=False with MIGRATION_MODULES management...")
                    creator.create_test_db(
                        verbosity=0,
                        autoclobber=True,
                        serialize=False,  # Don't serialize to avoid database issues
                        keepdb=False
                    )

                    # After create_test_db, check if MIGRATION_MODULES was restored
                    current_migration_modules = settings.MIGRATION_MODULES

                    # The fix ensures MIGRATION_MODULES is restored after the operation
                    if current_migration_modules != {'test_app': 'test_migrations'}:
                        print(f"ERROR: MIGRATION_MODULES not restored properly!")
                        print(f"  Expected: {{'test_app': 'test_migrations'}}")
                        print(f"  Current: {current_migration_modules}")
                        return False

                    # Check that migrate was called with run_syncdb=True
                    # This is what happens when MIGRATE=False and MIGRATION_MODULES is set to None
                    migrate_called = any(
                        call[0][0] == 'migrate' and call[1].get('run_syncdb') == True
                        for call in mock_call_command.call_args_list
                    )
                    if not migrate_called:
                        print("ERROR: migrate was not called with run_syncdb=True!")
                        return False

                    print("SUCCESS: MIGRATION_MODULES was properly managed!")
                    return True

                except Exception as e:
                    print(f"Error occurred: {type(e).__name__}: {e}")
                    # Without the fix, MIGRATION_MODULES is not set, causing issues
                    if "MIGRATION_MODULES" in str(e) or "not set" in str(e).lower():
                        print("This is the expected error - MIGRATION_MODULES not properly managed")
                        return False
                    raise
                finally:
                    # Clean up
                    settings.MIGRATION_MODULES = {}

if __name__ == '__main__':
    try:
        result = test_migrate_false_migration_modules()
        if result:
            print("Test PASSED - Issue is fixed!")
            sys.exit(0)
        else:
            print("Test FAILED - Issue reproduced!")
            sys.exit(1)
    except Exception as e:
        print(f"Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)