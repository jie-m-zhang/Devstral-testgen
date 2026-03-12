#!/usr/bin/env python
"""
Test to reproduce the issue where (-x/4 - S(1)/12)**x - 1
simplifies to an inequivalent expression.

The issue is that simplify() produces an expression that evaluates
to a different numerical value than the original expression.
"""

from sympy import *

def test_issue_reproduction():
    x = Symbol('x')
    e = (-x/4 - S(1)/12)**x - 1

    # Simplify the expression
    f = simplify(e)

    # Substitute x with S(9)/5 as in the issue
    a = S(9)/5
    e_subs = e.subs(x, a)
    f_subs = f.subs(x, a)

    # Get numerical values
    e_val = N(e_subs)
    f_val = N(f_subs)

    print(f"Original expression value: {e_val}")
    print(f"Simplified expression value: {f_val}")

    # The values should be equal (or very close)
    # On the buggy version, they will be different
    # On the fixed version, they should be the same
    assert abs(e_val - f_val) < 1e-10, f"Values differ: {e_val} vs {f_val}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()