"""
Test to reproduce the issue with wrong hint about recursive relationship.

The issue is that when there are more than 2 ForeignKeys in an intermediary model
of a m2m field and no through_fields have been set, Django shows an error with
a hint that incorrectly mentions ForeignKey instead of ManyToManyField.
"""

from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps, override_system_checks

@isolate_apps('test_reproduce', attr_name='apps')
@override_system_checks([checks.model_checks.check_all_models])
class TestRecursiveRelationshipHint(SimpleTestCase):
    def test_wrong_hint_message_non_symmetrical(self):
        """
        Test the hint message for non-symmetrical recursive relationships.

        This tests the error path (E334/E335) where the hint incorrectly
        mentions ForeignKey with symmetrical=False and through parameters.
        """
        # Create two different models
        class Person(models.Model):
            name = models.CharField(max_length=100)
            groups = models.ManyToManyField(
                'Group',
                through='Membership',
            )

            class Meta:
                app_label = 'test_reproduce'

        class Group(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                app_label = 'test_reproduce'

        # Create a through model with 2 ForeignKeys to Person (more than 1)
        # This should trigger error E334
        class Membership(models.Model):
            person1 = models.ForeignKey(Person, models.CASCADE, related_name='memberships1')
            person2 = models.ForeignKey(Person, models.CASCADE, related_name='memberships2')
            group = models.ForeignKey(Group, models.CASCADE)
            date_joined = models.DateField()

            class Meta:
                app_label = 'test_reproduce'

        # Run model checks
        errors = checks.run_checks(app_configs=self.apps.get_app_configs())

        print(f"Total errors: {len(errors)}")
        for e in errors:
            print(f"Error ID: {e.id}")
            print(f"Error msg: {e.msg}")
            if e.hint:
                print(f"Error hint: {e.hint}")
            print("---")

        # Find the error related to the relationship model
        # This should be error E334 (more than one FK from Person)
        relationship_errors = [e for e in errors if e.id in ['fields.E334', 'fields.E335']]

        # There should be at least one error
        self.assertGreater(len(relationship_errors), 0)

        # Check all errors to ensure none have the wrong hint
        for error in relationship_errors:
            if error.hint:
                print(f"Checking error with hint: {error.hint}")

                # The hint should mention ManyToManyField, not ForeignKey
                # This is the assertion that will FAIL on buggy code, PASS on fixed code
                self.assertIn("ManyToManyField", error.hint, f"Error hint should mention ManyToManyField: {error.hint}")

                # On the buggy version, the hint will contain "ForeignKey" which is wrong
                # On the fixed version, it will contain "ManyToManyField" which is correct
                self.assertNotIn("ForeignKey", error.hint, f"Error hint should not mention ForeignKey: {error.hint}")

                # On the buggy version, the hint will contain "symmetrical=False" which is wrong
                # On the fixed version, it will not contain "symmetrical=False"
                self.assertNotIn("symmetrical=False", error.hint, f"Error hint should not mention symmetrical=False: {error.hint}")

        print("Test passed - all hint messages are correct!")
        for error in relationship_errors:
            if error.hint:
                print(f"Hint: {error.hint}")

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

    from django.test.utils import get_runner
    from django.test.runner import DiscoverRunner

    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['__main__'])
    if failures:
        exit(1)
    else:
        exit(0)