"""
Test to reproduce the issue with abstract model fields being equal across models.

The issue is that fields from different models that inherit from the same
abstract model are considered equal when they shouldn't be.
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
            'test_app',
        ],
        USE_TZ=True,
    )
    django.setup()

# Now import the models
from test_app.models import A, B, C

def test_abstract_field_equality():
    """
    Test that fields from different models inheriting from the same abstract
    model should not be equal.
    """
    # Get the fields from models B and C
    field_b = B._meta.get_field('myfield')
    field_c = C._meta.get_field('myfield')

    # Test 1: Fields should not be equal
    print(f"Field B: {field_b}")
    print(f"Field C: {field_c}")
    print(f"Field B model: {field_b.model}")
    print(f"Field C model: {field_c.model}")
    print(f"Field B == Field C: {field_b == field_c}")

    # This should fail on the buggy version (fields are equal)
    # and pass on the fixed version (fields are not equal)
    assert field_b != field_c, "Fields from different models should not be equal"

    # Test 2: Set should contain both fields (not deduplicated)
    field_set = {field_b, field_c}
    print(f"Length of field set: {len(field_set)}")
    assert len(field_set) == 2, "Set should contain both fields, not deduplicate them"

    # Test 3: Hash should be different
    print(f"Hash of field_b: {hash(field_b)}")
    print(f"Hash of field_c: {hash(field_c)}")
    assert hash(field_b) != hash(field_c), "Hashes of fields from different models should be different"

    print("All tests passed!")

if __name__ == "__main__":
    test_abstract_field_equality()