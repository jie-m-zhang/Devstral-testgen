#!/usr/bin/env python
"""
Test to reproduce the issue with empty string handling in If-Modified-Since header.

The issue: Empty string used to be ignored for If-Modified-Since header, but now raises exception.
"""

import sys
sys.path.insert(0, '/testbed')

from django.views.static import was_modified_since

def test_empty_string():
    """Test that empty string doesn't raise TypeError."""
    print("Testing empty string...")

    try:
        result = was_modified_since(header="", mtime=1000)
        print(f"Result: {result}")
        print("✓ No exception raised")
        return True
    except TypeError as e:
        print(f"✗ TypeError raised: {e}")
        return False
    except Exception as e:
        print(f"✗ Other exception: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_empty_string()
    sys.exit(0 if success else 1)