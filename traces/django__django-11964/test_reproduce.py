#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Add the testbed to the path
sys.path.insert(0, '/testbed')

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
            'tests.model_enums',
        ],
        USE_TZ=True,
    )

# Setup Django
django.setup()

# Now import the models after Django is setup
from django.test import TestCase
from tests.model_enums.models import MyObject, MyChoice

class EnumTest(TestCase):
    def setUp(self):
        self.my_object = MyObject.objects.create(my_str_value=MyChoice.FIRST_CHOICE)

    def test_created_object_is_str(self):
        """Test that the value from a newly created object is a string"""
        my_object = self.my_object
        # The value should be a string
        self.assertIsInstance(my_object.my_str_value, str, f"Expected str, got {type(my_object.my_str_value)}")
        # The string value should be "first", not "MyChoice.FIRST_CHOICE"
        self.assertEqual(str(my_object.my_str_value), "first", f"Expected 'first', got '{str(my_object.my_str_value)}'")

    def test_retrieved_object_is_str(self):
        """Test that the value from a retrieved object is a string"""
        my_object = MyObject.objects.last()
        # The value should be a string
        self.assertIsInstance(my_object.my_str_value, str, f"Expected str, got {type(my_object.my_str_value)}")
        # The string value should be "first", not "MyChoice.FIRST_CHOICE"
        self.assertEqual(str(my_object.my_str_value), "first", f"Expected 'first', got '{str(my_object.my_str_value)}'")

if __name__ == '__main__':
    import django.test.utils
    from django.test.runner import DiscoverRunner

    runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    django.test.utils.get_runner(settings)()

    # Run the test
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['__main__.EnumTest'])
    sys.exit(bool(failures))