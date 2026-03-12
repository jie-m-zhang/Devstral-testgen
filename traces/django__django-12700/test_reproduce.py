#!/usr/bin/env python
"""
Test to reproduce the issue where settings with nested lists and tuples
are not properly cleansed by SafeExceptionReporterFilter.
"""

import os
import sys
import django
from pathlib import Path

# Add the testbed directory to the path
sys.path.insert(0, '/testbed')

# Configure Django settings before importing anything else
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        # This is the test setting with nested structures
        MY_SETTING={
            "foo": "value",
            "secret": "value",
            "token": "value",
            "something": [
                {"foo": "value"},
                {"secret": "value"},
                {"token": "value"},
            ],
            "else": [
                [
                    {"foo": "value"},
                    {"secret": "value"},
                    {"token": "value"},
                ],
                [
                    {"foo": "value"},
                    {"secret": "value"},
                    {"token": "value"},
                ],
            ],
            "with_tuple": (
                {"foo": "value"},
                {"secret": "value"},
                {"token": "value"},
            ),
        },
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
    )

# Now we can import Django components
from django.views.debug import SafeExceptionReporterFilter

def test_nested_structures_cleansing():
    """
    Test that nested structures (lists, tuples) in settings are properly cleansed.
    This should fail on the base commit and pass on the head commit.
    """
    filter_obj = SafeExceptionReporterFilter()
    safe_settings = filter_obj.get_safe_settings()

    my_setting = safe_settings.get('MY_SETTING', {})

    print("Testing nested structure cleansing...")
    print("=" * 60)

    # Test 1: Top-level sensitive keys should be cleansed
    print("\nTest 1: Top-level sensitive keys")
    print(f"  'secret' key: {my_setting.get('secret')}")
    print(f"  'token' key: {my_setting.get('token')}")
    assert my_setting.get('secret') == '********************', \
        f"Expected 'secret' to be '********************', got '{my_setting.get('secret')}'"
    assert my_setting.get('token') == '********************', \
        f"Expected 'token' to be '********************', got '{my_setting.get('token')}'"
    print("  Top-level sensitive keys are properly cleansed")

    # Test 2: Nested dictionaries in lists should be cleansed
    print("\nTest 2: Nested dictionaries in lists")
    something = my_setting.get('something', [])
    print(f"  'something' list: {something}")
    if len(something) >= 2:
        print(f"  'something[1]' (should have 'secret' cleansed): {something[1]}")
        assert something[1].get('secret') == '********************', \
            f"Expected 'something[1]['secret']' to be '********************', got '{something[1].get('secret')}'"
        print("  Nested dictionaries in lists are properly cleansed")

    # Test 3: Deeply nested structures should be cleansed
    print("\nTest 3: Deeply nested structures")
    else_list = my_setting.get('else', [])
    print(f"  'else' list: {else_list}")
    if len(else_list) >= 1 and len(else_list[0]) >= 2:
        print(f"  'else[0][1]' (should have 'secret' cleansed): {else_list[0][1]}")
        assert else_list[0][1].get('secret') == '********************', \
            f"Expected 'else[0][1]['secret']' to be '********************', got '{else_list[0][1].get('secret')}'"
        print("  Deeply nested structures are properly cleansed")

    # Test 4: Tuples should be cleansed
    print("\nTest 4: Tuples with nested dictionaries")
    with_tuple = my_setting.get('with_tuple')
    print(f"  'with_tuple': {with_tuple}")
    if with_tuple and len(with_tuple) >= 2:
        print(f"  'with_tuple[1]' (should have 'secret' cleansed): {with_tuple[1]}")
        assert with_tuple[1].get('secret') == '********************', \
            f"Expected 'with_tuple[1]['secret']' to be '********************', got '{with_tuple[1].get('secret')}'"
        print("  Tuples with nested dictionaries are properly cleansed")

    print("\n" + "=" * 60)
    print("All tests passed! Issue is fixed.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_nested_structures_cleansing()
        print("\nTest PASSED - All assertions passed")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTest FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest ERROR - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)