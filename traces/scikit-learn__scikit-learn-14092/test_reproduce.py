#!/usr/bin/env python
"""
Test to reproduce the NCA GridSearchCV issue with parameter type checking.

The issue is that NCA checks its parameters to have specific types (int, float),
which can easily fail in a GridSearch due to how param grid is made:
- For `tol`: 1 is not a float (it's an int)
- For `n_components`: np.int64 is not int

This test should FAIL on the base commit and PASS on the head commit.
"""

import numpy as np
import sys

# Try to import from both locations to handle different versions
try:
    from sklearn.neighbors.nca import NeighborhoodComponentsAnalysis
except ImportError:
    from sklearn.neighbors._nca import NeighborhoodComponentsAnalysis

from sklearn.neighbors.classification import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

def test_nca_gridsearch_parameter_types():
    """Test that NCA works with GridSearchCV parameter types."""

    # Create random data
    X = np.random.random_sample((100, 10))
    y = np.random.randint(2, size=100)

    # Create pipeline
    nca = NeighborhoodComponentsAnalysis()
    knn = KNeighborsClassifier()
    pipe = Pipeline([('nca', nca),
                     ('knn', knn)])

    # Create parameter grid with types that cause issues in base commit
    # - tol: 1 is an int, not a float
    # - n_components: np.arange creates np.int64, not int
    params = {'nca__tol': [0.1, 0.5, 1],  # 1 is int, not float
              'nca__n_components': np.arange(1, 10)}  # np.int64, not int

    # Run GridSearchCV
    gs = GridSearchCV(estimator=pipe, param_grid=params, error_score='raise')

    try:
        gs.fit(X, y)
        print("GridSearchCV completed successfully!")
        print("Best parameters:", gs.best_params_)
        print("Best score:", gs.best_score_)
        return True
    except (TypeError, ValueError) as e:
        print(f"GridSearchCV failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_nca_gridsearch_parameter_types()
    if success:
        print("\nTest PASSED - NCA works with GridSearchCV parameter types")
        sys.exit(0)
    else:
        print("\nTest FAILED - NCA does not work with GridSearchCV parameter types")
        sys.exit(1)