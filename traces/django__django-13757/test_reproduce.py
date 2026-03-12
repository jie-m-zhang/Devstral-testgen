#!/usr/bin/env python
"""
Test to reproduce the issue with KeyTransformIsNull lookup on SQLite and Oracle.

The issue is that using __isnull=True on a KeyTransform should not match JSON null
on SQLite and Oracle, but currently it does.

This test demonstrates the bug by checking that value__j__isnull=True should only
match objects that don't have the key 'j' at all, not objects that have 'j' with
a JSON null value.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.test.utils.setup_test_environment')
sys.path.insert(0, '/testbed')

# Minimal Django setup for testing
from django.conf import settings

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
            'tests.model_fields',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

django.setup()

from django.test import TestCase
from django.db import connection
from tests.model_fields.models import NullableJSONModel

class TestIsNullKeyBug(TestCase):
    """Test case to reproduce the KeyTransformIsNull bug."""

    @classmethod
    def setUpTestData(cls):
        # Create test data matching the structure in the original test
        cls.primitives = [True, False, 'yes', 7, 9.6]
        values = [
            None,  # objs[0] - SQL NULL
            [],    # objs[1] - empty list
            {},    # objs[2] - empty dict
            {'a': 'b', 'c': 14},  # objs[3] - has key 'a' but not 'j'
            {  # objs[4] - has key 'j' with JSON null value
                'a': 'b',
                'c': 14,
                'd': ['e', {'f': 'g'}],
                'h': True,
                'i': False,
                'j': None,  # JSON null - this is the key difference
                'k': {'l': 'm'},
                'n': [None],
                'o': '"quoted"',
                'p': 4.2,
            },
            [1, [2]],  # objs[5] - list
            {'k': True, 'l': False, 'foo': 'bax'},  # objs[6]
            {  # objs[7]
                'foo': 'bar',
                'baz': {'a': 'b', 'c': 'd'},
                'bar': ['foo', 'bar'],
                'bax': {'foo': 'bar'},
            },
        ]
        cls.objs = [
            NullableJSONModel.objects.create(value=value)
            for value in values
        ]

    def test_isnull_key_with_json_null(self):
        """
        Test that value__j__isnull=True should NOT match objects that have
        the key 'j' with a JSON null value.

        Expected behavior:
        - Objects without the key 'j' should match: objs[0], objs[1], objs[2], objs[3], objs[5:]
        - Objects with the key 'j' (even if value is JSON null) should NOT match: objs[4]

        This test will FAIL on the buggy version (base commit) because SQLite
        incorrectly includes objs[4] in the results.
        """
        # Objects that don't have key 'j' at all
        expected = self.objs[:4] + self.objs[5:]

        # Query for objects where key 'j' is null (doesn't exist)
        result = list(NullableJSONModel.objects.filter(value__j__isnull=True))

        # On the buggy version, this will include objs[4] (which has j: None)
        # On the fixed version, this will NOT include objs[4]
        print(f"Expected objects: {[obj.id for obj in expected]}")
        print(f"Result objects: {[obj.id for obj in result]}")

        # This assertion will fail on the buggy version because result will include objs[4]
        self.assertSequenceEqual(result, expected,
            msg="value__j__isnull=True should not match objects with JSON null value for key 'j'")

if __name__ == '__main__':
    import django.test.utils
    django.test.utils.setup_test_environment()

    # Create the database tables
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)

    # Run the test
    test_case = TestIsNullKeyBug()
    test_case.setUpTestData()

    print("Running test_isnull_key_with_json_null...")
    try:
        test_case.test_isnull_key_with_json_null()
        print("TEST PASSED - Issue is fixed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"TEST FAILED - Issue reproduced: {e}")
        sys.exit(1)