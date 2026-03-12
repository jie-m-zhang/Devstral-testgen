"""
Test to reproduce the named tuple issue with __range queries.

The issue is that when using named tuples as arguments to __range queries,
Django 3.0 fails with: TypeError: __new__() missing 1 required positional argument: 'far'.
This is because resolve_lookup_value() tries to reconstruct the tuple but doesn't
properly handle named tuples.
"""

from collections import namedtuple
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
            'tests.queries',
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

# Import after Django is configured
from django.test.utils import setup_test_environment, teardown_test_environment
from django.db import connection
from tests.queries.models import Number

def test_named_tuple_range_query():
    """
    Test that named tuples work as arguments to __range queries.

    This test should FAIL on the buggy version (base commit) and PASS on the fixed version (head commit).
    """
    # Setup test environment
    setup_test_environment()
    old_name = connection.settings_dict['NAME']

    # Create the database tables
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Number)

    try:
        # Create a named tuple type
        RangeTuple = namedtuple('RangeTuple', ['near', 'far'])

        # Create a named tuple instance
        range_values = RangeTuple(near=1, far=10)

        # Try to use it in a range query
        # This should work but will fail on the buggy version
        try:
            results = Number.objects.filter(num__range=range_values)
            # Force query execution
            list(results)
            print("SUCCESS: Named tuple range query worked!")
            return True
        except TypeError as e:
            print(f"FAILED: Named tuple range query failed with error: {e}")
            return False
    finally:
        # Cleanup
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Number)
        connection.settings_dict['NAME'] = old_name
        teardown_test_environment()

if __name__ == "__main__":
    success = test_named_tuple_range_query()
    if success:
        print("\nTest PASSED - issue is fixed")
        sys.exit(0)
    else:
        print("\nTest FAILED - issue reproduced")
        sys.exit(1)