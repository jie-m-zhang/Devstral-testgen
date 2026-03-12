#!/usr/bin/env python
"""
Test to reproduce the issue with inaccurate rendering of pi**(1/E)

The issue is that pi**(1/E) is rendered incorrectly in pretty print mode.
It should not show a root sign with -1___ above it.
"""

from sympy import symbols, pi, E, pprint
from sympy.printing.pretty.pretty import pretty

def test_pi_pow_1_over_E_pretty_print():
    """
    Test that pi**(1/E) is rendered correctly in pretty print.

    The bug causes it to show:
        -1___
        ╲╱ π

    Instead of the correct representation.
    """
    expr = pi**(1/E)

    # Get the pretty print output
    pretty_output = pretty(expr)

    # Convert to string to check content
    output_str = str(pretty_output)

    # The buggy version produces output with "-1___" and root sign
    # The fixed version should not have this incorrect representation
    # Check that the output doesn't contain the buggy pattern
    # The bug shows "-1___" followed by root sign characters

    # Let's check what the actual output is
    print("Pretty output string representation:")
    print(repr(output_str))
    print("\nActual pretty output:")
    print(output_str)

    # The buggy output contains "-1___" which is incorrect
    # This should NOT be in the output
    if "-1___" in output_str:
        print("\nERROR: Found buggy pattern '-1___' in output!")
        print("This indicates the expression is being incorrectly rendered as a root.")
        return False
    else:
        print("\nSUCCESS: No buggy pattern found.")
        return True

if __name__ == "__main__":
    success = test_pi_pow_1_over_E_pretty_print()
    if not success:
        print("\nTest FAILED - issue reproduced")
        exit(1)
    else:
        print("\nTest PASSED - issue is fixed")
        exit(0)