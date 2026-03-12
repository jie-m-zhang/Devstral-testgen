#!/usr/bin/env python
"""
Test to reproduce the issue where SimpleLazyObject doesn't implement __radd__.

This test should FAIL on the base commit (4c76ffc2d6c77c850b4bef8d9acc197d11c47937)
and PASS on the head commit (647480166bfe7532e8c471fef0146e3a17e6c0c9).
"""

from django.utils.functional import SimpleLazyObject

def test_radd_with_string():
    """Test that __radd__ works with string concatenation."""
    # Create a lazy object that wraps a string
    lazy_str = SimpleLazyObject(lambda: " world")

    # This should work: "hello" + lazy_str
    # This uses __radd__ on the lazy object
    try:
        result = "hello" + lazy_str
        print(f"Result: {result}")
        assert result == "hello world", f"Expected 'hello world', got '{result}'"
        print("Test passed - __radd__ works correctly with strings")
    except TypeError as e:
        print(f"Test failed - __radd__ not implemented: {e}")
        raise

def test_radd_with_list():
    """Test that __radd__ works with list concatenation."""
    # Create a lazy object that wraps a list
    lazy_list = SimpleLazyObject(lambda: [3, 4])

    # This should work: [1, 2] + lazy_list
    # This uses __radd__ on the lazy object
    try:
        result = [1, 2] + lazy_list
        print(f"Result: {result}")
        assert result == [1, 2, 3, 4], f"Expected '[1, 2, 3, 4]', got '{result}'"
        print("Test passed - __radd__ works correctly with lists")
    except TypeError as e:
        print(f"Test failed - __radd__ not implemented: {e}")
        raise

def test_radd_with_int():
    """Test that __radd__ works with integer addition."""
    # Create a lazy object that wraps an integer
    lazy_int = SimpleLazyObject(lambda: 5)

    # This should work: 10 + lazy_int
    # This uses __radd__ on the lazy object
    try:
        result = 10 + lazy_int
        print(f"Result: {result}")
        assert result == 15, f"Expected '15', got '{result}'"
        print("Test passed - __radd__ works correctly with integers")
    except TypeError as e:
        print(f"Test failed - __radd__ not implemented: {e}")
        raise

if __name__ == "__main__":
    print("Testing SimpleLazyObject __radd__ implementation...")
    print()

    print("Test 1: String concatenation")
    test_radd_with_string()
    print()

    print("Test 2: List concatenation")
    test_radd_with_list()
    print()

    print("Test 3: Integer addition")
    test_radd_with_int()
    print()

    print("All tests passed!")