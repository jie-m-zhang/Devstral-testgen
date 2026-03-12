"""
Test to reproduce the issue with pairplot/scatterplot failing when hue_order doesn't contain all hue values.

The issue: In seaborn 0.11.1, scatterplot/pairplot fails with a TypeError when hue_order
doesn't contain all values present in the hue column.

Expected behavior: Points with hue values not in hue_order should simply not be plotted.
"""

import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

def test_scatterplot_hue_order_subset():
    """Test that scatterplot works with hue_order containing only a subset of hue values."""

    # Load the iris dataset
    iris = sns.load_dataset("iris")

    # The hue column contains three different species
    # We want to plot only two of them using hue_order
    print("Creating pairplot with hue_order subset (diag_kind=None to avoid pandas issue)...")
    try:
        # This should work but fails in seaborn 0.11.1 (base commit)
        # Using diag_kind=None to avoid the kdeplot issue with pandas
        g = sns.pairplot(iris, hue="species", hue_order=["setosa", "versicolor"], diag_kind=None)
        print("Pairplot created successfully!")
        plt.close('all')
        return True
    except TypeError as e:
        if "ufunc 'isnan' not supported for the input types" in str(e):
            print(f"Expected error occurred: {type(e).__name__}: {e}")
            plt.close('all')
            return False
        else:
            # Some other TypeError, re-raise it
            raise
    except Exception as e:
        print(f"Unexpected error occurred: {type(e).__name__}: {e}")
        plt.close('all')
        raise

if __name__ == "__main__":
    # Run the test
    success = test_scatterplot_hue_order_subset()
    
    # The test should fail on base commit (return False)
    # and pass on head commit (return True)
    if not success:
        print("\nTest FAILED - Issue reproduced (expected on base commit)")
        exit(1)
    else:
        print("\nTest PASSED - Issue is fixed (expected on head commit)")
        exit(0)