#!/usr/bin/env python
"""
Test to reproduce the issue with apart() function.

The issue is that when calling apart(t) on an expression with symbol 'a',
it incorrectly returns -a*t instead of the proper partial fraction decomposition.

Expected behavior:
- bug.apart(t) should return a proper partial fraction decomposition
- bug.subs(a, 1).apart(t) returns: -t + 1/2 - 1/(2*(2*t - 1))

The bug was that apart(t) was returning just -a*t, missing the other terms.
"""

from sympy import symbols, simplify

def test_issue_reproduction():
    # Create symbols as described in the issue
    a = symbols('a', real=True)
    t = symbols('t', real=True, negative=False)

    # Create the expression from the issue
    bug = a * (-t + (-t + 1) * (2 * t - 1)) / (2 * t - 1)

    # Get the result of apart(t) on the expression with 'a'
    result = bug.apart(t)

    # The buggy result (what the buggy version returns)
    buggy_result = -a*t

    print("Expression:")
    print(bug)
    print("\nResult of bug.apart(t):")
    print(result)
    print("\nBuggy result:")
    print(buggy_result)

    # Test assertion: result should NOT be equal to the buggy result
    # The buggy version returns just -a*t, which is incorrect
    # The fixed version should return a proper partial fraction decomposition
    assert result != buggy_result, f"apart(t) incorrectly returned {result} which equals the buggy result {buggy_result}"

    # Additional check: the result should be a proper partial fraction decomposition
    # When we substitute a=1, we should get the same result as bug.subs(a, 1).apart(t)
    expected_when_a_1 = bug.subs(a, 1).apart(t)
    result_when_a_1 = result.subs(a, 1)

    print("\nExpected when a=1:")
    print(expected_when_a_1)
    print("\nResult when a=1:")
    print(result_when_a_1)

    # These should be equal (or simplify to be equal)
    assert simplify(result_when_a_1 - expected_when_a_1) == 0, \
        f"Result doesn't match expected when a=1. Got {result_when_a_1}, expected {expected_when_a_1}"

    print("\nTest passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()