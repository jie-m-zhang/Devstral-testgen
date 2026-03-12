"""
Test to reproduce the issue where deleting an index_together crashes
when there is a unique_together on the same fields.

This test should FAIL on the base commit and PASS on the head commit.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_sqlite')
sys.path.insert(0, '/testbed')

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
        ],
        SECRET_KEY='test-secret-key',
    )

django.setup()

from django.db import models, connection
from django.db.models import CharField, SlugField
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

def test_delete_index_together_with_unique_together():
    """
    Test that deleting index_together doesn't crash when unique_together
    exists on the same fields.
    """

    # Define a model with both unique_together and index_together on same fields
    class TestModel(models.Model):
        field1 = CharField(max_length=100)
        field2 = SlugField(max_length=100)

        class Meta:
            app_label = 'test_app'
            unique_together = [['field1', 'field2']]
            index_together = [['field1', 'field2']]

    # Create the table
    with connection.schema_editor() as editor:
        editor.create_model(TestModel)

    # Get constraints to verify both were created
    def get_constraints(table):
        with connection.cursor() as cursor:
            return connection.introspection.get_constraints(cursor, table)

    constraints = get_constraints(TestModel._meta.db_table)
    print("Constraints after creation:", list(constraints.keys()))

    # Count unique and index constraints on the same fields
    unique_constraints = [
        name for name, details in constraints.items()
        if set(details['columns']) == {'field1', 'field2'} and details['unique']
    ]
    index_constraints = [
        name for name, details in constraints.items()
        if set(details['columns']) == {'field1', 'field2'} and details['index'] and not details['unique']
    ]

    print(f"Unique constraints on field1,field2: {unique_constraints}")
    print(f"Index constraints on field1,field2: {index_constraints}")

    # There should be at least one unique constraint
    assert len(unique_constraints) >= 1, "Should have at least one unique constraint"

    # Now try to delete only the index_together (this should crash on buggy version)
    try:
        with connection.schema_editor() as editor:
            # This is what happens when index_together is removed but unique_together remains
            editor.alter_index_together(
                TestModel,
                [['field1', 'field2']],  # old index_together
                []                        # new index_together (empty)
            )
        print("SUCCESS: alter_index_together completed without error")
    except ValueError as e:
        print(f"FAILED: alter_index_together raised ValueError: {e}")
        # This is the expected failure on the buggy version
        if "Found wrong number (2) of constraints" in str(e):
            print("This is the expected error on the buggy version")
            raise AssertionError("Bug reproduced: Found 2 constraints when trying to delete index_together with unique_together on same fields")
        else:
            raise

    # Verify the unique constraint still exists
    constraints_after = get_constraints(TestModel._meta.db_table)
    unique_after = [
        name for name, details in constraints_after.items()
        if set(details['columns']) == {'field1', 'field2'} and details['unique']
    ]
    index_after = [
        name for name, details in constraints_after.items()
        if set(details['columns']) == {'field1', 'field2'} and details['index'] and not details['unique']
    ]

    print(f"After deletion - Unique constraints: {unique_after}")
    print(f"After deletion - Index constraints: {index_after}")

    # Unique constraint should still exist
    assert len(unique_after) >= 1, "Unique constraint should still exist"
    # Index constraint should be gone
    assert len(index_after) == 0, "Index constraint should be removed"

    print("Test passed - issue is fixed")

if __name__ == '__main__':
    test_delete_index_together_with_unique_together()