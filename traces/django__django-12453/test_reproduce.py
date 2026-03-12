#!/usr/bin/env python
"""
Test to reproduce the issue with TransactionTestCase.serialized_rollback
failing to restore objects due to ordering constraints.

The issue is that deserialize_db_from_string() doesn't wrap the deserialization
in a transaction, causing integrity errors when foreign key constraints are violated.
"""

import os
import sys
import django
from django.conf import settings

# Add testbed to path
sys.path.insert(0, '/testbed')

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'tests.test_serialized_rollback_fk',
        ],
        ROOT_URLCONF='',
        MIDDLEWARE=[],
        TEST_NON_SERIALIZED_APPS=['contenttypes', 'auth'],
    )

    django.setup()

from django.test.utils import get_runner
from django.db import connection
from django.core.management import call_command
from django.db.backends.base.creation import BaseDatabaseCreation
from io import StringIO
from django.core import serializers

# Import models after Django is set up
from tests.test_serialized_rollback_fk.models import Parent, Child

def test_deserialize_with_foreign_keys():
    """
    Test that deserialize_db_from_string properly handles foreign key relationships.

    This test should fail on the buggy version because deserialize_db_from_string
    doesn't wrap the deserialization in a transaction, causing integrity errors
    when objects are saved in an order that violates foreign key constraints.
    """
    print("Setting up test environment...")
    runner = get_runner(settings)(verbosity=0, interactive=False, keepdb=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()

    try:
        print("Creating tables...")
        call_command('migrate', '--run-syncdb', verbosity=0, database='default')

        print("Creating test data...")
        parent = Parent.objects.create(name="Parent1")
        child = Child.objects.create(name="Child1", parent=parent)

        print("Verifying data was created...")
        assert Parent.objects.count() == 1
        assert Child.objects.count() == 1

        print("Serializing data...")
        # Manually serialize in an order that will cause problems: child first, then parent
        # This simulates the issue where serialization order doesn't respect FK constraints
        out = StringIO()
        serializers.serialize("json", [child, parent], stream=out)
        data = out.getvalue()
        print(f"Serialized data length: {len(data)} bytes")

        # Clear the database to simulate a fresh start
        print("Clearing database...")
        Parent.objects.all().delete()
        Child.objects.all().delete()
        assert Parent.objects.count() == 0
        assert Child.objects.count() == 0

        print("Attempting to deserialize data (child before parent)...")
        print("This should fail on buggy version due to FK constraint violation")
        try:
            creation = BaseDatabaseCreation(connection)
            creation.deserialize_db_from_string(data)
            print("SUCCESS: Deserialization completed without errors")

            # Verify data was restored
            assert Parent.objects.count() == 1, f"Expected 1 parent, got {Parent.objects.count()}"
            assert Child.objects.count() == 1, f"Expected 1 child, got {Child.objects.count()}"

            print("All assertions passed!")
            return True
        except Exception as e:
            print(f"FAILURE: {e}")
            import traceback
            traceback.print_exc()
            return False

    finally:
        print("Tearing down...")
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()

if __name__ == '__main__':
    success = test_deserialize_with_foreign_keys()
    sys.exit(0 if success else 1)