#!/usr/bin/env python
"""
Test to reproduce the issue with bell(n).limit(n, oo)

The issue states that bell(n).limit(n, oo) should return oo (infinity)
but currently returns bell(oo).
"""

from sympy import symbols, bell, oo, limit

def test_bell_limit_infinity():
    """Test that bell(n).limit(n, oo) returns oo instead of bell(oo)"""
    n = symbols('n')

    # This should return oo (infinity)
    result = limit(bell(n), n, oo)

    # The expected result is oo
    expected = oo

    # This assertion will fail on the buggy version (returns bell(oo))
    # and pass on the fixed version (returns oo)
    assert result == expected, f"Expected {expected}, got {result}"

    print("Test passed - bell(n).limit(n, oo) correctly returns oo")

if __name__ == "__main__":
    test_bell_limit_infinity()