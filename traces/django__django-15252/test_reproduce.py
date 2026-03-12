"""
Test to reproduce the issue where MigrationRecorder does not obey db_router allow_migrate rules.

The issue is that when a router specifies that migrations should only happen on 'default' database,
the MigrationRecorder still tries to create the django_migrations table on other databases.
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection, connections
from django.db.migrations.executor import MigrationExecutor
from django.test import override_settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
            'other': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        SECRET_KEY='test-secret-key',
    )

    # Setup Django
    django.setup()

# Define a router that only allows migrations on 'default' database
class TestRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Only allow migrations on 'default' database
        return db == 'default'

def test_migration_recorder_respects_router():
    """
    Test that MigrationRecorder respects the db_router allow_migrate rules.

    The test creates a router that only allows migrations on 'default' database.
    When we try to migrate on 'other' database with an empty plan, the MigrationRecorder
    should NOT try to create the django_migrations table.
    """
    print("Testing MigrationRecorder with db_router...")

    # Get the executor for the 'other' database
    other_connection = connections['other']
    executor = MigrationExecutor(other_connection)

    # Check if the table exists before migrate
    has_table_before = executor.recorder.has_table()
    print(f"Has django_migrations table before migrate: {has_table_before}")
    assert not has_table_before, "Table should not exist before test"

    # Now test with the router that disallows migrations on 'other'
    with override_settings(DATABASE_ROUTERS=[TestRouter()]):
        # The key is to pass an empty plan explicitly (plan=[])
        # This simulates the scenario where there are no migrations to apply
        # In buggy version: ensure_schema() is always called, creating the table
        # In fixed version: when plan is empty, ensure_schema() is NOT called
        state = executor.migrate([], plan=[])

        has_table_after_migrate = executor.recorder.has_table()
        print(f"Has django_migrations table after migrate with empty plan: {has_table_after_migrate}")

        # This is the key assertion:
        # In the buggy version, the table will be created (has_table_after_migrate = True)
        # In the fixed version, the table will NOT be created (has_table_after_migrate = False)
        if has_table_after_migrate:
            print("BUG: django_migrations table was created even with empty migration plan!")
            print("This means MigrationRecorder does not respect db_router allow_migrate rules.")
            return False
        else:
            print("FIXED: django_migrations table was NOT created with empty migration plan.")
            print("MigrationRecorder respects db_router allow_migrate rules.")
            return True

if __name__ == "__main__":
    success = test_migration_recorder_respects_router()
    if not success:
        print("\nTest FAILED - issue reproduced")
        sys.exit(1)
    else:
        print("\nTest PASSED - issue is fixed")
        sys.exit(0)