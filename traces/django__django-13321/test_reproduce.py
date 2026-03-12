#!/usr/bin/env python
"""
Test to reproduce the issue where decoding invalid session data crashes.

The issue occurs when:
1. Session data has invalid base64 padding
2. The decode() method tries to decode it
3. It raises binascii.Error: Incorrect padding

The fix should handle this gracefully by catching BadSignature and returning {}
"""

import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.test.utils')
sys.path.insert(0, '/testbed')

# Minimal Django setup
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key-for-session',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.sessions',
        ],
        SESSION_ENGINE='django.contrib.sessions.backends.db',
        SESSION_SERIALIZER='django.contrib.sessions.serializers.JSONSerializer',
    )

django.setup()

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.backends.base import SessionBase
import base64

def test_decode_invalid_session_data():
    """
    Test that decoding invalid session data with incorrect padding doesn't crash.

    This reproduces the issue where session data with invalid base64 padding
    causes a crash with "binascii.Error: Incorrect padding".
    """
    # Create a session store
    session = SessionStore()

    # Create invalid session data with incorrect padding
    # This simulates corrupted session data that might exist in the database
    invalid_session_data = "OWUzNTNmNWQxNTBjOWExZmM4MmQ3NzNhMDRmMjU4NmYwNDUyNGI2NDp7ImEgdGVzdCBrZXkiOiJhIHRlc3QgdmFsdWUifQ"  # Missing padding

    print(f"Testing with invalid session data: {invalid_session_data}")

    try:
        # This should not crash - it should return an empty dict
        result = session.decode(invalid_session_data)
        print(f"Decode result: {result}")
        print("Test passed - no crash occurred")
        return True
    except Exception as e:
        print(f"Test failed - exception occurred: {type(e).__name__}: {e}")
        return False

def test_decode_badsignature_with_invalid_padding():
    """
    Test that BadSignature exception with subsequent invalid padding is handled.

    This specifically tests the scenario from the issue where:
    1. signing.loads() raises BadSignature
    2. _legacy_decode() is called
    3. base64.b64decode() raises binascii.Error due to incorrect padding
    """
    session = SessionStore()

    # Create data that will:
    # 1. Fail signing.loads() with BadSignature
    # 2. Fail base64 decoding with incorrect padding
    # This is a string that looks like base64 but has invalid padding
    bad_session_data = "invalid:base64:data:with:bad:padding:xxx"

    print(f"Testing with bad signature data: {bad_session_data}")

    try:
        result = session.decode(bad_session_data)
        print(f"Decode result: {result}")
        print("Test passed - no crash occurred")
        return True
    except Exception as e:
        print(f"Test failed - exception occurred: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Testing issue: Decoding invalid session data crashes")
    print("=" * 70)

    # Test 1: Invalid padding
    print("\nTest 1: Invalid base64 padding")
    print("-" * 70)
    test1_passed = test_decode_invalid_session_data()

    # Test 2: Bad signature with invalid padding
    print("\nTest 2: Bad signature with invalid padding")
    print("-" * 70)
    test2_passed = test_decode_badsignature_with_invalid_padding()

    print("\n" + "=" * 70)
    print("Summary:")
    print(f"Test 1 (Invalid padding): {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Test 2 (Bad signature): {'PASSED' if test2_passed else 'FAILED'}")

    if test1_passed and test2_passed:
        print("\nAll tests PASSED - issue is fixed!")
        sys.exit(0)
    else:
        print("\nSome tests FAILED - issue still exists!")
        sys.exit(1)