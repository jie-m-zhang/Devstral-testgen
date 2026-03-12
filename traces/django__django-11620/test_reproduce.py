"""
Test to reproduce the issue where Http404 raised in a path converter's to_python
method does not result in a technical response when DEBUG is True.

The issue is that in django/views/debug.py, the technical_404_response function
tries to resolve the request path and catches Resolver404, but it should catch
Http404 instead when a path converter raises Http404.
"""

import sys
from django.http import Http404
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import path, register_converter
from django.views.debug import technical_404_response

class Http404Converter:
    """
    A path converter that raises Http404 in its to_python method.
    This simulates the scenario described in the issue.
    """
    regex = r'[0-9]+'

    def to_python(self, value):
        # Raise Http404 to signal that this value doesn't match
        raise Http404("Object not found")

    def to_url(self, value):
        return str(value)

def test_view(request, pk):
    """A simple view that should never be reached when the converter raises Http404."""
    return None

# Register the converter first
register_converter(Http404Converter, 'http404')

# Create URL patterns after registering the converter
urlpatterns = [
    path('test/<http404:pk>/', test_view),
]

@override_settings(DEBUG=True, ALLOWED_HOSTS=['testserver', 'localhost'])
class ConverterHttp404Test(SimpleTestCase):
    def test_converter_http404_technical_response(self):
        """
        Test that when a path converter raises Http404, it results in a
        technical 404 response (not a generic server error).

        This test should FAIL on the base commit and PASS on the head commit.

        The key difference:
        - Buggy version: Http404 from converter is NOT caught, so technical_404_response raises Http404
        - Fixed version: Http404 from converter IS caught, so technical_404_response renders the page
        """
        # Create a request factory
        rf = RequestFactory()

        # Create a request to a URL that uses our Http404Converter
        request = rf.get('/test/123/')
        request.path = '/test/123/'

        # Try to resolve the URL - this should raise Http404 from the converter
        from django.urls import resolve
        try:
            resolve('/test/123/')
            self.fail("Expected Http404 to be raised")
        except Http404 as e:
            # Now call technical_404_response with this exception
            # This is what happens internally when DEBUG=True
            try:
                response = technical_404_response(request, e)

                # The response should be a 404
                self.assertEqual(response.status_code, 404)

                # The response should contain technical 404 information
                content = response.content.decode('utf-8')

                # Debug: print more of the content
                print("=== Full Response Content ===")
                print(content)
                print("=== End Full Response Content ===")

                # Check that it's a technical 404 response (has debugging info)
                self.assertInHTML('Page not found <span>(404)</span>', content)

                print("[PASS] Test passed - Http404 in converter produces technical 404 response")
                return True
            except Http404 as e2:
                # This is the bug! The technical_404_response function is calling resolve()
                # which again raises Http404 from the converter, but it's only catching
                # Resolver404, not Http404. So the Http404 propagates up instead of being
                # handled to produce a technical 404 response.
                print("[FAIL] Http404 was not caught in technical_404_response - this is the bug!")
                print(f"Exception: {e2}")
                self.fail("Http404 raised in converter should be caught by technical_404_response")

if __name__ == '__main__':
    # Run the test
    import django
    from django.conf import settings

    # Configure Django settings if not already configured
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key',
            ROOT_URLCONF='test_reproduce',
            ALLOWED_HOSTS=['testserver', 'localhost'],
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    # Run the test
    test_case = ConverterHttp404Test()
    try:
        test_case.test_converter_http404_technical_response()
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAILURE] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)