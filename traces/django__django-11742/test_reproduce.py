"""
Test to reproduce the issue where max_length is too small for choices values.

This test should FAIL on the base commit (no check exists) and PASS on the head commit (check added).
"""

from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps, override_system_checks

@isolate_apps('test_reproduce', attr_name='apps')
@override_system_checks([checks.model_checks.check_all_models])
class MaxLengthChoicesCheckTest(SimpleTestCase):
    def test_max_length_too_small_for_choices(self):
        """
        Test that a field with max_length smaller than the longest choice value
        produces a check error.
        """
        # Create a model with a CharField that has choices with values longer than max_length
        class TestModel(models.Model):
            # This field has max_length=3 but a choice value 'verylong' which is 8 characters
            status = models.CharField(
                max_length=3,
                choices=[
                    ('short', 'Short Value'),
                    ('verylong', 'Very Long Value'),  # This value is 8 chars, exceeds max_length=3
                ]
            )

            class Meta:
                app_label = 'test_reproduce'

        # Run checks on the model
        errors = checks.run_checks(app_configs=self.apps.get_app_configs())

        # Filter for the specific error we're looking for
        field_errors = [e for e in errors if e.id == 'fields.E009']

        # On the base commit (without the fix), this should be empty (no error detected)
        # On the head commit (with the fix), this should contain the error
        # Since we want F->P behavior (Fail to Pass):
        # - Base commit: Test FAILS (no error found, but we expect one)
        # - Head commit: Test PASSES (error found as expected)
        self.assertEqual(len(field_errors), 1, "Expected exactly one error about max_length being too small for choices")
        self.assertEqual(field_errors[0].id, 'fields.E009')
        self.assertIn("max_length' is too small to fit the longest value in 'choices'", field_errors[0].msg)

if __name__ == '__main__':
    import django
    from django.conf import settings

    # Configure minimal Django settings
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
            SECRET_KEY='test-secret-key',
        )
        django.setup()

    # Run the test
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(MaxLengthChoicesCheckTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)