#!/usr/bin/env python
"""
Test to reproduce the issue with comparing string to array in _estimate_mi.

The issue is that in _estimate_mi, there is a comparison:
    discrete_features == 'auto'

But discrete_features can be an array of indices or a boolean mask.
This will error in future versions of numpy and currently raises a FutureWarning.
"""

import numpy as np
import warnings
from sklearn.feature_selection.mutual_info_ import mutual_info_classif

def test_discrete_features_array_no_warning():
    """Test that discrete_features as array doesn't raise FutureWarning."""
    # Create some test data
    rng = np.random.RandomState(42)
    X = rng.rand(100, 5)
    y = rng.randint(0, 2, 100)

    # Test with discrete_features as an array of indices
    # This should NOT raise a FutureWarning in the fixed version
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        mi = mutual_info_classif(X, y, discrete_features=[0, 2], n_neighbors=3, random_state=0)

        # Check if any FutureWarning was raised
        future_warnings = [warning for warning in w if issubclass(warning.category, FutureWarning)]

        if future_warnings:
            print(f"FAIL: FutureWarning raised: {future_warnings[0].message}")
            print("This indicates the bug is present - comparing string to array")
            return False
        else:
            print("PASS: No FutureWarning raised")
            print(f"MI values: {mi}")
            return True

def test_discrete_features_boolean_mask_no_warning():
    """Test that discrete_features as boolean mask doesn't raise FutureWarning."""
    # Create some test data
    rng = np.random.RandomState(42)
    X = rng.rand(100, 5)
    y = rng.randint(0, 2, 100)

    # Test with discrete_features as a boolean mask
    discrete_mask = np.array([True, False, True, False, False])

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        mi = mutual_info_classif(X, y, discrete_features=discrete_mask, n_neighbors=3, random_state=0)

        # Check if any FutureWarning was raised
        future_warnings = [warning for warning in w if issubclass(warning.category, FutureWarning)]

        if future_warnings:
            print(f"FAIL: FutureWarning raised: {future_warnings[0].message}")
            print("This indicates the bug is present - comparing string to array")
            return False
        else:
            print("PASS: No FutureWarning raised")
            print(f"MI values: {mi}")
            return True

if __name__ == "__main__":
    print("Testing discrete_features parameter for FutureWarning...")

    print("\n1. Testing with array of indices:")
    result1 = test_discrete_features_array_no_warning()

    print("\n2. Testing with boolean mask:")
    result2 = test_discrete_features_boolean_mask_no_warning()

    if result1 and result2:
        print("\nAll tests passed - no FutureWarning detected!")
        exit(0)
    else:
        print("\nSome tests failed - FutureWarning detected!")
        exit(1)