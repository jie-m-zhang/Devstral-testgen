"""
Test to reproduce the issue with non-converged affinity propagation clustering.

The issue states that when AffinityPropagation doesn't converge, it should return:
- An empty array as cluster_center_indices
- -1 as label for each training sample

But currently it returns actual cluster centers and labels instead.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation

def test_non_converged_affinity_propagation():
    """
    Test that non-converged AffinityPropagation returns empty cluster centers
    and -1 labels as documented.
    """
    # Create the exact data from the issue
    data = pd.DataFrame([[1,0,0,0,0,0],[0,1,1,1,0,0],[0,0,1,0,0,1]])

    # Force non-convergence with max_iter=2
    af = AffinityPropagation(affinity='euclidean', verbose=True, copy=False, max_iter=2).fit(data)

    print("Cluster centers indices:", af.cluster_centers_indices_)
    print("Labels:", af.labels_)

    # According to the documentation, when algorithm does not converge:
    # - cluster_center_indices should be empty
    # - labels should be -1 for each sample
    assert len(af.cluster_centers_indices_) == 0, \
        f"Expected empty cluster_centers_indices_, got {af.cluster_centers_indices_}"

    expected_labels = np.array([-1, -1, -1])
    assert np.array_equal(af.labels_, expected_labels), \
        f"Expected labels {expected_labels}, got {af.labels_}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_non_converged_affinity_propagation()