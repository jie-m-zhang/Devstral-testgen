"""
Test to reproduce the issue with _print_SingularityFunction() got an unexpected keyword argument 'exp'

The issue occurs when trying to print a SingularityFunction in LaTeX format,
specifically when the _print_SingularityFunction method is called with an 'exp'
keyword argument that it doesn't accept in the buggy version.
"""

from sympy import symbols
from sympy.physics.continuum_mechanics import Beam
from sympy.printing.latex import latex

def test_singularity_function_latex_printing():
    """
    Test that reproduces the issue where _print_SingularityFunction doesn't accept 'exp' argument.

    This test creates a beam with a load and tries to print the shear force in LaTeX,
    which triggers the bug.
    """
    # Setup the beam problem as described in the issue
    E = symbols("E")  # Young's modulus
    L = symbols("L")  # length of the beam
    F = symbols("F")  # concentrated load at the end tip of the beam
    B, H = symbols("B, H")  # square cross section
    I = B * H**3 / 12
    d = {B: 1e-02, H: 1e-02, E: 210e09, L: 0.2, F: 100}

    b2 = Beam(L, E, I)
    b2.apply_load(-F, L / 2, -1)
    b2.apply_support(0, "fixed")
    R0, M0 = symbols("R_0, M_0")
    b2.solve_for_reaction_loads(R0, M0)

    # Get the shear force expression - this contains SingularityFunction
    shear_force_expr = b2.shear_force()

    # Try to convert to LaTeX - this should trigger the error in the buggy version
    # The error occurs because _print_SingularityFunction is called with exp parameter
    # when printing powers of SingularityFunction
    try:
        latex_result = latex(shear_force_expr)
        print("LaTeX conversion successful!")
        print(f"Result: {latex_result}")
        return True
    except TypeError as e:
        if "_print_SingularityFunction() got an unexpected keyword argument 'exp'" in str(e):
            print(f"ERROR: {e}")
            return False
        else:
            # Some other TypeError, re-raise it
            raise

def test_singularity_function_direct():
    """
    More direct test of the SingularityFunction with exponent.
    """
    from sympy.physics.continuum_mechanics.beam import SingularityFunction
    from sympy import symbols

    x, a, n = symbols('x a n')

    # Create a SingularityFunction
    sf = SingularityFunction(x, a, n)

    # Try to print it with an exponent (like sf**2)
    # This should trigger the exp parameter being passed
    sf_pow = sf**2

    try:
        latex_result = latex(sf_pow)
        print("Direct LaTeX conversion successful!")
        print(f"Result: {latex_result}")
        return True
    except TypeError as e:
        if "_print_SingularityFunction() got an unexpected keyword argument 'exp'" in str(e):
            print(f"ERROR: {e}")
            return False
        else:
            # Some other TypeError, re-raise it
            raise

if __name__ == "__main__":
    print("Testing SingularityFunction LaTeX printing...")
    print("\nTest 1: Beam shear force (from issue description)")
    result1 = test_singularity_function_latex_printing()

    print("\nTest 2: Direct SingularityFunction with exponent")
    result2 = test_singularity_function_direct()

    if result1 and result2:
        print("\n✓ All tests passed - issue is fixed")
    else:
        print("\n✗ Tests failed - issue reproduced")
        exit(1)