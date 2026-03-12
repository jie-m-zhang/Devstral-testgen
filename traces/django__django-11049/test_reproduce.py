#!/usr/bin/env python
"""
Test to reproduce the DurationField error message format issue.

The issue is that the error message for invalid DurationField format
currently says: "[DD] [HH:[MM:]]ss[.uuuuuu]"
But it should say: "[DD] [[HH:]MM:]ss[.uuuuuu]"

This test verifies that the error message uses the correct format.
"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        USE_TZ=True,
    )
    django.setup()

from django import forms
from django.core import exceptions
from django.db import models

def test_durationfield_error_message_format():
    """
    Test that the DurationField error message uses the correct format.

    The correct format should be: "[DD] [[HH:]MM:]ss[.uuuuuu]"
    This indicates that:
    - Seconds (ss) are mandatory
    - Minutes (MM) are optional
    - Hours (HH) are optional if minutes are provided
    """
    field = models.DurationField()

    # Try to clean an invalid duration value to trigger the error message
    try:
        field.clean('not a valid duration', None)
        print("ERROR: Expected ValidationError was not raised!")
        sys.exit(1)
    except exceptions.ValidationError as e:
        # Handle both list and string error messages
        if isinstance(e.message, list):
            error_message = str(e.message[0] % e.params)
        else:
            error_message = str(e.message % e.params)

        # Check if the error message contains the correct format
        # The correct format should be: "[DD] [[HH:]MM:]ss[.uuuuuu]"
        # The incorrect format is: "[DD] [HH:[MM:]]ss[.uuuuuu]"

        # Print ASCII-safe version
        safe_error_message = error_message.encode('ascii', 'ignore').decode('ascii')
        print(f"Error message received: {safe_error_message}")

        # The test should FAIL on base commit (buggy version)
        # and PASS on head commit (fixed version)
        if "[DD] [[HH:]MM:]ss[.uuuuuu]" in error_message:
            print("Test PASSED: Error message uses the correct format")
            return True
        elif "[DD] [HH:[MM:]]ss[.uuuuuu]" in error_message:
            print("Test FAILED: Error message uses the incorrect format")
            print("Expected: [DD] [[HH:]MM:]ss[.uuuuuu]")
            print("Got:      [DD] [HH:[MM:]]ss[.uuuuuu]")
            return False
        else:
            print(f"Test FAILED: Unexpected error message format: {safe_error_message}")
            return False

if __name__ == "__main__":
    success = test_durationfield_error_message_format()
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)