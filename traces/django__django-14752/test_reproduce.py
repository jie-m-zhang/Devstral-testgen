#!/usr/bin/env python
"""
Test to reproduce the issue with AutocompleteJsonView not supporting extra fields.

The issue is that to add custom fields to autocomplete results, you need to
override the entire get() method. The fix is to extract result serialization
into a separate serialize_result() method that can be easily overridden.
"""

import sys
import os

# Add testbed to path
sys.path.insert(0, '/testbed')

def test_serialize_result_exists():
    """
    Test that serialize_result() method exists in AutocompleteJsonView.

    This test should:
    - FAIL on base commit (serialize_result doesn't exist)
    - PASS on head commit (serialize_result exists)
    """
    from django.contrib.admin.views.autocomplete import AutocompleteJsonView

    # Check if serialize_result method exists
    if not hasattr(AutocompleteJsonView, 'serialize_result'):
        print("✗ FAILED: serialize_result() method does not exist in AutocompleteJsonView")
        print("   This is expected on the base commit (before the fix)")
        return False

    # Check if it's callable
    if not callable(getattr(AutocompleteJsonView, 'serialize_result')):
        print("✗ FAILED: serialize_result exists but is not callable")
        return False

    print("✓ PASSED: serialize_result() method exists in AutocompleteJsonView")
    return True

def test_serialize_result_override():
    """
    Test that serialize_result() can be overridden to add extra fields.

    This test should:
    - FAIL on base commit (serialize_result doesn't exist to override)
    - PASS on head commit (serialize_result can be overridden)
    """
    from django.contrib.admin.views.autocomplete import AutocompleteJsonView

    # Try to create a custom view that overrides serialize_result
    class CustomAutocompleteJsonView(AutocompleteJsonView):
        def serialize_result(self, obj, to_field_name):
            result = super().serialize_result(obj, to_field_name)
            result['custom_field'] = 'custom_value'
            return result

    # Check if the override works
    custom_view = CustomAutocompleteJsonView()

    # Check if the method exists on the custom view
    if not hasattr(custom_view, 'serialize_result'):
        print("✗ FAILED: serialize_result() method does not exist on custom view")
        return False

    # Try to call the method (this will fail on base commit because super() won't find it)
    try:
        # Create a mock object
        class MockObject:
            def __init__(self, pk):
                self.pk = pk
            def __str__(self):
                return f"Object {self.pk}"

        mock_obj = MockObject(1)
        result = custom_view.serialize_result(mock_obj, 'pk')

        # Check if custom field is present
        if 'custom_field' not in result:
            print("✗ FAILED: Custom field not present in result")
            print(f"   Result: {result}")
            return False

        if result['custom_field'] != 'custom_value':
            print(f"✗ FAILED: Expected custom_field='custom_value', got '{result['custom_field']}'")
            return False

        print("✓ PASSED: serialize_result() can be overridden to add extra fields")
        return True

    except AttributeError as e:
        if "serialize_result" in str(e) or "has no attribute" in str(e):
            print("✗ FAILED: Cannot override serialize_result() - parent method doesn't exist")
            print(f"   Error: {e}")
            return False
        raise

if __name__ == '__main__':
    print("Testing AutocompleteJsonView.serialize_result()...")
    print()

    # Test 1: Check if method exists
    print("Test 1: Check if serialize_result() method exists")
    test1_passed = test_serialize_result_exists()
    print()

    # Test 2: Check if method can be overridden
    print("Test 2: Check if serialize_result() can be overridden")
    test2_passed = test_serialize_result_override()
    print()

    # Summary
    if test1_passed and test2_passed:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)