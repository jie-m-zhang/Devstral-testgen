#!/usr/bin/env python
"""
Test to reproduce the issue where sympy.Array([]) fails with ValueError
while sympy.Matrix([]) works.

This test should:
- FAIL on base commit (c5cef2499d6eed024b0db5c792d6ec7c53baa470) with ValueError
- PASS on head commit (9a6104eab0ea7ac191a09c24f3e2d79dcd66bda5) without error
"""

def test_empty_array_creation():
    """
    Test that Array([]) can be created without error.

    The issue is that Array([]) fails with:
    ValueError: not enough values to unpack (expected 2, got 0)

    This happens in the _scan_iterable_shape method when trying to unpack
    an empty zip result.
    """
    from sympy import Array, Matrix

    # Test 1: Array([]) should work (this is the main issue)
    try:
        empty_array = Array([])
        print(f"✓ Array([]) created successfully: {empty_array}")
        print(f"  Shape: {empty_array.shape}")
        print(f"  Rank: {empty_array.rank()}")
        print(f"  Length: {len(empty_array)}")
    except ValueError as e:
        print(f"✗ Array([]) failed with ValueError: {e}")
        raise

    # Test 2: Matrix([]) should also work (for comparison)
    try:
        empty_matrix = Matrix([])
        print(f"✓ Matrix([]) created successfully: {empty_matrix}")
        print(f"  Shape: {empty_matrix.shape}")
    except Exception as e:
        print(f"✗ Matrix([]) failed with: {e}")
        raise

    # Test 3: Verify the shape is correct for empty array
    assert empty_array.shape == (0,), f"Expected shape (0,), got {empty_array.shape}"

    # Test 4: Verify rank is correct
    assert empty_array.rank() == 1, f"Expected rank 1, got {empty_array.rank()}"

    # Test 5: Verify length is correct
    assert len(empty_array) == 0, f"Expected length 0, got {len(empty_array)}"

    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_empty_array_creation()