#!/usr/bin/env python
"""
Test to reproduce the issue with empty lists/arrays in WCS transformations.

The issue is that passing empty lists/arrays to wcs_pix2world should return
empty lists/arrays instead of raising an InconsistentAxisTypesError.
"""

import numpy as np
from astropy.wcs import WCS

def test_empty_lists_wcs_pix2world():
    """
    Test that wcs_pix2world handles empty lists/arrays correctly.

    This should not raise an error but should return empty arrays.
    """
    # Create a simple WCS object
    w = WCS(naxis=2)
    w.wcs.crval = [0, 0]
    w.wcs.cdelt = [1, 1]
    w.wcs.crpix = [0, 0]
    w.wcs.ctype = ['RA---TAN', 'DEC--TAN']

    # Test with empty lists - this should not raise an error
    # On the buggy version, this will raise InconsistentAxisTypesError
    # On the fixed version, this will return empty arrays
    try:
        result = w.wcs_pix2world([], [], 0)
        # If we get here, the fix is working
        print(f"Test passed - result: {result}")
        print(f"Result type: {type(result)}")
        if isinstance(result, tuple):
            print(f"Result[0]: {result[0]}, shape: {result[0].shape}")
            print(f"Result[1]: {result[1]}, shape: {result[1].shape}")
        return True
    except Exception as e:
        print(f"Test failed with error: {type(e).__name__}: {e}")
        return False

def test_empty_arrays_wcs_pix2world():
    """
    Test that wcs_pix2world handles empty numpy arrays correctly.
    """
    # Create a simple WCS object
    w = WCS(naxis=2)
    w.wcs.crval = [0, 0]
    w.wcs.cdelt = [1, 1]
    w.wcs.crpix = [0, 0]
    w.wcs.ctype = ['RA---TAN', 'DEC--TAN']

    # Test with empty numpy arrays
    try:
        result = w.wcs_pix2world(np.array([]), np.array([]), 0)
        print(f"Test with empty arrays passed - result: {result}")
        print(f"Result type: {type(result)}")
        if isinstance(result, tuple):
            print(f"Result[0]: {result[0]}, shape: {result[0].shape}")
            print(f"Result[1]: {result[1]}, shape: {result[1].shape}")
        return True
    except Exception as e:
        print(f"Test with empty arrays failed with error: {type(e).__name__}: {e}")
        return False

def test_empty_array_single_arg():
    """
    Test that wcs_pix2world handles empty arrays with single argument correctly.
    """
    # Create a simple WCS object
    w = WCS(naxis=2)
    w.wcs.crval = [0, 0]
    w.wcs.cdelt = [1, 1]
    w.wcs.crpix = [0, 0]
    w.wcs.ctype = ['RA---TAN', 'DEC--TAN']

    # Test with empty array as single argument
    try:
        result = w.wcs_pix2world(np.array([]).reshape(0, 2), 0)
        print(f"Test with empty array (single arg) passed - result: {result}")
        print(f"Result type: {type(result)}")
        print(f"Result shape: {result.shape}")
        return True
    except Exception as e:
        print(f"Test with empty array (single arg) failed with error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("Testing empty lists/arrays in WCS transformations...")
    print("=" * 60)

    print("\nTest 1: Empty lists")
    print("-" * 60)
    test1_passed = test_empty_lists_wcs_pix2world()

    print("\nTest 2: Empty numpy arrays")
    print("-" * 60)
    test2_passed = test_empty_arrays_wcs_pix2world()

    print("\nTest 3: Empty array as single argument")
    print("-" * 60)
    test3_passed = test_empty_array_single_arg()

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Test 1 (empty lists): {'PASSED' if test1_passed else 'FAILED'}")
    print(f"  Test 2 (empty arrays): {'PASSED' if test2_passed else 'FAILED'}")
    print(f"  Test 3 (empty array single arg): {'PASSED' if test3_passed else 'FAILED'}")

    if test1_passed and test2_passed and test3_passed:
        print("\nAll tests PASSED - issue is fixed!")
        exit(0)
    else:
        print("\nSome tests FAILED - issue still exists!")
        exit(1)