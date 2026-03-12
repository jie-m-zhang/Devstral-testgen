#!/usr/bin/env python
"""
Test to reproduce the issue where FilePathField doesn't accept a callable for the path parameter.

The issue is that when path is a callable, it should be called in the formfield method,
but in the buggy version it's passed directly without being called.
"""

import os
import sys
import tempfile
import shutil

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.conf.global_settings')
sys.path.insert(0, '/testbed')

import django
from django.conf import settings

# Configure minimal settings
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

from django.db import models
from django import forms

def test_filepathfield_callable_path():
    """
    Test that FilePathField accepts a callable for the path parameter.

    This test should FAIL on the buggy version (base commit) because the callable
    won't be called in formfield, causing the path to be the callable object itself
    rather than the result of calling it.

    It should PASS on the fixed version (head commit) where the callable is properly called.
    """

    # Create a temporary directory structure for testing
    temp_dir = tempfile.mkdtemp()
    test_subdir = os.path.join(temp_dir, 'test_files')
    os.makedirs(test_subdir, exist_ok=True)

    # Create some test files
    with open(os.path.join(test_subdir, 'file1.txt'), 'w') as f:
        f.write('test content 1')
    with open(os.path.join(test_subdir, 'file2.txt'), 'w') as f:
        f.write('test content 2')

    try:
        # Define a callable that returns the path
        def get_test_path():
            return test_subdir

        # Create a FilePathField with a callable path
        field = models.FilePathField(path=get_test_path, match='.*.txt$')

        # Create a form field from the model field
        form_field = field.formfield()

        # Check that the form field's path is the result of calling the callable
        # In the buggy version, this will be the callable object itself
        # In the fixed version, this will be the string path returned by the callable

        print(f"Form field path type: {type(form_field.path)}")
        print(f"Form field path value: {form_field.path}")

        # The assertion: form_field.path should be a string (the result of calling the callable)
        # not the callable object itself
        assert isinstance(form_field.path, str), \
            f"Expected form_field.path to be a string, but got {type(form_field.path)}"

        # Also check that the path is actually the test_subdir
        assert form_field.path == test_subdir, \
            f"Expected path to be '{test_subdir}', but got '{form_field.path}'"

        print("Test passed - FilePathField correctly handles callable path")

    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    test_filepathfield_callable_path()