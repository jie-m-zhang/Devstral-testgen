#!/usr/bin/env python
"""
Test to reproduce the issue with decompose() function returning arbitrary order.

The issue is that decompose() with separate=True returns list(poly_dict.values()),
which has arbitrary ordering. This causes test failures.

The fix changes it to return a set instead, which has no ordering issues.
"""

from sympy.abc import x, y
from sympy.integrals.intpoly import decompose

def test_decompose_returns_set():
    """Test that decompose() with separate=True returns a set.

    On the buggy version (base commit), this will fail because it returns a list.
    On the fixed version (head commit), this will pass because it returns a set.
    """
    # Test expression from the docstring
    expr = x**2 + x*y + x + y + x**3*y**2 + y**5

    # Get the result with separate=True
    result = decompose(expr, separate=True)

    print(f"Type of result: {type(result)}")
    print(f"Result: {result}")

    # The fix changes the return type from list to set
    # This assertion will fail on buggy version (returns list)
    # This assertion will pass on fixed version (returns set)
    assert isinstance(result, set), f"Expected set, got {type(result)}"

    # Also check that it contains the expected elements
    expected_monomials = {x, y, x**2, y**5, x*y, x**3*y**2}
    assert result == expected_monomials, f"Expected {expected_monomials}, got {result}"

    print("Test passed!")

if __name__ == "__main__":
    test_decompose_returns_set()