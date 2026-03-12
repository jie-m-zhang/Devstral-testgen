"""
Test to reproduce the issue with print_changed_only and vector values.

The issue occurs when using print_changed_only=True with LogisticRegressionCV
that has Cs parameter set to a numpy array. The comparison in _changed_params
fails because it tries to compare arrays directly with !=, which raises:
"ValueError: The truth value of an array with more than one element is ambiguous."
"""

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegressionCV

def test_print_changed_only_vector_values():
    """
    Test that print_changed_only works with vector values like Cs in LogisticRegressionCV.

    This test should:
    - FAIL on base commit (0e3c1879b0) with ValueError about ambiguous truth value
    - PASS on head commit (7813f7efb5) after the fix
    """
    # Set print_changed_only to True
    sklearn.set_config(print_changed_only=True)

    # Create LogisticRegressionCV with Cs as a numpy array
    # This should trigger the bug in the base commit
    estimator = LogisticRegressionCV(Cs=np.array([0.1, 1]))

    # Try to print the estimator - this is where the error occurs
    try:
        output = str(estimator)
        # If we get here, the test passed (no error)
        print("Test PASSED - no error occurred")
        print("Output:", output)
        return True
    except ValueError as e:
        if "ambiguous" in str(e):
            print(f"Test FAILED (as expected on buggy version) - ValueError: {e}")
            return False
        else:
            # Some other ValueError
            raise
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        raise

if __name__ == "__main__":
    success = test_print_changed_only_vector_values()
    if not success:
        # Exit with non-zero code to indicate failure
        exit(1)
    else:
        exit(0)