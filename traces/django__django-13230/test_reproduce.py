"""
Test to reproduce the issue with item_comments not being supported in syndication framework.

The issue is that the syndication framework doesn't pass the comments parameter
to feed.add_item() even though it's supported by the feedgenerator.
"""

import os
import sys
import django
from io import StringIO
from unittest.mock import Mock, patch

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.syndication_tests.settings')
sys.path.insert(0, '/testbed')

# Import after setting up Django path
from django.conf import settings

# Configure minimal settings if not already configured
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.sites',
            'django.contrib.syndication',
        ],
        SITE_ID=1,
    )

django.setup()

from django.contrib.syndication import views
from django.utils import feedgenerator
from django.test import RequestFactory

# Create a simple model-like object for testing
class MockEntry:
    def __init__(self, title, link):
        self.title = title
        self.link = link
        self.pk = 1

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.link

# Create a feed class that defines item_comments
class TestCommentsFeed(views.Feed):
    title = "Test Feed with Comments"
    link = "/test/"
    description = "Test feed to verify item_comments support"

    def items(self):
        return [MockEntry("Test Entry", "http://example.com/test/")]

    def item_comments(self, item):
        # This should be passed to feed.add_item() as the comments parameter
        return "http://example.com/test/comments/"

# Test function
def test_item_comments_support():
    """
    Test that item_comments is properly passed to feed.add_item().

    This test should FAIL on the base commit (184a6eebb0) because
    the comments parameter is not being passed to feed.add_item().

    It should PASS on the head commit (65dfb06a1) where the fix is applied.
    """
    # Create a request
    factory = RequestFactory()
    request = factory.get('/test/')

    # Create the feed
    feed = TestCommentsFeed()

    # Mock get_current_site to avoid database dependency
    with patch('django.contrib.syndication.views.get_current_site') as mock_site:
        mock_site.return_value.domain = 'example.com'
        mock_site.return_value = Mock()

        # Get the feed object
        feed_obj = feed.get_feed(None, request)

        # Check if the feed has items
        assert len(feed_obj.items) > 0, "Feed should have at least one item"

        # Get the first item
        item = feed_obj.items[0]

        # Check if comments is in the item
        # This is the critical assertion - it should fail on base commit
        # because comments won't be in the item dict
        assert 'comments' in item, "Item should have 'comments' key"

        # Check if the comments value is correct
        assert item['comments'] == "http://example.com/test/comments/", \
            f"Expected comments to be 'http://example.com/test/comments/', got '{item.get('comments')}'"

    print("Test passed - item_comments is properly supported")

if __name__ == "__main__":
    test_item_comments_support()