#!/usr/bin/env python
"""
Test to reproduce the issue where @ (matmul) should fail if one argument is not a matrix.

The issue states that currently @ just copies __mul__ behavior, but it should only work
for actual matrix multiplication (like NumPy does).
"""

from sympy import Matrix

def test_matmul_with_scalar_should_fail():
    """
    Test that matrix multiplication with a scalar should fail.

    According to the issue, 2@B should raise an error (like NumPy does),
    but currently it works like 2*B (element-wise multiplication).
    """
    # Create a test matrix
    B = Matrix([[2, 3], [1, 2]])

    # This should work - matrix @ matrix
    A = Matrix([[1, 2], [3, 4]])
    result_matrix_matmul = A @ B
    print("Matrix @ Matrix works:", result_matrix_matmul)

    # This should work - matrix * scalar (element-wise multiplication)
    result_matrix_mul = 2 * B
    print("Scalar * Matrix works:", result_matrix_mul)

    # This is the issue: scalar @ matrix should FAIL but currently works
    try:
        result_scalar_matmul = 2 @ B
        print("Scalar @ Matrix result:", result_scalar_matmul)
        # If we get here, the bug is present (scalar @ matrix works when it shouldn't)
        print("ERROR: scalar @ matrix should have failed but didn't!")
        print("This demonstrates the bug - @ should only work for matrix multiplication")
        return False
    except (TypeError, ValueError) as e:
        print(f"Scalar @ Matrix correctly failed with: {e}")
        print("This is the expected behavior - @ should only work for matrix multiplication")
        return True

if __name__ == "__main__":
    success = test_matmul_with_scalar_should_fail()
    if not success:
        print("\nTest FAILED - bug is present (scalar @ matrix works when it shouldn't)")
        exit(1)
    else:
        print("\nTest PASSED - bug is fixed (scalar @ matrix correctly fails)")
        exit(0)