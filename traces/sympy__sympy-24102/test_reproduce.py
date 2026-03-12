#!/usr/bin/env python
"""
Test to reproduce the issue with parsing Greek characters in parse_mathematica.

The issue: parse_mathematica cannot parse Greek characters like 'λ',
while the old mathematica function can.

This test should:
- FAIL on base commit (58598660a3f6ab3d918781c4988c2e4b2bdd9297) with SyntaxError
- PASS on head commit (c6cb7c5602fa48034ab1bd43c2347a7e8488f12e) successfully parsing Greek characters
"""

from sympy.parsing.mathematica import parse_mathematica, mathematica
from sympy.core.symbol import Symbol
from sympy.utilities.exceptions import SymPyDeprecationWarning

def test_greek_characters_parse_mathematica():
    """
    Test that parse_mathematica can parse Greek characters.

    This is the main test that demonstrates the F->P behavior:
    - On base commit: FAILS with SyntaxError
    - On head commit: PASSES successfully
    """
    # Test parsing a simple Greek character 'λ' (lambda)
    result = parse_mathematica('λ')

    # The result should be a Symbol with name 'λ'
    assert isinstance(result, Symbol), f"Expected Symbol, got {type(result)}"
    assert str(result) == 'λ', f"Expected 'λ', got '{result}'"

    print("✓ Test passed: parse_mathematica successfully parsed Greek character 'λ'")

def test_old_mathematica_still_works():
    """
    Test that the old mathematica function still works (for comparison).
    This should pass on both commits.
    """
    # Suppress the deprecation warning for this test
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SymPyDeprecationWarning)

        result = mathematica('λ')
        assert isinstance(result, Symbol), f"Expected Symbol, got {type(result)}"
        assert str(result) == 'λ', f"Expected 'λ', got '{result}'"

    print("✓ Test passed: old mathematica function still works")

def test_other_greek_characters():
    """
    Test parsing other Greek characters to ensure the fix is comprehensive.
    """
    # Test various Greek characters
    greek_chars = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω',
                   'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω']

    for char in greek_chars:
        result = parse_mathematica(char)
        assert isinstance(result, Symbol), f"Expected Symbol for '{char}', got {type(result)}"
        assert str(result) == char, f"Expected '{char}', got '{result}'"

    print(f"✓ Test passed: successfully parsed {len(greek_chars)} Greek characters")

if __name__ == "__main__":
    print("Testing Greek character parsing in parse_mathematica...")
    print()

    # Run the main test that demonstrates F->P behavior
    try:
        test_greek_characters_parse_mathematica()
    except SyntaxError as e:
        print(f"✗ Test failed (expected on base commit): {e}")
        raise
    except Exception as e:
        print(f"✗ Test failed with unexpected error: {e}")
        raise

    # Run additional tests
    test_old_mathematica_still_works()
    test_other_greek_characters()

    print()
    print("All tests passed!")