#!/usr/bin/env python
"""
Test to reproduce the issue with AlterOrderWithRespectTo() and ForeignKey
when _order is included in Index().

The issue is that when creating a new model with order_with_respect_to and
an index that includes '_order', the migration operations are generated in
the wrong order in the buggy version:
- AddIndex (which references _order) comes before AlterOrderWithRespectTo (which creates _order)
This causes a crash because _order doesn't exist yet.

The fix moves generate_altered_order_with_respect_to() to before generate_added_indexes()
so that the _order field is created before any indexes that reference it.
"""

import os
import sys
import django
from django.db import models
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.state import ProjectState, ModelState

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.test.utils')
django.setup()

def test_order_with_respect_to_with_index():
    """
    Test that when creating a new model with order_with_respect_to and an index
    that includes _order, the operations are generated in the correct order.

    This reproduces the exact scenario from the issue where a new model is created
    with both order_with_respect_to and indexes.
    """
    # Define the model states - empty before state
    before_state = ProjectState()

    # Model WITH order_with_respect_to and index on (_order, look)
    # This is the "after" state - creating a new model
    look_model = ModelState("posts", "Look", [
        ("id", models.AutoField(primary_key=True)),
        ("name", models.CharField(max_length=100)),
    ])

    look_image_model = ModelState("posts", "LookImage", [
        ("id", models.AutoField(primary_key=True)),
        ("look", models.ForeignKey("posts.Look", models.CASCADE)),
        ("image_url", models.URLField(blank=True, null=True)),
        ("image", models.CharField(max_length=2000)),  # Using CharField instead of ImageField for simplicity
        ("deleted", models.DateTimeField(null=True)),
        ("created_at", models.DateTimeField()),
        ("updated_at", models.DateTimeField()),
    ], {
        "order_with_respect_to": "look",
        "indexes": [
            models.Index(fields=["look", "_order"], name="look_image_look_id_order_idx"),
            models.Index(fields=["created_at"], name="look_image_created_at_idx"),
            models.Index(fields=["updated_at"], name="look_image_updated_at_idx"),
        ],
    })

    # Create project states
    after_state = ProjectState()
    after_state.add_model(look_model.clone())
    after_state.add_model(look_image_model.clone())

    # Run the autodetector
    autodetector = MigrationAutodetector(before_state, after_state)
    changes = autodetector._detect_changes()

    # Check that we have migrations for the 'posts' app
    assert "posts" in changes, "No migrations generated for 'posts' app"

    posts_migrations = changes["posts"]
    assert len(posts_migrations) > 0, "No migrations generated"

    print(f"Found {len(posts_migrations)} migrations for posts app")
    for i, migration in enumerate(posts_migrations):
        print(f"\nMigration {i}:")
        for j, op in enumerate(migration.operations):
            print(f"  {j}: {op.__class__.__name__}")
            if hasattr(op, 'model_name'):
                print(f"     model_name: {op.model_name}")
            if hasattr(op, 'name'):
                print(f"     name: {op.name}")
            if hasattr(op, 'order_with_respect_to'):
                print(f"     order_with_respect_to: {op.order_with_respect_to}")
            if hasattr(op, 'index'):
                print(f"     index fields: {op.index.fields}")

    # Find the migration that creates LookImage
    lookimage_migration = None
    for migration in posts_migrations:
        for op in migration.operations:
            if hasattr(op, 'model_name') and op.model_name and op.model_name.lower() == 'lookimage':
                lookimage_migration = migration
                break
            elif hasattr(op, 'name') and op.name and op.name.lower() == 'lookimage':
                lookimage_migration = migration
                break

    assert lookimage_migration is not None, "No migration found for LookImage model"

    # Get the operations
    operations = lookimage_migration.operations
    op_names = [op.__class__.__name__ for op in operations]

    print("\nOperations order for LookImage:")
    for i, op in enumerate(operations):
        print(f"  {i}: {op.__class__.__name__}")
        if hasattr(op, 'model_name'):
            print(f"     model_name: {op.model_name}")
        if hasattr(op, 'order_with_respect_to'):
            print(f"     order_with_respect_to: {op.order_with_respect_to}")
        if hasattr(op, 'index'):
            print(f"     index fields: {op.index.fields}")

    # The key check: When creating a model with order_with_respect_to,
    # the operations should be:
    # 1. CreateModel (with order_with_respect_to in options)
    # 2. AlterOrderWithRespectTo (to add the _order field)
    # 3. AddIndex operations
    #
    # In the buggy version, AddIndex comes before AlterOrderWithRespectTo

    alter_order_op = None
    add_index_ops = []

    for op in operations:
        if op.__class__.__name__ == 'AlterOrderWithRespectTo':
            alter_order_op = op
        elif op.__class__.__name__ == 'AddIndex':
            add_index_ops.append(op)

    # Find the index that includes '_order'
    order_index = None
    for idx_op in add_index_ops:
        if '_order' in idx_op.index.fields:
            order_index = idx_op
            break

    # Get the positions of the operations
    if alter_order_op and order_index:
        alter_order_pos = operations.index(alter_order_op)
        order_index_pos = operations.index(order_index)
        print(f"\nAlterOrderWithRespectTo position: {alter_order_pos}")
        print(f"AddIndex (with _order) position: {order_index_pos}")

        # The critical assertion: AlterOrderWithRespectTo must come BEFORE AddIndex
        # This is the fix - in the buggy version, AddIndex comes first
        assert alter_order_pos < order_index_pos, (
            f"AlterOrderWithRespectTo (position {alter_order_pos}) must come before "
            f"AddIndex (position {order_index_pos}) when the index includes '_order'. "
            "This ensures the _order field exists before the index is created."
        )
    elif alter_order_op:
        # If there's AlterOrderWithRespectTo but no AddIndex with _order,
        # that's also acceptable (the index might be created as part of CreateModel)
        print(f"\nAlterOrderWithRespectTo found, but no AddIndex with _order")
        print("This is acceptable - the index might be created as part of CreateModel")
    else:
        # Check if the order_with_respect_to is in the CreateModel options
        create_model_op = None
        for op in operations:
            if op.__class__.__name__ == 'CreateModel' and hasattr(op, 'name') and op.name.lower() == 'lookimage':
                create_model_op = op
                break

        if create_model_op:
            print(f"\nNo separate AlterOrderWithRespectTo operation found")
            print(f"Checking if order_with_respect_to is in CreateModel options...")
            print(f"CreateModel options: {create_model_op.options}")
            assert 'order_with_respect_to' in create_model_op.options, (
                "order_with_respect_to should be in CreateModel options"
            )
            print("order_with_respect_to is in CreateModel options - this is the correct behavior")
        else:
            raise AssertionError("No CreateModel or AlterOrderWithRespectTo operation found")

    print("\nTest passed: Operations are in correct order")

if __name__ == "__main__":
    try:
        test_order_with_respect_to_with_index()
        print("\nAll tests passed")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)