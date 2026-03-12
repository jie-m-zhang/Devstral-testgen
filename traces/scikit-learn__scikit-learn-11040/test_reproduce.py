"""
Test to reproduce the issue with missing parameter validation in Neighbors estimator for float n_neighbors.

The issue is that when a float value is passed for n_neighbors, it should raise a helpful TypeError
but instead raises a confusing error deep in the code.
"""

from sklearn.neighbors import NearestNeighbors
from sklearn.datasets import make_blobs

def test_float_n_neighbors_in_constructor():
    """Test that float n_neighbors in constructor raises TypeError with helpful message."""
    X, y = make_blobs()

    # This should raise TypeError with a helpful message
    try:
        neighbors = NearestNeighbors(n_neighbors=3.)
        neighbors.fit(X)
        neighbors.kneighbors(X)
        # If we get here, the test should fail because we expected an error
        assert False, "Expected TypeError when passing float n_neighbors to constructor"
    except TypeError as e:
        # Check that the error message is helpful
        assert "n_neighbors does not take" in str(e), f"Expected helpful error message, got: {e}"
        print(f"Test 1 passed - got expected TypeError: {e}")

def test_float_n_neighbors_in_kneighbors():
    """Test that float n_neighbors in kneighbors method raises TypeError with helpful message."""
    X, y = make_blobs()
    neighbors = NearestNeighbors(n_neighbors=3)
    neighbors.fit(X)

    # This should raise TypeError with a helpful message
    try:
        neighbors.kneighbors(X, n_neighbors=3.)
        # If we get here, the test should fail because we expected an error
        assert False, "Expected TypeError when passing float n_neighbors to kneighbors method"
    except TypeError as e:
        # Check that the error message is helpful
        assert "n_neighbors does not take" in str(e), f"Expected helpful error message, got: {e}"
        print(f"Test 2 passed - got expected TypeError: {e}")

if __name__ == "__main__":
    print("Testing float n_neighbors validation...")
    test_float_n_neighbors_in_constructor()
    test_float_n_neighbors_in_kneighbors()
    print("All tests passed!")