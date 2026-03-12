"""
Test to reproduce the issue with Model.get_FOO_display() not working correctly
with inherited choices.

The issue: When a child model inherits from a base model and overrides the choices,
get_FOO_display() doesn't work correctly for the new choices added in the child.
"""

import os
import sys
import django
from django.conf import settings
from django.apps import apps

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

# Define the models as described in the issue
class A(models.Model):
    foo_choice = [("A", "output1"), ("B", "output2")]
    field_foo = models.CharField(max_length=254, choices=foo_choice)

    class Meta:
        abstract = True
        app_label = 'test_app'

class B(A):
    foo_choice = [("A", "output1"), ("B", "output2"), ("C", "output3")]
    field_foo = models.CharField(max_length=254, choices=foo_choice)

    class Meta:
        app_label = 'test_app'

def test_issue_reproduction():
    """
    Test that get_field_foo_display() works correctly for both inherited
    and new choices in the child model.
    """
    print("Testing get_FIELD_display() with inherited choices...")

    # Test with value "A" (inherited from parent)
    instance_a = B(field_foo="A")
    result_a = instance_a.get_field_foo_display()
    print(f"Value 'A': get_field_foo_display() = '{result_a}'")
    assert result_a == "output1", f"Expected 'output1', got '{result_a}'"

    # Test with value "B" (inherited from parent)
    instance_b = B(field_foo="B")
    result_b = instance_b.get_field_foo_display()
    print(f"Value 'B': get_field_foo_display() = '{result_b}'")
    assert result_b == "output2", f"Expected 'output2', got '{result_b}'"

    # Test with value "C" (new in child)
    instance_c = B(field_foo="C")
    result_c = instance_c.get_field_foo_display()
    print(f"Value 'C': get_field_foo_display() = '{result_c}'")
    # This is the critical test - it should return "output3" but returns "C" in buggy version
    assert result_c == "output3", f"Expected 'output3', got '{result_c}'"

    print("All tests passed!")

if __name__ == "__main__":
    test_issue_reproduction()