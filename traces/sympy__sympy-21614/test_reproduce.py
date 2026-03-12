#!/usr/bin/env python
"""
Test to reproduce the issue with Derivative.kind attribute.

The issue is that Derivative(A, x).kind returns UndefinedKind
when A is a MatrixSymbol, but it should return MatrixKind(NumberKind)
similar to how Integral(A, x).kind works.
"""

from sympy import Integral, Derivative
from sympy import MatrixSymbol
from sympy.abc import x

def test_derivative_kind():
    """Test that Derivative.kind returns the correct kind for MatrixSymbol."""
    A = MatrixSymbol('A', 2, 2)

    # Test Integral - this should work correctly
    i = Integral(A, x)
    print(f"Integral.kind: {i.kind}")
    assert str(i.kind) == "MatrixKind(NumberKind)", f"Expected 'MatrixKind(NumberKind)', got '{i.kind}'"

    # Test Derivative - this is the bug
    d = Derivative(A, x)
    print(f"Derivative.kind: {d.kind}")
    # The kind should be the same as the argument's kind
    # For MatrixSymbol, it should be MatrixKind(NumberKind)
    assert str(d.kind) != "UndefinedKind", f"Derivative.kind should not be UndefinedKind, got '{d.kind}'"
    assert str(d.kind) == "MatrixKind(NumberKind)", f"Expected 'MatrixKind(NumberKind)', got '{d.kind}'"

    print("Test passed - Derivative.kind works correctly!")

if __name__ == "__main__":
    test_derivative_kind()