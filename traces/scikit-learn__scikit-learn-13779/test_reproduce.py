"""Test to reproduce the issue with VotingClassifier when estimator is None and sample_weight is passed"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

def test_voting_classifier_none_estimator_with_sample_weight():
    """
    Test that VotingClassifier doesn't fail when an estimator is set to None
    and sample_weight is passed during fit.

    This test reproduces the issue described in the GitHub issue where
    calling fit with sample_weight after setting an estimator to None
    causes an AttributeError.
    """
    # Create synthetic data instead of using sklearn datasets
    # to avoid import issues on later commits
    np.random.seed(42)
    X = np.random.randn(100, 4)
    y = np.random.randint(0, 3, 100)

    # Create a VotingClassifier with two estimators
    voter = VotingClassifier(
        estimators=[('lr', LogisticRegression(solver='lbfgs', multi_class='auto')),
                    ('rf', RandomForestClassifier(n_estimators=10))]
    )

    # First fit should work fine
    voter.fit(X, y, sample_weight=np.ones(y.shape))

    # Set one estimator to None
    voter.set_params(lr=None)

    # This should not fail - the second fit should work even with lr=None
    # In the buggy version, this will raise:
    # AttributeError: 'NoneType' object has no attribute 'fit'
    try:
        voter.fit(X, y, sample_weight=np.ones(y.shape))
        print("Test passed - issue is fixed")
    except AttributeError as e:
        print(f"Test failed with AttributeError: {e}")
        raise

if __name__ == "__main__":
    test_voting_classifier_none_estimator_with_sample_weight()