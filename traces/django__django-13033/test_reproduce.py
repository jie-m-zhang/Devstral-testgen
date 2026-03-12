"""
Test to reproduce the issue with self-referencing foreign key ordering.

The issue is that when ordering by "record__root_id", the query incorrectly
applies a DESC sort order (from the model's default ordering) instead of
the expected ASC sort order.
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
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment

# Setup test environment
setup_test_environment()

# Define models
class OneModel(models.Model):
    class Meta:
        app_label = 'test_app'
        ordering = ("-id",)

    id = models.BigAutoField(primary_key=True)
    root = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    oneval = models.BigIntegerField(null=True)

    def __str__(self):
        return f"OneModel({self.id}, root={self.root_id if self.root else None}, oneval={self.oneval})"

class TwoModel(models.Model):
    class Meta:
        app_label = 'test_app'

    id = models.BigAutoField(primary_key=True)
    record = models.ForeignKey(OneModel, on_delete=models.CASCADE)
    twoval = models.BigIntegerField(null=True)

    def __str__(self):
        return f"TwoModel({self.id}, record={self.record_id}, twoval={self.twoval})"

# Create the table
from django.core.management import call_command
from django.db import connection

# Create tables
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(OneModel)
    schema_editor.create_model(TwoModel)

def test_self_referencing_fk_ordering():
    """
    Test that ordering by a self-referencing foreign key's _id field
    doesn't incorrectly apply the model's default ordering.
    """
    # Create test data
    one1 = OneModel.objects.create(oneval=1)
    one2 = OneModel.objects.create(oneval=2, root=one1)
    one3 = OneModel.objects.create(oneval=3, root=one1)

    two1 = TwoModel.objects.create(record=one1, twoval=10)
    two2 = TwoModel.objects.create(record=one2, twoval=20)
    two3 = TwoModel.objects.create(record=one3, twoval=30)

    # Test the problematic queryset
    qs = TwoModel.objects.filter(record__oneval__in=[1, 2, 3])
    qs = qs.order_by("record__root_id")

    # Get the SQL query
    sql = str(qs.query)

    print("Generated SQL:")
    print(sql)
    print()

    # Check that the SQL doesn't have DESC in the ORDER BY clause
    # The issue is that it incorrectly applies DESC from OneModel's ordering
    if "ORDER BY" in sql:
        order_by_clause = sql[sql.find("ORDER BY"):]
        print(f"ORDER BY clause: {order_by_clause}")

        # The bug causes DESC to appear when it shouldn't
        # We expect ASC or no direction specified (which defaults to ASC)
        if "DESC" in order_by_clause.upper():
            print("ERROR: ORDER BY clause contains DESC (bug present)")
            print("Expected: ASC or no direction specified")
            return False
        else:
            print("OK: ORDER BY clause does not contain DESC")
            return True
    else:
        print("ERROR: No ORDER BY clause found")
        return False

if __name__ == "__main__":
    try:
        success = test_self_referencing_fk_ordering()
        if success:
            print("\nTest PASSED - issue is fixed")
            sys.exit(0)
        else:
            print("\nTest FAILED - issue is present")
            sys.exit(1)
    except Exception as e:
        print(f"\nTest ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        teardown_test_environment()