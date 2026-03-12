#!/usr/bin/env python
"""
Test to reproduce the issue where uniq doesn't detect when the input sequence
is modified during iteration.

The issue states that when you iterate over a list and modify it during iteration,
the output will be silently wrong. The fix should raise a RuntimeError when this happens.
"""

from sympy.utilities.iterables import uniq

def test_uniq_modification_detection():
    """
    Test that uniq raises RuntimeError when the input sequence is modified during iteration.

    This test reproduces the issue described in the GitHub issue where modifying
    a list during iteration over uniq() produces incorrect results without warning.
    """
    # Create a list
    f = list('THISTLE')

    # Try to iterate over uniq(f) while modifying f
    # This should raise a RuntimeError in the fixed version
    try:
        result = []
        for i in uniq(f):
            f.remove(i)
            result.append(i)
        
        # If we get here without an exception, the bug is present
        # The result should be wrong because we modified the list during iteration
        print(f"Result: {result}")
        print("ERROR: No RuntimeError was raised - the bug is present!")
        return False
    except RuntimeError as e:
        # This is the expected behavior in the fixed version
        print(f"SUCCESS: RuntimeError was raised as expected: {e}")
        return True

if __name__ == "__main__":
    success = test_uniq_modification_detection()
    if not success:
        # Exit with non-zero code to indicate failure (bug is present)
        exit(1)
    else:
        # Exit with zero code to indicate success (bug is fixed)
        exit(0)