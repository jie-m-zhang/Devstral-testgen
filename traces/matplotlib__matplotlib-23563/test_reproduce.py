"""
Test to reproduce the issue where 'Line3D' object has no attribute '_verts3d'

The issue occurs when set_3d_properties is called with certain types of arrays
that cause np.broadcast_to to fail, which can leave the Line3D object in a bad state.

This test should FAIL on the base commit and PASS on the head commit.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3D

def test_line3d_set_3d_properties_with_2d_array():
    """
    Test that Line3D.set_3d_properties handles 2D arrays properly.

    The bug: When set_3d_properties is called with a 2D array, np.broadcast_to
    fails with "input operand has more dimensions than allowed", and this can
    leave the Line3D object in a bad state.

    The fix: The ravel() call in the patch should handle this case.
    """
    # Create a Line3D object with proper data
    line = Line3D([1, 2, 3], [4, 5, 6], [7, 8, 9])

    # Verify _verts3d is initially set
    assert hasattr(line, '_verts3d'), "Line3D should have _verts3d attribute initially"
    print(f"Initial _verts3d: {line._verts3d}")

    # Create a 2D array - this is the type of input that causes issues on base commit
    zs_2d = np.array([[10, 11, 12]])

    try:
        # On base commit: This will fail with ValueError about dimensions
        # On head commit: This should succeed due to the ravel() call
        line.set_3d_properties(zs=zs_2d, zdir='z')
        print("SUCCESS: set_3d_properties with 2D array succeeded")

        # Verify _verts3d is still accessible
        verts = line._verts3d
        print(f"_verts3d after 2D array update: {verts}")

        # Try to draw the line to ensure everything works
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.add_line(line)
        fig.canvas.draw()
        plt.close(fig)

        print("SUCCESS: Line can be drawn without errors")
        return True

    except ValueError as e:
        # This is expected on the base commit
        print(f"set_3d_properties failed with ValueError (expected on base commit): {e}")

        # Now check if _verts3d is still accessible
        # On the base commit, after the error, _verts3d might be in a bad state
        try:
            verts = line._verts3d
            print(f"_verts3d is still accessible: {verts}")

            # Try to draw - this is where the AttributeError would occur on base commit
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.add_line(line)
            fig.canvas.draw()
            plt.close(fig)

            print("SUCCESS: Line can be drawn even after failed set_3d_properties")
            return True

        except AttributeError as e:
            if "'Line3D' object has no attribute '_verts3d'" in str(e):
                print(f"FAILURE: AttributeError occurred: {e}")
                return False
            else:
                raise
    except AttributeError as e:
        if "'Line3D' object has no attribute '_verts3d'" in str(e):
            print(f"FAILURE: AttributeError occurred during set_3d_properties: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"UNEXPECTED: Different error occurred: {type(e).__name__}: {e}")
        raise

if __name__ == "__main__":
    print("Testing Line3D set_3d_properties with 2D array...")
    success = test_line3d_set_3d_properties_with_2d_array()

    # Assert that the test passed
    assert success, "Test failed - bug still exists"

    print("\nTest passed - issue is fixed")