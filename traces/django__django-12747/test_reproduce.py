"""
Test to reproduce the issue with QuerySet.delete() returning inconsistent results
when zero objects are deleted.

The issue: When deleting zero objects, fast-deletable models return (0, {'model_label': 0})
while non-fast-deletable models return (0, {}). This should be consistent.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_sqlite')
sys.path.insert(0, '/testbed')

# Configure Django settings
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
            'tests.delete',
        ],
        SECRET_KEY='test-secret-key',
    )

django.setup()

from django.core.management import call_command

# Setup the database
call_command('migrate', '--run-syncdb', verbosity=0)

from tests.delete.models import User, R

def test_issue_reproduction():
    """
    Test the issue: when deleting zero objects, the return value should be consistent.

    Expected behavior: Both should return (0, {})
    Buggy behavior: Fast-deletable returns (0, {'model_label': 0}), non-fast-deletable returns (0, {})
    """
    # Test 1: User model with fast delete (has FK but can be fast-deleted)
    user_result = User.objects.filter(avatar__desc='missing').delete()

    # Test 2: R model (has FK relationships, cannot be fast-deleted)
    r_result = R.objects.filter(pk=99999).delete()

    # Check for inconsistency
    if user_result != (0, {}) or r_result != (0, {}):
        print("[FAIL] INCONSISTENCY DETECTED!")
        print("   Fast-deletable models return (0, {'model_label': 0})")
        print("   Non-fast-deletable models return (0, {})")
        print(f"   User result: {user_result}")
        print(f"   R result: {r_result}")
        return False
    else:
        print("[PASS] CONSISTENT!")
        print("   Both return (0, {}) as expected")
        return True

if __name__ == '__main__':
    success = test_issue_reproduction()
    # Exit with 1 if inconsistent (bug exists), 0 if consistent (bug fixed)
    sys.exit(0 if success else 1)