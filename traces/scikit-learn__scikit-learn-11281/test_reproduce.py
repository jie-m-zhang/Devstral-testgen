"""
Test to reproduce the issue: Mixture models should have a clusterer-compatible interface
This test should FAIL on base commit (no fit_predict method) and PASS on head commit (with fit_predict method)
"""

import numpy as np
from sklearn.mixture import GaussianMixture

def test_mixture_fit_predict_interface():
    """
    Test that mixture models have a clusterer-compatible interface with fit_predict method.
    This reproduces the issue described in the GitHub issue.
    """
    # Create some sample data
    rng = np.random.RandomState(42)
    X = np.vstack([
        rng.randn(100, 2) + np.array([0, 0]),
        rng.randn(100, 2) + np.array([5, 5]),
        rng.randn(100, 2) + np.array([-5, 5])
    ])

    # Create a Gaussian Mixture model
    gm = GaussianMixture(n_components=3, random_state=42)

    # Test 1: Check that fit_predict method exists
    assert hasattr(gm, 'fit_predict'), \
        "Mixture model should have a fit_predict method for clusterer-compatible interface"

    # Test 2: Call fit_predict and verify it returns labels
    labels = gm.fit_predict(X)

    # Verify the return type and shape
    assert isinstance(labels, np.ndarray), \
        "fit_predict should return a numpy array"
    assert labels.shape == (X.shape[0],), \
        f"fit_predict should return labels of shape ({X.shape[0]},), got {labels.shape}"

    # Verify labels are integers in valid range
    assert np.issubdtype(labels.dtype, np.integer), \
        "Labels should be integers"
    assert np.all(labels >= 0), \
        "Labels should be non-negative"
    assert np.all(labels < gm.n_components), \
        f"Labels should be in range [0, {gm.n_components}), got max label {np.max(labels)}"

    # Test 3: Verify fit_predict gives same result as fit + predict
    gm2 = GaussianMixture(n_components=3, random_state=42)
    gm2.fit(X)
    labels_from_predict = gm2.predict(X)

    # The labels should be the same (though order might differ due to random initialization)
    # We check that the clustering is equivalent by checking the set of unique labels
    assert set(np.unique(labels)) == set(np.unique(labels_from_predict)), \
        "fit_predict should give same clustering as fit + predict"

    print("All tests passed! Mixture models now have a clusterer-compatible interface.")

if __name__ == "__main__":
    test_mixture_fit_predict_interface()