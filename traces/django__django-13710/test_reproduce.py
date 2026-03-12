"""
Test to reproduce the issue where Inline verbose_name_plural is not derived
from verbose_name when only verbose_name is specified.

The issue: When a verbose_name is specified for an Inline class in Django admin,
the verbose_name_plural should be automatically derived from it (like how it
works for model Meta classes), but currently it's not - it still uses the
model's verbose_name_plural.
"""

def test_issue_reproduction():
    """
    Test that when verbose_name is set on an Inline but verbose_name_plural is not,
    verbose_name_plural should be derived from verbose_name (by adding 's').
    """
    from django.contrib import admin
    from django.contrib.admin import TabularInline
    from django.db import models

    # Create test models
    class TestParent(models.Model):
        name = models.CharField(max_length=100)

        class Meta:
            app_label = 'test_reproduce'
            verbose_name = 'Test Parent'
            verbose_name_plural = 'Test Parents'

    class TestChild(models.Model):
        name = models.CharField(max_length=100)
        parent = models.ForeignKey(TestParent, on_delete=models.CASCADE)

        class Meta:
            app_label = 'test_reproduce'
            verbose_name = 'Test Child'
            verbose_name_plural = 'Test Children'

    # Create a custom inline with only verbose_name set
    class CustomVerboseNameInline(admin.TabularInline):
        model = TestChild
        verbose_name = 'Custom Child'  # Only set verbose_name, not verbose_name_plural

    from django.contrib.admin import AdminSite

    # Create an admin site
    site = AdminSite(name='testadmin')

    # Create a model admin with our custom inline
    class TestParentAdmin(admin.ModelAdmin):
        inlines = [CustomVerboseNameInline]

    # Register the model
    site.register(TestParent, TestParentAdmin)

    # Get the inline instance
    parent_admin = site._registry[TestParent]
    inline = parent_admin.inlines[0](TestParent, site)

    # Check the verbose_name (should be our custom one)
    assert inline.verbose_name == 'Custom Child', f"Expected verbose_name to be 'Custom Child', got '{inline.verbose_name}'"

    # Check the verbose_name_plural
    # In the buggy version, this will be 'Test Children' (from the model's Meta)
    # In the fixed version, this should be 'Custom Childs' (derived from verbose_name)
    print(f"verbose_name_plural: {inline.verbose_name_plural}")
    print(f"Expected: Custom Childs")
    print(f"Model's verbose_name_plural: {TestChild._meta.verbose_name_plural}")

    # This assertion will FAIL on buggy code (expects 'Custom Childs' but gets 'Test Children')
    # This assertion will PASS on fixed code (gets 'Custom Childs')
    assert inline.verbose_name_plural == 'Custom Childs', (
        f"Expected verbose_name_plural to be 'Custom Childs' (derived from verbose_name), "
        f"but got '{inline.verbose_name_plural}'. "
        f"This means verbose_name_plural is using the model's Meta.verbose_name_plural instead of "
        f"deriving it from the inline's verbose_name."
    )

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    # Setup Django
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
                'django.contrib.admin',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
        django.setup()

    # Run the test
    test_issue_reproduction()