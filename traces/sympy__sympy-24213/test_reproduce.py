"""
Test to reproduce the issue with collect_factor_and_dimension not detecting equivalent dimensions in addition.

The issue is that when adding quantities with equivalent dimensions (like velocity and acceleration*time),
the method raises a ValueError instead of recognizing they are equivalent.
"""

from sympy.physics import units
from sympy.physics.units.systems.si import SI

def test_equivalent_dimensions_in_addition():
    """
    Test that _collect_factor_and_dimension correctly handles equivalent dimensions in addition.

    This test reproduces the issue where:
    - v1 has dimension velocity
    - a1*t1 has dimension acceleration*time, which is equivalent to velocity
    - The expression a1*t1 + v1 should be valid since both terms have equivalent dimensions
    """

    # Create quantities
    v1 = units.Quantity('v1')
    SI.set_quantity_dimension(v1, units.velocity)
    SI.set_quantity_scale_factor(v1, 2 * units.meter / units.second)

    a1 = units.Quantity('a1')
    SI.set_quantity_dimension(a1, units.acceleration)
    SI.set_quantity_scale_factor(a1, -9.8 * units.meter / units.second**2)

    t1 = units.Quantity('t1')
    SI.set_quantity_dimension(t1, units.time)
    SI.set_quantity_scale_factor(t1, 5 * units.second)

    # Create expression: a1*t1 + v1
    # This should be valid because:
    # - a1*t1 has dimension acceleration*time = velocity
    # - v1 has dimension velocity
    # So both terms have equivalent dimensions
    expr1 = a1*t1 + v1

    # This should not raise an error
    # On buggy version: raises ValueError about dimension mismatch
    # On fixed version: works correctly
    try:
        result = SI._collect_factor_and_dimension(expr1)
        print("Test passed - issue is fixed")
        print(f"Result: {result}")
        return True
    except ValueError as e:
        print(f"Test failed - issue reproduced: {e}")
        return False

if __name__ == "__main__":
    success = test_equivalent_dimensions_in_addition()
    if not success:
        exit(1)
    else:
        exit(0)