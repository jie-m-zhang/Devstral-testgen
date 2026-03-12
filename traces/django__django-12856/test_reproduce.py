"""
Test to reproduce the issue where UniqueConstraint doesn't validate field existence.

This test should FAIL on the base commit (8328811f048fed0dd22573224def8c65410c9f2e)
and PASS on the head commit (3c7bf39e23fe9168f31132d929c9877c5835859b).
"""

from django.core.checks import Error, Warning
from django.db import models
from django.test import TestCase
from django.test.utils import isolate_apps

@isolate_apps('test_reproduce')
class UniqueConstraintFieldValidationTest(TestCase):
    databases = {'default'}

    def test_unique_constraint_with_nonexistent_field(self):
        """
        Test that UniqueConstraint raises an error when referencing a non-existent field.
        This should behave like unique_together does.
        """
        class TestModel(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                app_label = 'test_reproduce'
                # This should raise an error because 'nonexistent_field' doesn't exist
                constraints = [
                    models.UniqueConstraint(
                        fields=['name', 'nonexistent_field'],
                        name='unique_name_nonexistent'
                    ),
                ]

        # Check the model for errors
        errors = TestModel.check(databases=self.databases)

        # Filter out warnings (like auto-field warnings) and only check errors
        errors_only = [e for e in errors if isinstance(e, Error)]

        # Should have an error about the non-existent field
        self.assertEqual(len(errors_only), 1)
        self.assertEqual(errors_only[0].id, 'models.E012')
        self.assertIn("nonexistent_field", str(errors_only[0].msg))
        self.assertIn("constraints", str(errors_only[0].msg))

    def test_unique_constraint_with_valid_fields(self):
        """
        Test that UniqueConstraint doesn't raise an error when all fields exist.
        """
        class TestModel(models.Model):
            name = models.CharField(max_length=100)
            color = models.CharField(max_length=50)

            class Meta:
                app_label = 'test_reproduce'
                constraints = [
                    models.UniqueConstraint(
                        fields=['name', 'color'],
                        name='unique_name_color'
                    ),
                ]

        # Check the model for errors - should be no errors (only warnings are OK)
        errors = TestModel.check(databases=self.databases)
        errors_only = [e for e in errors if isinstance(e, Error)]
        self.assertEqual(errors_only, [])

    def test_unique_together_with_nonexistent_field(self):
        """
        Test that unique_together raises an error when referencing a non-existent field.
        This is the existing behavior that UniqueConstraint should match.
        """
        class TestModel(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                app_label = 'test_reproduce'
                unique_together = [['name', 'nonexistent_field']]

        # Check the model for errors
        errors = TestModel.check(databases=self.databases)

        # Filter out warnings and only check errors
        errors_only = [e for e in errors if isinstance(e, Error)]

        # Should have an error about the non-existent field
        self.assertEqual(len(errors_only), 1)
        self.assertEqual(errors_only[0].id, 'models.E012')
        self.assertIn("nonexistent_field", str(errors_only[0].msg))
        self.assertIn("unique_together", str(errors_only[0].msg))

if __name__ == "__main__":
    import django
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
                'test_reproduce',
            ],
            SECRET_KEY='test-secret-key',
        )
        django.setup()

    # Run the tests
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(UniqueConstraintFieldValidationTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)