"""
Test to reproduce the issue where filtering on query result overrides GROUP BY of internal query.

The issue is that when a subquery with GROUP BY is used in a filter, the GROUP BY
clause gets incorrectly changed from the grouped field to the primary key.
"""

import os
import sys

# Add the testbed to the path
sys.path.insert(0, '/testbed')

# Configure Django settings before importing Django
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
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        SECRET_KEY='test-secret-key',
    )

import django
django.setup()

from django.contrib.auth import models
from django.db.models import Max

def test_group_by_preserved_in_subquery():
    """
    Test that GROUP BY clause is preserved when using a subquery in a filter.

    The issue is that when a subquery with GROUP BY is used in a filter,
    the GROUP BY clause gets incorrectly changed from the grouped field to the primary key.
    """

    # Create a subquery with GROUP BY
    # This should GROUP BY email field
    a = models.User.objects.filter(email__isnull=True).values('email').annotate(m=Max('id')).values('m')

    # Print the query to see what it looks like
    query_str = str(a.query)
    print(f"Query a: {query_str}")

    # The query should contain GROUP BY "auth_user"."email"
    assert 'GROUP BY "auth_user"."email"' in query_str or 'GROUP BY `auth_user`.`email`' in query_str, \
        f"Expected GROUP BY on email field, got: {query_str}"

    # Slice to add LIMIT 1
    a_sliced = a[:1]
    query_str_sliced = str(a_sliced.query)
    print(f"Query a[:1]: {query_str_sliced}")

    # The sliced query should still contain GROUP BY "auth_user"."email"
    assert 'GROUP BY "auth_user"."email"' in query_str_sliced or 'GROUP BY `auth_user`.`email`' in query_str_sliced, \
        f"Expected GROUP BY on email field in sliced query, got: {query_str_sliced}"

    # Now use this subquery in a filter
    # This is where the bug occurs - the GROUP BY gets changed to GROUP BY on pk
    b = models.User.objects.filter(id=a_sliced)

    query_str_b = str(b.query)
    print(f"Query b (filter with subquery): {query_str_b}")

    # The subquery in the filter should still have GROUP BY "auth_user"."email"
    # NOT GROUP BY on the primary key
    # The bug causes it to be GROUP BY U0."id" instead of GROUP BY U0."email"

    # Check that the subquery contains GROUP BY on email, not on id/pk
    # We need to look for the subquery part
    # The bug is that it groups by U0."id" instead of U0."email"
    # Or it might group by both U0."email", U0."id" which is also wrong

    # Extract the subquery part
    subquery_start = query_str_b.find("(SELECT")
    subquery_end = query_str_b.rfind("LIMIT 1") + 7
    if subquery_start != -1 and subquery_end != -1:
        subquery = query_str_b[subquery_start:subquery_end]
        print(f"Subquery: {subquery}")

        # Check if the subquery has the bug
        # The bug is when it groups by id instead of email, or groups by both
        has_group_by_id = 'GROUP BY U0."id"' in subquery or 'GROUP BY `U0`.`id`' in subquery
        has_group_by_email = 'GROUP BY U0."email"' in subquery or 'GROUP BY `U0`.`email`' in subquery
        has_group_by_both = ('GROUP BY U0."email", U0."id"' in subquery or
                            'GROUP BY `U0`.`email`, `U0`.`id`' in subquery or
                            'GROUP BY U0."id", U0."email"' in subquery or
                            'GROUP BY `U0`.`id`, `U0`.`email`' in subquery)

        print(f"Has GROUP BY id: {has_group_by_id}")
        print(f"Has GROUP BY email: {has_group_by_email}")
        print(f"Has GROUP BY both: {has_group_by_both}")

        # The bug is present if:
        # 1. It groups by id only (not email)
        # 2. It groups by both fields (which is wrong)
        if has_group_by_id and not has_group_by_email:
            raise AssertionError(
                f"BUG DETECTED: GROUP BY is on id instead of email. Subquery: {subquery}\n"
                "Expected GROUP BY on email field only, but got GROUP BY on id field."
            )
        elif has_group_by_both:
            raise AssertionError(
                f"BUG DETECTED: GROUP BY is on both email and id. Subquery: {subquery}\n"
                "Expected GROUP BY on email field only, but got GROUP BY on both fields."
            )

        # The correct behavior is to have GROUP BY on email only
        assert has_group_by_email and not has_group_by_id and not has_group_by_both, \
            f"Expected GROUP BY on email field only in subquery, got: {subquery}"

    print("Test passed - GROUP BY clause is correctly preserved!")

if __name__ == "__main__":
    # Run the test
    try:
        test_group_by_preserved_in_subquery()
        print("\nTest PASSED - Issue is fixed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTest FAILED - Issue reproduced: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)