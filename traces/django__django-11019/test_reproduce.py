#!/usr/bin/env python
"""
Test to reproduce the MediaOrderConflictWarning issue when merging 3 or more media objects.

The issue: When merging media from multiple widgets, unnecessary warnings are thrown
and the final order of JS files is incorrect.

Expected behavior:
- No MediaOrderConflictWarning should be raised
- Final JS order should be: text-editor.js, text-editor-extras.js, color-picker.js

Buggy behavior (base commit):
- MediaOrderConflictWarning is raised
- Final JS order is incorrect
"""

import warnings
import django
from django.conf import settings
from django.forms.widgets import MediaOrderConflictWarning

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django import forms
from django.forms.widgets import Media

def test_media_merge_three_way_no_unnecessary_warning():
    """
    Test that merging 3 or more media objects doesn't throw unnecessary warnings.

    This reproduces the issue described in the GitHub issue where:
    - ColorPicker has: ['color-picker.js']
    - SimpleTextWidget has: ['text-editor.js']
    - FancyTextWidget has: ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']

    The expected final order is: ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']
    """

    # Define the widgets as described in the issue
    class ColorPicker(forms.Widget):
        class Media:
            js = ['color-picker.js']

    class SimpleTextWidget(forms.Widget):
        class Media:
            js = ['text-editor.js']

    class FancyTextWidget(forms.Widget):
        class Media:
            js = ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']

    # Create the form
    class MyForm(forms.Form):
        background_color = forms.CharField(widget=ColorPicker())
        intro = forms.CharField(widget=SimpleTextWidget())
        body = forms.CharField(widget=FancyTextWidget())

    # Capture warnings during media access
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Create form
        form = MyForm()

        # Access the form's media - this is where the warning should NOT be raised
        media = form.media

        # Print all warnings for debugging
        print(f"Total warnings captured: {len(w)}")
        for i, warning in enumerate(w):
            print(f"Warning {i+1}:")
            print(f"  Category: {warning.category.__name__}")
            print(f"  Message: {warning.message}")
            print(f"  Is MediaOrderConflictWarning: {issubclass(warning.category, MediaOrderConflictWarning)}")

        # Check that no MediaOrderConflictWarning was raised
        media_warnings = [warning for warning in w if issubclass(warning.category, MediaOrderConflictWarning)]
        if media_warnings:
            print(f"\nFAIL: Unexpected MediaOrderConflictWarning raised:")
            print(f"  {media_warnings[0].message}")
            print(f"  Media JS files: {media._js}")
            return False

        # Verify the final order of JS files
        expected_order = ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']
        actual_order = media._js

        if actual_order != expected_order:
            print(f"\nFAIL: Incorrect JS file order")
            print(f"  Expected: {expected_order}")
            print(f"  Actual: {actual_order}")
            return False

        print("\nPASS: No unnecessary warnings and correct order")
        print(f"  Final JS order: {actual_order}")
        return True

if __name__ == "__main__":
    success = test_media_merge_three_way_no_unnecessary_warning()
    if not success:
        exit(1)
    exit(0)