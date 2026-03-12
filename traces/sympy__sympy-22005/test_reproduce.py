#!/usr/bin/env python
"""
Test to reproduce the issue with infinite solution detection in solve_poly_system.

This test should:
- FAIL on the base commit (buggy version) - exit code != 0
- PASS on the head commit (fixed version) - exit code = 0

The issue is that solve_poly_system((y - 1,), x, y) incorrectly returns [(1,)]
instead of raising NotImplementedError for infinite solution systems.
"""

from sympy import Poly, symbols
from sympy.solvers.polysys import solve_poly_system
from sympy.testing.pytest import raises

def test_infinite_solution_detection():
    """Test that infinite solution systems are properly detected and raise NotImplementedError."""

    x, y = symbols('x y')

    # Test case 1: (x - 1) with generators (x, y)
    # This should raise NotImplementedError because we have 1 equation but 2 variables
    # which means infinite solutions
    print("Test 1: solve_poly_system([x-1,], (x, y))")
    raises(NotImplementedError, lambda: solve_poly_system([x-1,], (x, y)))
    print("Test 1 PASSED")

    # Test case 2: (y - 1) with generators (x, y)
    # This should also raise NotImplementedError
    # This is the main bug - it incorrectly returns [(1,)] instead of raising NotImplementedError
    print("Test 2: solve_poly_system([y-1,], (x, y))")
    raises(NotImplementedError, lambda: solve_poly_system([y-1,], (x, y)))
    print("Test 2 PASSED")

    print("\nAll tests passed!")

if __name__ == "__main__":
    test_infinite_solution_detection()