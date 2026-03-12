#!/usr/bin/env python
"""
Test to reproduce the issue with itermonomials returning incorrect monomials
when using min_degrees argument.

The bug: itermonomials uses max(powers.values()) instead of sum(powers.values())
to check against min_degree, causing it to only return monomials where at least
one variable has degree >= min_degree, rather than monomials where the total
degree is >= min_degree.
"""

import sympy as sp
from sympy.polys.orderings import monomial_key

def test_itermonomials_min_degrees():
    """Test that itermonomials returns all monomials with total degree >= min_degree."""
    # Create three symbolic variables
    x1, x2, x3 = sp.symbols('x1, x2, x3')
    states = [x1, x2, x3]
    max_degrees = 3
    min_degrees = 3

    # Generate monomials
    monomials = sorted(sp.itermonomials(states, max_degrees, min_degrees=min_degrees),
                       key=monomial_key('grlex', states))

    print("Generated monomials:")
    for m in monomials:
        print(f"  {m}")

    # For 3 variables with total degree 3, we should have 10 monomials:
    # x1**3, x1**2*x2, x1**2*x3, x1*x2**2, x1*x2*x3,
    # x1*x3**2, x2**3, x2**2*x3, x2*x3**2, x3**3
    expected_monomials = [
        x1**3,
        x1**2*x2,
        x1**2*x3,
        x1*x2**2,
        x1*x2*x3,
        x1*x3**2,
        x2**3,
        x2**2*x3,
        x2*x3**2,
        x3**3
    ]

    print(f"\nNumber of monomials generated: {len(monomials)}")
    print(f"Number of monomials expected: {len(expected_monomials)}")

    # Check that we have the correct number of monomials
    assert len(monomials) == len(expected_monomials), \
        f"Expected {len(expected_monomials)} monomials, got {len(monomials)}"

    # Check that all expected monomials are present
    for expected in expected_monomials:
        assert expected in monomials, \
            f"Expected monomial {expected} not found in generated monomials"

    print("\nTest passed - all expected monomials are present!")

def test_itermonomials_min_degrees_range():
    """Test that itermonomials works correctly with min_degree < max_degree."""
    # Create three symbolic variables
    x1, x2, x3 = sp.symbols('x1, x2, x3')
    states = [x1, x2, x3]
    max_degrees = 4
    min_degrees = 3

    # Generate monomials
    monomials = sorted(sp.itermonomials(states, max_degrees, min_degrees=min_degrees),
                       key=monomial_key('grlex', states))

    print("\nGenerated monomials (degree 3 and 4):")
    for m in monomials:
        print(f"  {m}")

    # For 3 variables with total degree 3, we should have 10 monomials
    # For 3 variables with total degree 4, we should have 15 monomials
    # Total: 25 monomials
    expected_count = 25

    print(f"\nNumber of monomials generated: {len(monomials)}")
    print(f"Number of monomials expected: {expected_count}")

    # Check that we have the correct number of monomials
    assert len(monomials) == expected_count, \
        f"Expected {expected_count} monomials, got {len(monomials)}"

    # Check that we have monomials of degree 3
    degree_3_monomials = [m for m in monomials if sp.total_degree(m) == 3]
    assert len(degree_3_monomials) == 10, \
        f"Expected 10 monomials of degree 3, got {len(degree_3_monomials)}"

    # Check that we have monomials of degree 4
    degree_4_monomials = [m for m in monomials if sp.total_degree(m) == 4]
    assert len(degree_4_monomials) == 15, \
        f"Expected 15 monomials of degree 4, got {len(degree_4_monomials)}"

    print("\nTest passed - correct number of monomials for each degree!")

if __name__ == "__main__":
    print("Testing itermonomials with min_degrees argument...")
    print("=" * 60)

    try:
        test_itermonomials_min_degrees()
        print("\n" + "=" * 60)
        test_itermonomials_min_degrees_range()
        print("\n" + "=" * 60)
        print("\nAll tests passed!")
    except AssertionError as e:
        print(f"\nTest failed with assertion error: {e}")
        exit(1)
    except Exception as e:
        print(f"\nTest failed with unexpected error: {e}")
        exit(1)