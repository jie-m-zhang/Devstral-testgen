#!/usr/bin/env python
"""
Test to reproduce the issue where accessing UserAdmin via to_field leads to
broken PasswordResetForm link (404).

The issue is that when UserAdmin is accessed via a to_field (e.g., uuid),
the URL structure changes but the password reset link in UserChangeForm still
uses a hardcoded relative path "../password/" which doesn't work correctly.

The fix changes the URL format to always use ../../{pk}/password/ which works
correctly in both cases.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
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
            'django.contrib.sessions',
            'django.contrib.admin',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

    django.setup()

# Run migrations
from django.core.management import call_command
call_command('migrate', '--run-syncdb', verbosity=0)

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.http import HttpRequest
from django.urls import reverse, NoReverseMatch
from django.test.utils import override_settings
import uuid

class TestUserChangeFormWithToField(TestCase):
    """Test that UserChangeForm generates correct password reset links when accessed via to_field."""

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.user.save()

        # Create an admin site
        self.site = AdminSite()

    def test_password_reset_link_format(self):
        """
        Test that password reset link uses the correct format.

        The bug was that the URL was hardcoded as "../password/" which doesn't
        work when UserAdmin is accessed via a to_field parameter.

        The fix changes it to use "../../{pk}/password/" which works correctly
        in both cases (access via pk and access via to_field).
        """
        # Create a form with the user instance
        form = UserChangeForm(instance=self.user)

        # Get the password field's help_text
        password_field = form.fields.get('password')
        self.assertIsNotNone(password_field, "Password field should exist")

        help_text = password_field.help_text

        # The help_text should contain a link
        self.assertIn('href=', help_text, "Help text should contain a link")

        # Extract the URL from the help_text
        import re
        match = re.search(r'href="([^"]*)"', help_text)
        self.assertIsNotNone(match, "Should find href in help_text")

        reset_url = match.group(1)
        print(f"Password reset URL: {reset_url}")

        # The correct URL format should be ../../{pk}/password/
        expected_correct_url = f"../../{self.user.pk}/password/"
        print(f"Expected correct URL: {expected_correct_url}")

        # This assertion will:
        # - FAIL on the buggy version (base commit) where URL is '../password/'
        # - PASS on the fixed version (head commit) where URL is '../../{pk}/password/'
        self.assertEqual(
            reset_url,
            expected_correct_url,
            f"Password reset URL should be '{expected_correct_url}' to work correctly with to_field, but got '{reset_url}'"
        )

if __name__ == '__main__':
    # Run the test
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUserChangeFormWithToField)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)