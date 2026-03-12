#!/usr/bin/env python
"""
Test to reproduce the issue where BoundWidget.id_for_label ignores id set by ChoiceWidget.options

The issue occurs when using CheckboxSelectMultiple with a custom auto_id format.
The BoundWidget.id_for_label() method should use the id from self.data['attrs']['id']
but instead generates its own id using 'id_%s_%s' % (self.data['name'], self.data['index']).
"""

import sys
import os
sys.path.insert(0, '/testbed')

# Configure Django settings
from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        USE_I18N=True,
        USE_L10N=True,
        USE_TZ=True,
    )

import django
django.setup()

from django import forms

def test_checkboxselectmultiple_custom_id():
    """
    Test that BoundWidget.id_for_label uses the custom ID from attrs when available.

    This test should FAIL on the buggy version and PASS on the fixed version.
    """
    # Create a form with a custom auto_id format
    class TestForm(forms.Form):
        # Use a custom auto_id format
        auto_id = 'custom_id_%s'

        choices = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[('a', 'Option A'), ('b', 'Option B'), ('c', 'Option C')]
        )

    # Instantiate the form
    form = TestForm()

    # Get the bound field
    bound_field = form['choices']

    # Get the subwidgets (BoundWidget instances)
    subwidgets = bound_field.subwidgets

    # Check that we have subwidgets
    assert len(subwidgets) == 3, f"Expected 3 subwidgets, got {len(subwidgets)}"

    # The first subwidget should have an ID like 'custom_id_choices_0'
    # because the widget's create_option method adds the index suffix
    first_widget = subwidgets[0]

    # Check the actual ID in the widget's attrs
    actual_id = first_widget.data['attrs'].get('id')
    print(f"Actual ID in attrs: {actual_id}")

    # The id_for_label should return the ID from attrs, not generate a new one
    id_for_label = first_widget.id_for_label
    print(f"id_for_label returned: {id_for_label}")

    # This is the key assertion - it should use the ID from attrs
    # On the buggy version, this will fail because id_for_label generates 'id_choices_0'
    # On the fixed version, this will pass because id_for_label returns the actual ID from attrs
    assert id_for_label == actual_id, f"Expected id_for_label to return '{actual_id}', but got '{id_for_label}'"

    print("Test passed!")

def test_checkboxselectmultiple_with_explicit_widget_id():
    """
    Test that BoundWidget.id_for_label uses the explicit widget ID when set via attrs.
    """
    # Create a form with an explicit ID on the widget
    class TestForm(forms.Form):
        choices = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(attrs={'id': 'my_custom_id'}),
            choices=[('a', 'Option A'), ('b', 'Option B')]
        )

    # Instantiate the form
    form = TestForm()

    # Get the bound field
    bound_field = form['choices']

    # Get the subwidgets (BoundWidget instances)
    subwidgets = bound_field.subwidgets

    # Check that we have subwidgets
    assert len(subwidgets) == 2, f"Expected 2 subwidgets, got {len(subwidgets)}"

    # The first subwidget should have an ID like 'my_custom_id_0'
    first_widget = subwidgets[0]

    # Check the actual ID in the widget's attrs
    expected_id = 'my_custom_id_0'
    actual_id = first_widget.data['attrs'].get('id')
    print(f"Expected ID in attrs: {expected_id}")
    print(f"Actual ID in attrs: {actual_id}")

    # The id_for_label should return the ID from attrs
    id_for_label = first_widget.id_for_label
    print(f"id_for_label returned: {id_for_label}")

    # This is the key assertion
    assert id_for_label == actual_id, f"Expected id_for_label to return '{actual_id}', but got '{id_for_label}'"

    print("Test passed!")

if __name__ == '__main__':
    print("Testing CheckboxSelectMultiple with custom auto_id...")
    try:
        test_checkboxselectmultiple_custom_id()
        print("✓ Test 1 passed")
    except AssertionError as e:
        print(f"✗ Test 1 failed: {e}")
        sys.exit(1)

    print("\nTesting CheckboxSelectMultiple with explicit widget ID...")
    try:
        test_checkboxselectmultiple_with_explicit_widget_id()
        print("✓ Test 2 passed")
    except AssertionError as e:
        print(f"✗ Test 2 failed: {e}")
        sys.exit(1)

    print("\nAll tests passed!")