#!/usr/bin/env python
"""
Test to reproduce the issue with Intersection not removing duplicates.

The issue is that Intersection({1},{1},{x}) incorrectly returns EmptySet()
instead of Piecewise(({1}, Eq(x, 1)), (S.EmptySet, True)) or remaining unevaluated.
"""

from sympy import Intersection, FiniteSet, Symbol, Piecewise, Eq, S

def test_intersection_duplicates():
    """Test that Intersection properly handles duplicate sets."""
    x = Symbol('x')

    # Test case 1: Intersection with duplicates {1}, {1}, {x}
    # This should return Piecewise(({1}, Eq(x, 1)), (S.EmptySet, True))
    # or remain unevaluated, NOT EmptySet()
    result1 = Intersection(FiniteSet(1), FiniteSet(1), FiniteSet(x))
    print(f"Intersection({{1}}, {{1}}, {{x}}) = {result1}")

    # The result should NOT be EmptySet() - that's the bug
    # It should either be a Piecewise expression or an unevaluated Intersection
    is_empty = result1 == S.EmptySet
    print(f"Result is EmptySet: {is_empty}")

    # Test case 2: Intersection without duplicates {1}, {x}
    # This should work correctly and return {1} when x=1
    result2 = Intersection(FiniteSet(1), FiniteSet(x))
    print(f"Intersection({{1}}, {{x}}) = {result2}")

    # For the bug: when there are duplicates, the result should not be EmptySet
    # The fix removes duplicates at the outset, so both cases should behave similarly
    assert not (result1 == S.EmptySet), \
        f"FAIL: Intersection({{1}}, {{1}}, {{x}}) should not be EmptySet(), got {result1}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_intersection_duplicates()