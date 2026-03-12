#!/usr/bin/env python
"""
Test to reproduce the issue where SI._collect_factor_and_dimension()
cannot properly detect that exponent is dimensionless.

This test should:
- FAIL on base commit (514579c655bf22e2af14f0743376ae1d7befe345)
- PASS on head commit (c6cb7c5602fa48034ab1bd43c2347a7e8488f12e)
"""

from sympy import exp
from sympy.physics import units
from sympy.physics.units.systems.si import SI

def test_issue_reproduction():
    # First, test that the basic expression is dimensionless
    expr = units.second / (units.ohm * units.farad)
    factor, dim = SI._collect_factor_and_dimension(expr)

    # This should pass - the expression is dimensionless
    assert SI.get_dimension_system().is_dimensionless(dim), \
        f"Expected dimensionless, but got {dim}"

    # Now test the buggy case with exp()
    # On base commit, this should raise ValueError
    # On head commit, this should work fine
    buggy_expr = 100 + exp(expr)
    try:
        factor2, dim2 = SI._collect_factor_and_dimension(buggy_expr)
        # If we get here, the fix is working
        print("Test passed - issue is fixed")
    except ValueError as e:
        # This is expected on the base commit
        print(f"Test failed (as expected on base commit): {e}")
        raise

if __name__ == "__main__":
    test_issue_reproduction()