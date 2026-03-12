#!/usr/bin/env python
"""
Test to reproduce the issue where migration optimizer does not reduce
multiple AlterField operations when they're not preceded by an AddField.
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
        USE_TZ=True,
    )
    django.setup()

from django.db import migrations, models
from django.db.migrations.optimizer import MigrationOptimizer

def test_alterfield_reduction():
    """
    Test that multiple AlterField operations on the same field are reduced.

    This test reproduces the issue described in the GitHub issue where
    multiple AlterField operations are not being optimized when they're
    not preceded by an AddField operation.
    """
    # Create the operations as described in the issue
    operations = [
        migrations.AlterField(
            model_name="book",
            name="title",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="book",
            name="title",
            field=models.CharField(max_length=128, null=True, help_text="help"),
        ),
        migrations.AlterField(
            model_name="book",
            name="title",
            field=models.CharField(max_length=128, null=True, help_text="help", default=None),
        ),
    ]

    # Optimize the operations
    optimizer = MigrationOptimizer()
    result = optimizer.optimize(operations, "books")

    # The expected behavior is that all three AlterField operations should be
    # reduced to just the last one (the one with all the attributes)
    # On the buggy version, all three operations will remain
    # On the fixed version, only the last one should remain
    print(f"Number of operations after optimization: {len(result)}")
    print(f"Operations: {result}")

    # The test should pass on the fixed version (only 1 operation remains)
    # and fail on the buggy version (3 operations remain)
    assert len(result) == 1, f"Expected 1 operation after optimization, got {len(result)}"

    # Verify that the remaining operation is the last AlterField
    assert isinstance(result[0], migrations.AlterField)
    assert result[0].field.max_length == 128
    assert result[0].field.null is True
    assert result[0].field.help_text == "help"
    assert result[0].field.default is None

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_alterfield_reduction()