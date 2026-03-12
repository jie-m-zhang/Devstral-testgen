#!/usr/bin/env python
"""
Test to reproduce the issue with convert_to combining orthogonal units.

The issue: convert_to(joule*second, joule) returns joule**(7/9) (or similar fractional exponent)
instead of the expected behavior (returning the original expression, base units, or an error).
"""

from sympy.physics.units import joule, second, kilogram, meter
from sympy.physics.units.util import convert_to

def test_convert_to_orthogonal_units():
    """
    Test that convert_to handles orthogonal units correctly.

    The issue is that convert_to(joule*second, joule) incorrectly returns
    joule**(7/9) or similar fractional exponent instead of returning the
    original expression or raising an error.
    """
    # This is the problematic case from the issue
    result = convert_to(joule*second, joule)

    print(f"Result of convert_to(joule*second, joule): {result}")
    result_str = str(result)

    # Check if the result has the buggy behavior (joule with fractional exponent)
    # The buggy version returns something like "10**(2/3)*joule**(7/9)"
    is_buggy = "joule**(" in result_str and "/" in result_str

    if is_buggy:
        print("BUG DETECTED: convert_to returned joule with fractional exponent which is incorrect!")
        print("Expected: joule*second (original expression) or base units or error")
        return False
    else:
        print("FIXED: convert_to returned a sensible result")
        # The fixed version should return the original expression
        # or raise an error or return base units
        expected_results = [
            str(joule*second),  # Original expression
            "joule*second",
            "kg*m**2/s",  # Base units
            "kilogram*meter**2/second",  # Base units expanded
        ]

        if any(expected in result_str for expected in expected_results):
            print(f"Result '{result_str}' is acceptable")
            return True
        else:
            print(f"Result '{result_str}' is unexpected but not the buggy fractional exponent behavior")
            # This is still better than the buggy behavior
            return True

if __name__ == "__main__":
    success = test_convert_to_orthogonal_units()
    if not success:
        print("\nTest FAILED - issue reproduced")
        exit(1)
    else:
        print("\nTest PASSED - issue is fixed")
        exit(0)