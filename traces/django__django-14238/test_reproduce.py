"""
Test to reproduce the issue with DEFAULT_AUTO_FIELD subclass check failing
for subclasses of BigAutoField and SmallAutoField.
"""

import os
import sys
import django
from django.conf import settings
from django.db import models

# Create a proper app structure
test_app_dir = os.path.join(os.path.dirname(__file__), 'test_app')
os.makedirs(test_app_dir, exist_ok=True)

# Create models.py in the test app
models_py_path = os.path.join(test_app_dir, 'models.py')
with open(models_py_path, 'w') as f:
    f.write("""
from django.db import models

class MyBigAutoField(models.BigAutoField):
    pass

class MySmallAutoField(models.SmallAutoField):
    pass

class MyModel(models.Model):
    pass
""")

# Add the test app directory to sys.path
sys.path.insert(0, os.path.dirname(test_app_dir))

# Configure Django settings
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
            'test_app',
        ],
        USE_TZ=True,
        SECRET_KEY='test-secret-key',
        DEFAULT_AUTO_FIELD='test_app.models.MyBigAutoField',
    )

# Setup Django
django.setup()

# Now try to import the models
try:
    from test_app import models as test_app_models
    print("Successfully imported test_app models")

    # Verify that the custom fields are recognized as AutoField subclasses
    assert issubclass(test_app_models.MyBigAutoField, models.AutoField), "MyBigAutoField should be a subclass of AutoField"
    assert issubclass(test_app_models.MySmallAutoField, models.AutoField), "MySmallAutoField should be a subclass of AutoField"

    print("All assertions passed!")

except ValueError as e:
    print(f"ERROR: {e}")
    print("This is the expected error on the buggy version")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)