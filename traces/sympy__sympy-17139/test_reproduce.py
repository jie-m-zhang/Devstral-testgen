#!/usr/bin/env python
"""
Test to reproduce the issue with simplify(cos(x)**I) raising TypeError.

The issue is that simplify(cos(x)**I) raises:
TypeError: Invalid comparison of complex I

This happens because in fu.py, the code tries to compare rv.exp < 0
when rv.exp is the imaginary unit I, which is complex and cannot be
compared with real numbers.

The fix adds a check for rv.exp.is_real before doing the comparison.
"""

from sympy import Symbol, cos, I, simplify

def test_issue_reproduction():
    """Test that simplify(cos(x)**I) works without raising TypeError."""
    x = Symbol('x')
    
    # This should not raise TypeError
    try:
        result = simplify(cos(x)**I)
        # If we get here, the issue is fixed
        print(f"Test passed - simplify(cos(x)**I) returned: {result}")
        return True
    except TypeError as e:
        # This is the bug - should not happen in fixed version
        print(f"Test failed - TypeError raised: {e}")
        return False

if __name__ == "__main__":
    success = test_issue_reproduction()
    if not success:
        exit(1)
    else:
        exit(0)