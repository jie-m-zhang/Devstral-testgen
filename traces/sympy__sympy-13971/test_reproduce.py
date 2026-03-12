"""
Test to reproduce the issue with SeqFormula() displaying backslash-escaped brackets.

The issue is that the LaTeX output for SeqFormula uses \[ and \] which are
being escaped as \left\[ and \right\] in the output. The fix changes these to
[ and ] without the backslash.
"""

import sympy as sp

def test_seqformula_brackets():
    """Test that SeqFormula LaTeX output doesn't use backslash-escaped brackets."""
    # Create a simple sequence
    n = sp.symbols('n', integer=True)
    seq = sp.SeqFormula(n**2, (n, 0, sp.oo))

    # Get the LaTeX representation
    latex_output = sp.latex(seq)

    print(f"LaTeX output: {latex_output}")

    # The buggy version produces: \left\[0, 1, 4, 9, \ldots\right\]
    # The fixed version should produce: \left[0, 1, 4, 9, \ldots\right]

    # Check that the output does NOT contain backslash-escaped brackets
    # In the buggy version, we get \left\[ and \right\]
    # In the fixed version, we get \left[ and \right]

    # The test should FAIL on buggy code (base commit) and PASS on fixed code (head commit)
    assert r'\left[' in latex_output, f"Expected '\\left[' in output, got: {latex_output}"
    assert r'\right]' in latex_output, f"Expected '\\right]' in output, got: {latex_output}"

    # These should NOT be present in the fixed version
    assert r'\left\[' not in latex_output, f"Found backslash-escaped '\\left\[' in output: {latex_output}"
    assert r'\right\]' not in latex_output, f"Found backslash-escaped '\\right\]' in output: {latex_output}"

    print("Test passed - SeqFormula uses correct brackets without backslash escaping")

if __name__ == "__main__":
    test_seqformula_brackets()