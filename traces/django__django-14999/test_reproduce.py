"""
Test to reproduce the issue where RenameModel with db_table should be a noop.

The issue: When a RenameModel operation is performed but the db_table hasn't actually
changed (e.g., when both old and new models have the same custom db_table), it should
be a noop but currently it's not. This causes unnecessary table operations in PostgreSQL
(drops and recreates foreign key constraints) and in SQLite it recreates the table.

The fix: Check if old_db_table == new_db_table and return early if they're the same.
"""

import sys
import os

# Add testbed to path
sys.path.insert(0, '/testbed')

# Minimal Django setup
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
        SECRET_KEY='test-secret-key',
        MIGRATION_MODULES={},
    )
django.setup()

from django.db import connection, migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import ProjectState

class TrackedSchemaEditor(BaseDatabaseSchemaEditor):
    """Schema editor that tracks alter_db_table calls."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alter_db_table_calls = []

    def alter_db_table(self, model, old_db_table, new_db_table):
        self.alter_db_table_calls.append({
            'model': model,
            'old_db_table': old_db_table,
            'new_db_table': new_db_table,
        })
        super().alter_db_table(model, old_db_table, new_db_table)

def test_rename_model_with_same_db_table_is_noop():
    """
    Test that RenameModel operation is a noop when the db_table doesn't change.

    This test creates a model with a custom db_table, then renames it but keeps
    the same db_table. The operation should not perform any database operations.
    """

    # Create initial model with custom db_table
    project_state = ProjectState()
    operation1 = migrations.CreateModel(
        'OldModel',
        [
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=100)),
        ],
        options={'db_table': 'custom_table'},
    )

    # Apply the create operation
    with connection.schema_editor() as editor:
        new_state = project_state.clone()
        operation1.state_forwards('test_app', new_state)
        operation1.database_forwards('test_app', editor, project_state, new_state)
        project_state = new_state

    # Verify the table exists with the custom name
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
        assert 'custom_table' in tables, f"Table 'custom_table' not found in {tables}"

    # Check the db_table in the state
    old_model_state = project_state.models['test_app', 'oldmodel']
    print(f"Old model db_table: {old_model_state.options.get('db_table', 'default')}")

    # Now create a RenameModel operation that keeps the same db_table
    operation2 = migrations.RenameModel('OldModel', 'NewModel')

    # Apply the rename operation - first update state
    new_state = project_state.clone()
    operation2.state_forwards('test_app', new_state)

    # Check the db_table in the new state
    new_model_state = new_state.models['test_app', 'newmodel']
    print(f"New model db_table: {new_model_state.options.get('db_table', 'default')}")

    # Create a tracked schema editor
    tracked_editor = TrackedSchemaEditor(connection)

    # Apply the rename operation with our tracked editor
    operation2.database_forwards('test_app', tracked_editor, project_state, new_state)

    # Print the alter_db_table calls
    print(f"Number of alter_db_table calls: {len(tracked_editor.alter_db_table_calls)}")
    for i, call in enumerate(tracked_editor.alter_db_table_calls):
        print(f"Call {i}: {call}")

    # Verify the table still exists with the same name
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
        assert 'custom_table' in tables, f"Table 'custom_table' not found in {tables}"

    # Check that the model was renamed in the state
    assert ('test_app', 'newmodel') in new_state.models, "New model not in state"
    assert ('test_app', 'oldmodel') not in new_state.models, "Old model still in state"

    # The key assertion: alter_db_table should NOT have been called
    # because the db_table didn't change
    assert len(tracked_editor.alter_db_table_calls) == 0, (
        f"Expected no alter_db_table calls, but found: {tracked_editor.alter_db_table_calls}"
    )

    print("Test passed - issue is fixed")

if __name__ == '__main__':
    try:
        test_rename_model_with_same_db_table_is_noop()
        print("\n✓ Test passed")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)