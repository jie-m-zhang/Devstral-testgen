"""
Test to reproduce the issue with missing make_hashable call on through_fields
in ManyToManyRel.

The issue occurs when:
1. A ManyToManyField has through_fields specified as a list
2. A proxy model is involved
3. Django tries to check the model (which involves hashing the identity)

This should fail on the base commit with:
TypeError: unhashable type: 'list'

And should pass on the head commit after the fix.
"""

import os
import sys
import django
from django.conf import settings

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
            'test_reproduce_app',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
        SILENCED_SYSTEM_CHECKS=[
            # We expect some checks to fail, that's what we're testing
            'fields.W342',
        ],
    )
    django.setup()

# Now import Django models
from django.db import models
from test_reproduce_app.models import Child, ProxyParent

def test_issue_reproduction():
    """
    Test that reproduces the issue with through_fields not being hashable.

    This test should:
    - FAIL on base commit (00ea883ef56fb5e092cbe4a6f7ff2e7470886ac4)
    - PASS on head commit (475cffd1d64c690cdad16ede4d5e81985738ceb4)
    """
    print("Testing ManyToManyField with through_fields and proxy model...")

    # The issue occurs during model checking, specifically when Django tries to
    # hash the identity of the ManyToManyRel object. This happens when checking
    # field name clashes, which involves putting fields in a set.

    try:
        # This should trigger the error - checking the Child model
        # which has a ManyToManyField with through_fields as a list
        errors = Child.check()

        # Also check the proxy model, which is where the issue manifests
        errors += ProxyParent.check()

        print(f"SUCCESS: Model checks passed - issue is fixed! Errors found: {len(errors)}")
        return True

    except TypeError as e:
        if "unhashable type: 'list'" in str(e):
            print(f"FAILED: Got expected error - {e}")
            print("This confirms the bug exists.")
            return False
        else:
            print(f"FAILED: Got unexpected error - {e}")
            raise

    except Exception as e:
        print(f"FAILED: Got unexpected error - {e}")
        raise

if __name__ == "__main__":
    # Run the test
    success = test_issue_reproduction()
    
    # Exit with appropriate code
    # On base commit (buggy): should exit with code 1 (fail)
    # On head commit (fixed): should exit with code 0 (pass)
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)