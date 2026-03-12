"""
Test to reproduce the bug with milli prefix.

The issue is that milli*W evaluates to 1 instead of milli watts (mW).
This test should FAIL on the base commit and PASS on the head commit.
"""

from sympy.physics.units import milli, W
from sympy.physics.units.prefixes import Prefix

def test_milli_prefix_bug():
    """
    Test that milli*W produces milli watts, not 1.

    On the buggy version (base commit):
    - milli*W == 1 evaluates to True (WRONG!)
    - milli*W evaluates to 1 (WRONG!)

    On the fixed version (head commit):
    - milli*W should evaluate to a proper expression representing milli watts
    - milli*W should NOT equal 1
    """
    # Test 1: milli*W should NOT equal 1
    result = milli * W
    print(f"milli * W = {result}")
    print(f"type(milli * W) = {type(result)}")
    print(f"milli * W == 1: {result == 1}")

    # This assertion should FAIL on base commit (where result == 1)
    # and PASS on head commit (where result != 1)
    assert result != 1, f"Bug: milli*W evaluates to 1 instead of milli watts. Got: {result}"

    # Test 2: The result should not be an integer
    # On base commit it's int, on head commit it should be an expression
    assert not isinstance(result, int), f"Bug: milli*W evaluates to int {result} instead of an expression"

    # Test 3: Check that W*milli also works correctly
    result2 = W * milli
    print(f"W * milli = {result2}")
    print(f"type(W * milli) = {type(result2)}")
    assert result2 != 1, f"Bug: W*milli evaluates to 1 instead of milli watts. Got: {result2}"
    assert not isinstance(result2, int), f"Bug: W*milli evaluates to int {result2} instead of an expression"

    print("All tests passed! The milli prefix bug is fixed.")

if __name__ == "__main__":
    test_milli_prefix_bug()