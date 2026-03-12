#!/usr/bin/env python
"""
Test to reproduce the issue with ASGIStaticFilesHandler missing get_response_async method.

This test should:
- FAIL on base commit (4652f1f0aa459a7b980441d629648707c32e36bf) with TypeError: 'NoneType' object is not callable
- PASS on head commit (65dfb06a1ab56c238cc80f5e1c31f61210c4577d) with proper Http404 handling
"""

import os
import sys
import asyncio
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.http import Http404

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY='test-secret-key',
        STATIC_URL='/static/',
        ROOT_URLCONF='test_urls',  # Use our test URL conf
        MIDDLEWARE=[],
        INSTALLED_APPS=[
            'django.contrib.staticfiles',
        ],
        USE_TZ=True,
    )

    # Setup Django
    import django
    django.setup()

async def test_asgi_static_files_handler():
    """Test that ASGIStaticFilesHandler properly handles static file requests."""

    # Create a simple application
    async def simple_app(scope, receive, send):
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [[b'content-type', b'text/plain']],
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello, World!',
        })

    # Create the ASGIStaticFilesHandler
    handler = ASGIStaticFilesHandler(simple_app)

    # Create a mock scope for a static file request
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/static/test.txt',
        'query_string': b'',
        'headers': [],
        'server': ('127.0.0.1', 8000),
        'client': ('127.0.0.1', 12345),
        'scheme': 'http',
    }

    # Create a mock receive channel
    async def receive():
        return {'type': 'http.request', 'body': b''}

    # Create a mock send channel
    messages = []
    async def send(message):
        messages.append(message)

    # Try to call the handler
    try:
        await handler(scope, receive, send)
        # If we get here, check if we got a proper response
        if messages:
            # Check if we got a 404 response (which is expected for non-existent file)
            start_message = messages[0]
            if start_message['type'] == 'http.response.start' and start_message['status'] == 404:
                print("SUCCESS: Got proper 404 response for non-existent static file")
                return True
            elif start_message['type'] == 'http.response.start':
                print(f"SUCCESS: Got response with status {start_message['status']}")
                return True
        print("FAILURE: No response messages received")
        return False
    except TypeError as e:
        if "'NoneType' object is not callable" in str(e):
            print(f"FAILURE: Got expected TypeError - {e}")
            return False
        else:
            print(f"FAILURE: Got unexpected TypeError - {e}")
            raise
    except Exception as e:
        print(f"FAILURE: Got unexpected exception - {type(e).__name__}: {e}")
        # If it's an Http404, that's actually expected behavior
        if isinstance(e, Http404):
            print("SUCCESS: Got Http404 exception (expected for non-existent file)")
            return True
        raise

def main():
    # Run the async test
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_asgi_static_files_handler())
    loop.close()

    if success:
        print("\nTest PASSED - issue is fixed")
        sys.exit(0)
    else:
        print("\nTest FAILED - issue reproduced")
        sys.exit(1)

if __name__ == '__main__':
    main()