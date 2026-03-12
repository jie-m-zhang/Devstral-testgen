#!/usr/bin/env python
"""
Test to reproduce the issue where GaussianMixture predict and fit_predict
disagree when n_init > 1.
"""

import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.utils.testing import assert_array_equal

def test_gaussian_mixture_fit_predict_with_n_init():
    """
    Test that fit_predict(X) and fit(X).predict(X) give the same results
    when n_init > 1.
    """
    # Set random seed for reproducibility
    rng = np.random.RandomState(42)
    X = rng.randn(1000, 5)

    # Test without n_init (should work)
    print("Testing without n_init...")
    gm = GaussianMixture(n_components=5, random_state=42)
    c1 = gm.fit_predict(X)
    c2 = gm.predict(X)
    assert_array_equal(c1, c2)
    print("Test passed without n_init")

    # Test with n_init=5 (should fail on buggy version)
    print("Testing with n_init=5...")
    gm = GaussianMixture(n_components=5, n_init=5, random_state=42)
    c1 = gm.fit_predict(X)
    c2 = gm.predict(X)

    # This assertion should fail on the buggy version
    assert_array_equal(c1, c2)
    print("Test passed with n_init=5")

if __name__ == "__main__":
    test_gaussian_mixture_fit_predict_with_n_init()
    print("\nAll tests passed!")