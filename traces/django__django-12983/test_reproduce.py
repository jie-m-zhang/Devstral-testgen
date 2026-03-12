#!/usr/bin/env python
"""
Test to reproduce the issue with django.utils.text.slugify() not stripping
dashes and underscores from the beginning and end of the string.

Issue: slugify("___This is a test ---") should return "this-is-a-test"
       but currently returns "___this-is-a-test-"
"""

from django.utils.text import slugify

def test_slugify_strips_dashes_and_underscores():
    """
    Test that slugify strips leading/trailing dashes and underscores.
    """
    # Test case from the issue description
    result = slugify("___This is a test ---")

    # Expected: "this-is-a-test" (no leading underscores, no trailing dashes)
    # Buggy behavior: "___this-is-a-test-" (keeps leading underscores and trailing dashes)
    expected = "this-is-a-test"

    print(f"Input: '___This is a test ---'")
    print(f"Expected: '{expected}'")
    print(f"Got: '{result}'")

    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("Test passed - issue is fixed")

def test_slugify_edge_cases():
    """
    Test additional edge cases for slugify with dashes and underscores.
    """
    test_cases = [
        # (input, expected_output)
        ("___test---", "test"),
        ("___test", "test"),
        ("test---", "test"),
        ("___", ""),  # Only underscores and dashes
        ("---", ""),  # Only dashes
        ("___test___", "test"),
        ("---test---", "test"),
        ("_t_e_s_t_", "t_e_s_t"),  # Underscores between chars are preserved
        ("-t-e-s-t-", "t-e-s-t"),  # Dashes between chars become single dashes
        ("___mixed-test---", "mixed-test"),
        ("___Test-With-Mixed_Case---", "test-with-mixed_case"),
        ("--test__", "test"),
        ("__test--", "test"),
        (" a-b_c ", "a-b_c"),  # Spaces are trimmed, but internal chars preserved
        ("___test_with_underscores---", "test_with_underscores"),
    ]

    for input_str, expected in test_cases:
        result = slugify(input_str)
        print(f"\nInput: '{input_str}'")
        print(f"Expected: '{expected}'")
        print(f"Got: '{result}'")
        assert result == expected, f"For input '{input_str}': Expected '{expected}', got '{result}'"

    print("\nAll edge case tests passed!")

if __name__ == "__main__":
    print("Testing slugify with dashes and underscores...\n")
    test_slugify_strips_dashes_and_underscores()
    print("\n" + "="*60 + "\n")
    test_slugify_edge_cases()