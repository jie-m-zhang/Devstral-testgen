#!/usr/bin/env python
"""
Test to reproduce the issue where tmpdir creation fails when the username
contains illegal characters for directory names.

This test sets the LOGNAME environment variable to a value with illegal
characters and then tries to create a temporary directory.
This should fail on the base commit and pass on the head commit.
"""
import os
import sys
import tempfile
from pathlib import Path
from _pytest.tmpdir import TempPathFactory, get_user

def test_tmpdir_with_illegal_username():
    """
    Test that tmpdir creation works even when username contains illegal characters.

    This reproduces the issue where getpass.getuser() returns a username with
    characters that are not allowed for directory names.
    """
    # Save original environment variables
    original_logname = os.environ.get('LOGNAME')
    original_user = os.environ.get('USER')
    original_username = os.environ.get('USERNAME')

    # Set LOGNAME to a value with illegal characters
    # Use a forward slash which is illegal in directory names on Windows
    # and also problematic on Linux
    os.environ['LOGNAME'] = 'contoso/john_doe'

    try:
        # Create a minimal config-like object
        class FakeConfig:
            basetemp = None
            trace = lambda self, *args: None
            option = lambda: None

        config = FakeConfig()
        factory = TempPathFactory(given_basetemp=None, trace=config.trace, _ispytest=True)

        # Try to get the base temp directory - this should fail on base commit
        # because it will try to create a directory with illegal characters
        basetemp = factory.getbasetemp()

        print(f"SUCCESS: Base temp directory created at: {basetemp}")

        # If we get here, the directory was created successfully
        return True

    except (FileNotFoundError, OSError) as e:
        # This is the expected failure on the base commit
        print(f"FAILED: Directory creation failed with error: {e}")
        return False
    finally:
        # Restore original environment variables
        if original_logname is not None:
            os.environ['LOGNAME'] = original_logname
        elif 'LOGNAME' in os.environ:
            del os.environ['LOGNAME']

        if original_user is not None:
            os.environ['USER'] = original_user
        elif 'USER' in os.environ:
            del os.environ['USER']

        if original_username is not None:
            os.environ['USERNAME'] = original_username
        elif 'USERNAME' in os.environ:
            del os.environ['USERNAME']

def test_get_user_with_illegal_chars():
    """
    Test that get_user() returns the problematic username.
    """
    # Save original environment variables
    original_logname = os.environ.get('LOGNAME')

    # Set LOGNAME to a value with illegal characters
    os.environ['LOGNAME'] = 'contoso/john_doe'

    try:
        user = get_user()
        print(f"get_user() returned: {user}")
        assert user is not None, "get_user() should return a value"
        assert '/' in user, f"Expected forward slash in username, got: {user}"
        print("get_user() test passed")
        return True
    finally:
        # Restore original environment
        if original_logname is not None:
            os.environ['LOGNAME'] = original_logname
        elif 'LOGNAME' in os.environ:
            del os.environ['LOGNAME']

if __name__ == "__main__":
    print("Testing get_user() with illegal characters...")
    if not test_get_user_with_illegal_chars():
        print("get_user() test failed - environment setup issue")
        sys.exit(1)

    print("\nTesting tmpdir creation with illegal username...")
    success = test_tmpdir_with_illegal_username()

    if success:
        print("\nTest PASSED - tmpdir creation succeeded")
        sys.exit(0)
    else:
        print("\nTest FAILED - tmpdir creation failed (expected on base commit)")
        sys.exit(1)