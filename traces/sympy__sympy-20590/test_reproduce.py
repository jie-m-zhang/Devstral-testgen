"""
Test to reproduce the issue where Symbol instances have __dict__ attribute.

In version 1.6.2, Symbol instances should not have __dict__ because they use __slots__.
In version 1.7, Symbol instances incorrectly have __dict__ due to Printable class
not defining __slots__.

This test should FAIL on the buggy version (base commit) and PASS on the fixed version (head commit).
"""

import sys
import sympy

def test_symbol_no_dict():
    """
    Test that Symbol instances do not have __dict__ attribute.

    Symbol instances should use __slots__ for memory efficiency and should not
    have a __dict__ attribute.
    """
    # Create a Symbol instance
    s = sympy.Symbol('s')

    # Check that the symbol has __slots__ defined
    assert hasattr(type(s), '__slots__'), \
        f"Symbol class should have __slots__ defined, but it doesn't"

    # Check that the symbol instance does NOT have __dict__ attribute
    # This is the key assertion that will fail on buggy version
    try:
        # Try to access __dict__ - this should raise AttributeError
        _ = s.__dict__
        # If we get here, the bug is present
        assert False, \
            f"Symbol instance should not have __dict__ attribute, but it does: {s.__dict__}"
    except AttributeError:
        # This is the expected behavior - __dict__ should not exist
        pass

    print("Test passed - Symbol instances correctly do not have __dict__ attribute")

if __name__ == "__main__":
    test_symbol_no_dict()