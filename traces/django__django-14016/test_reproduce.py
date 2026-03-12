#!/usr/bin/env python
"""
Test to reproduce the issue with Q objects and non-pickleable types.

The issue is that using the | operator on Q objects containing non-pickleable
types like dict_keys fails with a TypeError.
"""

from django.db.models import Q

def test_q_object_pickleable_issue():
    """
    Test that Q objects with non-pickleable types work with | operator.

    This test should FAIL on the base commit (1710cdbe79) with:
    TypeError: cannot pickle 'dict_keys' object

    This test should PASS on the head commit (475cffd1d6) after the fix.
    """
    # Create a Q object with dict_keys (non-pickleable)
    q1 = Q(x__in={}.keys())
    print(f"Created Q object: {q1}")

    # Create an empty Q object
    q2 = Q()
    print(f"Created empty Q object: {q2}")

    # Try to combine them with | operator - this should fail on base commit
    try:
        result = q2 | q1
        print(f"Successfully combined Q objects: {result}")
        print("Test PASSED - issue is fixed")
    except TypeError as e:
        print(f"Test FAILED with TypeError: {e}")
        print("This is expected on the base commit (buggy version)")
        raise

if __name__ == "__main__":
    test_q_object_pickleable_issue()