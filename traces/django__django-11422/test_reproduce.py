#!/usr/bin/env python
"""
Test to reproduce the issue where Autoreloader with StatReloader doesn't track changes in manage.py.

The issue is that when manage.py is run, it becomes the '__main__' module.
The buggy code skips modules that don't have a '__spec__' attribute, and '__main__'
modules often don't have '__spec__' set. The fix adds special handling for '__main__'
modules to use their '__file__' attribute instead.
"""

import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType

# Add the django directory to the path so we can import from it
sys.path.insert(0, '/testbed')

from django.utils.autoreload import iter_modules_and_files

def test_issue_reproduction():
    """
    Test that __main__ module's file is tracked by the autoreloader.

    This test creates a mock __main__ module and verifies that its file
    is included in the list of files watched by the autoreloader.
    """
    # Create a temporary file to act as our "manage.py"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('#!/usr/bin/env python\nprint("test manage.py")\n')
        temp_file = f.name

    try:
        # Create a mock __main__ module
        main_module = ModuleType('__main__')
        main_module.__file__ = temp_file
        # __main__ modules typically don't have __spec__ set
        main_module.__spec__ = None

        # Add it to sys.modules
        sys.modules['__main__'] = main_module

        # Get the list of watched files
        watched_files = iter_modules_and_files(tuple(sys.modules.values()), frozenset())

        # Convert to a set of strings for easier comparison
        watched_files_str = {str(f) for f in watched_files}

        # The test should verify that the __main__ module's file is being watched
        print(f"Temp file path: {temp_file}")
        print(f"Watched files: {watched_files_str}")

        # This assertion will fail on buggy code (base commit) because __main__ module
        # without __spec__ is skipped, so the file won't be in watched_files
        # It will pass on fixed code (head commit) because __main__ module is handled specially
        assert temp_file in watched_files_str, f"Expected '{temp_file}' to be in watched files, but it wasn't. Watched files: {watched_files_str}"

        print("Test passed - issue is fixed")

    finally:
        # Clean up
        if '__main__' in sys.modules:
            del sys.modules['__main__']
        os.unlink(temp_file)

if __name__ == "__main__":
    test_issue_reproduction()