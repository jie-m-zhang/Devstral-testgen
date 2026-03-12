"""
Test to reproduce the NDDataRef mask propagation issue in v5.3.

The issue is that when one of the operand does not have a mask,
the mask propagation when doing arithmetic with handle_mask=np.bitwise_or fails.
"""

import numpy as np
from astropy.nddata import NDDataRef

def test_mask_propagation_issue():
    """Test that reproduces the mask propagation issue."""

    # Create test data
    array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])

    # Create NDDataRef objects
    nref_nomask = NDDataRef(array)
    nref_mask = NDDataRef(array, mask=mask)

    # Test 1: multiply no mask by constant (no mask * no mask) - should work
    result1 = nref_nomask.multiply(1., handle_mask=np.bitwise_or)
    assert result1.mask is None, "Expected no mask for no mask * constant"

    # Test 2: multiply no mask by itself (no mask * no mask) - should work
    result2 = nref_nomask.multiply(nref_nomask, handle_mask=np.bitwise_or)
    assert result2.mask is None, "Expected no mask for no mask * no mask"

    # Test 3: multiply mask by itself (mask * mask) - should work
    result3 = nref_mask.multiply(nref_mask, handle_mask=np.bitwise_or)
    assert result3.mask is not None, "Expected mask for mask * mask"
    assert np.array_equal(result3.mask, mask), "Expected mask to be preserved"

    # Test 4: multiply mask by constant (mask * no mask) - this should fail on buggy version
    try:
        result4 = nref_mask.multiply(1., handle_mask=np.bitwise_or)
        # If we get here, the operation succeeded
        assert result4.mask is not None, "Expected mask for mask * constant"
        assert np.array_equal(result4.mask, mask), "Expected mask to be preserved for mask * constant"
        print("Test 4 passed: mask * constant works correctly")
    except TypeError as e:
        if "unsupported operand type(s) for |: 'int' and 'NoneType'" in str(e):
            print(f"Test 4 failed with expected error: {e}")
            raise  # Re-raise to fail the test
        else:
            raise  # Unexpected error

    # Test 5: multiply mask by no mask (mask * no mask) - this should fail on buggy version
    try:
        result5 = nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or)
        # If we get here, the operation succeeded
        assert result5.mask is not None, "Expected mask for mask * no mask"
        assert np.array_equal(result5.mask, mask), "Expected mask to be preserved for mask * no mask"
        print("Test 5 passed: mask * no mask works correctly")
    except TypeError as e:
        if "unsupported operand type(s) for |: 'int' and 'NoneType'" in str(e):
            print(f"Test 5 failed with expected error: {e}")
            raise  # Re-raise to fail the test
        else:
            raise  # Unexpected error

    print("All tests passed - issue is fixed")

if __name__ == "__main__":
    test_mask_propagation_issue()