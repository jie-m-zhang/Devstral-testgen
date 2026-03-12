"""
Test to reproduce the issue where JSONField values are displayed as dict
when readonly in the admin, instead of proper JSON.

The issue is that display_for_field() doesn't handle JSONField specially,
so it falls through to display_for_value() which converts the dict to a
string with single quotes instead of proper JSON with double quotes.
"""

from django.db import models
from django.contrib.admin.utils import display_for_field

def test_jsonfield_display_issue():
    """
    Test that JSONField values are properly displayed in admin when readonly.

    The test should FAIL on the buggy version (base commit) because:
    - display_for_field will return "{'foo': 'bar'}" (dict string representation)
    - This is not valid JSON

    The test should PASS on the fixed version (head commit) because:
    - display_for_field will return '{"foo": "bar"}' (proper JSON)
    """

    # Create a JSONField instance
    json_field = models.JSONField()

    # Test data - a dict that should be displayed as JSON
    test_value = {"foo": "bar"}

    # Call display_for_field with the JSON value
    result = display_for_field(test_value, json_field, empty_value_display="-empty-")

    # The result should be valid JSON with double quotes
    # On the buggy version, this will fail because it returns "{'foo': 'bar'}"
    # On the fixed version, this will pass because it returns '{"foo": "bar"}'
    print(f"Result: {result}")
    print(f"Result type: {type(result)}")

    # Check that the result is valid JSON (contains double quotes, not single quotes)
    assert '"' in result, f"Expected double quotes in result, got: {result}"
    assert "'" not in result or result.count("'") == 0, f"Unexpected single quotes in result: {result}"

    # Also check that it's actually valid JSON by trying to parse it
    import json
    try:
        parsed = json.loads(result)
        assert parsed == test_value, f"Parsed JSON doesn't match original value. Expected: {test_value}, Got: {parsed}"
        print("Test passed - JSON is properly formatted")
    except json.JSONDecodeError as e:
        assert False, f"Result is not valid JSON: {result}. Error: {e}"

if __name__ == "__main__":
    test_jsonfield_display_issue()