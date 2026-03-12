#!/usr/bin/env python
"""
Test to reproduce the logging format issue.

The issue is that the default log format should include the logger name (module name)
instead of just the base filename.

Expected format (after fix):
"%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s"

Old format (buggy):
"%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"
"""

def test_default_log_format():
    """Test that DEFAULT_LOG_FORMAT includes the logger name."""
    from _pytest.logging import DEFAULT_LOG_FORMAT

    # The expected format after the fix
    expected_format = "%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s"

    # The old format (buggy)
    old_format = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"

    print(f"Current DEFAULT_LOG_FORMAT: {DEFAULT_LOG_FORMAT}")
    print(f"Expected format: {expected_format}")
    print(f"Old format: {old_format}")

    # This assertion will fail on the buggy version (base commit)
    # and pass on the fixed version (head commit)
    assert DEFAULT_LOG_FORMAT == expected_format, (
        f"DEFAULT_LOG_FORMAT should be '{expected_format}', "
        f"but got '{DEFAULT_LOG_FORMAT}'"
    )

    print("✓ Test passed - DEFAULT_LOG_FORMAT includes logger name")

if __name__ == "__main__":
    test_default_log_format()