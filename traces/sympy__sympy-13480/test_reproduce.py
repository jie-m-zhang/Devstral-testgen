#!/usr/bin/env python
"""
Test to reproduce the issue with coth(log(tan(x))).subs(x, 2)
The issue is a NameError: name 'cotm' is not defined in hyperbolic.py
"""

from sympy import Symbol, coth, log, tan

def test_coth_log_tan_subs():
    """Test that coth(log(tan(x))).subs(x, 2) works without NameError"""
    x = Symbol('x')
    e = coth(log(tan(x)))

    # This should not raise a NameError
    # On the buggy version, this will fail with:
    # NameError: name 'cotm' is not defined
    try:
        result = e.subs(x, 2)
        print(f"Test passed - result: {result}")
        return True
    except NameError as e:
        print(f"Test failed with NameError: {e}")
        return False

if __name__ == "__main__":
    success = test_coth_log_tan_subs()
    if not success:
        exit(1)
    exit(0)