"""
Test to reproduce the issue where rendering empty_form crashes when empty_permitted
is passed to form_kwargs.

The issue occurs because in the empty_form property, **self.get_form_kwargs(None)
is expanded after empty_permitted=True, which means if form_kwargs contains
empty_permitted, it will override the explicitly set empty_permitted=True,
causing a KeyError.
"""

import os
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
        ],
        FORM_RENDERER='django.forms.renderers.DjangoTemplates',
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.forms import Form, CharField, formset_factory

class SimpleForm(Form):
    name = CharField()

def test_empty_form_with_empty_permitted_in_form_kwargs():
    """
    Test that empty_form can be rendered when empty_permitted is passed in form_kwargs.

    This should NOT raise a KeyError. The issue is that when empty_permitted is in
    form_kwargs, it overrides the empty_permitted=True that's explicitly set for
    empty_form, causing problems.
    """
    # Test with empty_permitted=True
    FormSet = formset_factory(SimpleForm)
    formset = FormSet(form_kwargs={'empty_permitted': True})

    # This should not raise a KeyError
    try:
        empty_form = formset.empty_form
        print("✓ Successfully accessed empty_form with empty_permitted=True")
    except KeyError as e:
        print(f"✗ KeyError occurred with empty_permitted=True: {e}")
        raise

    # Test with empty_permitted=False
    formset2 = FormSet(form_kwargs={'empty_permitted': False})

    # This should also not raise a KeyError
    try:
        empty_form2 = formset2.empty_form
        print("✓ Successfully accessed empty_form with empty_permitted=False")
    except KeyError as e:
        print(f"✗ KeyError occurred with empty_permitted=False: {e}")
        raise

    # Verify that empty_form has the correct empty_permitted value
    # It should always be True for empty_form regardless of what's in form_kwargs
    assert empty_form.empty_permitted == True, f"Expected empty_permitted=True, got {empty_form.empty_permitted}"
    assert empty_form2.empty_permitted == True, f"Expected empty_permitted=True, got {empty_form2.empty_permitted}"

    print("✓ Test passed - empty_form works correctly with empty_permitted in form_kwargs")

if __name__ == "__main__":
    test_empty_form_with_empty_permitted_in_form_kwargs()