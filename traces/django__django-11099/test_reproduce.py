#!/usr/bin/env python
"""
Test to reproduce the issue where UsernameValidator allows trailing newlines.

The issue: ASCIIUsernameValidator and UnicodeUsernameValidator use the regex
r'^[\w.@+-]+$' which incorrectly allows usernames ending with newlines because
$ matches trailing newlines in Python regexes.

The fix: Change the regex to r'\A[\w.@+-]+\Z' to properly reject such usernames.
"""

import sys
import os

# Add the Django project to the path
sys.path.insert(0, '/testbed')

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
    )
    django.setup()

from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.core.exceptions import ValidationError

def test_trailing_newline_in_username():
    """
    Test that usernames with trailing newlines are properly rejected.

    This test should:
    - FAIL on the buggy version (base commit) because it incorrectly accepts newlines
    - PASS on the fixed version (head commit) because it correctly rejects newlines
    """
    ascii_validator = ASCIIUsernameValidator()
    unicode_validator = UnicodeUsernameValidator()

    # Test cases with trailing newlines
    test_usernames_with_newlines = [
        'validuser\n',
        'test123\n',
        'user@domain\n',
        'user.name\n',
        'user-name\n',
        'user+name\n',
    ]

    # Test cases without newlines (should always be valid)
    test_usernames_valid = [
        'validuser',
        'test123',
        'user@domain',
        'user.name',
        'user-name',
        'user+name',
    ]

    print("Testing ASCIIUsernameValidator...")
    # Valid usernames should always pass
    for username in test_usernames_valid:
        try:
            ascii_validator(username)
            print("  [OK] Valid username '%s' accepted" % username)
        except ValidationError as e:
            print("  [FAIL] Valid username '%s' rejected: %s" % (username, e))
            return False

    # Usernames with trailing newlines should be rejected
    for username in test_usernames_with_newlines:
        try:
            ascii_validator(username)
            print("  [FAIL] Username with trailing newline '%s' incorrectly accepted" % repr(username))
            return False
        except ValidationError as e:
            print("  [OK] Username with trailing newline '%s' correctly rejected" % repr(username))

    print("\nTesting UnicodeUsernameValidator...")
    # Valid usernames should always pass
    for username in test_usernames_valid:
        try:
            unicode_validator(username)
            print("  [OK] Valid username '%s' accepted" % username)
        except ValidationError as e:
            print("  [FAIL] Valid username '%s' rejected: %s" % (username, e))
            return False

    # Usernames with trailing newlines should be rejected
    for username in test_usernames_with_newlines:
        try:
            unicode_validator(username)
            print("  [FAIL] Username with trailing newline '%s' incorrectly accepted" % repr(username))
            return False
        except ValidationError as e:
            print("  [OK] Username with trailing newline '%s' correctly rejected" % repr(username))

    print("\n[SUCCESS] All tests passed - issue is fixed")
    return True

if __name__ == "__main__":
    success = test_trailing_newline_in_username()
    if not success:
        print("\n[FAIL] Test failed - issue reproduced")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Test passed - issue is fixed")
        sys.exit(0)