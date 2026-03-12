#!/usr/bin/env python
"""
Test to reproduce the NumPy 1.24 deprecation warnings issue.

The issue occurs when calling plt.get_cmap() with an empty uint8 array,
which triggers deprecation warnings in NumPy 1.24+ about out-of-bound
Python integers being converted to integer arrays.
"""

import warnings
import matplotlib.pyplot as plt
import numpy as np

def test_numpy_deprecation_warnings():
    """
    Test that no NumPy deprecation warnings are raised when using colormaps.

    This test reproduces the issue described in the bug report where
    calling plt.get_cmap()(np.empty((0, ), dtype=np.uint8)) raises
    deprecation warnings in NumPy 1.24+.
    """
    # Capture all warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # This is the problematic code from the issue
        result = plt.get_cmap()(np.empty((0, ), dtype=np.uint8))

        # Check for deprecation warnings about integer conversion
        numpy_deprecation_warnings = [
            warning for warning in w
            if issubclass(warning.category, DeprecationWarning)
            and "NumPy will stop allowing conversion of out-of-bound Python integers" in str(warning.message)
        ]

        # The assertion: no NumPy deprecation warnings should be raised
        assert len(numpy_deprecation_warnings) == 0, (
            f"Expected no NumPy deprecation warnings, but got {len(numpy_deprecation_warnings)}:\n"
            + "\n".join(str(warning.message) for warning in numpy_deprecation_warnings)
        )

        print("Test passed - no NumPy deprecation warnings detected")

if __name__ == "__main__":
    test_numpy_deprecation_warnings()