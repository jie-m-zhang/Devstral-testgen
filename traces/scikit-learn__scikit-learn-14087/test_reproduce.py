import numpy as np
from sklearn.linear_model import LogisticRegressionCV

def test_logistic_regression_cv_refit_false():
    """
    Test that LogisticRegressionCV with refit=False doesn't throw IndexError.

    This test reproduces the issue where an IndexError is thrown when trying to
    estimate a regularization parameter via cross-validation without refitting.
    """
    np.random.seed(29)
    X = np.random.normal(size=(1000, 3))
    beta = np.random.normal(size=3)
    intercept = np.random.normal(size=None)
    y = np.sign(intercept + X @ beta)

    # This should not raise an IndexError
    try:
        model = LogisticRegressionCV(
            cv=5,
            solver='saga',
            tol=1e-2,
            refit=False
        ).fit(X, y)
        print("Test passed - no IndexError thrown")
        return True
    except IndexError as e:
        print(f"IndexError thrown: {e}")
        return False

if __name__ == "__main__":
    success = test_logistic_regression_cv_refit_false()
    if not success:
        exit(1)
    else:
        exit(0)