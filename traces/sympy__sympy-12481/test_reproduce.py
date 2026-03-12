#!/usr/bin/env python
"""
Test to reproduce the issue with non-disjoint cycles in Permutation constructor.

The issue states that calling Permutation([[0,1],[0,1]]) raises a ValueError
instead of constructing the identity permutation. When cycles are non-disjoint,
they should be applied in left-to-right order and the resulting permutation
should be returned.
"""

from sympy.combinatorics.permutations import Permutation

def test_non_disjoint_cycles():
    """
    Test that non-disjoint cycles are applied in left-to-right order.

    The permutation [[0,1],[0,1]] should be equivalent to applying
    cycle (0,1) twice, which results in the identity permutation.
    """
    # This should not raise ValueError but should create the identity permutation
    try:
        p = Permutation([[0, 1], [0, 1]])
        print(f"Permutation created successfully: {p}")
        print(f"Array form: {p.array_form}")
        print(f"Is identity: {p.is_Identity}")

        # The result should be the identity permutation of size 2
        expected_array = [0, 1]
        assert p.array_form == expected_array, f"Expected {expected_array}, got {p.array_form}"
        assert p.is_Identity, "Expected identity permutation"

        print("Test passed - non-disjoint cycles handled correctly")
        return True
    except ValueError as e:
        print(f"ValueError raised: {e}")
        print("Test failed - non-disjoint cycles should be allowed")
        return False

if __name__ == "__main__":
    success = test_non_disjoint_cycles()
    exit(0 if success else 1)