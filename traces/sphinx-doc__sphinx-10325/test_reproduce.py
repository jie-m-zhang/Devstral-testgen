#!/usr/bin/env python3
"""
Test to reproduce the issue with inherited-members not supporting multiple classes.

The issue is that :inherited-members: option should accept a list of classes
to ignore, but currently only accepts a single class name.
"""

import sys

# Add the testbed to the path
sys.path.insert(0, '/testbed')

from sphinx.ext.autodoc import inherited_members_option

def test_inherited_members_option():
    """Test the inherited_members_option function directly."""

    print("Testing inherited_members_option function...")

    # Test 1: None should return 'object' in buggy version, set() in fixed version
    result_none = inherited_members_option(None)
    print(f"inherited_members_option(None) = {result_none!r}")
    print(f"  Type: {type(result_none)}")

    # Test 2: True should return 'object' in buggy version, {'object'} in fixed version
    result_true = inherited_members_option(True)
    print(f"inherited_members_option(True) = {result_true!r}")
    print(f"  Type: {type(result_true)}")

    # Test 3: Single class name
    result_single = inherited_members_option('Base1')
    print(f"inherited_members_option('Base1') = {result_single!r}")
    print(f"  Type: {type(result_single)}")

    # Test 4: Multiple class names (comma-separated) - this is the key test
    result_multiple = inherited_members_option('Base1,Base2')
    print(f"inherited_members_option('Base1,Base2') = {result_multiple!r}")
    print(f"  Type: {type(result_multiple)}")

    # Test 5: Multiple class names with spaces
    result_multiple_spaces = inherited_members_option('Base1, Base2, Base3')
    print(f"inherited_members_option('Base1, Base2, Base3') = {result_multiple_spaces!r}")
    print(f"  Type: {type(result_multiple_spaces)}")

    print("\n" + "="*70)

    # The key assertion: in the fixed version, multiple classes should be split into a set
    if isinstance(result_multiple, str):
        print("FAIL: inherited_members_option returns a string for multiple classes")
        print("This is the bug - it should return a set")
        print(f"  Expected: set (e.g., {{'Base1', 'Base2'}})")
        print(f"  Got: {result_multiple!r}")
        return False
    elif isinstance(result_multiple, set):
        if result_multiple == {'Base1', 'Base2'}:
            print("PASS: inherited_members_option correctly splits multiple classes into a set")
            return True
        else:
            print(f"FAIL: inherited_members_option returned wrong set: {result_multiple!r}")
            print(f"  Expected: {{'Base1', 'Base2'}}")
            return False
    else:
        print(f"FAIL: inherited_members_option returned unexpected type: {type(result_multiple)}")
        return False

if __name__ == "__main__":
    try:
        success = test_inherited_members_option()
        if success:
            print("\n✓ Test passed - issue is fixed")
            sys.exit(0)
        else:
            print("\n✗ Test failed - issue reproduced")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)