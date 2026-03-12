#!/usr/bin/env python
"""
Test to reproduce the issue with indexed matrix-expression LaTeX printer.

The issue is that when printing (M*N)[i, j] where M and N are MatrixSymbols,
the LaTeX output contains double underscores like `_i_1` which is invalid LaTeX.
"""

from sympy import symbols, MatrixSymbol, latex

def test_matrix_element_latex():
    """Test that MatrixElement LaTeX printing properly handles indices."""
    i, j, k = symbols("i j k")
    M = MatrixSymbol("M", k, k)
    N = MatrixSymbol("N", k, k)

    # Get the LaTeX representation of (M*N)[i, j]
    result = latex((M*N)[i, j])

    print("Generated LaTeX:")
    print(result)

    # The issue is that the LaTeX contains double underscores like `_i_1`
    # which is invalid LaTeX. The expected output should have properly formatted
    # indices without double underscores.

    # Check if the result contains the problematic double underscore pattern
    # In the buggy version, we get something like: \sum_{i_{1}=0}^{k - 1} M_{i, _i_1} N_{_i_1, j}
    # Note the `_i_1` which has a double underscore

    # Let's check for the specific pattern that indicates the bug
    has_double_underscore_bug = False
    if "_{_i_" in result or "_{_j_" in result:
        has_double_underscore_bug = True
        print("\nBUG DETECTED: LaTeX contains double underscores (e.g., '_{_i_1}')")
        print("This is invalid LaTeX and won't render properly in MathJax.")

    # In the fixed version, the indices should be properly printed
    # The expected pattern should be like: \sum_{i_{1}=0}^{k - 1} M_{i, i_{1}} N_{i_{1}, j}
    # Note the `i_{1}` which is properly formatted

    # Check if the result has properly formatted indices
    has_proper_formatting = False
    if "_{i_{" in result or "_{j_{" in result:
        has_proper_formatting = True
        print("\nFIXED: LaTeX contains properly formatted indices (e.g., '_{i_{1}}')")

    # The test should fail on the buggy version and pass on the fixed version
    if has_double_underscore_bug:
        print("\nTest FAILED: Buggy LaTeX output detected")
        return False
    elif has_proper_formatting:
        print("\nTest PASSED: LaTeX output is properly formatted")
        return True
    else:
        print("\nTest UNCLEAR: Could not determine if bug is present")
        return False

if __name__ == "__main__":
    success = test_matrix_element_latex()
    if not success:
        exit(1)
    else:
        exit(0)