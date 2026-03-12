"""
Test to reproduce the issue where get_FOO_display() cannot be overridden in Django 2.2+.

The issue is that when a model has a field with choices and defines a custom
get_FIELD_display() method, the custom method is not called. Instead, the default
implementation is used.
"""

import os
import sys
import django
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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
            '__main__',
        ],
        USE_TZ=True,
    )
    django.setup()

from django.db import models

# Define a model with choices and overridden get_FIELD_display
class FooBar(models.Model):
    foo_bar = models.CharField(
        _("foo"),
        choices=[(1, 'foo'), (2, 'bar')],
        max_length=10
    )

    class Meta:
        app_label = 'test_app'

    def __str__(self):
        return self.get_foo_bar_display()

    def get_foo_bar_display(self):
        # This should return "something" but in Django 2.2+ it returns 'foo' or 'bar'
        return "something"

# Create the table
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(FooBar)

def test_issue_reproduction():
    """
    Test that get_FIELD_display() can be overridden.

    This test should FAIL on Django 2.2+ (base commit) because the overridden
    method is not called, and should PASS on the fixed version where the
    overridden method is properly called.
    """
    # Create an instance with value 1
    instance = FooBar(foo_bar=1)

    # Call the overridden get_foo_bar_display method
    result = instance.get_foo_bar_display()

    # The overridden method should return "something"
    # In Django 2.2+ (buggy version), it will return 'foo' instead
    print(f"Result: {result}")
    print(f"Expected: something")

    # This assertion will fail on buggy code (Django 2.2+), pass on fixed code
    assert result == "something", f"Expected 'something', got '{result}'"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()