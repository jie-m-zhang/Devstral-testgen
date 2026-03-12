#!/usr/bin/env python
"""
Test to reproduce the file upload permissions issue.

The issue is that when FILE_UPLOAD_PERMISSIONS is not set (None),
files uploaded to FileSystemStorage can have inconsistent permissions:
- TemporaryUploadedFile (used for large files) creates files with 0o600 permissions
- MemoryUploadedFile (used for small files) creates files with different permissions

This test verifies that FILE_UPLOAD_PERMISSIONS has a default value of 0o644.
"""

import os
import sys
import tempfile
import shutil
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.conf')

import django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile, TemporaryUploadedFile
from django.core.files.storage import FileSystemStorage

# Configure minimal Django settings
if not settings.configured:
    # Don't set FILE_UPLOAD_PERMISSIONS - we want to test the default value
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        MEDIA_ROOT=tempfile.mkdtemp(),
        # FILE_UPLOAD_PERMISSIONS is intentionally not set here
        # to test the default value from global_settings
    )

def test_file_upload_permissions_default():
    """
    Test that FILE_UPLOAD_PERMISSIONS has a sensible default value.

    In the buggy version, FILE_UPLOAD_PERMISSIONS defaults to None.
    In the fixed version, it should default to 0o644.
    """
    print(f"FILE_UPLOAD_PERMISSIONS value: {settings.FILE_UPLOAD_PERMISSIONS}")
    print(f"FILE_UPLOAD_PERMISSIONS type: {type(settings.FILE_UPLOAD_PERMISSIONS)}")

    # The assertion that will fail on buggy code, pass on fixed code
    # In the buggy version, FILE_UPLOAD_PERMISSIONS is None
    # In the fixed version, FILE_UPLOAD_PERMISSIONS is 0o644 (420 in decimal)
    assert settings.FILE_UPLOAD_PERMISSIONS is not None, \
        "FILE_UPLOAD_PERMISSIONS should have a default value, not None"

    # Check that it's set to 0o644 (420 in decimal)
    assert settings.FILE_UPLOAD_PERMISSIONS == 0o644, \
        f"FILE_UPLOAD_PERMISSIONS should be 0o644, got {settings.FILE_UPLOAD_PERMISSIONS}"

    print("Test passed - FILE_UPLOAD_PERMISSIONS has correct default value")

def test_file_upload_permissions_with_storage():
    """
    Test that FileSystemStorage uses the correct permissions when saving files.

    This test creates a file using FileSystemStorage and verifies that
    the file permissions are set correctly.
    """
    # Create a test file
    test_content = b"test content for file upload"
    test_file = SimpleUploadedFile("test_file.txt", test_content)

    # Create storage instance
    storage = FileSystemStorage()

    # Save the file
    saved_name = storage.save("test_upload.txt", test_file)
    saved_path = storage.path(saved_name)

    try:
        # Check file permissions
        file_stats = os.stat(saved_path)
        file_mode = file_stats.st_mode & 0o777  # Get just the permission bits

        print(f"File permissions: {oct(file_mode)}")

        # The file should have 0o644 permissions if FILE_UPLOAD_PERMISSIONS is set correctly
        # Note: This might not work on all systems due to umask, but we can at least
        # verify that the setting is being used
        expected_mode = settings.FILE_UPLOAD_PERMISSIONS
        if expected_mode is not None:
            assert file_mode == expected_mode, \
                f"File permissions should be {oct(expected_mode)}, got {oct(file_mode)}"

        print("Test passed - file has correct permissions")
    finally:
        # Clean up
        if os.path.exists(saved_path):
            os.remove(saved_path)

if __name__ == "__main__":
    # Run the tests
    try:
        test_file_upload_permissions_default()
        test_file_upload_permissions_with_storage()
        print("\nAll tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)