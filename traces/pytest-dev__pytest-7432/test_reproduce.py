"""
Test to reproduce the issue where --runxfail breaks pytest.mark.skip location reporting.

The issue: When using @pytest.mark.skip, the skip location should point to the test item itself.
Without --runxfail: SKIPPED [1] test_file.py:3: unconditional skip (correct)
With --runxfail: SKIPPED [1] src/_pytest/skipping.py:238: unconditional skip (wrong)

This test verifies that the skip location is reported correctly even with --runxfail.
"""

import subprocess
import sys
import tempfile
import os

def test_skip_location_with_runxfail():
    """Test that skip location reporting works correctly with --runxfail flag."""

    # Create a temporary test file
    test_content = '''
import pytest

@pytest.mark.skip
def test_skip_location():
    assert 0
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        test_file = f.name

    try:
        # Run pytest with -rs --runxfail
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', test_file, '-rs', '--runxfail'],
            capture_output=True,
            text=True,
            cwd='/testbed'
        )

        print("Return code:", result.returncode)
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)

        # Check that the output contains the correct location
        # It should point to the test file, not to skipping.py
        output = result.stdout

        # The test file path should appear in the skip message
        # Format should be: SKIPPED [1] <test_file>:3: unconditional skip
        if test_file in output and 'unconditional skip' in output:
            # Extract the line that contains the skip information
            skip_lines = [line for line in output.split('\n') if 'SKIPPED' in line and 'unconditional skip' in line]
            if skip_lines:
                skip_line = skip_lines[0]
                print(f"Found skip line: {skip_line}")

                # Check that it points to our test file, not to skipping.py
                if 'skipping.py' in skip_line:
                    print(f"ERROR: Skip location incorrectly points to skipping.py: {skip_line}")
                    return False
                elif test_file in skip_line:
                    print(f"SUCCESS: Skip location correctly points to test file: {skip_line}")
                    return True
                else:
                    print(f"ERROR: Skip location doesn't point to expected file: {skip_line}")
                    return False
            else:
                print("ERROR: No skip line found in output")
                return False
        else:
            print("ERROR: Test file or 'unconditional skip' not found in output")
            return False

    finally:
        # Clean up the temporary file
        os.unlink(test_file)

if __name__ == "__main__":
    success = test_skip_location_with_runxfail()
    if success:
        print("\n✓ Test PASSED - Skip location is correctly reported with --runxfail")
        sys.exit(0)
    else:
        print("\n✗ Test FAILED - Skip location is incorrectly reported with --runxfail")
        sys.exit(1)