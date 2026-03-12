#!/usr/bin/env python
"""
Test to reproduce the issue with sign().rewrite(Abs)

The issue is that sign(x).rewrite(Abs) should return x/Abs(x)
but this functionality is missing in the base commit.
"""

from sympy import sign, Abs, Symbol, Piecewise, Eq

def test_sign_rewrite_abs():
    """Test that sign(x).rewrite(Abs) returns x/Abs(x) with proper handling of zero"""
    x = Symbol('x')

    # This should rewrite sign(x) as x/Abs(x)
    result = sign(x).rewrite(Abs)

    # Expected result is Piecewise((0, Eq(x, 0)), (x/Abs(x), True))
    # This handles the case when x=0 separately to avoid division by zero
    expected = Piecewise((0, Eq(x, 0)), (x / Abs(x), True))

    # On the base commit, this will fail because rewrite(Abs) is not implemented
    # On the head commit, this will pass because the rewrite method is added
    assert result == expected, f"Expected {expected}, got {result}"

    print("Test passed - sign(x).rewrite(Abs) works correctly")

if __name__ == "__main__":
    test_sign_rewrite_abs()