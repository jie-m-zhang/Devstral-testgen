"""
Test to reproduce the issue with ExpressionWrapper for ~Q(pk__in=[]).
This test should FAIL on the base commit and PASS on the head commit.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, '/testbed')

# Create a minimal settings file
with open('/testbed/test_settings.py', 'w') as f:
    f.write("""
DEBUG=True
DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
INSTALLED_APPS=[
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'tests.expressions',
]
SECRET_KEY='test-secret-key'
USE_TZ=True
""")

# Configure Django settings
from django.conf import settings
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
            'tests.expressions',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

django.setup()

# Now import Django models
from django.db import models
from django.db.models import Q, ExpressionWrapper, BooleanField
from tests.expressions.models import Company, Employee

def test_expression_wrapper_negated_empty_q():
    """
    Test that ExpressionWrapper with ~Q(pk__in=[]) generates valid SQL.

    The issue is that ~Q(pk__in=[]) should produce valid SQL in SELECT clause,
    but instead produces invalid SQL like "SELECT AS "foo" FROM "table""
    (missing the expression before AS).
    """
    # Create test data
    ceo = Employee.objects.create(firstname='John', lastname='Doe', salary=100)
    company = Company.objects.create(
        name='Test Company',
        num_employees=10,
        num_chairs=5,
        ceo=ceo,
        based_in_eu=False
    )

    queryset = Company.objects.all()

    # Test 1: ExpressionWrapper with Q(pk__in=[]) - this should work
    print("Testing ExpressionWrapper(Q(pk__in=[]))...")
    qs1 = queryset.annotate(foo=ExpressionWrapper(Q(pk__in=[]), output_field=BooleanField()))
    sql1 = str(qs1.values("foo").query)
    print(f"SQL for Q(pk__in=[]): {sql1}")

    # Verify it contains a valid expression (should have "0 AS" or similar)
    assert '0 AS' in sql1 or 'SELECT 0' in sql1, f"Expected valid SQL with '0 AS', got: {sql1}"

    # Test 2: ExpressionWrapper with ~Q(pk__in=[]) - this is the bug
    print("\nTesting ExpressionWrapper(~Q(pk__in=[]))...")
    qs2 = queryset.annotate(foo=ExpressionWrapper(~Q(pk__in=[]), output_field=BooleanField()))
    sql2 = str(qs2.values("foo").query)
    print(f"SQL for ~Q(pk__in=[]): {sql2}")

    # The bug produces invalid SQL like "SELECT AS "foo" FROM "table""
    # (missing expression before AS)
    # On the fixed version, it should produce something like "SELECT 1 AS "foo" FROM "table""
    assert 'AS "foo"' in sql2, f"Expected 'AS \"foo\"' in SQL, got: {sql2}"

    # Check that there's actually an expression before AS
    # The buggy version produces "SELECT AS" (missing expression)
    # The fixed version should produce something like "SELECT 1 AS"
    parts = sql2.split('AS')
    select_part = parts[0].strip()
    assert select_part and select_part[-1] != ' ', f"Missing expression before AS in SQL: {sql2}"

    # More specific check: the expression should not be empty
    # In the buggy version, we get "SELECT AS" which means the part before AS is empty
    # In the fixed version, we should get "SELECT 1 AS" or similar
    if 'SELECT' in sql2:
        select_clause = sql2.split('FROM')[0].strip()
        assert 'SELECT' in select_clause
        # Extract what's between SELECT and FROM
        select_content = select_clause.split('SELECT')[1].strip()
        # Should have something before AS "foo"
        assert 'AS "foo"' in select_content
        before_as = select_content.split('AS "foo"')[0].strip()
        # The bug produces empty string here, fixed version should have "1" or similar
        assert before_as, f"Expression before AS is empty in: {sql2}"
        assert before_as != 'SELECT', f"Invalid SQL structure in: {sql2}"

    print("\nTest passed - issue is fixed!")

if __name__ == "__main__":
    # Create tables
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)

    try:
        test_expression_wrapper_negated_empty_q()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)