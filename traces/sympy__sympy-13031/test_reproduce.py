#!/usr/bin/env python
"""
Test to reproduce the issue with Matrix.hstack and vstack behavior
in sympy 1.1 when dealing with zero-row/zero-column matrices.

Issue: In sympy 1.0, hstack of zero-row matrices with different column counts
returns the correct shape, but in sympy 1.1 (buggy version) it returns incorrect shape.

The bug is specifically in SparseMatrix.col_join and SparseMatrix.row_join methods.
"""

import sympy as sy
from sympy.matrices import SparseMatrix

def test_hstack_zero_rows_sparse():
    """Test hstack with zero-row SparseMatrices - this is the main bug."""
    print("Testing hstack with zero-row SparseMatrices...")

    M1 = SparseMatrix.zeros(0, 0)
    M2 = SparseMatrix.zeros(0, 1)
    M3 = SparseMatrix.zeros(0, 2)
    M4 = SparseMatrix.zeros(0, 3)

    result = SparseMatrix.hstack(M1, M2, M3, M4)
    print(f"Result shape: {result.shape}")
    print(f"Expected shape: (0, 6)")

    # The expected behavior is (0, 6) - sum of all columns
    # In buggy version, this returns (0, 3) because M1 (0x0) gets replaced by M2 (0x1)
    assert result.shape == (0, 6), f"Expected (0, 6), got {result.shape}"

    print("✓ hstack test passed")

def test_vstack_zero_cols_sparse():
    """Test vstack with zero-column SparseMatrices - this is the main bug."""
    print("\nTesting vstack with zero-column SparseMatrices...")

    M1 = SparseMatrix.zeros(0, 0)
    M2 = SparseMatrix.zeros(1, 0)
    M3 = SparseMatrix.zeros(2, 0)
    M4 = SparseMatrix.zeros(3, 0)

    result = SparseMatrix.vstack(M1, M2, M3, M4)
    print(f"Result shape: {result.shape}")
    print(f"Expected shape: (6, 0)")

    # The expected behavior is (6, 0) - sum of all rows
    # In buggy version, this returns (3, 0) because M1 (0x0) gets replaced by M2 (1x0)
    assert result.shape == (6, 0), f"Expected (6, 0), got {result.shape}"

    print("✓ vstack test passed")

def test_hstack_normal_case_sparse():
    """Test hstack with normal (non-zero) SparseMatrices to ensure we don't break existing functionality."""
    print("\nTesting hstack with normal SparseMatrices...")

    M1 = SparseMatrix.zeros(1, 0)
    M2 = SparseMatrix.zeros(1, 1)
    M3 = SparseMatrix.zeros(1, 2)
    M4 = SparseMatrix.zeros(1, 3)

    result = SparseMatrix.hstack(M1, M2, M3, M4)
    print(f"Result shape: {result.shape}")
    print(f"Expected shape: (1, 6)")

    assert result.shape == (1, 6), f"Expected (1, 6), got {result.shape}"

    print("✓ Normal hstack test passed")

def test_vstack_normal_case_sparse():
    """Test vstack with normal (non-zero) SparseMatrices to ensure we don't break existing functionality."""
    print("\nTesting vstack with normal SparseMatrices...")

    M1 = SparseMatrix.zeros(0, 1)
    M2 = SparseMatrix.zeros(1, 1)
    M3 = SparseMatrix.zeros(2, 1)
    M4 = SparseMatrix.zeros(3, 1)

    result = SparseMatrix.vstack(M1, M2, M3, M4)
    print(f"Result shape: {result.shape}")
    print(f"Expected shape: (6, 1)")

    assert result.shape == (6, 1), f"Expected (6, 1), got {result.shape}"

    print("✓ Normal vstack test passed")

if __name__ == "__main__":
    print("Running tests to reproduce the issue...\n")

    try:
        test_hstack_zero_rows_sparse()
        test_vstack_zero_cols_sparse()
        test_hstack_normal_case_sparse()
        test_vstack_normal_case_sparse()

        print("\n" + "="*50)
        print("All tests passed - issue is fixed!")
        print("="*50)

    except AssertionError as e:
        print("\n" + "="*50)
        print(f"Test failed - issue reproduced: {e}")
        print("="*50)
        exit(1)