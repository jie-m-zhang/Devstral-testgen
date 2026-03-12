"""
Test to reproduce the INTERNALERROR when exception in __repr__ issue.

The issue is in saferepr.py's _format_repr_exception function.
On the buggy version, it tries to access obj.__class__.__name__ which triggers
__getattribute__ and causes a RuntimeError: No active exception to reraise.
On the fixed version, it uses type(obj).__name__ which doesn't trigger __getattribute__.
"""

import sys
sys.path.insert(0, '/testbed/src')

from _pytest._io.saferepr import saferepr

class SomeClass:
    def __getattribute__(self, attr):
        raise RuntimeError("Exception in __getattribute__")

    def __repr__(self):
        raise RuntimeError("Exception in __repr__")

def test_reproduce_issue():
    """
    This test directly exercises the saferepr functionality.
    On the buggy version, saferepr will crash when trying to format the object.
    On the fixed version, saferepr will handle it gracefully.
    """
    obj = SomeClass()

    # This should work on the fixed version but crash on the buggy version
    try:
        result = saferepr(obj)
        # On the fixed version, we should get a string representation
        assert isinstance(result, str), f"Expected string, got {type(result)}"
        assert "SomeClass" in result, f"Expected 'SomeClass' in result, got: {result}"
        print(f"SUCCESS: saferepr handled the object correctly: {result}")
        return 0
    except RuntimeError as e:
        # On the buggy version, we'll get a RuntimeError: No active exception to reraise
        if "No active exception to reraise" in str(e):
            print(f"FAILED: Buggy behavior detected - {e}")
            return 1
        else:
            # Some other RuntimeError
            print(f"UNEXPECTED: Different RuntimeError - {e}")
            return 1
    except Exception as e:
        print(f"UNEXPECTED: Different exception - {type(e).__name__}: {e}")
        return 1

if __name__ == "__main__":
    exit_code = test_reproduce_issue()
    sys.exit(exit_code)