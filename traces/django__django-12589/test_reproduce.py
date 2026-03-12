"""
Test to reproduce the GROUP BY clauses error with tricky field annotation issue.
This test should FAIL on Django 3.0 (base commit) and PASS on the fixed version.
"""

import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
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
        USE_TZ=True,
    )

django.setup()

from django.db import models
from django.db.models import Count, OuterRef, Subquery, Q

# Define models
class A(models.Model):
    class Meta:
        app_label = 'test_app'

class B(models.Model):
    class Meta:
        app_label = 'test_app'

class AB(models.Model):
    a = models.ForeignKey(A, on_delete=models.CASCADE)
    b = models.ForeignKey(B, on_delete=models.CASCADE)
    status = models.IntegerField()

    class Meta:
        app_label = 'test_app'

class C(models.Model):
    a = models.ForeignKey(A, null=True, blank=True, on_delete=models.SET_NULL, related_name="c")
    status = models.IntegerField()

    class Meta:
        app_label = 'test_app'

def setup_test_data():
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(A)
        schema_editor.create_model(B)
        schema_editor.create_model(AB)
        schema_editor.create_model(C)

    # Create test data
    a1 = A.objects.create()
    b1 = B.objects.create()
    AB.objects.create(a=a1, b=b1, status=10)
    C.objects.create(a=a1, status=100)

def test_group_by_ambiguous_column():
    """
    Test that reproduces the GROUP BY ambiguity issue.
    """
    setup_test_data()

    # Create subquery
    ab_query = AB.objects.filter(a=OuterRef("pk"), b=1)

    # Create main query with annotation
    query = A.objects.filter(pk=1).annotate(
        status=Subquery(ab_query.values("status")),
    )

    # Add JOIN to C table (which also has status field)
    # This creates the ambiguity in GROUP BY
    query = query.filter(c__isnull=False)

    # This triggers GROUP BY generation with ambiguous 'status'
    try:
        answer = query.values("status").annotate(total_count=Count("status"))
        result = list(answer)
        print("Query executed successfully!")
        return True
    except Exception as e:
        print(f"Query failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_group_by_ambiguous_column()
    sys.exit(0 if success else 1)