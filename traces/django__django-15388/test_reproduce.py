#!/usr/bin/env python
"""
Test to reproduce the issue where dev server fails to restart after adding
BASE_DIR to TEMPLATES[0]['DIRS'] in settings.

The issue is that when BASE_DIR is in template directories, changes to .py files
(like settings.py) trigger template reloads, which causes the autoreload to fail.
The fix is to skip .py files in the template_changed function.
"""

from pathlib import Path
from unittest import mock
import sys
import os

# Add the testbed to the path
sys.path.insert(0, '/testbed')

# Create a minimal settings module in the current directory
settings_content = '''
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

SECRET_KEY = 'test-secret-key'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR],  # This is the problematic setting
        'APP_DIRS': True,
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
'''

# Write the settings file in the current directory
with open('/testbed/test_settings.py', 'w') as f:
    f.write(settings_content)

# Set up Django settings before importing Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

# Now import Django and the autoreload module
import django
from django.conf import settings
django.setup()

from django.template import autoreload

def test_py_file_in_template_dir():
    """
    Test that .py files in template directories don't trigger autoreload.

    On the buggy version (base commit), this will fail because .py files
    in template directories will trigger reset_loaders().

    On the fixed version (head commit), this will pass because .py files
    are skipped.
    """
    # Create a mock sender
    mock_sender = mock.MagicMock()

    # Create a path to a .py file that would be in the template directory
    # Since BASE_DIR is in template directories, any .py file in BASE_DIR
    # would trigger the bug
    py_file_path = Path(settings.BASE_DIR) / 'test_file.py'

    # Mock reset_loaders to track if it's called
    with mock.patch('django.template.autoreload.reset_loaders') as mock_reset:
        # Call template_changed with a .py file path
        result = autoreload.template_changed(mock_sender, py_file_path)

        # On the buggy version, reset_loaders will be called and return True
        # On the fixed version, reset_loaders will NOT be called and return None
        if result is True:
            # Buggy behavior: .py file triggered template reload
            print("BUG DETECTED: .py file in template directory triggered autoreload")
            print(f"File path: {py_file_path}")
            print(f"Template directories: {autoreload.get_template_directories()}")
            print(f"reset_loaders called: {mock_reset.called}")
            return False
        else:
            # Fixed behavior: .py file did not trigger template reload
            print("FIXED: .py file in template directory did not trigger autoreload")
            print(f"File path: {py_file_path}")
            print(f"Template directories: {autoreload.get_template_directories()}")
            print(f"reset_loaders called: {mock_reset.called}")
            return True

def test_html_file_in_template_dir():
    """
    Test that .html files in template directories DO trigger autoreload.

    This should always work correctly.
    """
    # Create a mock sender
    mock_sender = mock.MagicMock()

    # Create a path to an .html file in the template directory
    html_file_path = Path(settings.BASE_DIR) / 'templates' / 'test.html'

    # Mock reset_loaders to track if it's called
    with mock.patch('django.template.autoreload.reset_loaders') as mock_reset:
        # Call template_changed with an .html file path
        result = autoreload.template_changed(mock_sender, html_file_path)

        # This should always trigger autoreload
        if result is True and mock_reset.called:
            print("CORRECT: .html file in template directory triggered autoreload")
            return True
        else:
            print("ERROR: .html file in template directory did not trigger autoreload")
            return False

if __name__ == '__main__':
    print("Testing autoreload behavior with BASE_DIR in TEMPLATES['DIRS']")
    print("=" * 70)

    # Test 1: .py file should NOT trigger autoreload (this is the bug)
    print("\nTest 1: .py file in template directory")
    print("-" * 70)
    py_test_passed = test_py_file_in_template_dir()

    # Test 2: .html file should trigger autoreload (this should always work)
    print("\nTest 2: .html file in template directory")
    print("-" * 70)
    html_test_passed = test_html_file_in_template_dir()

    print("\n" + "=" * 70)
    print("RESULTS:")
    print(f"  .py file test: {'PASSED' if py_test_passed else 'FAILED'}")
    print(f"  .html file test: {'PASSED' if html_test_passed else 'FAILED'}")

    # The overall test passes only if:
    # 1. .py files don't trigger autoreload (the fix)
    # 2. .html files do trigger autoreload (expected behavior)
    if py_test_passed and html_test_passed:
        print("\nOVERALL: PASSED - Issue is fixed!")
        sys.exit(0)
    else:
        print("\nOVERALL: FAILED - Issue still exists!")
        sys.exit(1)