"""
Test to reproduce the issue with saving parent object after setting on child
with non-numeric primary key leading to data loss.
"""

import os
import sys
import django
from django.conf import settings
from django.db import models
from django.db import transaction
from django.test.utils import get_runner
from django.test import TestCase

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

# Define test models
class Product(models.Model):
    sku = models.CharField(primary_key=True, max_length=50)

    class Meta:
        app_label = 'test_app'

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        app_label = 'test_app'

# Create the table
from django.core.management import call_command
from django.db import connection

def setup_database():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Product)
        schema_editor.create_model(Order)

def test_issue_reproduction():
    """
    Test that reproduces the issue where saving parent object after setting
    on child with non-numeric primary key leads to data loss.
    """
    setup_database()

    # Test case 1: The problematic case - setting primary key after assignment
    print("Test case 1: Setting primary key after assignment (should fail on buggy version)")
    try:
        with transaction.atomic():
            order = Order()
            order.product = Product()  # Empty instance without primary key
            order.product.sku = "foo"  # Set primary key after assignment
            order.product.save()       # Save the product
            print(f"Product saved with sku: '{order.product.sku}' and pk: '{order.product.pk}'")

            # Save the order - this is where the bug occurs
            order.save()               # Save the order

            # Check the raw value of product_id field
            product_id_value = order.product_id
            print(f"order.product_id value after save: '{product_id_value}'")

            # The bug is that product_id is set to empty string instead of "foo"
            if product_id_value == "":
                print("✗ BUG DETECTED: product_id is empty string instead of 'foo'")
                # This is the bug - we should raise an assertion error
                assert False, f"product_id is '{product_id_value}' but should be 'foo'"
            else:
                print(f"✓ product_id is correctly set to: '{product_id_value}'")

    except AssertionError as e:
        print(f"✗ Test case 1 FAILED (bug detected): {e}")
        raise
    except Exception as e:
        print(f"✗ Test case 1 FAILED with unexpected exception: {e}")
        raise

    # Test case 2: The working case - setting primary key before assignment
    print("\nTest case 2: Setting primary key before assignment (should always work)")
    try:
        with transaction.atomic():
            order2 = Order()
            order2.product = Product(sku="bar")  # Set primary key before assignment
            order2.product.save()
            order2.save()

            product_id_value2 = order2.product_id
            print(f"order2.product_id value: '{product_id_value2}'")

            if product_id_value2 == "bar":
                print("✓ Test case 2 PASSED - product_id is correctly set")
            else:
                print(f"✗ Test case 2 FAILED: product_id is '{product_id_value2}' but should be 'bar'")
                raise AssertionError(f"product_id is '{product_id_value2}' but should be 'bar'")

    except Exception as e:
        print(f"✗ Test case 2 FAILED with exception: {e}")
        raise

    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_issue_reproduction()