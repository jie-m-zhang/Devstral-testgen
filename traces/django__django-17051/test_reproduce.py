"""
Test to reproduce the issue where bulk_create() with update_conflicts doesn't return IDs.

This test should FAIL on the base commit and PASS on the head commit.
"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'tests.bulk_create',
        ],
        USE_TZ=True,
    )
    django.setup()

# Now import Django test utilities and models
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment
from django.db import connection
from tests.bulk_create.models import UpsertConflict

def test_bulk_create_update_conflicts_returns_ids():
    """
    Test that bulk_create with update_conflicts returns IDs.

    This test reproduces the issue where bulk_create() with update_conflicts=True
    doesn't return the primary keys in the returned queryset.
    """
    # Setup test environment
    setup_test_environment()
    connection.cursor().execute("DROP TABLE IF EXISTS bulk_create_upsertconflict")
    
    # Create the table
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(UpsertConflict)
    
    try:
        # Create initial objects
        initial_objects = [
            UpsertConflict(number=1, rank=1, name="John"),
            UpsertConflict(number=2, rank=2, name="Mary"),
        ]
        UpsertConflict.objects.bulk_create(initial_objects)
        
        # Now create conflicting objects with update_conflicts=True
        conflicting_objects = [
            UpsertConflict(number=1, rank=10, name="John Updated"),
            UpsertConflict(number=2, rank=20, name="Mary Updated"),
            UpsertConflict(number=3, rank=3, name="New Object"),
        ]
        
        # This is the key test - bulk_create with update_conflicts
        result = UpsertConflict.objects.bulk_create(
            conflicting_objects,
            update_conflicts=True,
            update_fields=['rank', 'name'],
            unique_fields=['number'],
        )
        
        # Check that IDs are set on the returned objects
        print(f"Number of objects returned: {len(result)}")
        for obj in result:
            print(f"Object: number={obj.number}, rank={obj.rank}, name={obj.name}, id={obj.id}")
        
        # The assertion that should fail on base commit and pass on head commit
        # On base commit, the IDs won't be set (they'll be None)
        # On head commit, the IDs will be properly set
        for obj in result:
            assert obj.id is not None, f"ID is None for object with number={obj.number}. This is the bug!"
        
        print("Test PASSED - IDs are properly returned!")

    finally:
        # Cleanup
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(UpsertConflict)
        teardown_test_environment()

if __name__ == "__main__":
    # Check if we support update_conflicts
    if not connection.features.supports_update_conflicts:
        print("Skipping test - database backend does not support update_conflicts")
        sys.exit(0)
    
    test_bulk_create_update_conflicts_returns_ids()