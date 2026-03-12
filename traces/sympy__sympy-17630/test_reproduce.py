#!/usr/bin/env python
"""
Test to reproduce the issue with BlockMatrix containing ZeroMatrix blocks.

The issue is that when multiplying a BlockMatrix with ZeroMatrix blocks,
the ZeroMatrix objects get converted to Zero objects (which don't have a 'cols' attribute),
causing an AttributeError when trying to access the 'cols' attribute.
"""

from sympy import MatrixSymbol, ZeroMatrix, BlockMatrix, block_collapse

def test_blockmatrix_zeromatrix_multiply():
    """Test that multiplying BlockMatrix with ZeroMatrix blocks works correctly."""
    # Create a block matrix with zero blocks
    a = MatrixSymbol("a", 2, 2)
    z = ZeroMatrix(2, 2)
    b = BlockMatrix([[a, z], [z, z]])

    # This should work without error
    try:
        result = block_collapse(b * b * b)
        print("block_collapse(b * b * b) succeeded")
        return True
    except AttributeError as e:
        if "'Zero' object has no attribute 'cols'" in str(e):
            print(f"Test failed with expected error: {e}")
            return False
        else:
            raise

if __name__ == "__main__":
    print("Testing BlockMatrix with ZeroMatrix blocks...")
    print("=" * 60)

    print("\nTest: block_collapse multiplication")
    print("-" * 60)
    try:
        result = test_blockmatrix_zeromatrix_multiply()
        if not result:
            print("✗ Test FAILED")
            exit(1)
        else:
            print("✓ Test PASSED")
    except Exception as e:
        print(f"✗ Test FAILED with error: {e}")
        exit(1)

    print("\n" + "=" * 60)
    print("All tests passed - issue is fixed!")
    print("=" * 60)