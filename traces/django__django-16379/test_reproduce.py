#!/usr/bin/env python
"""
Test to reproduce the race condition in FileBasedCache.has_key()

The issue occurs when:
1. has_key() checks if a file exists with os.path.exists() - returns True
2. Between that check and the open() call, another thread/process deletes the file
3. This causes a FileNotFoundError to be raised

The fix wraps the open() call in a try-except to handle FileNotFoundError.
"""
import os
import sys
import tempfile
import pickle
import zlib
import time
from django.core.cache.backends.filebased import FileBasedCache

def test_race_condition_via_monkey_patch():
    """
    Test that directly simulates the race condition by monkey-patching
    the open() function to delete the file after exists check.
    """
    # Create a temporary directory for the cache
    cache_dir = tempfile.mkdtemp()

    try:
        # Create a FileBasedCache instance
        cache = FileBasedCache(cache_dir, params={})

        # Create a cache entry manually
        test_key = "test_key_race"
        cache_file = cache._key_to_file(test_key)

        # Create a valid cache file
        expiry = time.time() + 300  # 5 minutes in the future
        value = "test_value"
        with open(cache_file, "wb") as f:
            f.write(pickle.dumps(expiry, cache.pickle_protocol))
            f.write(zlib.compress(pickle.dumps(value, cache.pickle_protocol)))

        # Verify the file exists
        assert os.path.exists(cache_file), "Cache file should exist"

        # Track if open was called
        open_called = False

        # Monkey-patch the built-in open function
        original_open = open
        def patched_open(file, *args, **kwargs):
            nonlocal open_called
            # If this is the cache file being opened in read-binary mode
            if file == cache_file and 'rb' in args:
                open_called = True
                # Simulate race condition: delete the file just before opening
                if os.path.exists(cache_file):
                    os.remove(cache_file)
            return original_open(file, *args, **kwargs)

        # Apply the patch
        import builtins
        original_builtins_open = builtins.open
        builtins.open = patched_open

        try:
            # Call has_key which should trigger the race condition
            result = cache.has_key(test_key)

            # Restore original open
            builtins.open = original_builtins_open

            # If we get here without exception, check the result
            if open_called:
                print(f"has_key returned: {result} (open was called, race condition triggered)")
                # In the buggy version, this would have raised FileNotFoundError
                # In the fixed version, it returns False
                assert result == False, "has_key should return False when file is deleted during race"
                print("TEST PASSED - Race condition handled correctly")
                return True
            else:
                print("has_key returned: {result} (open was not called, file didn't exist)")
                # File didn't exist, so no race condition occurred
                return True

        except FileNotFoundError as e:
            # Restore original open
            builtins.open = original_builtins_open
            # This is the bug - FileNotFoundError should be caught internally
            print(f"TEST FAILED - FileNotFoundError raised: {e}")
            print("This is the bug: has_key() should handle FileNotFoundError gracefully")
            return False
        finally:
            cache.clear()

    finally:
        # Clean up the cache directory
        import shutil
        shutil.rmtree(cache_dir, ignore_errors=True)

def test_expired_cache_race():
    """
    Test the race condition that occurs when _is_expired deletes the file
    while another thread is checking has_key.
    """
    # Create a temporary directory for the cache
    cache_dir = tempfile.mkdtemp()

    try:
        # Create a FileBasedCache instance
        cache = FileBasedCache(cache_dir, params={})

        # Create a cache entry with expired timeout
        test_key = "test_key_expired"
        test_value = "test_value"
        cache.set(test_key, test_value, timeout=-10)  # Already expired 10 seconds ago

        # Get the cache file path
        cache_file = cache._key_to_file(test_key)

        # Verify the file exists
        assert os.path.exists(cache_file), "Cache file should exist"

        # Call has_key multiple times to increase chance of race condition
        # The _is_expired method will delete the file
        for i in range(10):
            try:
                result = cache.has_key(test_key)
                # If the file was deleted by _is_expired, it should return False
                # without raising an exception
                if not os.path.exists(cache_file):
                    print(f"File deleted by _is_expired, has_key returned: {result}")
                    assert result == False, "has_key should return False for deleted expired cache"
                    print("TEST PASSED - Expired cache race condition handled")
                    return True
            except FileNotFoundError as e:
                print(f"TEST FAILED - FileNotFoundError raised: {e}")
                print("This is the bug: has_key() should handle FileNotFoundError gracefully")
                return False

        # If we get here, the file wasn't deleted yet, but that's okay
        print("File not yet deleted by _is_expired, but no exception raised")
        return True

    finally:
        # Clean up the cache directory
        import shutil
        shutil.rmtree(cache_dir, ignore_errors=True)

if __name__ == "__main__":
    print("Testing FileBasedCache.has_key() race condition...")
    print("=" * 60)

    # Run the monkey-patch test
    print("Running monkey-patch race condition test...")
    monkey_test_passed = test_race_condition_via_monkey_patch()

    # Run the expired cache test
    print("\n" + "=" * 60)
    print("Running expired cache race condition test...")
    expired_test_passed = test_expired_cache_race()

    print("\n" + "=" * 60)
    if monkey_test_passed and expired_test_passed:
        print("ALL TESTS PASSED - Issue is fixed!")
        sys.exit(0)
    else:
        print("TESTS FAILED - Issue still exists!")
        sys.exit(1)