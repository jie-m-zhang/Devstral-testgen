"""
Test to reproduce the issue where Queryset raises NotSupportedError when
RHS has filterable=False attribute.

The issue occurs when a model has a field named "filterable" with a value of False,
and we try to filter on a related model that has this field.
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

# Now import Django models
from django.db import models
from django.utils import timezone

# Define the models from the issue
class ProductMetaDataType(models.Model):
    label = models.CharField(max_length=255, unique=True, blank=False, null=False)
    filterable = models.BooleanField(default=False, verbose_name="filterable")

    class Meta:
        app_label = "test_app"

    def __str__(self):
        return self.label

class Product(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "test_app"

    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "test_app"

    def __str__(self):
        return self.name

class ProductMetaData(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE
    )
    value = models.TextField(null=False, blank=False)
    marketplace = models.ForeignKey(
        Platform, null=False, blank=False, on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(null=True, default=timezone.now)
    metadata_type = models.ForeignKey(
        ProductMetaDataType, null=False, blank=False, on_delete=models.CASCADE
    )

    class Meta:
        app_label = "test_app"

# Create the tables
from django.core.management import call_command
from django.db import connection

def setup_test_database():
    # Create tables
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(ProductMetaDataType)
        schema_editor.create_model(Product)
        schema_editor.create_model(Platform)
        schema_editor.create_model(ProductMetaData)

def test_filterable_field_issue():
    """
    Test that filtering on a model with a filterable=False field works correctly.

    This should reproduce the NotSupportedError on the base commit and pass on the head commit.
    """
    setup_test_database()

    # Create test data
    metadata_type = ProductMetaDataType.objects.create(label="brand", filterable=False)
    product = Product.objects.create(name="Test Product")
    platform = Platform.objects.create(name="Test Platform")

    # Create a ProductMetaData instance
    metadata = ProductMetaData.objects.create(
        product=product,
        value="Dark Vador",
        marketplace=platform,
        metadata_type=metadata_type
    )

    # This should NOT raise NotSupportedError
    # On the base commit, this will fail with:
    # django.db.utils.NotSupportedError: ProductMetaDataType is disallowed in the filter clause.
    try:
        results = ProductMetaData.objects.filter(value="Dark Vador", metadata_type=metadata_type)
        result_list = list(results)
        assert len(result_list) == 1, f"Expected 1 result, got {len(result_list)}"
        assert result_list[0].value == "Dark Vador", f"Expected 'Dark Vador', got '{result_list[0].value}'"
        print("Test passed - filtering with filterable=False field works correctly")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = test_filterable_field_issue()
    if success:
        print("\nTest completed successfully!")
        sys.exit(0)
    else:
        print("\nTest failed!")
        sys.exit(1)