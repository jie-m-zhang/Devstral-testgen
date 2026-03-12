"""
Test to reproduce the issue where method_decorator() doesn't preserve wrapper assignments.

The issue is that when a decorator uses @wraps(func), it expects the wrapped function
to have attributes like __name__, __module__, etc. But when method_decorator is used,
it creates a partial object that doesn't have these attributes.
"""

from functools import wraps
from django.utils.decorators import method_decorator

# Create a logger decorator that uses wraps
def logger(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # This will fail if func doesn't have __name__ attribute
        # which happens when func is a partial object
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = str(e)
        finally:
            # This line will trigger the AttributeError if func is a partial
            method_name = func.__name__
            print(f"{method_name} called with args: {args} and kwargs: {kwargs} resulting: {result}")
        return result
    return inner

class Test:
    @method_decorator(logger)
    def hello_world(self):
        return "hello"

def test_issue_reproduction():
    """
    Test that reproduces the AttributeError when method_decorator is used
    with a decorator that uses @wraps.
    """
    try:
        # This should fail with AttributeError: 'functools.partial' object has no attribute '__name__'
        result = Test().hello_world()
        # If we get here, the issue is fixed
        assert result == "hello", f"Expected 'hello', got '{result}'"
        print("Test passed - issue is fixed")
    except AttributeError as e:
        # This is the expected error on the buggy version
        assert "'functools.partial' object has no attribute '__name__'" in str(e), \
            f"Expected AttributeError about '__name__', got: {e}"
        print(f"Test failed (as expected on buggy version) - AttributeError: {e}")
        raise  # Re-raise to make the test fail

if __name__ == "__main__":
    test_issue_reproduction()