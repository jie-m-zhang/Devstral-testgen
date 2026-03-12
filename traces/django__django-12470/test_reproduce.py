"""
Test to reproduce the issue where inherited model doesn't correctly order by "-pk"
when specified on Parent.Meta.ordering
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

# Setup Django
django.setup()

from django.db import models
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment

# Setup test environment
setup_test_environment()

# Define test models
class Parent(models.Model):
    class Meta:
        app_label = 'test_app'
        ordering = ["-pk"]

class Child(Parent):
    class Meta:
        app_label = 'test_app'

# Create the database tables
from django.core.management import call_command
from django.db import connection

# Create tables
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Parent)
    schema_editor.create_model(Child)

def test_issue_reproduction():
    """
    Test that Child model inherits the ordering from Parent correctly.
    The issue is that when Parent has ordering = ["-pk"], the Child queryset
    should also be ordered by -pk (DESC), but it's incorrectly ordered by ASC.
    """
    # Create some test data
    parent1 = Parent.objects.create()
    parent2 = Parent.objects.create()
    parent3 = Parent.objects.create()

    child1 = Child.objects.create(parent_ptr=parent1)
    child2 = Child.objects.create(parent_ptr=parent2)
    child3 = Child.objects.create(parent_ptr=parent3)

    # Get the query to check the ORDER BY clause
    query = Child.objects.all().query
    query_str = str(query)

    print("Query string:")
    print(query_str)

    # Check if the query contains "ORDER BY" with "ASC" (bug) or "DESC" (correct)
    # The bug is that it orders by ASC instead of DESC
    if "ORDER BY" in query_str:
        if '"myapp_parent"."id" ASC' in query_str or '"test_app_parent"."id" ASC' in query_str:
            print("BUG REPRODUCED: Query is ordered ASC instead of DESC")
            print("Expected: ORDER BY ... DESC")
            print("Got: ORDER BY ... ASC")
            return False
        elif '"myapp_parent"."id" DESC' in query_str or '"test_app_parent"."id" DESC' in query_str:
            print("CORRECT: Query is ordered DESC as expected")
            return True
        else:
            print("WARNING: Could not determine ordering from query string")
            print("Query:", query_str)
            # Let's check the actual ordering by fetching results
            # Create more objects to verify ordering
            Child.objects.all().delete()
            Parent.objects.all().delete()

            # Create objects in a specific order
            p1 = Parent.objects.create(id=1)
            p2 = Parent.objects.create(id=2)
            p3 = Parent.objects.create(id=3)

            c1 = Child.objects.create(parent_ptr=p1)
            c2 = Child.objects.create(parent_ptr=p2)
            c3 = Child.objects.create(parent_ptr=p3)

            # Fetch all children and check order
            children = list(Child.objects.all())
            ids = [c.id for c in children]

            print(f"Child IDs in order: {ids}")

            # With DESC ordering, we should get [3, 2, 1]
            if ids == [3, 2, 1]:
                print("CORRECT: Children are ordered DESC by pk")
                return True
            elif ids == [1, 2, 3]:
                print("BUG REPRODUCED: Children are ordered ASC by pk (should be DESC)")
                return False
            else:
                print(f"UNEXPECTED: Children are ordered as {ids}")
                return False
    else:
        print("No ORDER BY clause found in query")
        return False

if __name__ == "__main__":
    try:
        result = test_issue_reproduction()
        if result:
            print("\nTest PASSED - issue is fixed")
            sys.exit(0)
        else:
            print("\nTest FAILED - issue reproduced")
            sys.exit(1)
    except Exception as e:
        print(f"\nTest ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        teardown_test_environment()