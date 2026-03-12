#!/usr/bin/env python
"""
Direct test of the TypeSerializer bug.

This test directly tests the TypeSerializer to ensure it uses __qualname__ instead of __name__
for nested classes.

The issue: When a Field subclass is defined as an inner class, the TypeSerializer generates
incorrect import paths (e.g., 'models.Inner' instead of 'models.Outer.Inner').
"""

import sys
import os

# Add the testbed to the path
sys.path.insert(0, '/testbed')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.conf.settings')
import django
from django.conf import settings

# Configure minimal settings if not already configured
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
from django.db.migrations.serializer import TypeSerializer

def test_type_serializer_qualname():
    """Test that TypeSerializer uses __qualname__ for nested classes."""

    # Create a nested class structure
    class Outer:
        class Inner(models.CharField):
            pass

    # Test the TypeSerializer directly
    serializer = TypeSerializer(Outer.Inner)
    serialized, imports = serializer.serialize()

    print(f"Serialized: {serialized}")
    print(f"Imports: {imports}")

    # The serialized form should use the qualified name
    # On the buggy version: __main__.Inner (uses __name__)
    # On the fixed version: __main__....Outer.Inner (uses __qualname__)
    if ".Outer.Inner" in serialized:
        print(f"PASS: Serialized form contains qualified name with '.Outer.Inner'")
        return True
    else:
        print(f"FAIL: Serialized form does not contain qualified name '.Outer.Inner'")
        print(f"Got: '{serialized}'")
        return False

if __name__ == "__main__":
    success = test_type_serializer_qualname()
    if not success:
        print("\nTest FAILED - issue reproduced")
        sys.exit(1)
    else:
        print("\nTest PASSED - issue is fixed")
        sys.exit(0)