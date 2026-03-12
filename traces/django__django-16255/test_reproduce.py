"""
Test to reproduce the issue where sitemaps without items raise ValueError on callable lastmod.

The issue occurs when:
1. A sitemap has no items (items() returns empty list)
2. The sitemap has a callable lastmod method
3. get_latest_lastmod() is called (which happens when rendering the sitemap index)

Expected behavior: Should return None gracefully
Actual behavior (buggy): Raises ValueError: max() arg is an empty sequence
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, '/testbed')

# Create minimal settings
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
            'django.contrib.sitemaps',
            'django.contrib.sites',
        ],
        SITE_ID=1,
        SECRET_KEY='test-secret-key',
        ROOT_URLCONF='',
        USE_TZ=True,
    )

django.setup()

from django.contrib.sitemaps import Sitemap

class EmptySitemapWithCallableLastmod(Sitemap):
    """
    A sitemap with no items but with a callable lastmod.
    This should reproduce the ValueError issue.
    """
    def items(self):
        # Return empty list - no items
        return []

    def lastmod(self, item):
        # This is callable but will never be called since items() is empty
        return datetime(2023, 1, 1, 10, 0, 0)

def test_empty_sitemap_callable_lastmod():
    """
    Test that a sitemap with no items and callable lastmod doesn't raise ValueError.
    """
    sitemap = EmptySitemapWithCallableLastmod()

    # This should not raise ValueError
    # In the buggy version, this will raise: ValueError: max() arg is an empty sequence
    # In the fixed version, this will return None
    try:
        result = sitemap.get_latest_lastmod()
        # If we get here, the bug is fixed
        print(f"Test passed - get_latest_lastmod() returned: {result}")
        assert result is None, f"Expected None, got {result}"
        return True
    except ValueError as e:
        # This is the bug - ValueError should not be raised
        print(f"Test failed - ValueError raised: {e}")
        return False

if __name__ == "__main__":
    success = test_empty_sitemap_callable_lastmod()
    if success:
        print("\n✓ Test passed - issue is fixed")
        sys.exit(0)
    else:
        print("\n✗ Test failed - issue reproduced")
        sys.exit(1)