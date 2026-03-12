#!/usr/bin/env python
"""
Test to reproduce the issue where Point.vel() should calculate velocity if possible.

The issue is that when you specify the position of two points and then ask for
the velocity between them, it should calculate the velocity (like it does for
orientations with ang_vel_in), but currently raises a ValueError.
"""

import sympy as sm
import sympy.physics.mechanics as me

def test_point_vel_calculation():
    """Test that Point.vel() calculates velocity when possible."""
    # Create a reference frame
    A = me.ReferenceFrame('A')

    # Create a dynamicsymbol
    q = me.dynamicsymbols('q')

    # Create two points
    P = me.Point('P')
    Q = me.Point('Q')

    # Set the velocity of P in frame A (needed for the calculation)
    P.set_vel(A, 0)  # P is stationary in frame A

    # Set the position of Q relative to P
    r = q * A.x + 2 * q * A.y
    Q.set_pos(P, r)

    # This should work and calculate the velocity
    # Currently raises ValueError on base commit
    try:
        result = Q.vel(A)
        # If we get here, the fix is working
        # The result should be the time derivative of r
        expected = r.dt(A)
        assert result == expected, f"Expected {expected}, got {result}"
        print("Test passed - velocity calculated correctly")
        return True
    except ValueError as e:
        print(f"Test failed with ValueError: {e}")
        return False

if __name__ == "__main__":
    success = test_point_vel_calculation()
    if not success:
        exit(1)
    else:
        exit(0)