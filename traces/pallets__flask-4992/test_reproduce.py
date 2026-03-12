import os
import tempfile
import sys

# Create a temporary directory for our test
test_dir = tempfile.mkdtemp()
config_file = os.path.join(test_dir, "config.toml")

# Create a simple TOML config file
toml_content = """
SECRET_KEY = "test-secret-key"
DEBUG = true
DATABASE_URI = "sqlite:///test.db"
"""

with open(config_file, "w") as f:
    f.write(toml_content)

# Add the test directory to sys.path so we can import flask
sys.path.insert(0, "/testbed/src")

import flask
import tomllib

def test_toml_config_loading():
    """Test that we can load TOML config files using tomllib.load()"""
    # Create a Flask app
    app = flask.Flask(__name__)

    # Try to load the TOML config file with text=False (binary mode)
    try:
        app.config.from_file(config_file, load=tomllib.load, text=False)
        print("SUCCESS: Config loaded successfully")
        print(f"SECRET_KEY: {app.config.get('SECRET_KEY')}")
        print(f"DEBUG: {app.config.get('DEBUG')}")
        print(f"DATABASE_URI: {app.config.get('DATABASE_URI')}")
        return True
    except TypeError as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_toml_config_loading()
    if not success:
        print("\nTest failed as expected on base commit (text mode issue)")
        sys.exit(1)
    else:
        print("\nTest passed on head commit (text parameter works)")
        sys.exit(0)