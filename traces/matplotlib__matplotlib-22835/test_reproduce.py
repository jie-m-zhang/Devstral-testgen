import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import BoundaryNorm

def test_boundary_norm_format_cursor_data():
    """
    Test that format_cursor_data works with BoundaryNorm.

    This test reproduces the issue where calling format_cursor_data on a
    ScalarMappable with BoundaryNorm would crash with:
    ValueError: BoundaryNorm is not invertible
    """
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Create a BoundaryNorm
    boundaries = np.linspace(-4, 4, 5)
    norm = BoundaryNorm(boundaries, 256)

    # Create an image with BoundaryNorm
    X = np.random.randn(10, 10)
    pc = ax.imshow(X, cmap='RdBu_r', norm=norm)

    # Try to format cursor data - this should crash on base commit
    # but work on head commit
    try:
        result = pc.format_cursor_data(0.5)
        print(f"Test passed - result: {result}")
        return True
    except ValueError as e:
        if "BoundaryNorm is not invertible" in str(e):
            print(f"Test failed with expected error: {e}")
            return False
        else:
            # Unexpected error
            print(f"Test failed with unexpected error: {e}")
            raise

if __name__ == "__main__":
    success = test_boundary_norm_format_cursor_data()
    if not success:
        exit(1)
    else:
        exit(0)