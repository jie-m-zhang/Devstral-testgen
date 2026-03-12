#!/usr/bin/env python
"""
Test to reproduce the issue where FormSets should add 'nonform' CSS class
for non-form errors, similar to how forms add 'nonfield' for non-field errors.
"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        USE_TZ=True,
    )
    django.setup()

from django import forms
from django.forms.formsets import BaseFormSet, formset_factory
from django.core.exceptions import ValidationError

class SimpleForm(forms.Form):
    name = forms.CharField(max_length=100)

class SimpleFormSet(BaseFormSet):
    def clean(self):
        # Add a non-form error
        raise ValidationError("This is a non-form error")

def test_nonform_error_class():
    """
    Test that non-form errors in FormSets have the 'nonform' CSS class.
    This should fail on the buggy version and pass on the fixed version.
    """
    # Create a formset with data
    formset_class = formset_factory(SimpleForm, formset=SimpleFormSet)
    
    # Create a formset instance with some data
    data = {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '0',
        'form-0-name': 'Test Name',
    }
    formset = formset_class(data)
    
    # Trigger validation
    is_valid = formset.is_valid()
    
    # Get non-form errors
    non_form_errors = formset.non_form_errors()
    
    # Check if the error list has the 'nonform' class
    # The error_class attribute should contain 'nonform'
    print(f"Non-form errors: {non_form_errors}")
    print(f"Error class attribute: {non_form_errors.error_class}")
    
    # The test: error_class should contain 'nonform'
    assert 'nonform' in non_form_errors.error_class, \
        f"Expected 'nonform' in error_class, got: {non_form_errors.error_class}"
    
    print("Test passed - 'nonform' CSS class is present in non-form errors")

if __name__ == "__main__":
    test_nonform_error_class()