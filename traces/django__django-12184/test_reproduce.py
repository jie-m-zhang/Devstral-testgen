"""
Test to reproduce the issue with optional URL params crashing view functions.

The issue: When using optional named groups in re_path, if the optional group
is not matched, Django incorrectly passes positional arguments to the view
instead of just the matched kwargs.
"""

import sys
import django
from django.conf import settings
from django.urls import re_path
from django.http import HttpResponse
from django.test import RequestFactory

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        ROOT_URLCONF='test_reproduce',
        ALLOWED_HOSTS=['*'],
    )
    django.setup()

# Define a view function that accepts optional format parameter
def modules_view(request, format='html'):
    """View that accepts an optional format parameter with default value."""
    return HttpResponse(f"Format: {format}")

# Define URL patterns with optional named group
urlpatterns = [
    re_path(r'^module/(?P<format>(html|json|xml))?/?$', modules_view, name='modules'),
]

# Test the issue
def test_optional_url_param():
    """
    Test that optional URL parameters work correctly.

    This test should FAIL on the buggy version (base commit) because:
    - When accessing /module/ (without format), the view receives 3 positional args
    - The view only accepts 1-2 args (request, format='html')
    - This causes: TypeError: modules_view() takes from 1 to 2 positional arguments but 3 were given

    This test should PASS on the fixed version (head commit) because:
    - When accessing /module/ (without format), the view receives only kwargs
    - The kwargs will be empty (format is optional and not provided)
    - The view's default parameter value will be used
    """
    from django.urls import resolve

    # Test case 1: URL without optional parameter
    print("Test 1: Resolving /module/ (without format parameter)")
    try:
        match = resolve('/module/')
        print(f"  match.args: {match.args}")
        print(f"  match.kwargs: {match.kwargs}")

        # The bug: args should be empty, but on buggy version it contains (None,)
        # This causes the view to receive extra positional arguments
        if match.args != ():
            print(f"  ERROR: Expected empty args, got {match.args}")
            print("  This will cause TypeError when calling the view!")
            return False

        # Simulate calling the view
        factory = RequestFactory()
        request = factory.get('/module/')
        try:
            response = modules_view(request, **match.kwargs)
            print(f"  SUCCESS: View called successfully, response: {response.status_code}")
        except TypeError as e:
            print(f"  ERROR: {e}")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    # Test case 2: URL with optional parameter
    print("\nTest 2: Resolving /module/json/ (with format parameter)")
    try:
        match = resolve('/module/json/')
        print(f"  match.args: {match.args}")
        print(f"  match.kwargs: {match.kwargs}")

        if match.args != ():
            print(f"  ERROR: Expected empty args, got {match.args}")
            return False

        if match.kwargs.get('format') != 'json':
            print(f"  ERROR: Expected format='json', got {match.kwargs}")
            return False

        # Simulate calling the view
        factory = RequestFactory()
        request = factory.get('/module/json/')
        try:
            response = modules_view(request, **match.kwargs)
            print(f"  SUCCESS: View called successfully, response: {response.status_code}")
        except TypeError as e:
            print(f"  ERROR: {e}")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    print("\nAll tests passed!")
    return True

if __name__ == '__main__':
    success = test_optional_url_param()
    if success:
        print("\nTest PASSED - Issue is fixed")
        sys.exit(0)
    else:
        print("\nTest FAILED - Issue reproduced")
        sys.exit(1)