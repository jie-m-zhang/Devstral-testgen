#!/usr/bin/env python3
"""
Test to reproduce the issue with ccode(sinc(x)) not working properly.

The issue is that ccode(sinc(x)) currently outputs:
'// Not supported in C:\\n// sinc\\nsinc(x)'

But it should output a Piecewise expression like:
'((x != 0) ? (\\n   sin(x)/x\\n)\\n: (\\n   1\\n))'
"""

from sympy import sinc, symbols, ccode, Piecewise, sin, Ne

def test_issue_reproduction():
    """Test that ccode(sinc(x)) produces the correct output."""
    x = symbols('x')

    # Get the current output from ccode(sinc(x))
    result = ccode(sinc(x))

    # The expected output should be a Piecewise expression
    # that represents sinc(x) = sin(x)/x for x != 0, and 1 for x = 0
    # Note: Ne(x, 0) gets printed as "x != 0" in C code
    expected_output = '((x != 0) ? (\n   sin(x)/x\n)\n: (\n   1\n))'

    # Print for debugging
    print(f"Current output: {repr(result)}")
    print(f"Expected output: {repr(expected_output)}")

    # This assertion will fail on buggy code, pass on fixed code
    # The test checks that ccode(sinc(x)) produces the correct Piecewise output
    assert result == expected_output, f"Expected {repr(expected_output)}, got {repr(result)}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()