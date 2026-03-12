#!/usr/bin/env python
"""
Test to reproduce the issue where Messages framework incorrectly serializes/deserializes
extra_tags when it's an empty string.

The bug: When a message is serialized and then deserialized with any of the built in
storage backends, extra_tags=="" is converted to extra_tags==None.
"""

from django.conf import settings

# Configure Django settings BEFORE importing messages modules
if not settings.configured:
    settings.configure()

from django.contrib.messages.storage.base import Message
from django.contrib.messages.storage.cookie import MessageEncoder, MessageDecoder

def test_extra_tags_empty_string():
    """
    Test that extra_tags="" is preserved during serialization/deserialization.
    This test should FAIL on the buggy version and PASS on the fixed version.
    """
    # Create a message with extra_tags as an empty string
    original_message = Message(10, "Here is a message", extra_tags="")

    # Verify the original message has extra_tags as empty string
    assert original_message.extra_tags == "", f"Original message extra_tags should be empty string, got: {repr(original_message.extra_tags)}"

    # Encode the message
    encoder = MessageEncoder()
    encoded_message = encoder.encode(original_message)

    # Decode the message
    decoder = MessageDecoder()
    decoded_message = decoder.decode(encoded_message)

    # Verify the decoded message has extra_tags as empty string (not None)
    # This assertion will FAIL on the buggy version (extra_tags will be None)
    # and PASS on the fixed version (extra_tags will be "")
    assert decoded_message.extra_tags == "", f"Decoded message extra_tags should be empty string, got: {repr(decoded_message.extra_tags)}"
    assert decoded_message.extra_tags is not None, f"Decoded message extra_tags should not be None, got: {repr(decoded_message.extra_tags)}"

    print("Test passed - extra_tags empty string is preserved correctly")

if __name__ == "__main__":
    test_extra_tags_empty_string()