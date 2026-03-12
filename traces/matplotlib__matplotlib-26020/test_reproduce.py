"""
Test to reproduce the issue with AxesGrid and non-default axis class.

The issue occurs when creating an AxesGrid with a custom axis class
where the 'axis' attribute is a method instead of a dictionary.
This causes a TypeError: 'method' object is not subscriptable
when _tick_only tries to access ax.axis["bottom"] and ax.axis["left"].
"""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import AxesGrid

class CustomAxes(Axes):
    """
    A custom axes class that has 'axis' as a method instead of a dictionary.
    This simulates the behavior of cartopy's GeoAxes.
    """
    def axis(self, *args, **kwargs):
        """
        Override axis to be a method instead of a dictionary.
        This reproduces the issue where ax.axis["bottom"] fails.
        """
        if args or kwargs:
            # Call parent's axis method if arguments are provided
            return super().axis(*args, **kwargs)
        # Return a method object (not subscriptable)
        return self._axis_method

    def _axis_method(self, *args, **kwargs):
        """Internal method to simulate axis behavior."""
        return super().axis(*args, **kwargs)

def test_issue_reproduction():
    """
    Test that reproduces the issue with AxesGrid and custom axis class.

    This test should FAIL on the buggy version and PASS on the fixed version.
    """
    try:
        fig = plt.figure()
        axes_class = (CustomAxes, {})
        gr = AxesGrid(fig, 111, nrows_ncols=(1, 1),
                      axes_class=axes_class)

        # If we get here without exception, the issue is fixed
        print("Test passed - issue is fixed")
        plt.close(fig)
        return True

    except TypeError as e:
        if "'method' object is not subscriptable" in str(e):
            print(f"Test failed (as expected on buggy version): {e}")
            return False
        else:
            print(f"Unexpected TypeError: {e}")
            raise
    except Exception as e:
        print(f"Unexpected exception: {e}")
        raise

if __name__ == "__main__":
    success = test_issue_reproduction()
    if not success:
        # Exit with non-zero code to indicate failure
        exit(1)