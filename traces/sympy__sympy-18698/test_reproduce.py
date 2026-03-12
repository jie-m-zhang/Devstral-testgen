#!/usr/bin/env python
"""
Test to reproduce the sqf_list issue.

The issue is that sqf_list should group factors with the same multiplicity together.
In the buggy version, factors with the same multiplicity are kept separate.
In the fixed version, they are multiplied together.
"""

from sympy import sqf_list, expand
from sympy.abc import x

def test_sqf_list_grouping():
    """Test that sqf_list groups factors with the same multiplicity."""

    # Test case from the issue
    expr = (x**2 + 1) * (x - 1)**2 * (x - 2)**3 * (x - 3)**3
    result = sqf_list(expr)

    print("Testing sqf_list on:", expr)
    print("Result:", result)

    coeff, factors = result

    # Count how many factors have multiplicity 3
    factors_with_mult_3 = [f for f, k in factors if k == 3]
    print(f"Number of factors with multiplicity 3: {len(factors_with_mult_3)}")

    # In the buggy version, there should be 2 factors with multiplicity 3
    # In the fixed version, there should be 1 factor with multiplicity 3
    # (which is the product of (x-2) and (x-3))

    if len(factors_with_mult_3) == 2:
        print("BUGGY VERSION: Factors with same multiplicity are NOT grouped")
        print("Factors with multiplicity 3:", factors_with_mult_3)

        # Check that these are indeed (x-2) and (x-3)
        if set(factors_with_mult_3) == {x - 2, x - 3}:
            print("Confirmed: The two factors are (x-2) and (x-3)")
            return False  # Bug is present
        else:
            print("Unexpected factors:", factors_with_mult_3)
            return False

    elif len(factors_with_mult_3) == 1:
        print("FIXED VERSION: Factors with same multiplicity ARE grouped")
        factor = factors_with_mult_3[0]
        print("Grouped factor with multiplicity 3:", factor)

        # Check that this is the product of (x-2) and (x-3)
        expected_product = expand((x - 2) * (x - 3))
        if factor == expected_product:
            print("Confirmed: The grouped factor is (x-2)*(x-3) =", expected_product)
            return True  # Bug is fixed
        else:
            print("Unexpected grouped factor:", factor)
            print("Expected:", expected_product)
            return False
    else:
        print(f"Unexpected number of factors with multiplicity 3: {len(factors_with_mult_3)}")
        return False

def test_sqf_list_no_grouping_needed():
    """Test that sqf_list works correctly when no grouping is needed."""

    # Test case from the issue where there's only one factor with multiplicity 2
    expr = x**5 - 2*x**4 - 2*x**3 + 4*x**2 + x - 2
    result = sqf_list(expr)

    print("\nTesting sqf_list on:", expr)
    print("Result:", result)

    expected_coeff = 1
    expected_factors = [(x - 2, 1), (x**2 - 1, 2)]

    if result[0] == expected_coeff and result[1] == expected_factors:
        print("✓ Test PASSED - No grouping needed, result is correct")
        return True
    else:
        print("✗ Test FAILED - Unexpected result")
        print("Expected:", (expected_coeff, expected_factors))
        print("Got:", result)
        return False

if __name__ == "__main__":
    success1 = test_sqf_list_grouping()
    success2 = test_sqf_list_no_grouping_needed()

    if success1 and success2:
        print("\n✓ All tests PASSED - Issue is fixed")
        exit(0)
    else:
        print("\n✗ Some tests FAILED - Issue is present")
        exit(1)