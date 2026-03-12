#!/usr/bin/env python
"""
Test to reproduce the PostgreSQL dbshell parameter ordering issue.

The issue: psql expects all options to proceed the database name, if provided.
In the buggy version, parameters are added AFTER the database name, causing psql to ignore them.
In the fixed version, parameters are added BEFORE the database name.
"""

from django.db.backends.postgresql.client import DatabaseClient

def test_parameter_ordering():
    """
    Test that additional parameters are passed before the database name.

    This test reproduces the issue where parameters like -c "select * from table"
    are ignored by psql when they come after the database name.
    """
    # Test case 1: Simple parameter like --help
    args, env = DatabaseClient.settings_to_cmd_args_env(
        {"NAME": "testdb"},
        ["--help"]
    )

    # The correct order should be: psql --help testdb
    # NOT: psql testdb --help
    expected_args = ["psql", "--help", "testdb"]

    print(f"Generated args: {args}")
    print(f"Expected args: {expected_args}")

    # This assertion will FAIL on buggy code (parameters after dbname)
    # This assertion will PASS on fixed code (parameters before dbname)
    assert args == expected_args, (
        f"Parameters should come before database name. "
        f"Expected {expected_args}, got {args}"
    )

    # Test case 2: More complex parameter like -c with a query
    args, env = DatabaseClient.settings_to_cmd_args_env(
        {"NAME": "testdb"},
        ["-c", "select * from some_table;"]
    )

    expected_args = ["psql", "-c", "select * from some_table;", "testdb"]

    print(f"Generated args: {args}")
    print(f"Expected args: {expected_args}")

    assert args == expected_args, (
        f"Parameters should come before database name. "
        f"Expected {expected_args}, got {args}"
    )

    # Test case 3: Multiple parameters
    args, env = DatabaseClient.settings_to_cmd_args_env(
        {"NAME": "testdb", "USER": "testuser", "HOST": "localhost", "PORT": "5432"},
        ["-c", "select 1;", "-v", "ON_ERROR_STOP=1"]
    )

    expected_args = [
        "psql",
        "-U", "testuser",
        "-h", "localhost",
        "-p", "5432",
        "-c", "select 1;",
        "-v", "ON_ERROR_STOP=1",
        "testdb"
    ]

    print(f"Generated args: {args}")
    print(f"Expected args: {expected_args}")

    assert args == expected_args, (
        f"Parameters should come before database name. "
        f"Expected {expected_args}, got {args}"
    )

    print("All tests passed - issue is fixed!")

if __name__ == "__main__":
    test_parameter_ordering()