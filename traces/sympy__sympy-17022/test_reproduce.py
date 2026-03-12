#!/usr/bin/env python
"""
Test to reproduce the issue with lambdify misinterpreting identity matrices.

The issue is that lambdify incorrectly interprets 'I' as the complex number 1j
instead of the identity matrix when working with matrix expressions.
"""

import numpy as np
from sympy import symbols, MatrixSymbol, Identity, lambdify

def test_identity_matrix_lambdify():
    """Test that lambdify correctly handles identity matrices."""
    # Create a matrix symbol with concrete size (2x2)
    A = MatrixSymbol("A", 2, 2)

    # Create a test numpy array
    a = np.array([[1, 2], [3, 4]])

    # Create a lambdified function that adds identity matrix to A
    f = lambdify(A, A + Identity(2))

    # Apply the function to the test array
    result = f(a)

    # Expected result: adding identity matrix to a
    # [[1, 2], [3, 4]] + [[1, 0], [0, 1]] = [[2, 2], [3, 5]]
    expected = np.array([[2, 2], [3, 5]])

    # Check if result is correct
    print(f"Result: {result}")
    print(f"Expected: {expected}")

    # The test should fail on buggy version (I interpreted as 1j)
    # and pass on fixed version (I interpreted as identity matrix)
    assert np.allclose(result, expected), \
        f"Expected {expected}, but got {result}. Identity matrix was not correctly interpreted."

    print("Test passed - identity matrix correctly interpreted")

if __name__ == "__main__":
    test_identity_matrix_lambdify()