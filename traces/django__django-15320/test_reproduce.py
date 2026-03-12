#!/usr/bin/env python
"""
Test to reproduce the Subquery.as_sql() issue.

The issue is that Subquery.as_sql() generates invalid SQL by removing
the first and last characters instead of absent brackets when subquery
is not set to True in the constructor.
"""

import os
import sys
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, '/testbed')
sys.path.insert(0, '/testbed/tests')  # Add tests directory to path

# Create a minimal settings module
with open('/testbed/test_settings.py', 'w') as f:
    f.write("""
SECRET_KEY = 'test-secret-key'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'expressions',
]
USE_TZ = True
""")

# Now setup Django
django.setup()

# Import after Django setup
from expressions.models import Employee
from django.db.models import Subquery

def test_subquery_as_sql():
    """
    Test that Subquery.as_sql() generates valid SQL.

    The bug: Subquery.as_sql() removes first and last characters instead of
    absent brackets, producing invalid SQL like:
    '(ELECT "expressions_employee"."id", ... FROM "expressions_employee")'
    instead of:
    '(SELECT "expressions_employee"."id", ... FROM "expressions_employee")'
    """
    # Create a Subquery from a queryset
    q = Subquery(Employee.objects.all())

    # Get the SQL string from str(q.query) - this should be valid
    query_sql = str(q.query)
    print(f"Query SQL: {query_sql}")
    assert query_sql.startswith('SELECT'), f"Expected query to start with 'SELECT', got: {query_sql}"

    # Now test as_sql() - this is where the bug occurs
    compiler = q.query.get_compiler('default')
    sql, params = q.as_sql(compiler, connection)

    print(f"Subquery as_sql result: {sql}")
    print(f"Params: {params}")

    # The SQL should start with '(' and contain 'SELECT'
    # On the buggy version, it will start with '(ELECT' (missing 'S')
    # On the fixed version, it will start with '(SELECT'
    assert sql.startswith('(SELECT'), f"Expected SQL to start with '(SELECT', got: '{sql}'"

    # The SQL should end with ')'
    # On the buggy version, it will end with a missing character
    # On the fixed version, it will end with ')'
    assert sql.endswith(')'), f"Expected SQL to end with ')', got: '{sql}'"

    print("Test passed - Subquery.as_sql() generates valid SQL")

if __name__ == "__main__":
    # Create the table first
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Employee)

    try:
        test_subquery_as_sql()
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)