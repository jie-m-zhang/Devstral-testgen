#!/usr/bin/env python
"""
Test to reproduce the issue with diophantine returning incomplete results
depending on syms order with permute=True.
"""

from sympy import symbols
from sympy.solvers.diophantine import diophantine

def test_diophantine_permute_order_issue():
    """
    Test that diophantine returns the same results regardless of syms order
    when permute=True.

    The issue is that:
    - diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(m,n), permute=True) returns 8 solutions
    - diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(n,m), permute=True) returns only 1 solution

    Both should return the same set of solutions.
    """
    m, n = symbols('m n', integer=True)

    # Equation: m^4 + n^4 = 2^4 + 3^4 = 16 + 81 = 97
    eq = n**4 + m**4 - 2**4 - 3**4

    # Get solutions with syms=(m,n)
    result_mn = diophantine(eq, syms=(m, n), permute=True)
    print(f"Solutions with syms=(m,n): {result_mn}")
    print(f"Number of solutions: {len(result_mn)}")

    # Get solutions with syms=(n,m)
    result_nm = diophantine(eq, syms=(n, m), permute=True)
    print(f"Solutions with syms=(n,m): {result_nm}")
    print(f"Number of solutions: {len(result_nm)}")

    # Both should return the same number of solutions
    # The expected solutions are all signed permutations of (2, 3) and (3, 2)
    expected_solutions = {(-3, -2), (-3, 2), (-2, -3), (-2, 3),
                          (2, -3), (2, 3), (3, -2), (3, 2)}

    print(f"Expected solutions: {expected_solutions}")
    print(f"Expected number of solutions: {len(expected_solutions)}")

    # The test should fail on the buggy version because result_nm will have only 1 solution
    # but should pass on the fixed version where both have 8 solutions
    assert len(result_mn) == len(expected_solutions), \
        f"Expected {len(expected_solutions)} solutions with syms=(m,n), got {len(result_mn)}"

    assert len(result_nm) == len(expected_solutions), \
        f"Expected {len(expected_solutions)} solutions with syms=(n,m), got {len(result_nm)}"

    # Both should return the same set of solutions (though order may differ)
    assert result_mn == result_nm, \
        f"Results differ based on syms order:\n  syms=(m,n): {result_mn}\n  syms=(n,m): {result_nm}"

    print("Test passed - issue is fixed!")

if __name__ == "__main__":
    test_diophantine_permute_order_issue()