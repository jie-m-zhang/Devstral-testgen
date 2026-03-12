#!/usr/bin/env python
"""
Test to reproduce the issue where ValidationErrors with identical messages
don't equal each other.

This test should FAIL on the base commit (buggy version) and PASS on the head commit (fixed version).
"""

from django.core.exceptions import ValidationError

def test_validation_error_equality():
    """Test that ValidationErrors with identical content are equal."""

    print("Testing ValidationError equality...")

    # Test 1: Simple ValidationError with same message
    print("\nTest 1: Simple ValidationError with same message")
    error1 = ValidationError("This field is required")
    error2 = ValidationError("This field is required")
    print(f"error1: {error1}")
    print(f"error2: {error2}")
    print(f"error1 == error2: {error1 == error2}")
    assert error1 == error2, "Simple ValidationErrors with same message should be equal"
    print("Test 1 passed")

    # Test 2: ValidationError with error_list
    print("\nTest 2: ValidationError with error_list")
    error3 = ValidationError(["Error 1", "Error 2"])
    error4 = ValidationError(["Error 1", "Error 2"])
    print(f"error3: {error3}")
    print(f"error4: {error4}")
    print(f"error3 == error4: {error3 == error4}")
    assert error3 == error4, "ValidationErrors with same error_list should be equal"
    print("Test 2 passed")

    # Test 3: ValidationError with error_list (different order)
    print("\nTest 3: ValidationError with error_list (different order)")
    error5 = ValidationError(["Error 1", "Error 2"])
    error6 = ValidationError(["Error 2", "Error 1"])
    print(f"error5: {error5}")
    print(f"error6: {error6}")
    print(f"error5 == error6: {error5 == error6}")
    assert error5 == error6, "ValidationErrors with same error_list (different order) should be equal"
    print("Test 3 passed")

    # Test 4: ValidationError with error_dict
    print("\nTest 4: ValidationError with error_dict")
    error7 = ValidationError({
        'field1': ['Error 1', 'Error 2'],
        'field2': ['Error 3']
    })
    error8 = ValidationError({
        'field1': ['Error 1', 'Error 2'],
        'field2': ['Error 3']
    })
    print(f"error7: {error7}")
    print(f"error8: {error8}")
    print(f"error7 == error8: {error7 == error8}")
    assert error7 == error8, "ValidationErrors with same error_dict should be equal"
    print("Test 4 passed")

    # Test 5: ValidationError with error_dict (different field order)
    print("\nTest 5: ValidationError with error_dict (different field order)")
    error9 = ValidationError({
        'field1': ['Error 1', 'Error 2'],
        'field2': ['Error 3']
    })
    error10 = ValidationError({
        'field2': ['Error 3'],
        'field1': ['Error 1', 'Error 2']
    })
    print(f"error9: {error9}")
    print(f"error10: {error10}")
    print(f"error9 == error10: {error9 == error10}")
    assert error9 == error10, "ValidationErrors with same error_dict (different field order) should be equal"
    print("Test 5 passed")

    # Test 6: ValidationError with code and params
    print("\nTest 6: ValidationError with code and params")
    error11 = ValidationError("Error: %(value)s", code='invalid', params={'value': 'test'})
    error12 = ValidationError("Error: %(value)s", code='invalid', params={'value': 'test'})
    print(f"error11: {error11}")
    print(f"error12: {error12}")
    print(f"error11 == error12: {error11 == error12}")
    assert error11 == error12, "ValidationErrors with same message, code, and params should be equal"
    print("Test 6 passed")

    # Test 7: ValidationError with code and params (different param order)
    print("\nTest 7: ValidationError with code and params (different param order)")
    error13 = ValidationError("Error: %(val1)s %(val2)s", code='invalid', params={'val1': 'a', 'val2': 'b'})
    error14 = ValidationError("Error: %(val1)s %(val2)s", code='invalid', params={'val2': 'b', 'val1': 'a'})
    print(f"error13: {error13}")
    print(f"error14: {error14}")
    print(f"error13 == error14: {error13 == error14}")
    assert error13 == error14, "ValidationErrors with same message, code, and params (different order) should be equal"
    print("Test 7 passed")

    # Test 8: Different ValidationErrors should not be equal
    print("\nTest 8: Different ValidationErrors should not be equal")
    error15 = ValidationError("Error 1")
    error16 = ValidationError("Error 2")
    print(f"error15: {error15}")
    print(f"error16: {error16}")
    print(f"error15 == error16: {error15 == error16}")
    assert error15 != error16, "ValidationErrors with different messages should not be equal"
    print("Test 8 passed")

    print("\nAll tests passed!")

if __name__ == "__main__":
    test_validation_error_equality()