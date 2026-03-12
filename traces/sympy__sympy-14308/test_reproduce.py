#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test to reproduce the vector pretty printing issue.
The issue is that vectors with fractional scalars break pretty printing,
showing the basis vector multiple times.
"""

from sympy.vector import CoordSysCartesian
from sympy.printing.pretty import pretty
from sympy.abc import x, y, t

def test_vector_pretty_printing_with_fraction():
    """Test that vector expressions with fractions are pretty printed correctly."""
    # Create coordinate system
    e = CoordSysCartesian('e')

    # Create expression with fraction: (x/y)**t * e.j
    expr = (x/y)**t * e.j

    # Get pretty printed output
    result = pretty(expr, use_unicode=True, wrap_line=False)

    # The bug causes e_j to appear twice in the output
    # Once incorrectly inside the fraction and once correctly at the end
    # Count occurrences of 'e_j' in the result
    e_j_count = result.count('e_j')

    # In the buggy version, e_j appears twice
    # In the fixed version, e_j appears only once
    print(f"Pretty printed output:")
    print(repr(result))
    print(f"Number of 'e_j' occurrences: {e_j_count}")

    # The assertion: in the fixed version, e_j should appear exactly once
    # In the buggy version, it appears twice
    assert e_j_count == 1, f"Expected 'e_j' to appear once, but it appears {e_j_count} times. Output: {repr(result)}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_vector_pretty_printing_with_fraction()