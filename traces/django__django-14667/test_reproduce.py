#!/usr/bin/env python
"""
Test to reproduce the issue with QuerySet.defer() not clearing deferred fields
when chaining with only().

The issue: When chaining .only() with .defer() where all fields in only() are
also deferred, the deferred loading state should be cleared and all fields should
be loaded immediately.
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
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

    django.setup()

# Import after Django setup
from django.db import models
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment

# Setup test environment
setup_test_environment()

# Define a simple Company model for testing
class Company(models.Model):
    name = models.CharField(max_length=100)
    trade_number = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    class Meta:
        app_label = 'test_app'

def test_defer_only_chaining_issue():
    """
    Test that reproduces the issue where defer() doesn't clear deferred fields
    when chaining with only().

    The expected behavior:
    - Company.objects.only("name").defer("name") should load all fields (0 deferred fields)
    - Company.objects.only("name").defer("name").defer("country") should defer only "country" (1 deferred field)
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    # Create the table
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Company)

    # Create a test instance
    company = Company.objects.create(
        name="Test Company",
        trade_number="TN123",
        country="USA"
    )

    # Test case 1: only("name").defer("name") should load all fields (0 deferred fields)
    print("Test case 1: only('name').defer('name')")
    qs1 = Company.objects.only("name").defer("name")
    obj1 = qs1[0]
    deferred_fields_1 = obj1.get_deferred_fields()
    print(f"Deferred fields: {deferred_fields_1}")
    print(f"Number of deferred fields: {len(deferred_fields_1)}")

    # Should have 0 deferred fields (all fields loaded)
    assert len(deferred_fields_1) == 0, f"Expected 0 deferred fields, got {len(deferred_fields_1)}: {deferred_fields_1}"

    # Test case 2: only("name").defer("name").defer("country") should defer only "country"
    print("\nTest case 2: only('name').defer('name').defer('country')")
    qs2 = Company.objects.only("name").defer("name").defer("country")
    obj2 = qs2[0]
    deferred_fields_2 = obj2.get_deferred_fields()
    print(f"Deferred fields: {deferred_fields_2}")
    print(f"Number of deferred fields: {len(deferred_fields_2)}")

    # Should have 1 deferred field (country)
    assert len(deferred_fields_2) == 1, f"Expected 1 deferred field, got {len(deferred_fields_2)}: {deferred_fields_2}"
    assert 'country' in deferred_fields_2, f"Expected 'country' to be deferred, got: {deferred_fields_2}"

    # Test case 3: only("name", "country").defer("name") should defer only "name" and "trade_number"
    print("\nTest case 3: only('name', 'country').defer('name')")
    qs3 = Company.objects.only("name", "country").defer("name")
    obj3 = qs3[0]
    deferred_fields_3 = obj3.get_deferred_fields()
    print(f"Deferred fields: {deferred_fields_3}")
    print(f"Number of deferred fields: {len(deferred_fields_3)}")

    # Should have 2 deferred fields (name and trade_number)
    assert len(deferred_fields_3) == 2, f"Expected 2 deferred fields, got {len(deferred_fields_3)}: {deferred_fields_3}"
    assert 'name' in deferred_fields_3, f"Expected 'name' to be deferred, got: {deferred_fields_3}"
    assert 'trade_number' in deferred_fields_3, f"Expected 'trade_number' to be deferred, got: {deferred_fields_3}"

    print("\nAll tests passed!")

if __name__ == "__main__":
    try:
        test_defer_only_chaining_issue()
        print("\n✓ Test PASSED - Issue is fixed")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test FAILED - Issue reproduced: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        teardown_test_environment()