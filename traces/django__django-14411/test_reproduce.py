"""
Test to reproduce the issue where ReadOnlyPasswordHashWidget's label
points to a non-labelable element.
"""

import os
import sys
import django
from django import forms

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, '/testbed')

# Create minimal settings
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        }],
        USE_TZ=True,
    )

django.setup()

from django.contrib.auth.forms import ReadOnlyPasswordHashWidget, ReadOnlyPasswordHashField
from django.contrib.auth.hashers import make_password

def test_readonly_password_hash_widget_label():
    """
    Test that ReadOnlyPasswordHashWidget doesn't have a 'for' attribute in its label.

    The widget renders text (not an input), so the label should not have a 'for' attribute.
    """
    # Create a form with ReadOnlyPasswordHashField
    class TestForm(forms.Form):
        password = ReadOnlyPasswordHashField(
            label="Password",
            initial=make_password("testpassword")
        )

    # Instantiate the form
    form = TestForm()

    # Get the bound field
    bound_field = form['password']

    # Render the label
    label_html = bound_field.label_tag()

    print("Label HTML:", label_html)

    # Check if the label has a 'for' attribute
    has_for_attr = 'for="' in label_html

    # On the base commit (buggy version), the label will have a 'for' attribute
    # On the head commit (fixed version), the label should NOT have a 'for' attribute
    # So we assert that it should NOT have a 'for' attribute
    assert not has_for_attr, f"Label should not have 'for' attribute, but got: {label_html}"

    print("Test passed - label does not have 'for' attribute")

if __name__ == "__main__":
    test_readonly_password_hash_widget_label()