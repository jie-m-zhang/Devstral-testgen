"""
Test to reproduce the issue where class methods from nested classes cannot be used as Field.default.

The issue is in FunctionTypeSerializer.serialize() which uses klass.__name__ instead of klass.__qualname__.
"""

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

from django.db.migrations.serializer import FunctionTypeSerializer

def test_nested_class_method_serialization():
    """
    Test that FunctionTypeSerializer uses __qualname__ for nested classes.

    This directly tests the code path that the patch fixes.
    """
    # Create a nested class with a classmethod
    class OuterClass:
        class InnerClass:
            @classmethod
            def method(cls):
                return "test"

    # Get the method
    method = OuterClass.InnerClass.method

    # Serialize it
    serializer = FunctionTypeSerializer(method)
    serialized_value, imports = serializer.serialize()

    print(f"Serialized value: {serialized_value}")
    print(f"Imports: {imports}")

    # With the bug (using __name__), it would be "__main__.InnerClass.method"
    # With the fix (using __qualname__), it should include "OuterClass" in the path
    assert "OuterClass" in serialized_value, \
        f"Expected 'OuterClass' in serialized value (using __qualname__), got: {serialized_value}"

    print("Test passed - __qualname__ is used correctly!")

if __name__ == "__main__":
    test_nested_class_method_serialization()