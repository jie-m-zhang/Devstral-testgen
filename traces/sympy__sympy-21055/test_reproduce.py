#!/usr/bin/env python
"""
Test to reproduce the issue where refine() does not understand how to simplify complex arguments.

The issue is that refine(arg(a), Q.positive(a)) should return 0, but instead returns arg(a).
Similarly, refine(arg(a), Q.negative(a)) should return pi, but instead returns arg(a).
"""

from sympy import var, arg, Q, refine, S

def test_refine_arg_positive():
    """Test that refine(arg(a), Q.positive(a)) returns 0"""
    a = var('a')
    result = refine(arg(a), Q.positive(a))
    # On buggy version: result == arg(a)
    # On fixed version: result == 0
    assert result == S.Zero, f"Expected S.Zero (0), got {result}"

def test_refine_arg_negative():
    """Test that refine(arg(a), Q.negative(a)) returns pi"""
    a = var('a')
    result = refine(arg(a), Q.negative(a))
    # On buggy version: result == arg(a)
    # On fixed version: result == pi
    assert result == S.Pi, f"Expected S.Pi (pi), got {result}"

if __name__ == "__main__":
    print("Testing refine(arg(a), Q.positive(a))...")
    test_refine_arg_positive()
    print("✓ Test passed: refine(arg(a), Q.positive(a)) returns 0")

    print("\nTesting refine(arg(a), Q.negative(a))...")
    test_refine_arg_negative()
    print("✓ Test passed: refine(arg(a), Q.negative(a)) returns pi")

    print("\nAll tests passed!")