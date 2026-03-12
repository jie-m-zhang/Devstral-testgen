#!/usr/bin/env python
"""
Test to reproduce the display bug with sympy.vector objects in pretty_print.

The issue is that unit vectors are inserted in the middle of expressions
instead of at the end when using pretty_print.
"""

from sympy import *
from sympy.vector import CoordSys3D, Del

def test_vector_pretty_print_bug():
    """Test that vector pretty printing doesn't insert unit vectors in the middle of expressions."""

    init_printing()

    delop = Del()
    CC_ = CoordSys3D("C")
    x,    y,    z    = CC_.x, CC_.y, CC_.z
    xhat, yhat, zhat = CC_.i, CC_.j, CC_.k

    t = symbols("t")
    ten = symbols("10", positive=True)
    eps, mu = 4*pi*ten**(-11), ten**(-5)

    Bx = 2 * ten**(-4) * cos(ten**5 * t) * sin(ten**(-3) * y)
    vecB = Bx * xhat
    vecE = (1/eps) * Integral(delop.cross(vecB/mu).doit(), t)

    # Get the pretty printed output as string
    vecE_doit_str = pretty(vecE.doit())
    vecE_doit_str_repr = str(vecE_doit_str)

    # The bug causes the unit vector (like k_C) to appear in the middle of the expression
    # Specifically, we look for the pattern where a unit vector appears between
    # two vertical bar characters (⎜...⎟ or ⎟...⎟), which indicates it's in the middle

    # Check for the specific bug pattern: unit vector between ⎟ and ⎟
    # This is the key indicator of the bug
    has_bug = False
    lines = vecE_doit_str_repr.split('\n')

    for line in lines:
        # Look for pattern: ⎟ [unit vector] ⎟
        # This indicates the unit vector is in the middle of the expression
        if '⎟' in line:
            # Check if there's a unit vector between two ⎟ characters
            parts = line.split('⎟')
            for i, part in enumerate(parts[:-1]):  # Don't check the last part
                if ' k_C' in part or ' i_C' in part or ' j_C' in part:
                    # Make sure this is not at the very end
                    remaining = '⎟'.join(parts[i+1:])
                    if remaining.strip() and not remaining.strip().startswith('k_C'):
                        has_bug = True
                        break
            if has_bug:
                break

    # Alternative check: look for the specific pattern from the issue
    # In buggy version: "⎟ k_C ⎟" appears
    # In fixed version: "⎟ ⎟ k_C" appears (unit vector at the end)
    if not has_bug:
        # Check for the specific problematic pattern
        import re
        # Pattern: closing vertical bar, then unit vector, then another closing vertical bar
        bug_pattern = re.compile(r'⎟\s*[ijk]_C\s*⎟')
        if bug_pattern.search(vecE_doit_str_repr):
            has_bug = True

    # The test should fail on buggy code (has_bug = True)
    # and pass on fixed code (has_bug = False)
    assert not has_bug, f"Bug detected: unit vector appears in middle of expression. Output:\n{vecE_doit_str_repr}"

    print("Test passed - no bug detected in vector pretty printing")

if __name__ == "__main__":
    test_vector_pretty_print_bug()