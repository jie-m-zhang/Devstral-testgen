"""Test to reproduce the regression in input validation of clustering metrics."""
import numpy as np
from sklearn.metrics.cluster import mutual_info_score

def test_mutual_info_score_with_object_dtype():
    """
    Test that mutual_info_score works with string data with object dtype.

    This test reproduces the issue where mutual_info_score raises ValueError
    when given string data with .astype(object), but works without it.

    The issue is that check_array was trying to convert object arrays to float,
    which fails for strings. The fix is to pass dtype=None to check_array.
    """
    # Create string data with object dtype (this should work)
    x = np.random.choice(['a', 'b'], size=20).astype(object)

    # This should not raise ValueError
    # On the buggy version, this will raise: ValueError: could not convert string to float: 'b'
    # On the fixed version, this will work correctly
    try:
        result = mutual_info_score(x, x)
        # If we get here, the test passes (issue is fixed)
        print(f"Test passed - mutual_info_score returned: {result}")
        assert isinstance(result, (float, np.floating)), f"Expected float, got {type(result)}"
        assert result >= 0.0, f"Expected non-negative result, got {result}"
        return True
    except ValueError as e:
        # If we get a ValueError about converting string to float, the bug is present
        if "could not convert string to float" in str(e):
            print(f"Test failed (bug present) - ValueError: {e}")
            return False
        else:
            # Some other ValueError - re-raise it
            raise

if __name__ == "__main__":
    success = test_mutual_info_score_with_object_dtype()
    if not success:
        exit(1)  # Exit with non-zero code to indicate failure
    else:
        exit(0)  # Exit with zero code to indicate success