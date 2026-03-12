#!/usr/bin/env python
"""
Test to reproduce the issue where django-admin startapp with trailing slash
in directory name results in error.

The issue is that when a directory name has a trailing slash (e.g., "mydir/"),
os.path.basename() returns an empty string, which then fails validation.
"""

import os
import sys
import tempfile
import shutil
from io import StringIO

# Add the Django testbed to the path
sys.path.insert(0, '/testbed')

# Set up Django
import django
from django.conf import settings
from django.core.management import call_command, CommandError

def test_startapp_with_trailing_slash():
    """
    Test that startapp works with a trailing slash in the directory name.

    This test should:
    - FAIL on the base commit (29345aecf6) because basename() returns empty string
    - PASS on the head commit (475cffd1d) because the fix uses top_dir instead
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a subdirectory where we'll try to create the app
        test_dir = os.path.join(tmpdir, "myapps")
        os.makedirs(test_dir, exist_ok=True)

        # Change to the temp directory
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Try to create an app with trailing slash - this should work
            # On buggy version, this will fail with:
            # CommandError: '' is not a valid app directory. Please make sure the directory is a valid identifier.
            app_name = "testapp"
            target_dir = os.path.join(test_dir, "")  # Add trailing slash

            print(f"Creating app '{app_name}' in directory '{target_dir}'")
            print(f"Directory exists: {os.path.exists(test_dir)}")

            # This should work but will fail on buggy version
            try:
                call_command('startapp', app_name, target_dir)
                print("SUCCESS: App created successfully with trailing slash!")
                return True
            except CommandError as e:
                error_msg = str(e)
                print(f"FAILED: CommandError occurred: {error_msg}")
                if "'' is not a valid app directory" in error_msg:
                    print("This is the expected error on the buggy version")
                    return False
                else:
                    print(f"Unexpected error: {error_msg}")
                    raise

        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    # Configure minimal Django settings
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

    print("Testing django-admin startapp with trailing slash in directory name...")
    print("=" * 70)

    success = test_startapp_with_trailing_slash()

    print("=" * 70)
    if success:
        print("TEST PASSED - Issue is fixed!")
        sys.exit(0)
    else:
        print("TEST FAILED - Issue reproduced!")
        sys.exit(1)