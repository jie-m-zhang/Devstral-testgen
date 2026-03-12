#!/usr/bin/env python
"""
Test to reproduce the issue with sympify and evaluate(False) context manager
with Point2D.

The issue is that with evaluate(False) context manager, sympify crashes with
"Imaginary coordinates are not permitted." error when parsing Point2D.
"""

import sympy as sp
import sys

def test_issue_reproduction():
    """
    Test that reproduces the issue with evaluate(False) and Point2D.

    This test should:
    - FAIL on base commit (3ff4717b6a) with ValueError
    - PASS on head commit (fd40404e7) without error
    """
    print("Testing sympify with evaluate(False) context manager...")

    # This should crash on base commit with "Imaginary coordinates are not permitted."
    try:
        with sp.evaluate(False):
            result = sp.S('Point2D(Integer(1),Integer(2))')
        print(f"SUCCESS: Result = {result}")
        return True
    except ValueError as e:
        print(f"FAILED: ValueError occurred: {e}")
        return False
    except Exception as e:
        print(f"FAILED: Unexpected error: {type(e).__name__}: {e}")
        return False

def test_working_cases():
    """
    Test the cases that should work (for comparison).
    These should work on both commits.
    """
    print("\nTesting working cases...")

    # Test 1: Without evaluate(False) context manager
    try:
        result1 = sp.S('Point2D(Integer(1),Integer(2))')
        print(f"Test 1 (no evaluate): SUCCESS - {result1}")
    except Exception as e:
        print(f"Test 1 (no evaluate): FAILED - {type(e).__name__}: {e}")
        return False

    # Test 2: With evaluate=False parameter
    try:
        result2 = sp.S('Point2D(Integer(1),Integer(2))', evaluate=False)
        print(f"Test 2 (evaluate=False param): SUCCESS - {result2}")
    except Exception as e:
        print(f"Test 2 (evaluate=False param): FAILED - {type(e).__name__}: {e}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing issue: sympify with evaluate(False) and Point2D")
    print("=" * 60)

    # Test the working cases first
    working = test_working_cases()

    # Test the issue reproduction
    issue_fixed = test_issue_reproduction()

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Working cases: {'PASS' if working else 'FAIL'}")
    print(f"Issue test: {'PASS' if issue_fixed else 'FAIL'}")
    print("=" * 60)

    # Exit with appropriate code
    # On base commit: issue_fixed should be False (FAIL)
    # On head commit: issue_fixed should be True (PASS)
    if not issue_fixed:
        print("\nTest FAILED as expected on base commit (issue reproduced)")
        sys.exit(1)
    else:
        print("\nTest PASSED (issue is fixed)")
        sys.exit(0)