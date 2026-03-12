#!/usr/bin/env python
"""
Test to reproduce the issue with Python code printer not respecting tuple with one element.

The issue: lambdify([], tuple([1])) should generate code that returns (1,)
but in SymPy 1.10 it generates code that returns (1), which is just an integer.
"""

import inspect
from sympy import lambdify

def test_single_element_tuple():
    """Test that lambdify correctly generates code for single-element tuples."""
    # Get the generated source code for a single-element tuple
    source = inspect.getsource(lambdify([], tuple([1])))

    # The source should contain '(1,)' not '(1)'
    print("Generated source:")
    print(source)

    # Check that the source contains the correct tuple syntax
    assert '(1,)' in source, f"Expected '(1,)' in source, but got: {source}"

    # Also verify it doesn't contain the incorrect '(1)' without comma
    # (but only if it's not part of a larger expression)
    lines = source.split('\n')
    return_line = [line for line in lines if 'return' in line][0]
    print(f"Return line: {return_line}")

    # The return statement should have '(1,)' not '(1)'
    assert '(1,)' in return_line, f"Expected '(1,)' in return line, got: {return_line}"
    assert 'return (1)' not in return_line, f"Found incorrect 'return (1)' in: {return_line}"

    print("Test passed - single element tuple is correctly formatted!")

def test_multi_element_tuple():
    """Test that lambdify correctly generates code for multi-element tuples (should still work)."""
    # Get the generated source code for a multi-element tuple
    source = inspect.getsource(lambdify([], tuple([1, 2])))

    print("\nGenerated source for multi-element tuple:")
    print(source)

    # Check that the source contains valid tuple syntax
    # After the fix, tuples have trailing commas, so we accept both (1, 2) and (1, 2,)
    assert '(1, 2' in source, f"Expected '(1, 2' in source, but got: {source}"

    print("Test passed - multi-element tuple is correctly formatted!")

if __name__ == "__main__":
    print("Testing single-element tuple issue...")
    test_single_element_tuple()
    print("\nTesting multi-element tuple (should work)...")
    test_multi_element_tuple()
    print("\nAll tests passed!")