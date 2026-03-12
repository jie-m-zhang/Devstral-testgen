#!/usr/bin/env python
"""
Test to reproduce the issue where lambdify does not work with certain MatrixSymbol names
even with dummify=True.

The issue is that lambdify works with:
1. curly braces in a symbol name
2. MatrixSymbol

But fails with:
3. MatrixSymbol with curly braces in the name, even with dummify=True
"""

import sympy as sy

def test_lambdify_with_curly_braces_and_matrixsymbol():
    """Test that reproduces the issue with lambdify and MatrixSymbol with curly braces."""

    # Create symbols with curly braces
    curlyx = sy.symbols("{x}")

    # Create MatrixSymbols
    v = sy.MatrixSymbol("v", 2, 1)
    curlyv = sy.MatrixSymbol("{v}", 2, 1)

    # Test 1: lambdify with curly braces in symbol name - should work
    print("Test 1: lambdify with curly braces in symbol name")
    try:
        curlyScalarId = sy.lambdify(curlyx, curlyx)
        print("  ✓ Works: lambdify(curlyx, curlyx)")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        raise

    # Test 2: lambdify with MatrixSymbol - should work
    print("Test 2: lambdify with MatrixSymbol")
    try:
        vectorId = sy.lambdify(v, v)
        print("  ✓ Works: lambdify(v, v)")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        raise

    # Test 3: lambdify with MatrixSymbol with curly braces - should fail on base commit
    print("Test 3: lambdify with MatrixSymbol with curly braces")
    try:
        curlyVectorId = sy.lambdify(curlyv, curlyv)
        print("  ✓ Works: lambdify(curlyv, curlyv)")
    except SyntaxError as e:
        print(f"  ✗ Failed with SyntaxError: {e}")
        # This is expected on the base commit
        raise AssertionError(f"lambdify failed with MatrixSymbol containing curly braces: {e}")
    except Exception as e:
        print(f"  ✗ Failed with unexpected error: {e}")
        raise

    # Test 4: lambdify with MatrixSymbol with curly braces and dummify=True - should fail on base commit
    print("Test 4: lambdify with MatrixSymbol with curly braces and dummify=True")
    try:
        curlyVectorIdDummified = sy.lambdify(curlyv, curlyv, dummify=True)
        print("  ✓ Works: lambdify(curlyv, curlyv, dummify=True)")
    except SyntaxError as e:
        print(f"  ✗ Failed with SyntaxError: {e}")
        # This is expected on the base commit
        raise AssertionError(f"lambdify failed with MatrixSymbol containing curly braces even with dummify=True: {e}")
    except Exception as e:
        print(f"  ✗ Failed with unexpected error: {e}")
        raise

    print("\nAll tests passed!")

if __name__ == "__main__":
    test_lambdify_with_curly_braces_and_matrixsymbol()