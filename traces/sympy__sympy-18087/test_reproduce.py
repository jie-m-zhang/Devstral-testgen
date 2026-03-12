from sympy import symbols, Rational, Integer, S, Mul, sqrt, sin, cos, trigsimp, I, factor_terms
from sympy.core.exprtools import Factors

def test_issue_18059():
    """
    Test for issue #18059: Factors().as_expr() with rational exponents.

    The bug is that when using plain 0 instead of S.Zero in Factors.__init__,
    and when checking isinstance(exp, (int, Integer)) in as_expr(),
    expressions with rational exponents (like S.Half) are not handled correctly.

    This test should fail on the buggy version and pass on the fixed version.
    """
    x = symbols('x')

    # Test case from issue #18059
    expr = (x**2)**S.Half
    print(f"Expression: {expr}")
    print(f"Type of exponent (S.Half): {type(S.Half)}")
    print(f"Is S.Half an Integer? {isinstance(S.Half, Integer)}")
    print(f"Is S.Half a Rational? {isinstance(S.Half, Rational)}")

    # Create Factors object
    factors = Factors(expr)
    print(f"Factors: {factors.factors}")

    # Try to reconstruct the expression
    # On the buggy version, this might fail or return incorrect result
    try:
        reconstructed = factors.as_expr()
        print(f"Reconstructed: {reconstructed}")
        print(f"Equal to original? {reconstructed == expr}")

        # This assertion should fail on buggy version
        assert reconstructed == expr, f"Reconstruction failed: {reconstructed} != {expr}"
        print("Test passed!")
    except Exception as e:
        print(f"Error during reconstruction: {e}")
        raise

def test_rational_exponents():
    """
    Test various expressions with rational exponents.
    """
    x = symbols('x')

    test_cases = [
        (x**Rational(1, 2), "x**(1/2)"),
        (x**Rational(3, 4), "x**(3/4)"),
        ((x**2)**Rational(1, 3), "(x**2)**(1/3)"),
        ((x**3)**S.Half, "(x**3)**S.Half"),
    ]

    for expr, desc in test_cases:
        print(f"\nTesting: {desc}")
        print(f"Expression: {expr}")

        # Create Factors and reconstruct
        factors = Factors(expr)
        print(f"Factors: {factors.factors}")

        try:
            reconstructed = factors.as_expr()
            print(f"Reconstructed: {reconstructed}")
            assert reconstructed == expr, f"Failed for {desc}: {reconstructed} != {expr}"
            print(f"✓ Passed for {desc}")
        except Exception as e:
            print(f"✗ Failed for {desc}: {e}")
            raise

if __name__ == "__main__":
    print("Testing issue #18059...")
    test_issue_18059()

    print("\n" + "="*60)
    print("Testing various rational exponents...")
    test_rational_exponents()