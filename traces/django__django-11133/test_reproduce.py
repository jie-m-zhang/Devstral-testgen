#!/usr/bin/env python
"""
Test to reproduce the issue with HttpResponse not handling memoryview objects correctly.

The issue: When a memoryview object is passed to HttpResponse, it should be converted
to bytes properly, but currently it's showing the memoryview object representation
instead of the actual content.

Expected behavior:
- HttpResponse(memoryview(b"My Content")).content should return b'My Content'

Buggy behavior (base commit):
- HttpResponse(memoryview(b"My Content")).content returns b'<memory at 0x...>'
"""

import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        DEFAULT_CHARSET='utf-8',
    )
    django.setup()

from django.http import HttpResponse

def test_memoryview_handling():
    """Test that HttpResponse correctly handles memoryview objects."""
    # Test with regular bytes (should work)
    response_bytes = HttpResponse(b"My Content")
    assert response_bytes.content == b"My Content", f"Expected b'My Content', got {response_bytes.content}"

    # Test with string (should work)
    response_str = HttpResponse("My Content")
    assert response_str.content == b"My Content", f"Expected b'My Content', got {response_str.content}"

    # Test with memoryview (this is the bug we're testing)
    test_data = b"My Content"
    memory_view = memoryview(test_data)
    response_mv = HttpResponse(memory_view)

    # This assertion should fail on the buggy version and pass on the fixed version
    assert response_mv.content == b"My Content", f"Expected b'My Content', got {response_mv.content}"

    print("Test passed - memoryview is handled correctly")

if __name__ == "__main__":
    test_memoryview_handling()