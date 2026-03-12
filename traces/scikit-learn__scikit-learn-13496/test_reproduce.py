"""
Test to reproduce the issue with warm_start not being exposed in IsolationForest.__init__()
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.utils.testing import assert_equal

def test_warm_start_in_init():
    """
    Test that warm_start parameter can be passed to IsolationForest.__init__()
    and that it works correctly for incremental fitting.
    """
    # Generate some random data
    rng = np.random.RandomState(42)
    X = rng.randn(100, 5)

    # Test 1: Try to create IsolationForest with warm_start=True in constructor
    # This should work after the fix, but fail before the fix
    try:
        clf = IsolationForest(n_estimators=10, warm_start=True, random_state=42)
    except TypeError as e:
        if "warm_start" in str(e):
            raise AssertionError(
                "warm_start parameter not accepted in IsolationForest.__init__() - "
                "this is the bug we're testing for!"
            )
        else:
            raise

    # Fit the model initially
    clf.fit(X)

    # Check that we have 10 estimators
    assert_equal(len(clf.estimators_), 10, "Should have 10 estimators initially")

    # Now increase n_estimators and fit again with warm_start
    clf.set_params(n_estimators=20)
    clf.fit(X)

    # Check that we now have 20 estimators (warm_start should have added 10 more)
    assert_equal(len(clf.estimators_), 20, "Should have 20 estimators after warm_start")

    print("Test passed - warm_start works correctly in IsolationForest")

if __name__ == "__main__":
    test_warm_start_in_init()