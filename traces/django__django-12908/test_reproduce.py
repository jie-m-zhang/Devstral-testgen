#!/usr/bin/env python
"""
Standalone test to reproduce the issue where Union queryset should raise on distinct().

This test reproduces the issue described in the GitHub issue where:
1. Two querysets are annotated with different values
2. They are unioned together
3. distinct() is called on the union
4. This should raise NotSupportedError but doesn't on the buggy version

The test should:
- FAIL on base commit (49ae7ce50a) - distinct() doesn't raise an error (bug)
- PASS on head commit (65dfb06a1a) - distinct() raises NotSupportedError (fixed)
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_sqlite')
sys.path.insert(0, '/testbed')

# Configure Django settings for testing
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
        USE_TZ=True,
    )

django.setup()

from django.core.management import call_command
from django.db import NotSupportedError, connection
from django.db.models import IntegerField, Value
from tests.queries.models import Number

def test_union_annotated_distinct():
    """
    Test that distinct() raises NotSupportedError when called on a union queryset.

    This test reproduces the issue where union querysets should raise an error
    when distinct() is called on them, but currently don't.
    """
    # Create the database tables
    call_command('migrate', '--run-syncdb', verbosity=0)

    # Create test data
    Number.objects.bulk_create([Number(num=i, other_num=10 - i) for i in range(10)])

    # Create two querysets with different annotations (similar to the issue description)
    qs1 = Number.objects.filter(num__lte=5).annotate(rank=Value(0, IntegerField()))
    qs2 = Number.objects.filter(num__gte=6).annotate(rank=Value(1, IntegerField()))

    # Union them together
    qs = qs1.union(qs2)

    # Try to call distinct() - this should raise NotSupportedError
    try:
        qs.distinct()
        # If we get here, the bug is present (distinct() didn't raise an error)
        print("FAIL: distinct() did not raise NotSupportedError on union queryset")
        print("This is the bug - distinct() should raise an error on union querysets")
        return False
    except NotSupportedError as e:
        # If we get here, the bug is fixed (distinct() correctly raised an error)
        print(f"PASS: distinct() correctly raised NotSupportedError: {e}")
        return True
    except Exception as e:
        # Unexpected error
        print(f"FAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Run the test
    success = test_union_annotated_distinct()

    if success:
        print("\nTest passed - issue is fixed")
        sys.exit(0)
    else:
        print("\nTest failed - issue is present")
        sys.exit(1)