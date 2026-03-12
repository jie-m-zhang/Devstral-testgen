"""
Test to reproduce the issue where Django throws an error when different apps
with different models have the same table name, even when DATABASE_ROUTERS is configured.

The test should:
- FAIL on base commit (65e86948b8) with Error E028
- PASS on head commit (419a78300) with Warning W035
"""

import os
import sys
import django
from django.conf import settings
from django.core import checks
from django.core.checks import Error, Warning
from django.db import models
from django.test.utils import isolate_apps, override_system_checks
from django.apps import apps

# Create a simple database router class
class TestRouter:
    def db_for_read(self, model, **hints):
        if model._meta.label == 'app2.model2':
            return 'other'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.label == 'app2.model2':
            return 'other'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
            'other': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DATABASE_ROUTERS=['__main__.TestRouter'],  # Configure database routers
        SECRET_KEY='test-secret-key',
    )
    django.setup()

def test_issue_reproduction():
    """
    Test that demonstrates the issue with duplicate table names across apps.

    On base commit: Should raise Error (E028)
    On head commit: Should raise Warning (W035)
    """
    # Create two simple model classes
    class Model1(models.Model):
        name = models.CharField(max_length=100)

        class Meta:
            app_label = 'app1'
            db_table = 'shared_table'

    class Model2(models.Model):
        name = models.CharField(max_length=100)

        class Meta:
            app_label = 'app2'
            db_table = 'shared_table'

    # Import and call the actual check_all_models function
    from django.core.checks.model_checks import check_all_models

    # Create a mock app config that returns our models
    from collections import namedtuple
    from django.apps import AppConfig

    # Create a simple app config
    class MockAppConfig:
        def __init__(self, label, models):
            self.label = label
            self._models = models

        def get_models(self):
            return self._models

    # Create app configs with our models
    app1_config = MockAppConfig('app1', [Model1])
    app2_config = MockAppConfig('app2', [Model2])

    # Run the actual check
    all_checks = check_all_models(app_configs=[app1_config, app2_config])

    # Filter for the specific check we're interested in
    table_name_errors = [
        check for check in all_checks
        if 'db_table' in check.msg and 'shared_table' in check.msg
    ]

    print(f"Found {len(table_name_errors)} checks related to shared_table")
    for check in table_name_errors:
        print(f"  - {check.level}: {check.msg} (id={check.id})")

    # On base commit (buggy): Should have an Error with id 'models.E028'
    # On head commit (fixed): Should have a Warning with id 'models.W035'
    if table_name_errors:
        check = table_name_errors[0]
        print(f"\nCheck details:")
        print(f"  Level: {check.level}")
        print(f"  ID: {check.id}")
        print(f"  Message: {check.msg}")

        # On base commit, this should be an Error (E028)
        # On head commit, this should be a Warning (W035)
        if check.id == 'models.E028':
            print("\nTest FAILED (as expected on base commit): Got Error E028")
            print("This is the bug - should be a Warning when DATABASE_ROUTERS is configured")
            return False
        elif check.id == 'models.W035':
            print("\nTest PASSED: Got Warning W035")
            print("This is correct behavior when DATABASE_ROUTERS is configured")
            return True
        else:
            print(f"\nTest FAILED: Unexpected check id: {check.id}")
            return False
    else:
        print("\nTest FAILED: No checks found for shared_table")
        return False

if __name__ == '__main__':
    # Run the test
    success = test_issue_reproduction()

    # Exit with appropriate code
    # On base commit: should fail (exit code != 0)
    # On head commit: should pass (exit code = 0)
    sys.exit(0 if success else 1)