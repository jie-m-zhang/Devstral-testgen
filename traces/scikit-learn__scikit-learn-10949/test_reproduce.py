"""Test to reproduce the issue with warn_on_dtype and DataFrame"""

import warnings
import numpy as np
import pandas as pd
from sklearn.utils.validation import check_array
from sklearn.exceptions import DataConversionWarning

def test_warn_on_dtype_dataframe():
    """Test that warn_on_dtype works with pandas DataFrame with dtype=object"""

    # Create a DataFrame with dtype=object
    df = pd.DataFrame([[1, 2, 3], [2, 3, 4]], dtype=object)

    # Call check_array with warn_on_dtype=True
    # This should raise a DataConversionWarning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        checked = check_array(df, warn_on_dtype=True)

        # Check that a warning was raised
        assert len(w) == 1, f"Expected 1 warning, got {len(w)}"
        assert issubclass(w[0].category, DataConversionWarning), \
            f"Expected DataConversionWarning, got {w[0].category}"
        assert "object" in str(w[0].message), \
            f"Expected 'object' in warning message, got: {w[0].message}"
        assert "float64" in str(w[0].message), \
            f"Expected 'float64' in warning message, got: {w[0].message}"

    print("Test passed - DataConversionWarning was raised as expected")

if __name__ == "__main__":
    test_warn_on_dtype_dataframe()