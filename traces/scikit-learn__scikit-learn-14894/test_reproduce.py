"""
Test to reproduce ZeroDivisionError in _sparse_fit for SVM with empty support_vectors_

This test reproduces the issue where using sparse data with SVR causes a
ZeroDivisionError when support_vectors_ is empty.

The test should:
- FAIL on base commit (fdbaa58acbead5a254f2e6d597dc1ab3b947f4c6) with ZeroDivisionError
- PASS on head commit (7e85a6d1f038bbb932b36f18d75df6be937ed00d) without error
"""

import numpy as np
import scipy.sparse as sp
from sklearn.svm import SVR

def test_sparse_svm_empty_support_vectors():
    """
    Test that SVR with sparse data doesn't raise ZeroDivisionError
    when support_vectors_ is empty.
    """
    # Training data from the issue
    x_train = np.array([[0, 1, 0, 0],
                       [0, 0, 0, 1],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])
    y_train = np.array([0.04, 0.04, 0.10, 0.16])

    # Create SVR model with parameters from the issue
    model = SVR(C=316.227766017, cache_size=200, coef0=0.0, degree=3, epsilon=0.1,
                gamma=1.0, kernel='linear', max_iter=15000,
                shrinking=True, tol=0.001, verbose=False)

    # Dense x_train should work without error
    model.fit(x_train, y_train)
    print("Dense data fitting completed successfully")

    # Convert to sparse - this should trigger the ZeroDivisionError on buggy version
    xtrain = sp.csr_matrix(x_train)

    try:
        model.fit(xtrain, y_train)
        print("Sparse data fitting completed successfully")

        # Verify that dual_coef_ is a sparse matrix
        # On the fixed version, this should be an empty sparse matrix
        assert sp.issparse(model.dual_coef_), "dual_coef_ should be a sparse matrix"
        print("Test passed - dual_coef_ is a sparse matrix as expected")

    except ZeroDivisionError as e:
        print(f"ZeroDivisionError occurred (expected on buggy version): {e}")
        raise  # Re-raise to fail the test

if __name__ == "__main__":
    test_sparse_svm_empty_support_vectors()