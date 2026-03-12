"""
Test to reproduce the issue with multiline RawSQL order_by clauses being incorrectly removed.

The issue is that when using multiline RawSQL expressions in order_by clauses,
the SQLCompiler incorrectly identifies them as duplicates because it only looks at
the last line of each multiline SQL when checking for duplicates.
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
        ],
        USE_TZ=True,
    )
    django.setup()

from django.db import models
from django.db.models.expressions import RawSQL

# Create a test model
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_datetime = models.DateTimeField(null=True, blank=True)
    preferred_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'test_app'

def test_multiline_rawsql_order_by():
    """
    Test that multiline RawSQL order_by clauses are not incorrectly removed.

    The bug is that when multiple RawSQL expressions have the same last line,
    they are incorrectly identified as duplicates and only the first one is kept.
    """
    from django.db import connection
    from django.test.utils import setup_test_environment, teardown_test_environment

    # Setup test environment
    setup_test_environment()

    # Create the table
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(TestModel)

    # Create test data
    TestModel.objects.create(
        name='Test 1',
        status='accepted',
        accepted_datetime='2023-01-01T10:00:00Z',
        preferred_datetime='2023-01-02T10:00:00Z'
    )
    TestModel.objects.create(
        name='Test 2',
        status='verification',
        accepted_datetime='2023-01-03T10:00:00Z',
        preferred_datetime='2023-01-04T10:00:00Z'
    )
    TestModel.objects.create(
        name='Test 3',
        status='pending',
        accepted_datetime='2023-01-05T10:00:00Z',
        preferred_datetime='2023-01-06T10:00:00Z'
    )

    # Build the query with multiline RawSQL order_by clauses
    # These all end with the same line: 'else null end'
    queryset = TestModel.objects.all().order_by(
        RawSQL('''
            case when status in ('accepted', 'verification')
                 then 2 else 1 end''', []).desc(),
        RawSQL('''
            case when status in ('accepted', 'verification')
                 then (accepted_datetime, preferred_datetime)
                 else null end''', []).asc(),
        RawSQL('''
            case when status not in ('accepted', 'verification')
                 then (accepted_datetime, preferred_datetime, created_at)
                 else null end''', []).desc()
    )

    # Get the SQL query
    sql = str(queryset.query)

    print("Generated SQL:")
    print(sql)
    print("\n")

    # Check that all three ORDER BY clauses are present
    # The bug causes the second RawSQL (with asc()) to be removed
    # because it ends with 'else null end' just like the third one

    # Count the number of ORDER BY clauses
    order_by_section = sql[sql.upper().find('ORDER BY'):] if 'ORDER BY' in sql.upper() else ''

    # We should have 3 ORDER BY clauses
    # Let's check for the presence of key patterns from each RawSQL
    # Note: The SQL will have the RawSQL wrapped in parentheses
    expected_patterns = [
        "then 2 else 1 end) DESC",  # First RawSQL
        "accepted_datetime, preferred_datetime",  # Second RawSQL (unique part)
        "created_at"  # Third RawSQL (unique part)
    ]

    print("Checking for expected patterns in ORDER BY clause:")
    for i, pattern in enumerate(expected_patterns, 1):
        present = pattern in order_by_section
        print(f"Pattern {i} ({'First' if i==1 else 'Second' if i==2 else 'Third'} RawSQL): {'FOUND' if present else 'MISSING'}")
        if not present:
            print(f"  Expected: {pattern}")

    print("\n")

    # The bug is present if the second or third patterns are missing
    if expected_patterns[1] not in order_by_section or expected_patterns[2] not in order_by_section:
        print("BUG REPRODUCED: One or more RawSQL order_by clauses are missing!")
        print("The regex only looks at the last line when checking for duplicates.")
        return False
    else:
        print("All ORDER BY clauses are present - bug is fixed!")
        return True

    # Clean up
    teardown_test_environment()
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(TestModel)

if __name__ == "__main__":
    success = test_multiline_rawsql_order_by()
    if not success:
        print("\nTest FAILED - issue reproduced")
        sys.exit(1)
    else:
        print("\nTest PASSED - issue is fixed")
        sys.exit(0)