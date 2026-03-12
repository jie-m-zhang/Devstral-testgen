#!/usr/bin/env python3
"""
Test to reproduce the issue with printing of Pow expressions in denominators.

The issue is that when we have a Pow with exponent -1 whose base is itself a Pow,
the string representation should add parentheses around the base to avoid ambiguity.

For example: x / (y**(-1)) should be printed as x/(y**(-1)) or x/(1/y), not x/1/y

The patch fixes this by adding Pow to the condition that checks when to add
parentheses around terms in the denominator.
"""

from sympy import symbols, Pow, Mul

def test_issue_reproduction():
    x, y = symbols('x y')

    # Create an expression: x / (y**(-1))
    # This is: x * (y**(-1))**(-1) = x * y
    # But we want to test the printing of the unevaluated form

    # Create the expression without simplification
    # The denominator is Pow(y, -1), and we're raising it to -1
    # So we have: x * Pow(Pow(y, -1, evaluate=False), -1, evaluate=False)
    # This should print as x/(1/y) with parentheses, not x/1/y

    expr = Mul(x, Pow(Pow(y, -1, evaluate=False), -1, evaluate=False), evaluate=False)

    result = str(expr)
    expected = "x/(1/y)"  # SymPy simplifies y**(-1) to 1/y

    print(f"Expression: {expr}")
    print(f"Result: {result}")
    print(f"Expected: {expected}")

    # This assertion will fail on buggy code (gives x/1/y), pass on fixed code (gives x/(1/y))
    assert result == expected, f"Expected '{expected}', got '{result}'"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()