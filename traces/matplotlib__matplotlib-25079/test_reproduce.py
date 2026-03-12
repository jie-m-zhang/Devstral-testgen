"""
Test to reproduce the issue with setting LogNorm after colorbar creation.

The issue is that setting the norm to a LogNorm after the colorbar has been created
fails with an "Invalid vmin" value in matplotlib 3.6.3.

This test should:
- FAIL on base commit (66f7956984cbfc3647e867c6e5fde889a89c64ef) with ValueError
- PASS on head commit (73909bcb408886a22e2b84581d6b9e6d9907c813)
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

def test_log_norm_after_colorbar():
    """
    Test that setting LogNorm after colorbar creation works correctly.

    This reproduces the issue where setting norm to LogNorm after creating
    a colorbar fails with "Invalid vmin or vmax" error.
    """
    # Create some random data to fill a 2d plot
    rng = np.random.default_rng(0)
    img = rng.uniform(1, 5, (25, 25))

    # Plot it
    fig, ax = plt.subplots(layout="constrained")
    plot = ax.pcolormesh(img)
    cbar = fig.colorbar(plot, ax=ax)

    vmin = 1
    vmax = 5

    # This should work without raising an error
    try:
        plot.norm = LogNorm(vmin, vmax)
        plot.autoscale()

        # Force a draw to trigger the error
        fig.canvas.draw()

        # If we get here, the test passed
        print("Test PASSED - LogNorm set successfully after colorbar creation")
        return True
    except ValueError as e:
        if "Invalid vmin or vmax" in str(e):
            print(f"Test FAILED - Got expected error: {e}")
            return False
        else:
            print(f"Test FAILED - Got unexpected error: {e}")
            return False
    except Exception as e:
        print(f"Test FAILED - Got unexpected exception: {e}")
        return False

if __name__ == "__main__":
    result = test_log_norm_after_colorbar()
    if not result:
        exit(1)
    else:
        exit(0)