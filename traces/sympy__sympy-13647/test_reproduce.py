#!/usr/bin/env python
"""
Test to reproduce the Matrix.col_insert() bug.

The issue is that when inserting columns into a matrix, the resulting matrix
has incorrect values. Specifically, the 3x3 identity matrix to the right of
the inserted columns appears shifted incorrectly.
"""

import sympy as sm

def test_col_insert_bug():
    """Test that reproduces the col_insert bug from issue description."""
    # Create a 6x6 identity matrix
    M = sm.eye(6)
    
    # Create a 6x2 matrix of twos
    V = 2 * sm.ones(6, 2)
    
    # Insert V into column 3 of M
    result = M.col_insert(3, V)
    
    # Expected result: 6x8 matrix with:
    # - Columns 0-2: original identity columns 0-2
    # - Columns 3-4: the inserted matrix V (all twos)
    # - Columns 5-7: original identity columns 3-5 (shifted right by 2)
    
    # Check the shape
    assert result.shape == (6, 8), f"Expected shape (6, 8), got {result.shape}"
    
    # Check columns 0-2 (should be identity)
    for i in range(6):
        for j in range(3):
            if i == j:
                assert result[i, j] == 1, f"Expected result[{i}, {j}] = 1, got {result[i, j]}"
            else:
                assert result[i, j] == 0, f"Expected result[{i}, {j}] = 0, got {result[i, j]}"
    
    # Check columns 3-4 (should be all 2s)
    for i in range(6):
        for j in range(3, 5):
            assert result[i, j] == 2, f"Expected result[{i}, {j}] = 2, got {result[i, j]}"
    
    # Check columns 5-7 (should be shifted identity)
    # This is where the bug manifests - the identity is incorrectly shifted
    for i in range(6):
        for j in range(5, 8):
            col_in_original = j - 2  # We inserted 2 columns, so shift by 2
            if i == col_in_original:
                assert result[i, j] == 1, f"Expected result[{i}, {j}] = 1, got {result[i, j]}"
            else:
                assert result[i, j] == 0, f"Expected result[{i}, {j}] = 0, got {result[i, j]}"
    
    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_col_insert_bug()