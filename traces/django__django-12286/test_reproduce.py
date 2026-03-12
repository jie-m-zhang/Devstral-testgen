"""
Test to reproduce the issue where translation.E004 shouldn't be raised on sublanguages
when a base language is available.

According to Django documentation:
If a base language is available but the sublanguage specified is not, Django
uses the base language. For example, if a user specifies de-at (Austrian German)
but Django only has de available, Django uses de.
"""

from django.core.checks import Error
from django.core.checks.translation import check_language_settings_consistent
from django.test import SimpleTestCase

class SublanguageFallbackTest(SimpleTestCase):
    """
    Test that sublanguages fall back to base languages when available.
    """

    def test_sublanguage_with_base_language_available(self):
        """
        Test that when LANGUAGE_CODE is set to a sublanguage (e.g., 'de-at')
        but only the base language (e.g., 'de') is in LANGUAGES, no error
        should be raised because Django should fall back to the base language.
        """
        # Set LANGUAGE_CODE to 'de-at' (Austrian German)
        # Set LANGUAGES to only include 'de' (German)
        with self.settings(
            LANGUAGE_CODE='de-at',
            LANGUAGES=[('de', 'German')]
        ):
            # This should NOT raise an error because 'de' is available
            # and Django should fall back to it
            errors = check_language_settings_consistent(None)
            self.assertEqual(errors, [], 
                "Expected no errors when base language 'de' is available for sublanguage 'de-at'")

    def test_sublanguage_with_base_language_available_es_ar(self):
        """
        Test with another sublanguage example (es-ar) to ensure the fix works generally.
        """
        # Set LANGUAGE_CODE to 'es-ar' (Argentinian Spanish)
        # Set LANGUAGES to only include 'es' (Spanish)
        with self.settings(
            LANGUAGE_CODE='es-ar',
            LANGUAGES=[('es', 'Spanish')]
        ):
            # This should NOT raise an error because 'es' is available
            # and Django should fall back to it
            errors = check_language_settings_consistent(None)
            self.assertEqual(errors, [],
                "Expected no errors when base language 'es' is available for sublanguage 'es-ar'")

    def test_sublanguage_without_base_language(self):
        """
        Test that when neither the sublanguage nor the base language is available,
        an error IS raised (this should still fail).
        """
        # Set LANGUAGE_CODE to 'de-at' (Austrian German)
        # Set LANGUAGES to only include 'en' (English) - no German at all
        with self.settings(
            LANGUAGE_CODE='de-at',
            LANGUAGES=[('en', 'English')]
        ):
            # This SHOULD raise an error because neither 'de-at' nor 'de' is available
            errors = check_language_settings_consistent(None)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].id, 'translation.E004')

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
            USE_I18N=True,
            USE_L10N=True,
            LANGUAGE_CODE='en-us',
            LANGUAGES=[
                ('en', 'English'),
            ],
        )
        django.setup()

    # Run the test
    test_case = SublanguageFallbackTest()
    test_case.setUp()

    print("Running test_sublanguage_with_base_language_available...")
    try:
        test_case.test_sublanguage_with_base_language_available()
        print("PASS: de-at with de available")
    except AssertionError as e:
        print("FAIL: de-at with de available")
        print(f"Error: {e}")
        exit(1)

    print("Running test_sublanguage_with_base_language_available_es_ar...")
    try:
        test_case.test_sublanguage_with_base_language_available_es_ar()
        print("PASS: es-ar with es available")
    except AssertionError as e:
        print("FAIL: es-ar with es available")
        print(f"Error: {e}")
        exit(1)

    print("Running test_sublanguage_without_base_language...")
    try:
        test_case.test_sublanguage_without_base_language()
        print("PASS: de-at without de available (should still fail)")
    except AssertionError as e:
        print("FAIL: de-at without de available (should still fail)")
        print(f"Error: {e}")
        exit(1)

    print("All tests passed!")