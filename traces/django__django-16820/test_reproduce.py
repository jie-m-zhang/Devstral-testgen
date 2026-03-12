#!/usr/bin/env python
"""
Test to reproduce the issue with squashing migrations with Meta.index_together -> Meta.indexes transition.

The issue is that when squashing migrations, the reduce() method in CreateModel should handle
IndexOperation types (AddIndex, RemoveIndex, RenameIndex) to properly convert index_together
to indexes and remove deprecation warnings.
"""

import os
import sys
import warnings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.test.utils')

import django
from django.conf import settings

# Configure minimal settings
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

from django.db import migrations, models
from django.db.migrations.operations.models import CreateModel, AddIndex, RemoveIndex, RenameIndex
from django.db.migrations.state import ProjectState
from django.utils.deprecation import RemovedInDjango51Warning

def test_create_model_reduce_with_add_index():
    """
    Test that CreateModel.reduce() properly handles AddIndex operations.

    This should convert index_together to indexes when an AddIndex operation is reduced.
    """
    print("Testing CreateModel.reduce() with AddIndex...")

    # Create a CreateModel operation with index_together
    create_model = CreateModel(
        "TestModel",
        fields=[
            ("id", models.AutoField(primary_key=True)),
            ("field1", models.CharField(max_length=100)),
            ("field2", models.CharField(max_length=100)),
        ],
        options={
            "index_together": [("field1", "field2")],
        },
    )

    # Create an AddIndex operation
    add_index = AddIndex(
        "TestModel",
        models.Index(fields=["field1", "field2"], name="test_index"),
    )

    # Try to reduce the operations
    result = create_model.reduce(add_index, "test_app")

    # The result should be a list of operations (not False)
    assert result is not False, "Expected reduction to succeed, got False"
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 1, f"Expected 1 operation, got {len(result)}"
    assert isinstance(result[0], CreateModel), f"Expected CreateModel, got {type(result[0])}"

    new_create_model = result[0]
    print(f"Original options: {create_model.options}")
    print(f"New options: {new_create_model.options}")

    # Check that indexes option exists and contains the new index
    assert "indexes" in new_create_model.options, "Expected 'indexes' in options"
    assert len(new_create_model.options["indexes"]) == 1, f"Expected 1 index, got {len(new_create_model.options['indexes'])}"

    # Check that the index was added
    index = new_create_model.options["indexes"][0]
    assert index.name == "test_index", f"Expected index name 'test_index', got '{index.name}'"
    assert list(index.fields) == ["field1", "field2"], f"Expected fields ['field1', 'field2'], got {list(index.fields)}"

    print("✓ Test passed: AddIndex properly reduced with CreateModel")

def test_create_model_reduce_with_remove_index():
    """
    Test that CreateModel.reduce() properly handles RemoveIndex operations.
    """
    print("\nTesting CreateModel.reduce() with RemoveIndex...")

    # Create a CreateModel operation with indexes
    test_index = models.Index(fields=["field1", "field2"], name="test_index")
    create_model = CreateModel(
        "TestModel",
        fields=[
            ("id", models.AutoField(primary_key=True)),
            ("field1", models.CharField(max_length=100)),
            ("field2", models.CharField(max_length=100)),
        ],
        options={
            "indexes": [test_index],
        },
    )

    # Create a RemoveIndex operation
    remove_index = RemoveIndex("TestModel", "test_index")

    # Try to reduce the operations
    result = create_model.reduce(remove_index, "test_app")

    # The result should be a list of operations (not False)
    assert result is not False, "Expected reduction to succeed, got False"
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 1, f"Expected 1 operation, got {len(result)}"
    assert isinstance(result[0], CreateModel), f"Expected CreateModel, got {type(result[0])}"

    new_create_model = result[0]
    print(f"Original options: {create_model.options}")
    print(f"New options: {new_create_model.options}")

    # Check that indexes option exists but is empty or doesn't contain the removed index
    assert "indexes" in new_create_model.options, "Expected 'indexes' in options"
    assert len(new_create_model.options["indexes"]) == 0, f"Expected 0 indexes after removal, got {len(new_create_model.options['indexes'])}"

    print("✓ Test passed: RemoveIndex properly reduced with CreateModel")

def test_create_model_reduce_with_rename_index():
    """
    Test that CreateModel.reduce() properly handles RenameIndex operations with old_fields.
    """
    print("\nTesting CreateModel.reduce() with RenameIndex (old_fields)...")

    # Create a CreateModel operation with index_together
    create_model = CreateModel(
        "TestModel",
        fields=[
            ("id", models.AutoField(primary_key=True)),
            ("field1", models.CharField(max_length=100)),
            ("field2", models.CharField(max_length=100)),
        ],
        options={
            "index_together": [("field1", "field2")],
        },
    )

    # Create a RenameIndex operation with old_fields
    rename_index = RenameIndex(
        "TestModel",
        new_name="new_index_name",
        old_fields=("field1", "field2"),
    )

    # Try to reduce the operations
    result = create_model.reduce(rename_index, "test_app")

    # The result should be a list of operations (not False)
    assert result is not False, "Expected reduction to succeed, got False"
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 1, f"Expected 1 operation, got {len(result)}"
    assert isinstance(result[0], CreateModel), f"Expected CreateModel, got {type(result[0])}"

    new_create_model = result[0]
    print(f"Original options: {create_model.options}")
    print(f"New options: {new_create_model.options}")

    # Check that indexes option exists and contains the renamed index
    assert "indexes" in new_create_model.options, "Expected 'indexes' in options"
    assert len(new_create_model.options["indexes"]) == 1, f"Expected 1 index, got {len(new_create_model.options['indexes'])}"

    # Check that the index was renamed
    index = new_create_model.options["indexes"][0]
    assert index.name == "new_index_name", f"Expected index name 'new_index_name', got '{index.name}'"
    assert list(index.fields) == ["field1", "field2"], f"Expected fields ['field1', 'field2'], got {list(index.fields)}"

    # Check that index_together was removed or converted
    assert "index_together" not in new_create_model.options, "Expected 'index_together' to be removed"

    print("✓ Test passed: RenameIndex properly reduced with CreateModel")

def test_main():
    """
    Run all tests to reproduce the issue.
    """
    print("=" * 70)
    print("Testing migration squashing with index_together -> indexes transition")
    print("=" * 70)

    # Capture warnings to check for deprecation warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        try:
            test_create_model_reduce_with_add_index()
        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

        try:
            test_create_model_reduce_with_remove_index()
        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

        try:
            test_create_model_reduce_with_rename_index()
        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)

if __name__ == "__main__":
    test_main()