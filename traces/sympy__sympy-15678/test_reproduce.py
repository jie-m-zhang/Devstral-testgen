#!/usr/bin/env python
"""
Test to reproduce the idiff issues described in the GitHub issue.

The test should:
1. FAIL on base commit (31c68eef3ffef39e2e792b0ec92cd92b7010eb2a) - reproducing the issue
2. PASS on head commit (73b3f90093754c5ed1561bd885242330e3583004) - showing the issue is fixed

Issue to test:
- idiff doesn't support f(x) instead of y - raises ValueError
"""

from sympy import symbols, Function, exp
from sympy.geometry.util import idiff

def test_idiff_with_function():
    """Test that idiff works with Function objects like f(x)."""
    x = symbols('x')
    f = Function('f')
    # This should work but raises ValueError on base commit
    result = idiff(f(x)*exp(f(x)) - x*exp(x), f(x), x)
    # Expected result should be a derivative expression
    assert result is not None, "idiff with Function should not raise an exception"
    print(f"✓ idiff with Function works: {result}")

def test_idiff_with_expression():
    """Test that idiff still works with regular expressions (regression test)."""
    x, y = symbols('x y')
    # This should work on both commits
    result = idiff(y*exp(y) - x*exp(x), y, x)
    expected = (x + 1)*exp(x - y)/(y + 1)
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"✓ idiff with expression works: {result}")

def test_issue_reproduction():
    """Main test function that runs all tests."""
    print("Testing idiff issues...")

    # Test 1: Function support
    try:
        test_idiff_with_function()
        print("✓ Test 1 PASSED: idiff with Function works")
    except ValueError as e:
        print(f"✗ Test 1 FAILED: idiff with Function raised ValueError: {e}")
        raise
    except Exception as e:
        print(f"✗ Test 1 FAILED: idiff with Function raised unexpected exception: {e}")
        raise

    # Test 2: Regular expression (should always work)
    try:
        test_idiff_with_expression()
        print("✓ Test 2 PASSED: idiff with expression works")
    except Exception as e:
        print(f"✗ Test 2 FAILED: idiff with expression raised exception: {e}")
        raise

    print("\nAll tests passed!")

if __name__ == "__main__":
    test_issue_reproduction()