#!/usr/bin/env python3
"""
Test to reproduce the issue with mathematica_code giving wrong output with Max.

The issue: mathematica_code(Max(x,2)) outputs 'Max(2, x)' instead of 'Max[2, x]'
Expected: 'Max[2, x]' (valid Mathematica code with square brackets)
Actual (buggy): 'Max(2, x)' (invalid Mathematica code with parentheses)
"""

from sympy import symbols, Max, Min, mathematica_code

def test_max_output():
    """Test that Max outputs correct Mathematica code with square brackets."""
    x = symbols('x')
    result = mathematica_code(Max(x, 2))
    expected = "Max[2, x]"  # Max sorts its arguments, so order is (2, x)

    print(f"Result: {result}")
    print(f"Expected: {expected}")

    # This assertion will fail on buggy code, pass on fixed code
    assert result == expected, f"Expected '{expected}', got '{result}'"

    print("Test passed - Max outputs correct Mathematica code")

def test_min_output():
    """Test that Min outputs correct Mathematica code with square brackets."""
    x = symbols('x')
    result = mathematica_code(Min(x, 2))
    expected = "Min[2, x]"  # Min sorts its arguments, so order is (2, x)

    print(f"Result: {result}")
    print(f"Expected: {expected}")

    # This assertion will fail on buggy code, pass on fixed code
    assert result == expected, f"Expected '{expected}', got '{result}'"

    print("Test passed - Min outputs correct Mathematica code")

if __name__ == "__main__":
    print("Testing Max output...")
    test_max_output()
    print("\nTesting Min output...")
    test_min_output()
    print("\nAll tests passed!")