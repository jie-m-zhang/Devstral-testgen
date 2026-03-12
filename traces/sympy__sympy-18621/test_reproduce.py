#!/usr/bin/env python
"""
Test to reproduce the issue where BlockDiagMatrix with one element
cannot be converted to regular Matrix.

This test should:
- FAIL on base commit (b17ef6effe278d5b861d65896cc53442a6370d8f)
- PASS on head commit (28b41c73c12b70d6ad9f6e45109a80649c4456da)
"""

import sympy

def test_blockdiag_single_matrix_conversion():
    """
    Test that a BlockDiagMatrix with one element can be converted to a regular Matrix.

    This reproduces the issue where:
    M = sympy.Matrix([[1, 2], [3, 4]])
    D = sympy.BlockDiagMatrix(M)
    B = sympy.Matrix(D)  # This should fail on base commit
    """
    # Create a regular Matrix
    M = sympy.Matrix([[1, 2], [3, 4]])

    # Create a BlockDiagMatrix with one element
    D = sympy.BlockDiagMatrix(M)

    # Try to convert back to regular Matrix - this should fail on base commit
    try:
        B = sympy.Matrix(D)
        # If we get here, the conversion succeeded
        print("Conversion succeeded!")
        print("Result matrix:")
        print(B)

        # Verify the result is correct
        expected = sympy.Matrix([[1, 2], [3, 4]])
        assert B == expected, f"Expected {expected}, got {B}"

        # Test passed
        print("Test PASSED - issue is fixed")
        return True

    except TypeError as e:
        print(f"Test FAILED - issue reproduced: {e}")
        return False

if __name__ == "__main__":
    success = test_blockdiag_single_matrix_conversion()
    if not success:
        exit(1)  # Exit with non-zero code to indicate failure