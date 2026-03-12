#!/usr/bin/env python
"""
Test to reproduce the issue where 0**-oo produces 0 instead of zoo (ComplexInfinity).

This test should:
- FAIL on base commit (a106f4782a9dbe7f8fd16030f15401d977e03ae9) - exit code != 0
- PASS on head commit (cffd4e0f86fefd4802349a9f9b19ed70934ea354) - exit code = 0
"""

from sympy import S, oo

def test_issue_reproduction():
    """
    Test that 0**-oo returns zoo (ComplexInfinity) as documented.

    According to the documentation for the Pow class:
    | expr | value | reason |
    | :-- | :-- | :--|
    | `0**-oo` | `zoo` | This is not strictly true, as 0**oo may be oscillating between positive and negative values or rotating in the complex plane. It is convenient, however, when the base is positive.|
    """
    # Code to reproduce the issue
    result = S.Zero**-oo

    # This assertion will fail on buggy code (base commit), pass on fixed code (head commit)
    # On base commit: result = 0
    # On head commit: result = zoo (ComplexInfinity)
    assert result == S.ComplexInfinity, f"Expected 'zoo' (ComplexInfinity), got '{result}'"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()