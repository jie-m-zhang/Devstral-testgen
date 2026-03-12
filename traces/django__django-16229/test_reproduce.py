"""
Test to reproduce the issue with ModelForm fields with callable defaults not
correctly propagating default values.

The issue: When a form has validation errors and is re-submitted, fields with
callable defaults should preserve the submitted value in the hidden initial field,
not reset to the default.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django settings
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
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.forms',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )
    django.setup()

from django.db import models
from django import forms
from django.core.exceptions import ValidationError

# Create test model with a field that has a callable default
class TestModel(models.Model):
    # Field with callable default
    my_field = models.CharField(max_length=100, default=list)

    class Meta:
        app_label = 'test_app'

# Create test form with validation error
class TestForm(forms.ModelForm):
    def clean(self):
        raise ValidationError("whatever")

    class Meta:
        model = TestModel
        fields = '__all__'

def test_callable_default_propagation():
    """
    Test that fields with callable defaults correctly propagate values
    when there are validation errors.

    The key issue is that when only_initial=True and the hidden initial name is in form.data,
    the value should come from form data, not from the field's default.
    """
    # Create a form instance with data including the initial field
    data = {
        'my_field': 'test_value',
        'initial-my_field': 'initial_test_value',  # This is what the hidden initial field would submit
    }

    # Create the form with the data
    form = TestForm(data=data)

    # The form should be invalid due to clean() method
    assert not form.is_valid(), "Form should be invalid due to clean() method"

    # Get the bound field
    bound_field = form['my_field']

    # Force show_hidden_initial to True to test the issue
    bound_field.field.show_hidden_initial = True

    print(f"HTML initial name: {bound_field.html_initial_name}")
    print(f"Is html_initial_name in form.data? {bound_field.html_initial_name in form.data}")

    # The key test: when only_initial=True and html_initial_name is in form.data,
    # the value should come from form data, not from value()

    # Render the hidden initial field
    hidden_initial = bound_field.as_hidden(only_initial=True)

    print("Hidden initial HTML:", hidden_initial)

    # The bug is that as_hidden(only_initial=True) calls value() which may return
    # the prepared default value instead of the form data
    # In the buggy version, it will use value() which might not get the initial data correctly
    # In the fixed version, it should use _widget_data_value to get the initial data

    # Check if the hidden initial contains the initial value from form data
    if 'value="initial_test_value"' in hidden_initial:
        print("PASS: Hidden initial field contains the initial value from form data")
        return True
    else:
        print("FAIL: Hidden initial field does not contain the initial value from form data")
        print("  Expected to find 'initial_test_value' in hidden initial field")
        print("  This indicates the bug is present")
        return False

if __name__ == '__main__':
    # Create the tables
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(TestModel)

    # Run the test
    success = test_callable_default_propagation()
    if success:
        print("\nTest PASSED - issue is fixed")
        sys.exit(0)
    else:
        print("\nTest FAILED - issue is present")
        sys.exit(1)