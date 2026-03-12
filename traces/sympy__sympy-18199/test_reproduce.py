#!/usr/bin/env python3
"""
Test to reproduce the issue where nthroot_mod function misses one root of x = 0 mod p
when a % p == 0.

The issue states that when in the equation x**n = a mod p, when a % p == 0,
then x = 0 mod p is also a root of this equation. But the buggy version of
nthroot_mod does not check for this condition.

Example from the issue: nthroot_mod(17*17, 5, 17) has a root 0 mod 17.
"""

from sympy.ntheory.residue_ntheory import nthroot_mod

def test_nthroot_mod_zero_root():
    """
    Test that nthroot_mod returns 0 as a root when a % p == 0.

    This test should FAIL on the buggy version (base commit) and PASS on the
    fixed version (head commit).
    """
    # Test case from the issue: nthroot_mod(17*17, 5, 17)
    # 17*17 = 289, 289 mod 17 = 0, so 0 should be a root
    a = 17 * 17
    n = 5
    p = 17
    result = nthroot_mod(a, n, p, all_roots=True)
    print(f"nthroot_mod({a}, {n}, {p}, all_roots=True) = {result}")

    # Verify that 0 is in the result
    assert result is not None, "nthroot_mod should return a list of roots, not None"
    assert 0 in result, f"0 should be in the roots, but got {result}"

    # Verify that 0 is indeed a root: 0^n mod p should equal a mod p
    assert pow(0, n, p) == a % p, "0 should satisfy the equation x^n = a mod p"

    print("Test passed!")

def test_nthroot_mod_zero_root_simple():
    """
    Test a simpler case where a = 0.
    """
    a = 0
    n = 5
    p = 17
    result = nthroot_mod(a, n, p, all_roots=True)
    print(f"nthroot_mod({a}, {n}, {p}, all_roots=True) = {result}")

    assert result is not None, "nthroot_mod should return a list of roots, not None"
    assert 0 in result, f"0 should be in the roots, but got {result}"

    print("Test passed!")

def test_nthroot_mod_zero_root_with_p_minus_1_divisible_by_n():
    """
    Test the case where a = 0 and (p-1) % n == 0.
    This is the case that fails in the buggy version because it tries to compute
    a discrete log that doesn't exist.
    """
    # Test case from the patch: nthroot_mod(0, 12, 37, True) should return [0]
    # (p-1) = 36, 36 % 12 = 0, so it will try to use _nthroot_mod1
    a = 0
    n = 12
    p = 37
    try:
        result = nthroot_mod(a, n, p, all_roots=True)
        print(f"nthroot_mod({a}, {n}, {p}, all_roots=True) = {result}")

        # Verify that 0 is in the result
        assert result is not None, "nthroot_mod should return a list of roots, not None"
        assert 0 in result, f"0 should be in the roots, but got {result}"

        print("Test passed!")
    except ValueError as e:
        print(f"FAILED with ValueError: {e}")
        print("This is expected on the buggy version because it tries to compute")
        print("a discrete log that doesn't exist when a=0 and (p-1) % n == 0")
        raise

def test_nthroot_mod_zero_root_composite():
    """
    Test with composite modulus.
    """
    # Test case: nthroot_mod(0, 7, 100) should return [0, 10, 20, ..., 90]
    a = 0
    n = 7
    p = 100
    try:
        result = nthroot_mod(a, n, p, all_roots=True)
        print(f"nthroot_mod({a}, {n}, {p}, all_roots=True) = {result}")

        assert result is not None, "nthroot_mod should return a list of roots, not None"
        assert 0 in result, f"0 should be in the roots, but got {result}"
        # All roots should be multiples of 10 (since 100 = 2^2 * 5^2)
        for root in result:
            assert root % 10 == 0, f"All roots should be multiples of 10, but got {root}"

        print("Test passed!")
    except NotImplementedError as e:
        print(f"FAILED with NotImplementedError: {e}")
        print("This is expected on the buggy version because composite p is not supported")
        raise

if __name__ == "__main__":
    print("Testing nthroot_mod with a % p == 0...")
    print()

    print("Test 1: Original issue example")
    try:
        test_nthroot_mod_zero_root()
    except AssertionError as e:
        print(f"FAILED: {e}")
        exit(1)
    print()

    print("Test 2: Simple case with a = 0")
    try:
        test_nthroot_mod_zero_root_simple()
    except AssertionError as e:
        print(f"FAILED: {e}")
        exit(1)
    print()

    print("Test 3: Case where (p-1) % n == 0 (this should fail on buggy version)")
    try:
        test_nthroot_mod_zero_root_with_p_minus_1_divisible_by_n()
    except (AssertionError, ValueError) as e:
        print(f"FAILED: {e}")
        exit(1)
    print()

    print("Test 4: Composite modulus (this should fail on buggy version)")
    try:
        test_nthroot_mod_zero_root_composite()
    except (AssertionError, NotImplementedError) as e:
        print(f"FAILED: {e}")
        exit(1)
    print()

    print("All tests passed!")