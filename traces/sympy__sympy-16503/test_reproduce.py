#!/usr/bin/env python
"""
Test to reproduce the bad centering issue in Sum pretty print.

The issue is that when printing Sum(x, (x, 1, oo)) + 3, the 'x' and '+ 3'
are not properly aligned.

In the buggy version, they appear on separate lines with misalignment.
In the fixed version, they appear on the same line, properly aligned.
"""

import io
import sys
from sympy import Sum, symbols, pprint, oo

def test_sum_pretty_print_alignment():
    """Test that Sum pretty print aligns elements properly."""
    x = symbols('x')
    
    # Create the expression from the issue
    expr = Sum(x, (x, 1, oo)) + 3
    
    # Capture the pprint output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        pprint(expr)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    
    # Split into lines to analyze alignment
    lines = output.split('\n')
    
    # Find the line with 'x' and the line with '+ 3'
    x_line_idx = None
    plus_line_idx = None
    
    for i, line in enumerate(lines):
        if 'x' in line and x_line_idx is None:
            x_line_idx = i
        if '+ 3' in line or '+3' in line:
            plus_line_idx = i
    
    # Both should be found
    assert x_line_idx is not None, "Could not find 'x' in output"
    assert plus_line_idx is not None, "Could not find '+ 3' in output"
    
    # Get the positions of 'x' and '+'
    x_line = lines[x_line_idx]
    plus_line = lines[plus_line_idx]
    
    x_pos = x_line.find('x')
    plus_pos = plus_line.find('+')
    
    # They should be aligned (same column position)
    # The issue states they are not aligned in the buggy version
    print(f"Output:")
    print(output)
    print(f"x_line: '{x_line}' (x at position {x_pos})")
    print(f"plus_line: '{plus_line}' (+ at position {plus_pos})")
    
    # In the fixed version, x and + should be on the same line
    if x_line_idx == plus_line_idx:
        print("PASS: x and + are on the same line (fixed)")
        return True
    else:
        print(f"FAIL: x and + are on different lines (buggy)")
        print(f"x on line {x_line_idx}, + on line {plus_line_idx}")
        return False

if __name__ == "__main__":
    result = test_sum_pretty_print_alignment()
    if not result:
        exit(1)
    else:
        exit(0)