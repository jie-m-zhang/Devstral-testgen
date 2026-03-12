"""
Test to reproduce the issue with RidgeClassifierCV's store_cv_values parameter.

The issue is that RidgeClassifierCV doesn't accept the store_cv_values parameter
even though the documentation mentions it and the base class supports it.
"""

import numpy as np
from sklearn import linear_model as lm

def test_ridge_classifier_cv_store_cv_values():
    """
    Test that RidgeClassifierCV accepts store_cv_values parameter.

    This test should FAIL on the buggy version (base commit) because
    RidgeClassifierCV.__init__ doesn't accept store_cv_values parameter.

    This test should PASS on the fixed version (head commit) because
    RidgeClassifierCV.__init__ will accept store_cv_values parameter.
    """
    # Create test data - for classification, y should be class labels
    np.random.seed(42)
    n = 100
    x = np.random.randn(n, 30)
    # Create binary classification labels
    y = np.random.randint(0, 2, size=n)

    # Try to create RidgeClassifierCV with store_cv_values=True
    # This should work but will fail on buggy version
    try:
        rr = lm.RidgeClassifierCV(
            alphas=np.arange(0.1, 1000, 0.1),
            normalize=True,
            store_cv_values=True
        )
        rr.fit(x, y)

        # If we get here, the parameter was accepted
        # Now check that cv_values_ attribute exists if store_cv_values=True
        if hasattr(rr, 'cv_values_'):
            print("Test passed - store_cv_values parameter is supported")
            return True
        else:
            print("Test failed - store_cv_values parameter accepted but cv_values_ attribute not set")
            return False

    except TypeError as e:
        if "unexpected keyword argument 'store_cv_values'" in str(e):
            print(f"Test failed (as expected on buggy version) - {e}")
            return False
        else:
            print(f"Test failed with unexpected error - {e}")
            return False
    except Exception as e:
        print(f"Test failed with unexpected error - {e}")
        return False

if __name__ == "__main__":
    success = test_ridge_classifier_cv_store_cv_values()
    if not success:
        exit(1)
    else:
        exit(0)