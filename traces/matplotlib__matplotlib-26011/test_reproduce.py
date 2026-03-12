"""
Test to reproduce the issue where xlim_changed callbacks are not emitted on shared axes.

The issue is that when an axis is shared with another, its registered "xlim_changed"
callbacks do not get called when the change is induced by a shared axis.
"""

import matplotlib.pyplot as plt

def test_shared_axis_xlim_changed_callback():
    """
    Test that xlim_changed callbacks are emitted on shared axes.

    This test creates two axes that share an x-axis, registers a callback
    on the second axis, and then changes the xlim on the first axis. The
    callback should be triggered on the second axis as well.
    """
    # Create a figure with two subplots sharing the x-axis
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # Track whether the callback was called
    callback_called = False

    def on_xlim_changed(axes):
        nonlocal callback_called
        callback_called = True
        print(f"Callback called on axes: {axes}")

    # Register the callback on the second axis
    cid = ax2.callbacks.connect('xlim_changed', on_xlim_changed)

    # Change the xlim on the first axis - this should trigger the callback
    # on the second axis as well since they share the x-axis
    ax1.set_xlim(0, 10)

    # Check if the callback was called
    assert callback_called, "Callback was not called on shared axis when xlim was changed"

    # Clean up
    ax2.callbacks.disconnect(cid)
    plt.close(fig)

    print("Test passed - callback was called on shared axis")

if __name__ == "__main__":
    test_shared_axis_xlim_changed_callback()