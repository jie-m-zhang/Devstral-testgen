"""
Test to reproduce the issue where delete() on instances of models without any
dependencies doesn't clear PKs.

The issue is that when a model instance with no dependencies is deleted via the
fast delete path, the primary key is not cleared on the instance.
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
    )
    django.setup()

from django.db import models
from django.test import TestCase

# Define a simple model with no dependencies
class SimpleModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'test_app'

# Create the table
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(SimpleModel)

def test_pk_cleared_after_delete():
    """
    Test that the primary key is cleared after calling delete() on a model
    instance with no dependencies.
    """
    # Create an instance
    instance = SimpleModel.objects.create(name="test")
    original_pk = instance.pk

    print(f"Created instance with PK: {original_pk}")

    # Verify the instance has a PK
    assert instance.pk is not None, "Instance should have a PK after creation"

    # Delete the instance
    instance.delete()

    # The PK should be cleared (set to None) after deletion
    # This is the assertion that will fail on the buggy version
    assert instance.pk is None, f"PK should be None after delete(), but got: {instance.pk}"

    print("Test passed - PK was properly cleared after delete()")

if __name__ == "__main__":
    test_pk_cleared_after_delete()