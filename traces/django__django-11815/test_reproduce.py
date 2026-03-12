#!/usr/bin/env python
"""
Test to reproduce the issue where migrations use the value of an enum object
instead of its name, causing problems with translated values.
"""

import enum
import sys
import os

# Add the testbed directory to the path
sys.path.insert(0, '/testbed')

# Setup minimal Django settings before importing Django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        USE_I18N=True,
        USE_L10N=True,
        USE_TZ=True,
    )

from django.db import models
from django.db.migrations.writer import MigrationWriter

def test_enum_serialization_uses_name():
    """
    Test that enum serialization uses the enum name instead of its value.
    This is critical when the enum value might change (e.g., through translation).
    """
    # Define an enum with string values
    class Status(enum.Enum):
        GOOD = 'Good'
        BAD = 'Bad'

        def __str__(self):
            return self.name

    # Create a field with the enum as default
    field = models.CharField(default=Status.GOOD, max_length=128)

    # Serialize the field
    serialized_string, imports = MigrationWriter.serialize(field)

    print("Serialized string:", serialized_string)
    print("Imports:", imports)

    # The issue: On the buggy version, it will serialize as:
    # models.CharField(default=test_reproduce.Status('Good'), max_length=128)
    # But if 'Good' is translated or changed, this will fail

    # The fix: It should serialize as:
    # models.CharField(default=Status['GOOD'], max_length=128)
    # This uses the enum name which is stable

    # Check if the serialization uses the enum name (correct behavior)
    # or the enum value (buggy behavior)
    if "Status['GOOD']" in serialized_string:
        print("[PASS] Serialization uses enum name (Status['GOOD'])")
        return True
    elif "Status(" in serialized_string and "'Good'" in serialized_string:
        print("[FAIL] Serialization uses enum value (Status('Good')) - this is the bug!")
        print("  If 'Good' is translated, this will fail with: ValueError: 'Good' is not a valid Status")
        return False
    else:
        print("[UNKNOWN] Unexpected serialization format")
        print("  Serialized string:", serialized_string)
        return False

def test_enum_direct_serialization():
    """
    Test that we can serialize an enum member directly.
    """
    class Status(enum.Enum):
        GOOD = 'Good'
        BAD = 'Bad'

    # Serialize the enum member directly
    serialized_string, imports = MigrationWriter.serialize(Status.GOOD)
    print("\nDirect enum serialization test:")
    print("Serialized string:", serialized_string)

    # Check the format
    if "Status['GOOD']" in serialized_string:
        print("[PASS] Uses enum name format")
        return True
    elif "Status(" in serialized_string:
        print("[FAIL] Uses enum value format (buggy)")
        return False
    else:
        print("[UNKNOWN] Unexpected format")
        return False

if __name__ == "__main__":
    print("Testing enum serialization issue...")
    print("=" * 70)

    # Test 1: Check serialization format
    test1_passed = test_enum_serialization_uses_name()

    # Test 2: Check direct enum serialization
    test2_passed = test_enum_direct_serialization()

    print("\n" + "=" * 70)
    print("Results:")
    print("  Test 1 (field serialization):", "PASS" if test1_passed else "FAIL")
    print("  Test 2 (direct enum serialization):", "PASS" if test2_passed else "FAIL")

    # On buggy version: both tests should fail
    # On fixed version: both tests should pass
    if test1_passed and test2_passed:
        print("\n[SUCCESS] ALL TESTS PASSED - Issue is fixed!")
        sys.exit(0)
    else:
        print("\n[FAILURE] TESTS SHOW BUG - Issue reproduced!")
        sys.exit(1)