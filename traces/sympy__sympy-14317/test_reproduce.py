#!/usr/bin/env python
"""
Test to reproduce the issue where LaTeX printer does not use the same order of monomials as pretty and str.

The issue: When printing a Poly, str and pretty printers use logical order (highest to lowest degrees),
but latex printer does not maintain this order.

Expected behavior: All printers should show monomials in the same order from highest to lowest degrees.
"""

from sympy import Poly, var
from sympy.printing.latex import latex
from sympy.printing.pretty.pretty import pretty

def test_latex_monomial_order():
    """Test that latex printer uses the same monomial order as str and pretty."""
    # Create variables and polynomial as shown in the issue
    var('a b c x')
    p = Poly([a, 1, b, 2, c, 3], x)

    # Get the string representation (correct order)
    str_repr = str(p)
    print(f"str(p): {str_repr}")

    # Get the pretty representation (correct order)
    pretty_repr = pretty(p)
    print(f"pretty(p): {pretty_repr}")

    # Get the latex representation
    latex_repr = latex(p)
    print(f"latex(p): {latex_repr}")

    # The expected order is: a x^5, x^4, b x^3, 2 x^2, c x, 3
    # In the buggy version, latex shows: a x^{5} + b x^{3} + c x + x^{4} + 2 x^{2} + 3
    # In the fixed version, latex should show: a x^{5} + x^{4} + b x^{3} + 2 x^{2} + c x + 3

    # Check that the latex representation has terms in the correct order
    # We'll look for the pattern where x^4 comes AFTER a x^5 but BEFORE b x^3
    # In the buggy version, x^4 comes AFTER b x^3, which is wrong

    # Find positions of key terms in the latex string
    a_x5_pos = latex_repr.find('a x^{5}')
    x4_pos = latex_repr.find('x^{4}')
    b_x3_pos = latex_repr.find('b x^{3}')

    print(f"Position of 'a x^{5}': {a_x5_pos}")
    print(f"Position of 'x^{4}': {x4_pos}")
    print(f"Position of 'b x^{3}': {b_x3_pos}")

    # All terms should be found
    assert a_x5_pos != -1, "Could not find 'a x^{5}' in latex output"
    assert x4_pos != -1, "Could not find 'x^{4}' in latex output"
    assert b_x3_pos != -1, "Could not find 'b x^{3}' in latex output"

    # The correct order should be: a_x5_pos < x4_pos < b_x3_pos
    # In the buggy version, we have: a_x5_pos < b_x3_pos < x4_pos (wrong!)

    print(f"Order check: a_x5_pos ({a_x5_pos}) < x4_pos ({x4_pos}) < b_x3_pos ({b_x3_pos})")

    # This assertion will fail on the buggy version because x4 comes after b_x3
    assert a_x5_pos < x4_pos < b_x3_pos, \
        f"Terms are not in correct order. Expected: a x^5 < x^4 < b x^3, but got positions: {a_x5_pos} < {x4_pos} < {b_x3_pos}"

    print("✓ All terms are in the correct order (highest to lowest degree)")

if __name__ == "__main__":
    test_latex_monomial_order()