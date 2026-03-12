"""
Test to reproduce the issue with check_for_template_tags_with_the_same_name
when libraries are added to TEMPLATES['OPTIONS']['libraries'].

The issue is that the same library path gets added twice (once from custom_libraries
and once from get_template_tag_modules()), causing a false positive error about
duplicate template tag modules.
"""

import os
import sys
import django
from django.conf import settings

# Add the testbed and tests directory to the path
sys.path.insert(0, '/testbed')
sys.path.insert(0, '/testbed/tests')

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
            # Add a test app with template tags
            'check_framework.template_test_apps.same_tags_app_1',
        ],
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'OPTIONS': {
                    # This is the key part - adding a library that also exists
                    # as a template tag module in an installed app
                    'libraries': {
                        'same_tags': 'check_framework.template_test_apps.same_tags_app_1.templatetags.same_tags',
                    },
                },
            },
        ],
    )

    django.setup()

from django.core.checks.templates import check_for_template_tags_with_the_same_name

def test_issue_reproduction():
    """
    Test that adding a library to TEMPLATES['OPTIONS']['libraries'] that also
    exists as a template tag module doesn't cause a false positive error.
    """
    print("Running test to reproduce the issue...")

    # Run the check
    errors = check_for_template_tags_with_the_same_name(None)

    # Print the errors for debugging
    print(f"Number of errors found: {len(errors)}")
    for error in errors:
        print(f"Error: {error}")

    # The test should pass if there are NO errors
    # On the buggy version (base commit), this will fail because it will report
    # a false duplicate (the same library path appears twice)
    # On the fixed version (head commit), this will pass because the set will
    # handle duplicates correctly

    if errors:
        print("FAIL: Found false positive errors about duplicate template tags")
        print("This is the bug - the same library is being counted twice")
        return False
    else:
        print("PASS: No false positive errors found")
        return True

if __name__ == "__main__":
    success = test_issue_reproduction()
    if not success:
        print("\nTest FAILED - issue reproduced (this is expected on base commit)")
        sys.exit(1)
    else:
        print("\nTest PASSED - issue is fixed (this is expected on head commit)")
        sys.exit(0)