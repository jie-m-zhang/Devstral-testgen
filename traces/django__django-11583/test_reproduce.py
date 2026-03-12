#!/usr/bin/env python
"""
Test to reproduce the "ValueError: embedded null byte" issue in autoreload.

The issue occurs when path.resolve() is called on a path that contains
embedded null bytes, which can happen on network filesystems or mount points.

The test directly patches Path.resolve to raise ValueError to simulate the issue.
"""
import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest.mock import patch, MagicMock

# Add the testbed to the path so we can import django.utils.autoreload
sys.path.insert(0, '/testbed')

from django.utils.autoreload import iter_modules_and_files

def test_embedded_null_byte_with_patch():
    """
    Test that patches pathlib.Path.resolve to raise ValueError with "embedded null byte".

    This simulates what happens on network filesystems when path.resolve()
    encounters a path with embedded null bytes.
    """
    # Create a real temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tmp:
        tmp.write(b'# test module')
        tmp_path = tmp.name

    try:
        # Create a mock module that looks like a real module
        mock_module = MagicMock(spec=ModuleType)
        mock_module.__name__ = 'test_module'  # Not '__main__'
        mock_module.__spec__ = MagicMock()
        mock_module.__spec__.has_location = True
        mock_module.__spec__.origin = tmp_path
        mock_module.__spec__.loader = MagicMock()  # Not a zipimporter

        # We need to patch the resolve method on Path instances
        # Let's patch it at the module level where it's used
        import django.utils.autoreload as autoreload_module

        original_resolve = Path.resolve
        resolve_called = False

        def mock_resolve(self, *args, **kwargs):
            nonlocal resolve_called
            resolve_called = True
            # Check if this is our test path
            if str(self) == tmp_path:
                # Simulate the exact error from the issue
                print(f"Mock resolve called with path: {self}")
                raise ValueError("embedded null byte")
            return original_resolve(self, *args, **kwargs)

        # Patch Path.resolve where it's used
        with patch.object(autoreload_module.Path, 'resolve', mock_resolve):
            modules = (mock_module,)  # Must be a tuple
            extra_files = frozenset()

            # Clear cache
            iter_modules_and_files.cache_clear()

            # This should either:
            # - Raise ValueError on buggy version (before fix)
            # - Return successfully on fixed version (after fix)
            result = iter_modules_and_files(modules, extra_files)

            print(f"Resolve was called: {resolve_called}")

            # If we get here, the fix is working
            print("Test passed - ValueError was handled gracefully")
            return True

    except ValueError as e:
        if "embedded null byte" in str(e):
            print(f"Test failed (as expected on buggy version) - ValueError: {e}")
            return False
        else:
            # Some other ValueError - re-raise
            raise
    finally:
        # Clean up
        try:
            os.unlink(tmp_path)
        except:
            pass

if __name__ == "__main__":
    print("Running test_embedded_null_byte_with_patch...")
    result = test_embedded_null_byte_with_patch()

    if result:
        print("\n=== TEST PASSED ===")
        print("The fix is working - ValueError is being handled gracefully")
        sys.exit(0)
    else:
        print("\n=== TEST FAILED ===")
        print("ValueError is not being handled - this is the buggy version")
        sys.exit(1)