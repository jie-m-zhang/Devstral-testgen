"""
Test to reproduce the boolean color mapping issue.

The issue occurs when using boolean data for color mapping in seaborn Plot.
It should fail on the base commit and pass on the head commit.

Base commit (buggy): 4a9e54962a29c12a8b103d75f838e0e795a6974d
Head commit (fixed): 72710354ecc8470683e15f452ba0af841464e84a
"""

import numpy as np
import seaborn.objects as so

def test_boolean_color_mapping():
    """
    Test that boolean color mapping works correctly.

    This test reproduces the issue where using boolean data for color
    causes a TypeError in the scale setup when computing:
        b = forward(vmax) - forward(vmin)

    The fix converts vmin, vmax to float using map(float, ...) before
    the subtraction operation.
    """
    # Create a simple plot with boolean color data
    # This should fail on the base commit with TypeError about numpy boolean subtract
    p = so.Plot(["a", "b"], [1, 2], color=[True, False]).add(so.Bar())
    
    try:
        # Try to plot it - this is where the error occurs in _setup_scales
        result = p.plot()
        # If we get here, the plot was successful
        print("Plot created successfully")
        return True
    except Exception as e:
        # Check if it's the specific error we're looking for
        error_msg = str(e)
        cause_msg = str(getattr(e, '__cause__', ''))

        # Check both the main error and the cause
        all_msgs = error_msg + " " + cause_msg
        if "numpy boolean subtract" in all_msgs or ("boolean" in all_msgs.lower() and "subtract" in all_msgs.lower()):
            print(f"Expected error occurred: {e}")
            return False

        # Some other error - re-raise it
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    # Run the test
    success = test_boolean_color_mapping()
    
    if success:
        print("Test PASSED - boolean color mapping works")
        exit(0)
    else:
        print("Test FAILED - boolean color mapping issue reproduced")
        exit(1)