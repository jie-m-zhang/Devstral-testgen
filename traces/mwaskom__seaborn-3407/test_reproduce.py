"""
Test to reproduce the MultiIndex DataFrame pairplot KeyError issue.
This test should FAIL on the base commit and PASS on the head commit.
"""
import numpy as np
import pandas as pd
import seaborn as sns

def test_pairplot_multiindex_dataframe():
    """
    Test that pairplot works with MultiIndex DataFrame.

    This reproduces the issue where pairplot raises KeyError when
    trying to plot a DataFrame with MultiIndex columns.

    The error occurs in map_diag when trying to access self.data[var]
    where var is a single level of the MultiIndex instead of the full tuple.
    """
    # Create a DataFrame with MultiIndex columns
    data = {
        ("A", "1"): np.random.rand(100),
        ("A", "2"): np.random.rand(100),
        ("B", "1"): np.random.rand(100),
        ("B", "2"): np.random.rand(100),
    }
    df = pd.DataFrame(data)

    # This should not raise a KeyError
    # On the base commit, this will fail with:
    # KeyError: "['1'] not in index"
    try:
        ax = sns.pairplot(df)
        # If we get here without exception, the test passes
        print("Test passed - pairplot succeeded with MultiIndex DataFrame")
        return True
    except KeyError as e:
        # This is the expected failure on the base commit
        print(f"Test failed with KeyError (expected on base commit): {e}")
        return False

if __name__ == "__main__":
    result = test_pairplot_multiindex_dataframe()
    if not result:
        exit(1)
    else:
        exit(0)