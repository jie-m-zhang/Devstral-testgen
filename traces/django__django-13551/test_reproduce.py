#!/usr/bin/env python
"""
Test to reproduce the issue where changing a user's email could invalidate password reset tokens.

The test should:
1. Create a user with email foo@test.com
2. Generate a password reset token
3. Change the user's email to bar@test.com
4. Verify the token is now invalid (should fail on buggy version, pass on fixed version)
"""

import sys
import os

# Add tests directory to path
sys.path.insert(0, '/testbed/tests')

# Configure Django settings before importing models
from auth_tests.settings import *
from django.conf import settings

# Configure INSTALLED_APPS
settings.configure(
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    SECRET_KEY='test-secret-key',
    PASSWORD_RESET_TIMEOUT=3600,
    USE_TZ=True,
)

import django
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.management import call_command

def test_email_change_invalidates_token():
    """Test that changing a user's email invalidates password reset tokens."""

    # Create tables
    call_command('migrate', '--run-syncdb', verbosity=0)

    # Create a user with email foo@test.com
    user = User.objects.create_user('testuser', 'foo@test.com', 'testpass123')

    # Generate a password reset token
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)

    # Verify the token is valid initially
    assert token_generator.check_token(user, token), "Token should be valid initially"

    # Change the user's email
    user.email = 'bar@test.com'
    user.save()

    # Refresh user from database
    user = User.objects.get(pk=user.pk)

    # The token should now be invalid because the email changed
    # This assertion will FAIL on the buggy version (token still valid)
    # This assertion will PASS on the fixed version (token invalidated)
    assert not token_generator.check_token(user, token), "Token should be invalid after email change"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_email_change_invalidates_token()