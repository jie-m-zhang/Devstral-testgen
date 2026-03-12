#!/usr/bin/env python
"""
Test to reproduce the Mathematica code printer issue with Derivative.

This test should:
- FAIL on base commit (ca6ef27272be31c9dc3753ede9232c39df9a75d8)
- PASS on head commit (50b81f9f6be151014501ffac44e5dc6b2416938f)
"""

from sympy import symbols, Function, Derivative, mathematica_code

def test_derivative_issue():
    """Test that Derivative is properly converted to D[...] in Mathematica code."""
    f = Function('f')
    t = symbols('t')

    # Test basic derivative
    result = mathematica_code(Derivative(f(t), t))
    expected = "Hold[D[f[t], t]]"
    assert result == expected, f"Expected '{expected}', got '{result}'"

    # Test derivative with multiple variables
    x, y = symbols('x y')
    g = Function('g')
    result2 = mathematica_code(Derivative(g(x, y), x, y))
    expected2 = "Hold[D[g[x, y], x, y]]"
    assert result2 == expected2, f"Expected '{expected2}', got '{result2}'"

    print("✓ Derivative test passed")

if __name__ == "__main__":
    print("Testing Mathematica code printer Derivative issue...")
    test_derivative_issue()
    print("\nTest passed - Derivative issue is fixed!")