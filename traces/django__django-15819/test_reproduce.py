#!/usr/bin/env python
"""
Test to reproduce the inspectdb issue with multiple foreign keys to the same model.

The issue is that when inspectdb generates models with multiple foreign keys
to the same related model, it doesn't add related_name, causing a clash error.

This test creates a database with such a structure and verifies that:
1. On the buggy version: related_name is NOT added (test will fail)
2. On the fixed version: related_name IS added (test will pass)
"""

import os
import sys
import tempfile
from io import StringIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
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

from django.core.management import call_command
from django.db import connection

def create_test_database():
    """Create a test database with tables that have multiple FKs to the same model."""
    with connection.cursor() as cursor:
        # Create a simple model table
        cursor.execute("""
            CREATE TABLE test_person (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        # Create a table with two foreign keys to test_person
        cursor.execute("""
            CREATE TABLE test_relationship (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person1_id INTEGER NOT NULL,
                person2_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                FOREIGN KEY (person1_id) REFERENCES test_person(id),
                FOREIGN KEY (person2_id) REFERENCES test_person(id)
            )
        """)

def test_inspectdb_multiple_fk_related_name():
    """Test that inspectdb generates related_name for multiple FKs to same model."""
    # Create test database
    create_test_database()

    # Capture inspectdb output
    output = StringIO()
    call_command('inspectdb', 'test_relationship', stdout=output)
    inspectdb_output = output.getvalue()

    print("Inspectdb output:")
    print(inspectdb_output)
    print("\n" + "="*80 + "\n")

    # Check if related_name is present in the output
    # The fix should add related_name for the second FK to avoid clashes
    lines = inspectdb_output.split('\n')

    # Find the relationship model
    relationship_model_lines = []
    in_relationship_model = False
    for line in lines:
        if 'class TestRelationship(models.Model):' in line:
            in_relationship_model = True
        elif in_relationship_model and line.startswith('class '):
            break
        elif in_relationship_model:
            relationship_model_lines.append(line)

    print("Relationship model lines:")
    for line in relationship_model_lines:
        print(line)

    # Check for related_name in the fields
    person1_field = None
    person2_field = None

    for line in relationship_model_lines:
        if 'person1' in line.lower() and 'foreignkey' in line.lower():
            person1_field = line
        elif 'person2' in line.lower() and 'foreignkey' in line.lower():
            person2_field = line

    print("\n" + "="*80 + "\n")
    print(f"person1 field: {person1_field}")
    print(f"person2 field: {person2_field}")

    # The issue: without related_name, both fields will have the same reverse accessor
    # The fix: the second field should have related_name added

    # Check if related_name is present in person2 field
    if person2_field and 'related_name' in person2_field:
        print("\n✓ SUCCESS: related_name found in person2 field")
        print("This means the fix is working correctly!")
        return True
    else:
        print("\n✗ FAILURE: related_name NOT found in person2 field")
        print("This is the bug - multiple FKs to same model need related_name to avoid clashes")
        print("Expected: person2 field should have related_name parameter")
        return False

if __name__ == "__main__":
    try:
        result = test_inspectdb_multiple_fk_related_name()
        if result:
            print("\n" + "="*80)
            print("TEST PASSED - Issue is fixed!")
            print("="*80)
            sys.exit(0)
        else:
            print("\n" + "="*80)
            print("TEST FAILED - Issue reproduced!")
            print("="*80)
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)