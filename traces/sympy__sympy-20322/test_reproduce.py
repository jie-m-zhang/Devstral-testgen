#!/usr/bin/env python
"""
Test to reproduce the inconsistent behavior for sympify/simplify with ceiling.

The issue: In sympy v1.6.2, sympify with evaluate=False produces different
results after simplify() compared to evaluate=True, which is inconsistent.
"""

import sympy

def test_ceiling_consistency():
    """Test that sympify with evaluate=False and evaluate=True produce consistent results after simplify()."""
    x = sympy.symbols('x')

    # Test with evaluate=False
    expr_false = sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=False)
    result_false = expr_false.simplify()

    # Test with evaluate=True
    expr_true = sympy.sympify('4*ceiling(x/4 - 3/4)', evaluate=True)
    result_true = expr_true.simplify()

    print(f"evaluate=False result: {result_false}")
    print(f"evaluate=True result: {result_true}")

    # The results should be the same for consistent behavior
    assert result_false == result_true, (
        f"Inconsistent behavior detected!\n"
        f"  evaluate=False: {result_false}\n"
        f"  evaluate=True:  {result_true}\n"
        f"These should be equal for consistent behavior."
    )

    print("Test passed - behavior is consistent")

if __name__ == "__main__":
    test_ceiling_consistency()