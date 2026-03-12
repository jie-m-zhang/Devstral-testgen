#!/usr/bin/env python
"""
Test to reproduce the issue where shell command crashes when passing
Python code with functions using the -c option.

The issue is that exec() is called without passing a globals dictionary,
so code with functions can't access the global namespace (like 'django').
"""

import os
import sys
import subprocess
import tempfile
import shutil

def test_shell_command_with_function():
    """Test that shell -c works with code containing functions."""

    # Create a temporary directory for Django project
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a minimal Django settings file
        settings_file = os.path.join(temp_dir, 'settings.py')
        with open(settings_file, 'w') as f:
            f.write("""
SECRET_KEY = 'test-secret-key'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
            """)

        # Set DJANGO_SETTINGS_MODULE
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

        # Change to temp directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        # The Python code to execute with a function
        # This should work like: python -c "import django; def f(): print(django.__version__); f()"
        test_code = """
import django
def f():
    return django.__version__
result = f()
print(result)
"""

        # Run the shell command with -c option
        cmd = [sys.executable, '-m', 'django', 'shell', '-c', test_code]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = proc.communicate()

        # On the buggy version, this will fail with NameError
        # On the fixed version, this will succeed and print the Django version
        if proc.returncode != 0:
            print("FAILED: Command returned non-zero exit code")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False

        # Check that the output contains a version number
        if not stdout.strip():
            print("FAILED: No output from command")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False

        # Try to verify it's a valid version string
        output = stdout.strip()
        if not output or not output.replace('.', '').isdigit():
            print(f"FAILED: Unexpected output: {output}")
            return False

        print(f"SUCCESS: Command executed successfully, output: {output}")
        return True

    finally:
        # Cleanup
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)
        if 'DJANGO_SETTINGS_MODULE' in os.environ:
            del os.environ['DJANGO_SETTINGS_MODULE']

if __name__ == "__main__":
    success = test_shell_command_with_function()
    if success:
        print("\nTest PASSED - issue is fixed")
        sys.exit(0)
    else:
        print("\nTest FAILED - issue reproduced")
        sys.exit(1)