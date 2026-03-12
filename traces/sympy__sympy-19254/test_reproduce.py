#!/usr/bin/env python
"""
Test to reproduce the issue with dup_zz_mignotte_bound.

The issue is that the old Mignotte bound implementation returns
significantly larger bounds than necessary. The new Knuth-Cohen bound
implementation should return much smaller (tighter) bounds.

This test verifies that the bound is improved for specific polynomials
mentioned in the issue.
"""

from sympy.polys.factortools import dup_zz_mignotte_bound
from sympy.polys.domains import ZZ

def test_mignotte_bound_improvement():
    """Test that the Mignotte bound is improved with Knuth-Cohen bound."""

    # Test case 1: Polynomial from the issue description
    # f = 87*x**7 + 4*x**6 + 80*x**5 + 17*x**4 + 9*x**3 + 12*x**2 + 49*x + 26
    # Old bound: 1937664
    # New bound: 744
    f1 = [87, 4, 80, 17, 9, 12, 49, 26]  # coefficients from highest to lowest degree
    bound1 = dup_zz_mignotte_bound(f1, ZZ)

    print(f"Test 1 - Polynomial: 87*x**7 + 4*x**6 + 80*x**5 + 17*x**4 + 9*x**3 + 12*x**2 + 49*x + 26")
    print(f"  Computed bound: {bound1}")

    # The new implementation should return 744, which is much smaller than the old 1937664
    # On the base commit (old implementation), this will be 1937664
    # On the head commit (new implementation), this should be 744
    assert bound1 == 744, f"Expected bound to be 744 (Knuth-Cohen), got {bound1}"

    # Test case 2: Another polynomial from the examples
    # f = x**3 + 14*x**2 + 56*x + 64
    # Expected bound: 152
    f2 = [1, 14, 56, 64]  # coefficients from highest to lowest degree
    bound2 = dup_zz_mignotte_bound(f2, ZZ)

    print(f"\nTest 2 - Polynomial: x**3 + 14*x**2 + 56*x + 64")
    print(f"  Computed bound: {bound2}")

    assert bound2 == 152, f"Expected bound to be 152, got {bound2}"

    # Test case 3: Irreducible polynomial
    # f = 2*x**2 + 3*x + 4
    # Expected bound: 6
    f3 = [2, 3, 4]  # coefficients from highest to lowest degree
    bound3 = dup_zz_mignotte_bound(f3, ZZ)

    print(f"\nTest 3 - Polynomial: 2*x**2 + 3*x + 4")
    print(f"  Computed bound: {bound3}")

    assert bound3 == 6, f"Expected bound to be 6, got {bound3}"

    print("\nAll tests passed - Knuth-Cohen bound is working correctly!")

if __name__ == "__main__":
    test_mignotte_bound_improvement()