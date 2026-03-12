#!/usr/bin/env python
"""
Test to reproduce the Product pretty print issue.

The issue is that the Product pretty printing has:
1. An empty line at the bottom of the ∏ (inside the product symbol)
2. The ∏ is too fat
3. The top bar could be extended

The test checks that the pretty printing output matches the expected format.
"""

from sympy import Product, symbols, oo
from sympy.printing.pretty import pretty as xpretty

def test_product_pretty_print():
    """Test that Product pretty printing has the correct format."""
    n = symbols('n')

    # Test case 1: Simple product Product(1, (n, 1, oo))
    expr1 = Product(1, (n, 1, oo))
    result1 = xpretty(expr1, use_unicode=True, wrap_line=False)
    print("Test 1 - Product(1, (n, 1, oo)):")
    print(result1)
    print()

    # Test case 2: Product with fraction Product(1/n, (n, 1, oo))
    expr2 = Product(1/n, (n, 1, oo))
    result2 = xpretty(expr2, use_unicode=True, wrap_line=False)
    print("Test 2 - Product(1/n, (n, 1, oo)):")
    print(result2)
    print()

    # Test case 3: Product with fraction and power Product(1/n**2, (n, 1, oo))
    expr3 = Product(1/n**2, (n, 1, oo))
    result3 = xpretty(expr3, use_unicode=True, wrap_line=False)
    print("Test 3 - Product(1/n**2, (n, 1, oo)):")
    print(result3)
    print()

    # Split into lines to analyze
    lines1 = result1.split('\n')
    lines2 = result2.split('\n')
    lines3 = result3.split('\n')

    print("Analysis:")
    print(f"Test 1 has {len(lines1)} lines")
    print(f"Test 2 has {len(lines2)} lines")
    print(f"Test 3 has {len(lines3)} lines")
    print()

    # Check the structure of the output
    # Expected structure (fixed version):
    # Line 0: "  ∞    "  <- limit
    # Line 1: "─┬─┬─  "  <- top bar with horizontal extensions
    # Line 2: " │ │  1"  <- function with spaces around vertical bars
    # Line 3: " │ │   "  <- NO empty line (this is the key fix)
    # Line 4: "n = 1  "  <- limit

    # The key differences between buggy and fixed:
    # 1. Buggy: Top line is "┬───┬  " (no horizontal extensions)
    #    Fixed: Top line is "─┬─┬─  " (with horizontal extensions)
    # 2. Buggy: Vertical bars are flush: "│   │ 1"
    #    Fixed: Vertical bars have spaces: " │ │  1"

    def check_product_format(lines):
        """Check if the product has the correct format."""
        if len(lines) < 4:
            return False, "Not enough lines"

        # Line 1 should be the top bar
        # In fixed version, it should start with '─' (not '┬')
        top_line = lines[1].rstrip()  # Remove trailing spaces
        if top_line.startswith('─'):
            print(f"  ✓ Top bar has horizontal extensions: {repr(top_line)}")
            has_extensions = True
        else:
            print(f"  ✗ Top bar missing horizontal extensions: {repr(top_line)}")
            has_extensions = False

        # Check vertical bars have spaces around them
        # Look for lines with '│' that have spaces before and after
        has_spaced_bars = False
        for line in lines[1:-1]:  # Skip first and last line
            if '│' in line:
                # Check if there's a space before and after the bar
                if ' │ ' in line:
                    has_spaced_bars = True
                    print(f"  ✓ Vertical bars have spaces: {repr(line)}")
                    break
        if not has_spaced_bars:
            print(f"  ✗ Vertical bars don't have spaces")

        return has_extensions and has_spaced_bars, "Format check"

    print("Checking product format:")
    result1_ok, msg1 = check_product_format(lines1)
    print(f"Test 1: {'PASS' if result1_ok else 'FAIL'}")

    result2_ok, msg2 = check_product_format(lines2)
    print(f"Test 2: {'PASS' if result2_ok else 'FAIL'}")

    result3_ok, msg3 = check_product_format(lines3)
    print(f"Test 3: {'PASS' if result3_ok else 'FAIL'}")

    # Overall result
    if result1_ok and result2_ok and result3_ok:
        print("\nPASS: All products have correct format")
        return True
    else:
        print("\nFAIL: Products don't have correct format (buggy behavior)")
        return False

if __name__ == "__main__":
    success = test_product_pretty_print()
    if success:
        print("\nAll tests passed!")
    else:
        print("\nTest failed - issue reproduced!")
        exit(1)