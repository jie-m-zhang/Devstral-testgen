#!/usr/bin/env python
"""
Test to reproduce the issue with customizable management command formatters.

The issue is that when a command has a help text with newlines, users cannot
use custom formatters (like RawDescriptionHelpFormatter) to preserve the formatting.

In the buggy version, formatter_class is passed as a positional argument to
CommandParser, which means custom formatters cannot override it. In the fixed
version, formatter_class is set as a default in kwargs, allowing custom
formatters to override it.
"""

import os
import sys
import io
from argparse import ArgumentParser, RawDescriptionHelpFormatter

# Add the testbed to the path so we can import Django
sys.path.insert(0, '/testbed')

# Set up minimal Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
import django
from django.conf import settings

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
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.core.management.base import BaseCommand, CommandParser

class TestCommand(BaseCommand):
    """Test command with multi-line help text."""
    help = '''Import a contract from tzkt.
Example usage:
    ./manage.py tzkt_import 'Tezos Mainnet' KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
'''

    def add_arguments(self, parser):
        parser.add_argument('blockchain', help='Name of the blockchain to import into')
        parser.add_argument('target', help='Id of the contract to import')

    def handle(self, *args, **options):
        pass

def test_custom_formatter_override():
    """
    Test that custom formatters can be passed and override the default.

    This is the core issue - in the buggy version, formatter_class is passed
    as a positional argument, so custom formatters cannot override it.

    The fix allows users to pass formatter_class as a kwarg to create_parser,
    which should override the default DjangoHelpFormatter.
    """
    cmd = TestCommand()

    # Try to create parser with custom formatter (RawDescriptionHelpFormatter)
    # This should work in the fixed version but fail in the buggy version
    try:
        parser = cmd.create_parser('manage.py', 'test_command', formatter_class=RawDescriptionHelpFormatter)
        print("SUCCESS: Custom formatter was accepted")

        # Check if the formatter is actually the custom one
        if parser.formatter_class is RawDescriptionHelpFormatter:
            print("PASS: Custom formatter is being used")
            return True
        else:
            print(f"FAIL: Custom formatter not used. Got {parser.formatter_class} instead of {RawDescriptionHelpFormatter}")
            return False

    except TypeError as e:
        if "multiple values for keyword argument 'formatter_class'" in str(e):
            print(f"FAIL: Buggy version - cannot override formatter_class: {e}")
            return False
        else:
            print(f"FAIL: Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"FAIL: Could not set custom formatter: {e}")
        return False

def test_default_formatter():
    """
    Test that the default formatter still works.
    """
    cmd = TestCommand()

    # Create parser without custom formatter
    parser = cmd.create_parser('manage.py', 'test_command')

    # Check if the default formatter is being used
    from django.core.management.base import DjangoHelpFormatter
    if parser.formatter_class is DjangoHelpFormatter:
        print("PASS: Default DjangoHelpFormatter is being used")
        return True
    else:
        print(f"FAIL: Default formatter not used. Got {parser.formatter_class}")
        return False

if __name__ == "__main__":
    print("Testing default formatter...")
    test1_passed = test_default_formatter()

    print("\n" + "="*60)
    print("Testing custom formatter override (main issue)...")
    test2_passed = test_custom_formatter_override()

    print("\n" + "="*60)
    if test1_passed and test2_passed:
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)