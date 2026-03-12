#!/usr/bin/env python
"""
Test to reproduce the issue where the 'model' key is missing from app_list context.

This test should:
- FAIL on base commit (0456d3e42795481a186db05719300691fe2a1029) - 'model' key is missing
- PASS on head commit (3733ae895780f17430924f1e20ee320556c62d05) - 'model' key is present
"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings
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
            'django.contrib.admin',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

# Setup Django
django.setup()

# Now import Django components
from django.contrib import admin
from django.contrib.auth.models import User
from django.test import RequestFactory

def test_model_in_app_list_context():
    """
    Test that the 'model' key is present in the app_list context.

    This reproduces the issue where users need access to the model class
    in the app_list context for custom admin views.
    """
    # Create an admin site
    site = admin.AdminSite(name="test_site")

    # Register a model
    site.register(User)

    # Create a mock request with a superuser
    factory = RequestFactory()
    request = factory.get('/admin/')
    request.user = User(username='admin', is_staff=True, is_superuser=True, is_active=True)

    # We need to mock the reverse function to avoid URL resolution issues
    # The actual test is about the structure of the model_dict, not the URLs
    original_reverse = None
    try:
        from django.urls import reverse
        original_reverse = reverse

        def mock_reverse(viewname, *args, **kwargs):
            # Return a dummy URL for testing purposes
            return f"/admin/{viewname}/"

        # Monkey patch reverse temporarily
        from django.urls import reverse
        import django.contrib.admin.sites
        django.urls.reverse = mock_reverse
        django.contrib.admin.sites.reverse = mock_reverse

        # Call _build_app_dict directly to get the app dictionary
        app_dict = site._build_app_dict(request)

        # Verify we have at least one app
        assert len(app_dict) > 0, "No apps found in app_dict"

        # Get the first app
        app_label = list(app_dict.keys())[0]
        first_app = app_dict[app_label]

        # Verify the app has models
        assert len(first_app['models']) > 0, "No models found in app"

        # Get the first model
        first_model = first_app['models'][0]

        # Check if 'model' key exists in the model dict
        # This is the key assertion that will:
        # - FAIL on base commit (where 'model' key is missing)
        # - PASS on head commit (where 'model' key is present)
        assert 'model' in first_model, "Missing 'model' key in model dict - this is the bug!"

        # Verify the model key contains the actual model class
        assert first_model['model'] == User, f"Expected User model, got {first_model['model']}"

        print("✓ Test passed: 'model' key is present in app_list context")
        return True

    finally:
        # Restore original reverse function
        if original_reverse:
            from django.urls import reverse
            import django.contrib.admin.sites
            django.urls.reverse = original_reverse
            django.contrib.admin.sites.reverse = original_reverse

if __name__ == '__main__':
    try:
        test_model_in_app_list_context()
        print("\n✓ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)