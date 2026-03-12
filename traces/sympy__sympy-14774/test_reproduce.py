#!/usr/bin/env python
"""
Test to reproduce the issue with LaTeX printer not supporting full inverse trig function names for acsc and asec.

The issue is that latex(acsc(x), inv_trig_style="full") should return
'\\operatorname{arccsc}{\\left (x \\right )}' but currently returns
'\\operatorname{acsc}{\\left (x \\right )}'

Similarly for asec.
"""

from sympy import symbols, acsc, asec, asin, latex

def test_issue_reproduction():
    x = symbols('x')

    # Test asin with full style - this should work (baseline)
    result_asin = latex(asin(x), inv_trig_style="full")
    expected_asin = r'\arcsin{\left (x \right )}'
    print(f"asin test: {result_asin}")
    assert result_asin == expected_asin, f"Expected '{expected_asin}', got '{result_asin}'"

    # Test acsc with full style - this should fail on buggy version
    result_acsc = latex(acsc(x), inv_trig_style="full")
    expected_acsc = r'\operatorname{arccsc}{\left (x \right )}'
    print(f"acsc test: {result_acsc}")
    assert result_acsc == expected_acsc, f"Expected '{expected_acsc}', got '{result_acsc}'"

    # Test asec with full style - this should also fail on buggy version
    result_asec = latex(asec(x), inv_trig_style="full")
    expected_asec = r'\operatorname{arccsc}{\left (x \right )}'.replace('csc', 'sec')
    print(f"asec test: {result_asec}")
    assert result_asec == expected_asec, f"Expected '{expected_asec}', got '{result_asec}'"

    print("All tests passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()