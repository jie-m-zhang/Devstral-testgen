"""
Test to reproduce the issue where Axis.set_ticks only validates kwargs if ticklabels are set.

The issue is that when calling set_xticks with kwargs but without labels,
the kwargs are silently ignored instead of raising an error.

This test should:
- FAIL on the base commit (buggy version) - no error is raised
- PASS on the head commit (fixed version) - ValueError is raised
"""

import matplotlib.pyplot as plt
import matplotlib.axes as maxes

def test_set_ticks_with_kwargs_no_labels():
    """
    Test that set_ticks raises ValueError when kwargs are passed without labels.

    This reproduces the issue described in the GitHub issue where kwargs
    are silently ignored when labels is None.
    """
    # Create a simple figure and axis
    fig, ax = plt.subplots()

    # Try to call set_xticks with kwargs but without labels
    # According to the docstring, kwargs should only take effect if labels are passed
    # So this should raise an error
    try:
        ax.set_xticks([0, 1], fontsize=12)  # fontsize is a Text property
        # If we get here, no error was raised (buggy behavior)
        print("ERROR: No exception was raised - this is the buggy behavior")
        return False
    except ValueError as e:
        # This is the expected behavior after the fix
        print(f"SUCCESS: ValueError was raised as expected: {e}")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected exception: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = test_set_ticks_with_kwargs_no_labels()
    if result:
        print("\nTest PASSED - issue is fixed")
        exit(0)
    else:
        print("\nTest FAILED - issue still exists")
        exit(1)