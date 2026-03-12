#!/usr/bin/env python
"""
Test to reproduce the IndexError in numberformat.py when number is None or empty string.

The issue occurs when str_number[0] == "-" tries to access index 0 of an empty string,
which happens when number is an empty string or None.
"""

import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, '/testbed')

# Create minimal Django settings
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        USE_L10N=True,
        USE_THOUSAND_SEPARATOR=True,
    )

django.setup()

from django.utils.numberformat import format

def test_empty_string():
    """Test that empty string causes IndexError in buggy version"""
    try:
        # This should cause IndexError: string index out of range on buggy version
        result = format("", decimal_sep='.', decimal_pos=2)
        # If we get here on the fixed version, result should be empty string
        assert result == "", f"Expected empty string, got {result!r}"
        print("Test passed - empty string handled correctly")
        return True
    except IndexError as e:
        print(f"Test failed with IndexError (expected on buggy version): {e}")
        return False

def test_none_value():
    """Test that None value is handled correctly"""
    try:
        # This should return the string 'None' on the fixed version (mark_safe(None) returns 'None')
        result = format(None, decimal_sep='.', decimal_pos=2)
        # If we get here on the fixed version, result should be the string 'None'
        assert result == "None", f"Expected 'None', got {result!r}"
        print("Test passed - None value handled correctly")
        return True
    except Exception as e:
        print(f"Test failed with exception: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("Testing numberformat.py with empty string...")
    test1_passed = test_empty_string()

    print("\nTesting numberformat.py with None value...")
    test2_passed = test_none_value()

    if test1_passed and test2_passed:
        print("\nAll tests passed - issue is fixed")
        sys.exit(0)
    else:
        print("\nTests failed - issue reproduced")
        sys.exit(1)