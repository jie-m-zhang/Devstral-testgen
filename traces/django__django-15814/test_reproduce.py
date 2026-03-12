#!/usr/bin/env python
"""
Test to reproduce the issue with QuerySet.only() after select_related() on proxy models.

This test reproduces the issue described in the GitHub issue where using
select_related() and only() together on a proxy model causes a ValueError:
'ValueError: 'id' is not in list'
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

from django.db import models
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test import TestCase

# Setup test environment
setup_test_environment()

# Define test models
class CustomModel(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        app_label = 'test_app'

class ProxyCustomModel(CustomModel):
    class Meta:
        proxy = True
        app_label = 'test_app'

class AnotherModel(models.Model):
    custom = models.ForeignKey(
        ProxyCustomModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        app_label = 'test_app'

def test_select_related_only_proxy():
    """
    Test that select_related() and only() work together on proxy models.

    This should fail on the buggy version with:
    ValueError: 'id' is not in list

    And should pass on the fixed version.
    """
    # Create the database tables
    from django.core.management import call_command
    from django.db import connection

    # Create tables
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(CustomModel)
        schema_editor.create_model(AnotherModel)

    try:
        # Create test data
        custom_obj = ProxyCustomModel.objects.create(name="test")
        another_obj = AnotherModel.objects.create(custom=custom_obj)

        # This is the problematic query that should fail on buggy version
        # and pass on fixed version
        print("Executing query: AnotherModel.objects.select_related('custom').only('custom__name').all()")
        objs = list(AnotherModel.objects.select_related("custom").only("custom__name").all())

        # If we get here without exception, the test passes
        print(f"Query executed successfully. Retrieved {len(objs)} object(s).")

        # Verify we got the expected object
        assert len(objs) == 1, f"Expected 1 object, got {len(objs)}"
        assert objs[0].id == another_obj.id, f"Expected id {another_obj.id}, got {objs[0].id}"

        print("Test PASSED - issue is fixed!")

    except ValueError as e:
        print(f"Test FAILED with ValueError: {e}")
        print("This is expected on the buggy version.")
        raise
    except Exception as e:
        print(f"Test FAILED with unexpected error: {e}")
        raise
    finally:
        # Clean up
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(AnotherModel)
            schema_editor.delete_model(CustomModel)

if __name__ == "__main__":
    test_select_related_only_proxy()