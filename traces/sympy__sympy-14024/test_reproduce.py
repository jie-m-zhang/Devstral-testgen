#!/usr/bin/env python
"""
Test to reproduce the inconsistency when simplifying (-a)**x * a**(-x)
where a is a positive integer.

The issue shows that:
- When a is a symbol with integer=True, positive=True: simplification works correctly
- When a is a concrete positive integer (like S(2)): simplification gives wrong results
"""

from sympy import Symbol, S, simplify, N

def test_issue_reproduction():
    x = Symbol('x')

    # Case 1: a is a symbol with integer=True, positive=True
    a = Symbol('a', integer=True, positive=True)
    e1 = (-a)**x * a**(-x)
    f1 = simplify(e1)

    # Case 2: a is a concrete positive integer (S(2))
    a_val = S(2)
    e2 = (-a_val)**x * a_val**(-x)
    f2 = simplify(e2)

    # Test with specific exponent value
    t = -S(10)/3

    # Substitute and compute numerical values
    n1_sym = e1.subs(x, t)
    n2_sym = f1.subs(x, t)
    n1_concrete = e2.subs(x, t)
    n2_concrete = f2.subs(x, t)

    # Numerical evaluation
    n1_sym_val = N(n1_sym)
    n2_sym_val = N(n2_sym)
    n1_concrete_val = N(n1_concrete)
    n2_concrete_val = N(n2_concrete)

    print("Symbolic a case:")
    print(f"  Original expression: {n1_sym_val}")
    print(f"  Simplified expression: {n2_sym_val}")
    print(f"  Match: {n1_sym_val == n2_sym_val}")

    print("\nConcrete a=2 case:")
    print(f"  Original expression: {n1_concrete_val}")
    print(f"  Simplified expression: {n2_concrete_val}")
    print(f"  Match: {n1_concrete_val == n2_concrete_val}")

    # The issue: for concrete a=2, the simplified version gives wrong result
    # n1_concrete_val should equal n2_concrete_val, but they don't
    # Also, n1_concrete_val should equal n1_sym_val (same mathematical expression)

    # Assert that the original and simplified should give same results
    # For symbolic case (this should pass)
    assert n1_sym_val == n2_sym_val, \
        f"Symbolic case failed: {n1_sym_val} != {n2_sym_val}"

    # For concrete case (this will fail on buggy version)
    assert n1_concrete_val == n2_concrete_val, \
        f"Concrete case failed: {n1_concrete_val} != {n2_concrete_val}"

    # Also verify that both original expressions give same result
    # (they represent the same mathematical expression)
    assert n1_sym_val == n1_concrete_val, \
        f"Original expressions differ: {n1_sym_val} != {n1_concrete_val}"

    print("\nTest passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()