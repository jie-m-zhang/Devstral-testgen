#!/usr/bin/env python
"""
Test to reproduce the issue with pretty printing MatAdd containing MatrixSymbol with '*' in name.

The issue occurs when trying to pretty print MatrixSymbol('x', n, n) + MatrixSymbol('y*', n, n)
because the _print_MatAdd method tries to use S(item.args[0]).is_negative which attempts
to sympify the string 'y*' and fails.
"""

from sympy import MatrixSymbol, pprint
from sympy.printing.pretty.pretty import pretty
from sympy.core.sympify import SympifyError

def test_matadd_pretty_print_with_star_in_name():
    """Test that pretty printing MatAdd with '*' in MatrixSymbol name works."""
    n = 3

    # Create two MatrixSymbols, one with '*' in the name
    x = MatrixSymbol('x', n, n)
    y_star = MatrixSymbol('y*', n, n)

    # Create a MatAdd expression
    expr = x + y_star

    # This should not raise an exception
    try:
        result = pretty(expr)
        print("Pretty printing succeeded!")
        print("Result:", result)
        return True
    except SympifyError as e:
        print(f"SympifyError occurred: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return False

def test_matadd_pretty_print_with_various_names():
    """Test pretty printing MatAdd with various special characters in names."""
    n = 3

    test_cases = [
        ('x', 'y*'),    # The original failing case
        ('x', 'y**'),   # Double star
        ('x*', 'y'),    # Star in first matrix
        ('x*y', 'z'),   # Star in first matrix name
    ]

    all_passed = True

    for name1, name2 in test_cases:
        print(f"\nTesting: MatrixSymbol('{name1}', {n}, {n}) + MatrixSymbol('{name2}', {n}, {n})")
        try:
            x = MatrixSymbol(name1, n, n)
            y = MatrixSymbol(name2, n, n)
            expr = x + y
            result = pretty(expr)
            print(f"  ✓ Success")
        except SympifyError as e:
            print(f"  ✗ SympifyError: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ✗ Unexpected error: {type(e).__name__}: {e}")
            all_passed = False

    return all_passed

if __name__ == "__main__":
    print("=" * 70)
    print("Testing MatAdd pretty printing with special characters in MatrixSymbol names")
    print("=" * 70)

    # Test the specific case from the issue
    print("\n1. Testing the original issue case:")
    print("-" * 70)
    success1 = test_matadd_pretty_print_with_star_in_name()

    # Test various edge cases
    print("\n2. Testing various special character cases:")
    print("-" * 70)
    success2 = test_matadd_pretty_print_with_various_names()

    print("\n" + "=" * 70)
    if success1 and success2:
        print("All tests PASSED!")
        print("=" * 70)
        exit(0)
    else:
        print("Some tests FAILED!")
        print("=" * 70)
        exit(1)