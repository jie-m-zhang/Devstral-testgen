"""
Test to reproduce the issue where Q(...) & Exists(...) raises a TypeError
while Exists(...) & Q(...) works fine.
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
from django.db.models import Q, Exists

# Create a simple model for testing
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField()

    class Meta:
        app_label = 'test_app'

def test_q_and_exists_commutative():
    """
    Test that Q() & Exists(...) and Exists(...) & Q() should both work
    (they should be commutative operations).
    """
    # Create a simple queryset for Exists
    # We can't actually execute the query without a database, but we can test
    # that the combination works at the expression level
    queryset = TestModel.objects.all()
    exists_expr = Exists(queryset)

    # This should work (and does work)
    try:
        result1 = exists_expr & Q()
        print(f"Exists(...) & Q() works: {result1}")
        print(f"  Type: {type(result1)}")
    except Exception as e:
        print(f"Exists(...) & Q() failed: {e}")
        raise

    # This should also work but raises TypeError in the buggy version
    try:
        result2 = Q() & exists_expr
        print(f"Q() & Exists(...) works: {result2}")
        print(f"  Type: {type(result2)}")
    except TypeError as e:
        print(f"Q() & Exists(...) failed with TypeError: {e}")
        raise AssertionError(f"Q() & Exists(...) should work but raised TypeError: {e}")

    # Both operations should work without raising TypeError
    # When combining empty Q() with a conditional expression, the result should be the conditional expression
    assert result1 is not None, "Result should not be None"
    assert result2 is not None, "Result should not be None"

    print("Test passed - both operations work correctly")

if __name__ == "__main__":
    test_q_and_exists_commutative()