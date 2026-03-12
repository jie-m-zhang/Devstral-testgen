"""
Test to reproduce the issue with updating colorbar after changing mappable.norm to LogNorm.

The issue is that when changing the norm to LogNorm without vmin/vmax set,
the colorbar's _process_values method sets vmin=0 and vmax=1, which causes
an error when LogNorm.inverse is called because vmin=0 is invalid for log scale.

This test should FAIL on the base commit (78bf53caac) and PASS on the head commit (0849036fd9).
"""

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import sys

def test_colorbar_log_norm_update():
    """
    Test that colorbar can be updated after changing mappable's norm to LogNorm.

    On the buggy version (base commit), this test will fail with:
    ValueError: Invalid vmin or vmax

    On the fixed version (head commit), this test will pass.
    """
    # Create test data with positive values suitable for log scale
    np.random.seed(42)  # For reproducibility
    img = 10**np.random.normal(1, 1, size=(50, 50))
    img = np.abs(img)  # Ensure all values are positive

    # Create figure and plot
    fig, ax = plt.subplots(1, 1)
    plot = ax.imshow(img, cmap='gray')

    # Create colorbar
    cb = fig.colorbar(plot, ax=ax)

    # Change the norm to LogNorm WITHOUT setting vmin/vmax
    # This is the problematic case - LogNorm needs proper vmin/vmax
    # When the colorbar tries to update, it should call autoscale_None on the mappable
    # to set proper vmin/vmax before attempting to use them
    new_norm = LogNorm()
    plot.norm = new_norm

    # If we get here without an exception, the test passed
    # The fix should have called autoscale_None on the mappable
    # which sets proper vmin/vmax for the LogNorm
    plt.close(fig)
    return True

if __name__ == "__main__":
    print("Testing colorbar update after changing mappable.norm to LogNorm...")
    try:
        success = test_colorbar_log_norm_update()
        if success:
            print("Test PASSED - issue is fixed")
            sys.exit(0)
        else:
            print("Test FAILED - issue reproduced")
            sys.exit(1)
    except Exception as e:
        print(f"Test FAILED with exception: {type(e).__name__}: {e}")
        sys.exit(1)