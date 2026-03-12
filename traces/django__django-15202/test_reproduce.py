#!/usr/bin/env python
"""
Test to reproduce the issue where URLValidator throws ValueError instead of ValidationError.

The issue: URLValidator raises ValueError instead of ValidationError for certain invalid IPv6 URLs.

Expected behavior: Should raise ValidationError
Buggy behavior: Raises ValueError

The bug occurs when urlsplit() is called in the else block (after regex validation passes)
and raises ValueError for invalid IPv6 URLs. This ValueError is not caught and converted to ValidationError.
"""

import sys
import os

# Add the Django project to the path
sys.path.insert(0, '/testbed')

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

# Create minimal settings if they don't exist
if not os.path.exists('/testbed/test_settings.py'):
    with open('/testbed/test_settings.py', 'w') as f:
        f.write('SECRET_KEY = "test-secret-key"\n')
        f.write('INSTALLED_APPS = []\n')

import django
django.setup()

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

def test_urlvalidator_valueerror_issue():
    """
    Test that URLValidator raises ValidationError (not ValueError) for invalid IPv6 URLs.

    This test should:
    - FAIL on base commit (4fd3044ca0...) - raises ValueError
    - PASS on head commit (647480166...) - raises ValidationError
    """
    validator = URLValidator()

    # Test cases that pass regex validation but fail urlsplit in the else block
    # These inputs match the regex pattern but have invalid IPv6 addresses
    test_cases = [
        'http://[1:2:3:4:5:6:7:8:9]',  # Too many IPv6 groups
        'http://[a.b.c.d]',  # Invalid IPv6 format
    ]

    all_passed = True

    for test_input in test_cases:
        print(f"\nTesting: {test_input}")
        try:
            validator(test_input)
            print(f"  ERROR: Expected ValidationError but validation succeeded")
            all_passed = False
        except ValidationError as e:
            # This is the expected behavior (fixed version)
            print(f"  SUCCESS: Got expected ValidationError")
        except ValueError as e:
            # This is the buggy behavior (base commit)
            print(f"  FAILURE: Got ValueError instead of ValidationError: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ERROR: Got unexpected exception: {type(e).__name__}: {e}")
            all_passed = False

    return all_passed

if __name__ == "__main__":
    print("=" * 70)
    print("Testing URLValidator ValueError issue")
    print("=" * 70)

    success = test_urlvalidator_valueerror_issue()

    print("\n" + "=" * 70)
    if success:
        print("All tests PASSED - issue is fixed")
        print("=" * 70)
        sys.exit(0)
    else:
        print("Some tests FAILED - issue reproduced")
        print("=" * 70)
        sys.exit(1)