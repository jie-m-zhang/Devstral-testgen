"""
Test to reproduce the issue where related_name on symmetrical ManyToManyFields
should raise a warning.

The issue: When a ManyToManyField is symmetrical (either explicitly set or
self-referential), the related field on the target model is not created.
However, if a developer passes in the related_name not understanding this fact,
they may be confused. The fix should raise a warning when both symmetrical
is True and related_name is provided.
"""

from django.core import checks
from django.db import models

def test_symmetrical_self_referential_with_related_name():
    """
    Test that a self-referential ManyToManyField with related_name
    raises a warning about related_name having no effect.
    """
    # Define a model with a self-referential ManyToManyField
    # that has a related_name (which should trigger the warning)
    class Person(models.Model):
        name = models.CharField(max_length=100)
        friends = models.ManyToManyField(
            'self',
            related_name='my_friends',  # This should trigger the warning
            symmetrical=True  # Explicitly set (though it's the default for self)
        )

        class Meta:
            app_label = 'test_app'

    # Get the field and run its check method
    field = Person._meta.get_field('friends')

    # Run the field's check method
    check_results = field.check()

    # Look for the warning about related_name having no effect
    warnings = [result for result in check_results if result.id == 'fields.W345']

    # On the base commit (buggy version), no warning should be raised
    # On the head commit (fixed version), a warning should be raised
    if warnings:
        # Fixed version - warning is raised
        assert len(warnings) == 1
        assert 'related_name has no effect on ManyToManyField' in str(warnings[0].msg)
        print("✓ Test passed - warning is raised as expected")
        return True
    else:
        # Buggy version - no warning (test should fail)
        print("✗ Test failed - expected warning about related_name on symmetrical ManyToManyField but got none")
        return False

def test_symmetrical_explicit_with_related_name():
    """
    Test that an explicitly symmetrical ManyToManyField with related_name
    raises a warning about related_name having no effect.
    """
    # Define two models with a symmetrical ManyToManyField
    class Person(models.Model):
        name = models.CharField(max_length=100)

        class Meta:
            app_label = 'test_app'

    class Friendship(models.Model):
        people = models.ManyToManyField(
            Person,
            related_name='friendships',  # This should trigger the warning
            symmetrical=True  # Explicitly symmetrical
        )

        class Meta:
            app_label = 'test_app'

    # Get the field and run its check method
    field = Friendship._meta.get_field('people')

    # Run the field's check method
    check_results = field.check()

    # Look for the warning about related_name having no effect
    warnings = [result for result in check_results if result.id == 'fields.W345']

    # On the base commit (buggy version), no warning should be raised
    # On the head commit (fixed version), a warning should be raised
    if warnings:
        # Fixed version - warning is raised
        assert len(warnings) == 1
        assert 'related_name has no effect on ManyToManyField' in str(warnings[0].msg)
        print("✓ Test passed - warning is raised as expected")
        return True
    else:
        # Buggy version - no warning (test should fail)
        print("✗ Test failed - expected warning about related_name on symmetrical ManyToManyField but got none")
        return False

if __name__ == '__main__':
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
            ],
            SECRET_KEY='test-secret-key',
        )
        django.setup()

    # Run the tests
    print("Running test_symmetrical_self_referential_with_related_name...")
    result1 = test_symmetrical_self_referential_with_related_name()

    print("\nRunning test_symmetrical_explicit_with_related_name...")
    result2 = test_symmetrical_explicit_with_related_name()

    # Exit with appropriate code
    if result1 and result2:
        print("\n✓ All tests passed")
        exit(0)
    else:
        print("\n✗ Some tests failed")
        exit(1)