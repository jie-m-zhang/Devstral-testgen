"""
Test to reproduce the issue where ModelChoiceIteratorValue is not hashable.
This test should FAIL on the base commit and PASS on the head commit.
"""

import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
sys.path.insert(0, '/testbed')

# Create a minimal settings module
with open('/testbed/test_settings.py', 'w') as f:
    f.write("""
SECRET_KEY = 'test-secret-key'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
USE_TZ = True
""")

# Setup Django
django.setup()

from django.db import models
from django import forms

# Create a simple model for testing
class TestModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'test_app'

def test_modelchoiceiteratorvalue_hashable():
    """
    Test that ModelChoiceIteratorValue is hashable and can be used as a dict key.
    This reproduces the issue described in the GitHub issue.
    """
    from django.forms.models import ModelChoiceIteratorValue

    # Create a ModelChoiceIteratorValue instance
    value = ModelChoiceIteratorValue(1, None)

    # Test 1: Check if it's hashable (should fail on base commit)
    try:
        hash(value)
        print("ModelChoiceIteratorValue is hashable")
    except TypeError as e:
        print(f"ModelChoiceIteratorValue is not hashable: {e}")
        raise

    # Test 2: Use it as a key in a dictionary (the actual use case from the issue)
    show_fields = {value: ['field1', 'field2']}

    # Test 3: Check if it can be used in dictionary lookups
    if value in show_fields:
        print("ModelChoiceIteratorValue can be used as a dict key")
    else:
        print("ModelChoiceIteratorValue cannot be used as a dict key")
        raise AssertionError("ModelChoiceIteratorValue not found in dictionary")

    # Test 4: Verify the hash is based on the value attribute
    value2 = ModelChoiceIteratorValue(1, None)
    if hash(value) == hash(value2):
        print("ModelChoiceIteratorValue hash is based on value attribute")
    else:
        print("ModelChoiceIteratorValue hash is not consistent")
        raise AssertionError("Hash values should be equal for same value")

    print("All tests passed!")

if __name__ == "__main__":
    test_modelchoiceiteratorvalue_hashable()