"""Test to reproduce the issue where set_visible(False) doesn't work for 3D projection."""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.backend_bases

def test_3d_axes_set_visible():
    """Test that set_visible(False) works for 3D axes."""
    # Create a figure with 3D subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'projection': '3d'})

    # Add some data to both axes
    ax1.scatter([1], [1], [1])
    ax2.scatter([1], [1], [1], c='r')

    # Set the first axes to be invisible
    ax1.set_visible(False)

    # Create a mock renderer to test drawing behavior
    # We'll use the figure's renderer
    renderer = fig.canvas.get_renderer()

    # Track if draw was called by checking if any artists were drawn
    # We'll check the patch (background) of the axes
    patch1 = ax1.patch
    patch2 = ax2.patch

    # Store the original draw methods
    original_draw1 = patch1.draw
    original_draw2 = patch2.draw

    # Add counters to track if draw was called
    draw_count1 = [0]
    draw_count2 = [0]

    def counting_draw1(self, renderer):
        draw_count1[0] += 1
        return original_draw1(renderer)

    def counting_draw2(self, renderer):
        draw_count2[0] += 1
        return original_draw2(renderer)

    # Monkey patch the draw methods
    patch1.draw = lambda renderer: counting_draw1(patch1, renderer)
    patch2.draw = lambda renderer: counting_draw2(patch2, renderer)

    # Draw the axes
    ax1.draw(renderer)
    ax2.draw(renderer)

    # Restore original draw methods
    patch1.draw = original_draw1
    patch2.draw = original_draw2

    print(f"Invisible axes patch draw count: {draw_count1[0]}")
    print(f"Visible axes patch draw count: {draw_count2[0]}")

    # The invisible axes should NOT have its patch drawn
    # In the buggy version, draw_count1 will be > 0
    # In the fixed version, draw_count1 will be 0
    assert draw_count1[0] == 0, (
        f"Invisible axes patch was drawn {draw_count1[0]} times. "
        f"set_visible(False) is not working for 3D axes."
    )

    # The visible axes should have its patch drawn
    assert draw_count2[0] > 0, (
        f"Visible axes patch was drawn {draw_count2[0]} times. "
        f"Expected it to be drawn at least once."
    )

    plt.close(fig)
    print("Test passed - set_visible(False) works correctly for 3D axes")

if __name__ == "__main__":
    test_3d_axes_set_visible()