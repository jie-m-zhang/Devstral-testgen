#!/usr/bin/env python
"""
Test to reproduce the issue with ManagementForm raising deprecation warnings
for "default.html" template usage.

The issue is that ManagementForm doesn't have a template_name set, so it uses
the default "django/forms/default.html" which triggers a RemovedInDjango50Warning.

The fix is to set template_name = "django/forms/div.html" in the ManagementForm class.
"""

import warnings
import os
import sys
import django
from django import conf
from io import StringIO

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
if not conf.settings.configured:
    conf.settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        FORM_RENDERER='django.forms.renderers.DjangoTemplates',
        USE_TZ=True,
    )
    django.setup()

from django.forms import Form, CharField, formset_factory
from django.utils.deprecation import RemovedInDjango50Warning

def test_management_form_template_warning():
    """
    Test that ManagementForm doesn't raise deprecation warnings when rendered.

    This test should FAIL on the buggy version (base commit) because the
    ManagementForm will use the default "django/forms/default.html" template
    which triggers a RemovedInDjango50Warning.

    This test should PASS on the fixed version (head commit) because the
    ManagementForm will use "django/forms/div.html" template which doesn't
    trigger the warning.
    """

    # Create a simple form
    class TestForm(Form):
        name = CharField()

    # Create a formset from the form
    TestFormSet = formset_factory(TestForm, extra=1)

    # Create an instance of the formset
    formset = TestFormSet()

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Render the management form - this should trigger the warning in buggy version
        management_form_html = str(formset.management_form)

        # Check if any RemovedInDjango50Warning was raised
        deprecation_warnings = [
            warning for warning in w
            if issubclass(warning.category, RemovedInDjango50Warning)
        ]

        # The test should fail if any deprecation warnings are found
        # (this is the buggy behavior)
        if deprecation_warnings:
            print(f"FAIL: Found {len(deprecation_warnings)} RemovedInDjango50Warning(s)")
            for warning in deprecation_warnings:
                print(f"  Warning message: {warning.message}")
                print(f"  Warning category: {warning.category}")
            return False
        else:
            print("PASS: No RemovedInDjango50Warning raised")
            return True

if __name__ == "__main__":
    success = test_management_form_template_warning()
    if not success:
        print("\nTest FAILED - ManagementForm raised deprecation warning (buggy behavior)")
        sys.exit(1)
    else:
        print("\nTest PASSED - No deprecation warning raised (fixed behavior)")
        sys.exit(0)