from sympy import *

def test_trig_simplify_with_rational():
    """
    Test that trigonometric expressions with Rational numbers simplify correctly.
    This reproduces the issue where sin/cos with Rational numbers don't simplify.
    """
    # Test case 1: With symbols - this should work
    x, y = symbols('x, y', real=True)
    r_symbols = sin(x)*sin(y) + cos(x)*cos(y)
    r_symbols_simplified = r_symbols.simplify()
    print(f"Symbols: {r_symbols} -> {r_symbols_simplified}")
    assert r_symbols_simplified == cos(x - y), f"Expected cos(x - y), got {r_symbols_simplified}"

    # Test case 2: With Rational numbers - this should also work but currently doesn't
    r_rational = sin(Rational(1, 50))*sin(Rational(1, 25)) + cos(Rational(1, 50))*cos(Rational(1, 25))
    r_rational_simplified = r_rational.simplify()
    print(f"Rational: {r_rational} -> {r_rational_simplified}")

    # The expected simplified form should be cos(Rational(1, 50) - Rational(1, 25))
    expected = cos(Rational(1, 50) - Rational(1, 25))
    print(f"Expected: {expected}")

    # This assertion should fail on the buggy version and pass on the fixed version
    assert r_rational_simplified == expected, f"Expected {expected}, got {r_rational_simplified}"

    print("Test passed - trigonometric simplification with Rational numbers works correctly")

if __name__ == "__main__":
    test_trig_simplify_with_rational()