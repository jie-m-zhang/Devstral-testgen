#!/usr/bin/env python
"""
Test to reproduce the issue where sqlmigrate wraps its output in BEGIN/COMMIT
even if the database doesn't support transactional DDL.

The test should:
1. FAIL on base commit (buggy version) - because it will show BEGIN/COMMIT even when can_rollback_ddl=False
2. PASS on head commit (fixed version) - because it will NOT show BEGIN/COMMIT when can_rollback_ddl=False
"""

import io
import sys
from unittest import mock

# Add the testbed to the path
sys.path.insert(0, '/testbed')
sys.path.insert(0, '/testbed/tests')

# Configure Django settings
from django.conf import settings
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
        'migrations',
    ],
    SECRET_KEY='test-secret-key',
)

import django
django.setup()

from django.core.management import call_command
from django.db import connection
from django.test.utils import override_settings

def test_sqlmigrate_respects_can_rollback_ddl():
    """
    Test that sqlmigrate doesn't wrap output in BEGIN/COMMIT when
    the database doesn't support transactional DDL, even for atomic migrations.

    This reproduces the issue described in the ticket.
    """
    # Mock can_rollback_ddl to False to simulate a database that doesn't support transactional DDL
    with mock.patch.object(connection.features, 'can_rollback_ddl', False):
        out = io.StringIO()
        # Use an atomic migration (test_migrations.0001 is atomic by default)
        with override_settings(MIGRATION_MODULES={"migrations": "tests.migrations.test_migrations"}):
            call_command("sqlmigrate", "migrations", "0001", stdout=out)

        output = out.getvalue().lower()
        queries = [q.strip() for q in output.splitlines()]

        # When can_rollback_ddl is False, BEGIN/COMMIT should NOT be in the output
        # even for atomic migrations
        if connection.ops.start_transaction_sql():
            assert connection.ops.start_transaction_sql().lower() not in queries, \
                f"BEGIN transaction found in output when can_rollback_ddl=False: {output}"
        assert connection.ops.end_transaction_sql().lower() not in queries, \
            f"COMMIT transaction found in output when can_rollback_ddl=False: {output}"

    print("Test passed - sqlmigrate correctly respects can_rollback_ddl=False")

if __name__ == "__main__":
    test_sqlmigrate_respects_can_rollback_ddl()