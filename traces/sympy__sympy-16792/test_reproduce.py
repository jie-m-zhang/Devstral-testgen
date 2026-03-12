#!/usr/bin/env python
"""
Test to reproduce the issue where autowrap with cython backend fails when array
arguments do not appear in the wrapped expression.
"""

from sympy.utilities.autowrap import autowrap
from sympy import MatrixSymbol
import numpy as np

def test_autowrap_unused_array_arg():
    """
    Test that autowrap works correctly when array arguments don't appear in the expression.

    This should return 1.0 but on the buggy version fails with:
    TypeError: only size-1 arrays can be converted to Python scalars

    The issue is that the C function is generated with incorrect signature:
    - Buggy: double autofunc(double x)
    - Fixed: double autofunc(double *x)
    """
    x = MatrixSymbol('x', 2, 1)
    expr = 1.0
    f = autowrap(expr, args=(x,), backend='cython')

    # Call the function with a numpy array
    result = f(np.array([[1.0, 2.0]]))

    # Should return 1.0
    assert result == 1.0, f"Expected 1.0, got {result}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_autowrap_unused_array_arg()