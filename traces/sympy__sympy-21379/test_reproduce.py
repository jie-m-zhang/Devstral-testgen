from sympy import *
from sympy.core.cache import clear_cache

def test_issue_reproduction():
    """
    Test for unexpected PolynomialError when using subs() for particular expressions.
    This test reproduces the issue described in the GitHub issue.
    """
    # Clear cache to ensure consistent behavior
    clear_cache()

    # Create symbols with real=True (this is critical for the bug)
    x, y, z = symbols('x y z', real=True)

    # Create the problematic expression
    expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))

    # This should not raise PolynomialError
    # The bug occurs on the first call to subs after cache is cleared
    try:
        result = expr.subs({1: 1.0})
        # If we get here, the test passes (no exception)
        print("Test passed - no PolynomialError raised")
        return True
    except PolynomialError as e:
        # If we get here, the bug is present
        print(f"Test failed - PolynomialError raised: {e}")
        return False

if __name__ == "__main__":
    success = test_issue_reproduction()
    if not success:
        # Exit with non-zero code to indicate failure
        exit(1)
    else:
        # Exit with zero code to indicate success
        exit(0)