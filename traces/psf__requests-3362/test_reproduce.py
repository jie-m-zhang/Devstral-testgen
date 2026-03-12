#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test to reproduce the issue with iter_content(decode_unicode=True) returning bytes instead of unicode.
"""

import requests
import json
from io import BytesIO

def test_iter_content_decode_unicode_no_encoding():
    """
    Test that iter_content(decode_unicode=True) returns unicode strings, not bytes,
    even when response.encoding is None.

    This reproduces the issue described in GitHub issue where iter_content
    with decode_unicode=True was returning bytes instead of unicode when
    the response encoding was None.
    """

    # Create a mock response with JSON content but no explicit encoding
    # This simulates the scenario described in the issue
    test_data = {"message": "Hello, 世界!"}
    json_content = json.dumps(test_data).encode('utf-8')

    # Create a response object manually
    response = requests.Response()
    response.status_code = 200
    response.headers['Content-Type'] = 'application/json'
    response.encoding = None  # This is the key - no explicit encoding
    response._content = False  # This ensures we use the streaming path
    response._content_consumed = False

    # Create a mock raw object that simulates urllib3's stream behavior
    class MockRaw:
        def __init__(self, content):
            self.content = BytesIO(content)
            self._fp = self.content

        def stream(self, chunk_size, decode_content=True):
            while True:
                chunk = self.content.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        def release_conn(self):
            pass

        def close(self):
            pass

    response.raw = MockRaw(json_content)

    # Get chunks from iter_content with decode_unicode=True
    chunks = list(response.iter_content(1024, decode_unicode=True))

    # The chunks should be unicode strings, not bytes
    # In the buggy version, it returns bytes
    # In the fixed version, it should return unicode strings
    print(f"Number of chunks: {len(chunks)}")
    if chunks:
        print(f"Type of first chunk: {type(chunks[0])}")
        print(f"First chunk content: {chunks[0]}")

        # This assertion will fail on buggy code (returns bytes), pass on fixed code (returns str)
        assert isinstance(chunks[0], str), f"Expected str type, got {type(chunks[0])}"
    else:
        # If no chunks, the test should fail
        assert False, "No chunks returned from iter_content"

    print("Test passed - iter_content(decode_unicode=True) correctly returns unicode strings")

if __name__ == "__main__":
    test_iter_content_decode_unicode_no_encoding()