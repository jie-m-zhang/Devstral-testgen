"""
Test to reproduce the issue with skip() error message at module level.

This test creates a test module that uses skip() at module level without allow_module_level=True,
then verifies that the error message is improved in the fixed version.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

def test_skip_module_level_error_message():
    """
    Test that the error message for using skip() at module level is improved.

    The test should:
    - FAIL on base commit: error message doesn't mention allow_module_level
    - PASS on head commit: error message mentions allow_module_level=True
    """

    # Create a temporary directory for our test module
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a test module that uses skip() at module level without allow_module_level=True
        test_module_content = '''
from pytest import skip
import sys

# This will trigger the error - skip() at module level without allow_module_level=True
if sys.version_info < (3, 10):
    skip(msg="Requires Python >= 3.10")

def test_example():
    assert True
'''

        test_file = tmpdir_path / "test_skip_module.py"
        test_file.write_text(test_module_content)

        # Run pytest on the test file and capture the output
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v"],
            capture_output=True,
            text=True,
            cwd="/testbed"
        )

        # Check that pytest failed (as expected)
        assert result.returncode != 0, f"Expected pytest to fail, but it succeeded. stdout: {result.stdout}"

        # Combine stdout and stderr to find the error message
        combined_output = result.stdout + result.stderr

        print(f"Combined output: {combined_output}")

        # On the base commit, the error message should NOT mention allow_module_level
        # On the head commit, the error message SHOULD mention allow_module_level=True

        # Check if the error message contains the improved text
        if "allow_module_level=True" in combined_output:
            print("✓ Error message correctly mentions allow_module_level=True")
            return True
        else:
            print("✗ Error message does NOT mention allow_module_level=True")
            print("This is the expected behavior on the base commit (buggy version)")
            return False

if __name__ == "__main__":
    success = test_skip_module_level_error_message()
    if not success:
        print("\nTest FAILED (as expected on base commit)")
        sys.exit(1)
    else:
        print("\nTest PASSED (as expected on head commit)")
        sys.exit(0)