"""
Test to reproduce the mplcursor + matplotlib 3.7.1 AttributeError issue.

The issue occurs when:
1. Using mplcursor with matplotlib
2. Clicking on data points multiple times
3. The ref_artist.figure becomes None
4. The disconnect method tries to access self.canvas which is now None

This test directly tests the DraggableBase class to reproduce the issue.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.offsetbox import DraggableBase
from matplotlib.backend_bases import MouseButton, MouseEvent, PickEvent

def test_draggable_base_disconnect_issue():
    """
    Test that reproduces the AttributeError when disconnecting DraggableBase.

    This should FAIL on the buggy version (base commit) with:
    AttributeError: 'NoneType' object has no attribute 'canvas'

    This should PASS on the fixed version (head commit) without errors.
    """
    # Create a figure and scatter plot
    fig, ax = plt.subplots()
    x = np.arange(1, 11)
    y = x
    scatter = ax.scatter(x, y, picker=True)

    # Create a draggable annotation (this uses DraggableBase internally)
    da = DrawingArea(20, 20, 0, 0)
    ab = AnnotationBbox(da, (0.5, 0.5), xycoords='data')
    ax.add_artist(ab)  # Add to axes so it has a figure

    # Create a DraggableBase directly
    draggable = DraggableBase(ab, use_blit=False)

    # Simulate a pick event to trigger the on_pick callback
    # This will connect the motion_notify_event callback
    mouse_event = MouseEvent(
        'button_press_event',
        fig.canvas,
        *ab.xy,  # Use the annotation position
        MouseButton.LEFT
    )

    pick_event = PickEvent(
        'pick_event',
        fig.canvas,
        mouse_event,
        ab  # Use the annotation box as the artist
    )

    # Manually call on_pick to simulate the pick event
    # This connects the motion_notify_event callback
    draggable.on_pick(pick_event)

    # Now simulate the problematic scenario:
    # Directly set ref_artist.figure to None to simulate the issue
    draggable.ref_artist.figure = None

    # This should trigger the AttributeError in the buggy version
    # because disconnect() tries to access self.canvas which is now None
    try:
        draggable.disconnect()
        print("Test PASSED - disconnect() succeeded without error")
        return True
    except AttributeError as e:
        if "'NoneType' object has no attribute 'canvas'" in str(e):
            print(f"Test FAILED - Got expected AttributeError: {e}")
            return False
        else:
            # Different AttributeError, re-raise it
            raise
    except Exception as e:
        print(f"Test FAILED - Got unexpected error: {e}")
        raise

if __name__ == "__main__":
    success = test_draggable_base_disconnect_issue()
    if not success:
        exit(1)
    else:
        exit(0)