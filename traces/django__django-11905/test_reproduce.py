"""
Test to reproduce the issue where __isnull lookup accepts non-boolean values.
The test should FAIL on base commit (no warning raised) and PASS on head commit (warning raised).
"""

import warnings
import os
import sys

# Configure Django settings BEFORE importing any models
import django
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
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

# Now import Django components
from django.db.models import Value, Field
from django.db.models.lookups import IsNull

def test_isnull_with_non_boolean_value():
    """
    Test that using non-boolean values with __isnull lookup raises a deprecation warning.
    This test directly tests the IsNull lookup class without needing a full database setup.
    """
    print("Testing IsNull lookup with non-boolean value...")

    # Create a simple field for testing
    test_field = Field()
    test_field.set_attributes_from_name('test_field')
    test_field.model = type('TestModel', (), {})

    # Create an IsNull lookup with a non-boolean value (integer 1)
    lookup = IsNull(lhs=Value('test'), rhs=1)

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Try to call as_sql - this should trigger the warning in the fixed version
        try:
            from django.db.models.sql.compiler import SQLCompiler
            from django.db.models.sql.query import Query

            # Create a minimal compiler to test as_sql
            query = Query(model=type('TestModel', (), {}))
            compiler = SQLCompiler(query, connection=None, using='default')

            # This should trigger the warning check in the fixed version
            lookup.as_sql(compiler, connection=None)
        except Exception as e:
            # We expect this to fail due to missing connection, but we're just checking for warnings
            pass

        # Check if the deprecation warning was raised
        warning_found = False
        for warning in w:
            print(f"Warning caught: {warning.category.__name__}: {warning.message}")
            if ("non-boolean" in str(warning.message).lower() or
                "isnull" in str(warning.message).lower()):
                warning_found = True
                break

        # Also check for the specific RemovedInDjango40Warning if it exists
        if not warning_found:
            try:
                from django.utils.deprecation import RemovedInDjango40Warning
                for warning in w:
                    if (issubclass(warning.category, RemovedInDjango40Warning) and
                        "non-boolean" in str(warning.message).lower()):
                        warning_found = True
                        break
            except ImportError:
                pass

        # This assertion will FAIL on base commit (no warning) and PASS on head commit (warning raised)
        assert warning_found, "Expected a deprecation warning when using non-boolean value with __isnull lookup"
        print("Test passed - warning was raised for non-boolean value")

def test_isnull_with_boolean_value():
    """
    Test that using boolean values (True/False) with __isnull lookup works without warnings.
    """
    print("Testing IsNull lookup with boolean value...")

    # Create a simple field for testing
    test_field = Field()
    test_field.set_attributes_from_name('test_field')
    test_field.model = type('TestModel', (), {})

    # Create an IsNull lookup with a boolean value (True)
    lookup = IsNull(lhs=Value('test'), rhs=True)

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Try to call as_sql
        try:
            from django.db.models.sql.compiler import SQLCompiler
            from django.db.models.sql.query import Query

            query = Query(model=type('TestModel', (), {}))
            compiler = SQLCompiler(query, connection=None, using='default')

            lookup.as_sql(compiler, connection=None)
        except Exception:
            pass

        # Check that no deprecation warning was raised for boolean values
        warning_found = any(
            "non-boolean" in str(warning.message).lower()
            for warning in w
        )

        if warning_found:
            print("Test failed - unexpected warning for boolean value")
            assert False, "Boolean values should not trigger deprecation warnings for __isnull lookup"
        else:
            print("Test passed - no warning for boolean value")

if __name__ == "__main__":
    try:
        test_isnull_with_non_boolean_value()
        test_isnull_with_boolean_value()
        print("\nAll tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)