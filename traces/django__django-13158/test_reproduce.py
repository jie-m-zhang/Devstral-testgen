"""
Test to reproduce the issue where QuerySet.none() on combined queries
(using union()) returns all results instead of none.
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
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.db import models
from django.db.models import Q

def test_union_none_issue():
    """
    Test that demonstrates the issue with QuerySet.none() on combined queries.

    The issue is that when you have a union() queryset and call .none() on it,
    it should return an empty queryset, but instead it returns all results.
    """
    from django.db.models.sql.query import Query

    # Create a simple test model
    class TestModel(models.Model):
        id = models.AutoField(primary_key=True)
        name = models.CharField(max_length=100)

        class Meta:
            app_label = 'test_app'
            managed = False

    # Create a query object
    query = Query(TestModel)

    # Simulate a combined query (like union() does)
    from django.db.models.sql.query import Query
    combined_query1 = Query(TestModel)
    combined_query2 = Query(TestModel)

    # Set up the combined queries
    query.combined_queries = (combined_query1, combined_query2)

    # Call set_empty() - this should mark all combined queries as empty too
    query.set_empty()

    # Check if the main query is empty
    assert query.is_empty(), "Main query should be empty"

    # Check if combined queries are also empty (this is what the fix does)
    # On the buggy version, combined queries won't be marked as empty
    for combined_query in query.combined_queries:
        if not combined_query.is_empty():
            print(f"FAIL: Combined query is not empty (this is the bug)")
            return False

    print("PASS: All combined queries are properly marked as empty")
    return True

if __name__ == "__main__":
    print("Testing Query.set_empty() behavior with combined queries...")
    result = test_union_none_issue()

    if not result:
        print("\nBug reproduced: Combined queries are not marked as empty when set_empty() is called")
        sys.exit(1)

    print("\nAll tests passed!")
    sys.exit(0)