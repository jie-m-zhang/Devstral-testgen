"""
Test to reproduce the RecursionError when checking is_zero of cosh expression.

Issue: Bug: maximum recursion depth error when checking is_zero of cosh expression
The expression cosh(acos(-i + acosh(-g + i))) causes a RecursionError when
checking if it is zero.

This test should:
- FAIL on base commit (126f805781) with RecursionError
- PASS on head commit (f9a6f50ec0) without error
"""

from sympy import sympify, symbols

def test_cosh_is_zero_recursion_error():
    """Test that checking is_zero on cosh expression doesn't cause RecursionError."""
    # Create the problematic expression
    expr = sympify("cosh(acos(-i + acosh(-g + i)))")

    # This should not raise a RecursionError
    # On base commit: will raise RecursionError
    # On head commit: will return None or False (can't determine if zero)
    try:
        result = expr.is_zero
        # If we get here, the bug is fixed
        # The result can be None (unknown) or False (not zero)
        # Both are acceptable - the important thing is no RecursionError
        print(f"Test passed - no RecursionError, is_zero = {result}")
        return True
    except RecursionError as e:
        # This is the bug - should not happen on fixed version
        print(f"Test failed - RecursionError occurred: {e}")
        raise AssertionError("RecursionError occurred when checking is_zero") from e

if __name__ == "__main__":
    test_cosh_is_zero_recursion_error()