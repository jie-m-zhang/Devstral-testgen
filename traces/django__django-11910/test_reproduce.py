"""
Test to reproduce the issue where ForeignKey's to_field parameter gets the old field's name when renaming a PrimaryKey.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django settings
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

# Now import Django components
from django.db import models
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.questioner import MigrationQuestioner
from django.db.migrations.state import ProjectState, ModelState

def test_foreignkey_to_field_rename_field():
    """
    Test that when renaming a field, ForeignKey's to_field
    parameter is updated to point to the new field name.

    This test checks that the deconstructed field value is correct.
    """
    # Define the initial state (before rename)
    # Foo has a field called 'field'
    # Bar has a ForeignKey to Foo with to_field='field'
    before = [
        ModelState('app', 'Foo', [
            ('id', models.AutoField(primary_key=True)),
            ('field', models.IntegerField(unique=True)),
        ]),
        ModelState('app', 'Bar', [
            ('id', models.AutoField(primary_key=True)),
            ('foo', models.ForeignKey('app.Foo', models.CASCADE, to_field='field')),
        ]),
    ]

    # Define the new state (after rename)
    # Foo's field is renamed to 'renamed_field'
    # Bar's ForeignKey should now have to_field='renamed_field'
    after = [
        ModelState('app', 'Foo', [
            ('id', models.AutoField(primary_key=True)),
            ('renamed_field', models.IntegerField(unique=True)),
        ]),
        ModelState('app', 'Bar', [
            ('id', models.AutoField(primary_key=True)),
            ('foo', models.ForeignKey('app.Foo', models.CASCADE, to_field='renamed_field')),
        ]),
    ]

    # Create project states
    before_state = ProjectState()
    for model in before:
        before_state.add_model(model.clone())

    after_state = ProjectState()
    for model in after:
        after_state.add_model(model.clone())

    # Create autodetector with rename questioner
    autodetector = MigrationAutodetector(
        before_state,
        after_state,
        MigrationQuestioner({"ask_rename": True})
    )

    # Get the changes
    changes = autodetector._detect_changes()

    # Check that we have changes for app
    assert 'app' in changes, "No changes detected for app"

    # Get the migration for app
    migration = changes['app'][0]

    # Check that we have a RenameField operation
    rename_ops = [op for op in migration.operations if op.__class__.__name__ == 'RenameField']
    assert len(rename_ops) == 1, f"Expected 1 RenameField operation, got {len(rename_ops)}"
    rename_op = rename_ops[0]
    assert rename_op.old_name == 'field', f"Expected old_name='field', got '{rename_op.old_name}'"
    assert rename_op.new_name == 'renamed_field', f"Expected new_name='renamed_field', got '{rename_op.new_name}'"

    # Now check the deconstructed field value
    # The bug is that the deconstructed field should have to_field='renamed_field'
    # but in the buggy version it has to_field='field' (the old name)
    # We need to get the field from the after_state
    after_model = after_state.models['app', 'bar']
    foo_field = after_model.get_field('foo')
    path, args, kwargs = foo_field.deconstruct()

    print(f"Deconstructed field: path={path}, args={args}, kwargs={kwargs}")
    print(f"to_field in kwargs: {kwargs.get('to_field', 'NOT SET')}")

    # The key assertion: the to_field should be 'renamed_field' (new name)
    # In the buggy version, it will be 'field' (old name)
    assert kwargs.get('to_field') == 'renamed_field', (
        f"ForeignKey to_field should be 'renamed_field' (new name), "
        f"but it is '{kwargs.get('to_field')}' (old name)"
    )

    print("Test passed - ForeignKey to_field correctly updated in deconstructed field")

if __name__ == "__main__":
    test_foreignkey_to_field_rename_field()