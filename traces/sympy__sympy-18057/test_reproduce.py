#!/usr/bin/env python
"""
Test to reproduce the issue where Sympy incorrectly attempts to eval reprs in its __eq__ method.

This test should:
1. FAIL on base commit (62000f37b8821573ba00280524ffb4ac4a380875) with AttributeError
2. PASS on head commit (28b41c73c12b70d6ad9f6e45109a80649c4456da) without errors
"""

import sympy

def test_eq_with_malicious_repr():
    """
    Test that comparing a Symbol with an object whose repr is 'x.y'
    doesn't trigger an AttributeError.
    """
    class C:
        def __repr__(self):
            return 'x.y'

    try:
        # This should not raise AttributeError
        result = sympy.Symbol('x') == C()
        # The result should be False (not equal)
        assert result is False, f"Expected False, got {result}"
        print("Test 1 passed: No AttributeError when comparing with malicious repr")
    except AttributeError as e:
        print(f"Test 1 FAILED with AttributeError: {e}")
        raise

def test_eq_with_simple_repr():
    """
    Test that comparing a Symbol with an object whose repr is 'x'
    correctly returns False (not equal).
    """
    class C:
        def __repr__(self):
            return 'x'

    # This should return False (not equal)
    result = sympy.Symbol('x') == C()
    assert result is False, f"Expected False, got {result}"
    print("Test 2 passed: Object with repr 'x' is not equal to Symbol('x')")

if __name__ == "__main__":
    print("Running test for Sympy __eq__ issue...")
    print()

    # Test 1: Should fail on buggy version with AttributeError
    test_eq_with_malicious_repr()

    # Test 2: Should fail on buggy version (incorrectly returns True)
    test_eq_with_simple_repr()

    print()
    print("All tests passed!")