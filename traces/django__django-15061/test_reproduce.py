#!/usr/bin/env python
"""
Test to reproduce the issue with MultiWidget's id_for_label method.

The issue is that MultiWidget.id_for_label() adds '_0' to the id, which doesn't make sense.
The fix is to return an empty string instead.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, '/testbed')

# Minimal Django settings for testing
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        USE_TZ=True,
    )

django.setup()

from django.forms.widgets import MultiWidget, TextInput

def test_multiwidget_id_for_label():
    """
    Test that MultiWidget.id_for_label() returns an empty string.

    On the buggy version, it will return 'test_id_0' (fails the assertion).
    On the fixed version, it will return '' (passes the assertion).
    """
    # Create a simple MultiWidget with TextInput widgets
    widget = MultiWidget([TextInput, TextInput])

    # Test the id_for_label method
    test_id = 'test_id'
    result = widget.id_for_label(test_id)

    # The expected behavior is to return an empty string
    # This will fail on the buggy version (returns 'test_id_0')
    # This will pass on the fixed version (returns '')
    assert result == '', f"Expected empty string, got '{result}'"

    print(f"Test passed! id_for_label('{test_id}') returned '{result}'")

if __name__ == '__main__':
    test_multiwidget_id_for_label()