#!/usr/bin/env python
"""
Test to reproduce the issue where 'Poly3DCollection' object has no attribute '_facecolors2d'
when calling get_facecolors() on a plot_surface result.

This test should:
- FAIL on base commit (29a86636a9c45ab5ac4d80ac76eaee497f460dce) with AttributeError
- PASS on head commit (de98877e3dc45de8dd441d008f23d88738dc015d) without error
"""

import numpy as np
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def test_issue_reproduction():
    """Test that get_facecolors() works on Poly3DCollection from plot_surface."""
    # Create test data
    y, x = np.ogrid[1:10:100j, 1:10:100j]
    z2 = np.cos(x)**3 - np.sin(y)**2

    # Create figure and plot surface
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    r = ax.plot_surface(x, y, z2, cmap='hot')

    # This should fail on base commit with AttributeError
    # and pass on head commit after the fix
    facecolors = r.get_facecolors()

    # Basic assertion to verify we got a result
    assert facecolors is not None, "get_facecolors() returned None"
    assert hasattr(facecolors, '__len__'), "get_facecolors() did not return an array-like object"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()