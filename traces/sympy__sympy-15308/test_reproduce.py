#!/usr/bin/env python
"""
Test to reproduce the LaTeX printing issue for Matrix Expression.

The issue is that latex(trace(A**2)) returns 'Trace(A**2)' instead of
the proper LaTeX format '\operatorname{tr}\left(A^{2} \right)'.
"""

from sympy import MatrixSymbol, trace, latex

def test_latex_trace_matrix():
    """Test that LaTeX printing of trace works correctly."""
    n = 3
    A = MatrixSymbol("A", n, n)

    # Get the LaTeX representation
    result = latex(trace(A**2))

    print(f"Current output: {result}")

    # The expected output should be proper LaTeX with:
    # 1. \operatorname{tr} for the trace function
    # 2. A^{2} for the matrix power (not A**2)
    expected = r"\operatorname{tr}\left(A^{2} \right)"

    # This assertion will fail on the buggy version
    assert result == expected, f"Expected '{expected}', got '{result}'"

    print("Test passed - LaTeX printing of trace is correct!")

if __name__ == "__main__":
    test_latex_trace_matrix()