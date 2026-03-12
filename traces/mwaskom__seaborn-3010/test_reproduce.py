"""
Test to reproduce the issue with PolyFit not being robust to missing data.

The issue is that when there's a None value in the data, PolyFit fails with a LinAlgError.
This test should FAIL on the base commit and PASS on the head commit.
"""

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_equal

# Import the PolyFit stat directly
from seaborn._stats.regression import PolyFit
from seaborn._core.groupby import GroupBy

def test_polyfit_with_missing_data():
    """
    Test that PolyFit handles missing data (None values) gracefully.

    This test reproduces the issue by directly calling PolyFit on data with None values.
    """

    # Create data with missing values (None)
    df = pd.DataFrame({
        'x': [1, 2, 3, None, 4],
        'y': [1, 2, 3, 4, 5],
        'group': ['a', 'a', 'a', 'a', 'a']  # Add a grouping column
    })

    # Create a GroupBy object with a grouping variable
    groupby = GroupBy(["group"])

    # Try to fit PolyFit - this should trigger the error
    # On the base commit, this will raise LinAlgError
    # On the head commit, this should work fine
    try:
        result = PolyFit()(df, groupby, "x", {})
        # If we get here, the fit was successful
        result_check = True
    except np.linalg.LinAlgError as e:
        # If we get a LinAlgError, the bug is present
        result_check = False
        print(f"LinAlgError occurred: {e}")
        raise  # Re-raise to see the full traceback

    # Assert that the fit was successful (no LinAlgError)
    assert result_check, "PolyFit should handle missing data without raising LinAlgError"

    # Also check that the result is not empty
    assert len(result) > 0, "PolyFit should return non-empty result"

    print("Test passed - PolyFit handles missing data correctly")

if __name__ == "__main__":
    test_polyfit_with_missing_data()