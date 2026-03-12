"""
Test to reproduce the issue with json_script not accepting a custom encoder parameter.

The issue is that django.utils.html.json_script() is hardcoded to use DjangoJSONEncoder
and doesn't allow passing a custom encoder class.
"""

import json
import sys
from django.utils.html import json_script
from django.core.serializers.json import DjangoJSONEncoder

class CustomObject:
    """A custom object that we want to encode specially."""
    def __init__(self, value):
        self.value = value

class CustomEncoder(DjangoJSONEncoder):
    """A custom JSON encoder that knows how to encode CustomObject."""
    def default(self, obj):
        if isinstance(obj, CustomObject):
            return f"CustomObject({obj.value})"
        return super().default(obj)

def test_custom_encoder_parameter():
    """
    Test that json_script accepts and uses a custom encoder parameter.

    This test should:
    - FAIL on the base commit (where encoder parameter doesn't exist)
    - PASS on the head commit (where encoder parameter is implemented)
    """
    # Create a test object that our custom encoder can handle
    test_obj = CustomObject("test_value")

    # Try to use json_script with our custom encoder
    # On the base commit, this will fail because json_script doesn't accept an encoder parameter
    try:
        result = json_script(test_obj, element_id="test", encoder=CustomEncoder)
        print("json_script with custom encoder succeeded")
    except TypeError as e:
        # This is expected on the base commit
        print(f"json_script with custom encoder failed with TypeError: {e}")
        # The test should fail on base commit
        print("Test failed - json_script does not accept encoder parameter")
        return False

    # Verify that the custom encoder was used
    # The output should contain our custom encoding
    if "CustomObject(test_value)" not in result:
        print(f"Test failed - custom encoder was not used. Result: {result}")
        return False

    print("Test passed - custom encoder parameter works correctly!")
    return True

if __name__ == "__main__":
    success = test_custom_encoder_parameter()
    sys.exit(0 if success else 1)